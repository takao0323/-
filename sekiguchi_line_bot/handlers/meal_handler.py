#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
②今日の食事 ハンドラー（Gemini AI 自動解析）
"""

import os
import requests
from io import BytesIO
from PIL import Image
import google.generativeai as genai
from linebot.models import TextSendMessage
import json
import re

# Gemini API 初期化
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ユーザーの食事記録モード管理
user_meal_mode = {}


def is_meal_input_mode(user_id):
    """食事記録モードかどうか"""
    return user_id in user_meal_mode and user_meal_mode[user_id]


def handle_meal_menu(line_bot_api, event):
    """
    食事メニューがタップされた時の処理
    """
    user_id = event.source.user_id

    # 食事記録モードON
    user_meal_mode[user_id] = True

    reply_text = """🍽️ 今日の食事を記録しましょう！

📸 食事の写真を送ってください

AIが自動的に：
✓ 食事内容を認識
✓ カロリーを推定
✓ PFCバランスを分析
✓ フィードバックを提供

※ 写真は料理全体が写るように撮影してください"""

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


def handle_meal_image(line_bot_api, event):
    """
    食事写真が送られた時の処理（Gemini AI 自動解析）

    Args:
        line_bot_api: LINE Bot APIインスタンス
        event: MessageEvent
    """
    user_id = event.source.user_id
    message_id = event.message.id

    try:
        # 1. 画像をLINEからダウンロード
        message_content = line_bot_api.get_message_content(message_id)
        image_data = BytesIO(message_content.content)
        image = Image.open(image_data)

        # 2. Gemini APIで画像解析
        analysis_result = analyze_meal_with_gemini(image)

        if not analysis_result:
            # 解析失敗時
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="⚠️ 画像の解析に失敗しました。もう一度撮影してください。")
            )
            return

        # 3. フィードバックメッセージ生成
        feedback_message = generate_meal_feedback(analysis_result)

        # 4. 返信
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=feedback_message)
        )

        # 5. 食事記録モードOFF
        if user_id in user_meal_mode:
            del user_meal_mode[user_id]

    except Exception as e:
        print(f"Error in handle_meal_image: {e}")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="⚠️ エラーが発生しました。もう一度お試しください。")
        )
        # エラー時もモードOFF
        if user_id in user_meal_mode:
            del user_meal_mode[user_id]


def analyze_meal_with_gemini(image):
    """
    Gemini AI で食事画像を解析

    Args:
        image: PIL.Image オブジェクト

    Returns:
        dict: {
            'dishes': str,
            'total_calories': float,
            'protein_g': float,
            'fat_g': float,
            'carbs_g': float,
            'balance_evaluation': str
        }
        or None (解析失敗時)
    """
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set")
        return None

    try:
        # Gemini Pro Vision モデル使用
        model = genai.GenerativeModel('gemini-1.5-flash')

        # プロンプト作成
        prompt = """この食事画像を分析して、以下の情報をJSON形式で返してください：

1. dishes: 料理名（複数ある場合はカンマ区切り）
2. total_calories: 総カロリー（kcal）の推定値（数値のみ）
3. protein_g: タンパク質（g）の推定値（数値のみ）
4. fat_g: 脂質（g）の推定値（数値のみ）
5. carbs_g: 炭水化物（g）の推定値（数値のみ）
6. balance_evaluation: PFCバランスの評価（「良好」「タンパク質不足」「炭水化物過多」など）

必ずJSON形式で返してください。例：
{
  "dishes": "鶏胸肉のグリル、ブロッコリー、玄米",
  "total_calories": 650,
  "protein_g": 45,
  "fat_g": 15,
  "carbs_g": 70,
  "balance_evaluation": "良好"
}"""

        # 画像解析実行
        response = model.generate_content([prompt, image])

        # レスポンス解析
        response_text = response.text.strip()

        # JSON部分を抽出（```json ... ``` の場合も対応）
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # JSONブロックがない場合、全体をJSONとして解析
            json_str = response_text

        # JSON パース
        result = json.loads(json_str)

        # 必須フィールドチェック
        required_fields = ['dishes', 'total_calories', 'protein_g', 'fat_g', 'carbs_g', 'balance_evaluation']
        if all(field in result for field in required_fields):
            return result
        else:
            print(f"Missing fields in Gemini response: {result}")
            return None

    except Exception as e:
        print(f"Error in analyze_meal_with_gemini: {e}")
        return None


def generate_meal_feedback(analysis_result):
    """
    解析結果からフィードバックメッセージを生成

    Args:
        analysis_result: dict (Gemini解析結果)

    Returns:
        str: フィードバックメッセージ
    """
    dishes = analysis_result.get('dishes', '不明')
    calories = analysis_result.get('total_calories', 0)
    protein = analysis_result.get('protein_g', 0)
    fat = analysis_result.get('fat_g', 0)
    carbs = analysis_result.get('carbs_g', 0)
    balance = analysis_result.get('balance_evaluation', '')

    # PFC比率計算
    total_kcal_from_pfc = (protein * 4) + (fat * 9) + (carbs * 4)
    if total_kcal_from_pfc > 0:
        protein_ratio = (protein * 4 / total_kcal_from_pfc) * 100
        fat_ratio = (fat * 9 / total_kcal_from_pfc) * 100
        carbs_ratio = (carbs * 4 / total_kcal_from_pfc) * 100
    else:
        protein_ratio = fat_ratio = carbs_ratio = 0

    # 4要素哲学メッセージ選択
    expert_msg = generate_expert_message(protein, fat, carbs, balance)
    cheerleader_msg = generate_cheerleader_message(balance)
    bartender_msg = generate_bartender_message(balance)
    comedian_msg = generate_comedian_message(dishes, calories)

    # フィードバック構築
    feedback = f"""🍽️ 食事記録完了！

【AI解析結果】
📋 料理: {dishes}

【栄養情報】
🔥 カロリー: {calories:.0f} kcal

タンパク質: {protein:.1f}g ({protein_ratio:.1f}%)
脂質: {fat:.1f}g ({fat_ratio:.1f}%)
炭水化物: {carbs:.1f}g ({carbs_ratio:.1f}%)

PFCバランス: {balance}

【関口からのフィードバック】

{expert_msg}

{cheerleader_msg}

{bartender_msg}

{comedian_msg}

この調子で頑張りましょう💪"""

    return feedback


def generate_expert_message(protein, fat, carbs, balance):
    """専門家メッセージ生成"""
    if "タンパク質不足" in balance or protein < 20:
        return """🎓 専門家として:
タンパク質が少し不足しています。
1食あたり20g以上を目安に、
鶏肉・魚・卵などを追加しましょう。"""
    elif "炭水化物過多" in balance or carbs > 100:
        return """🎓 専門家として:
炭水化物がやや多めです。
減量中は1食40-60gを目安に
調整していきましょう。"""
    elif "脂質過多" in balance or fat > 30:
        return """🎓 専門家として:
脂質がやや多めです。
揚げ物や油の使用を控えめにして
脂質を1食15-20gに抑えましょう。"""
    else:
        return """🎓 専門家として:
素晴らしいPFCバランスです！
このバランスを継続することで
健康的に減量できます。"""


def generate_cheerleader_message(balance):
    """チアリーダーメッセージ生成"""
    if "良好" in balance:
        return """🎺 チアリーダーとして:
完璧なバランスですね！
この調子で継続していきましょう！"""
    else:
        return """🎺 チアリーダーとして:
記録を続けていますね！素晴らしい！
少しずつ改善していきましょう！"""


def generate_bartender_message(balance):
    """バーテンダーメッセージ生成"""
    if "良好" in balance:
        return """🍸 バーテンダーとして:
バランスを意識できていますね。
素晴らしいです。"""
    else:
        return """🍸 バーテンダーとして:
完璧を目指さなくても大丈夫です。
少しずつ改善していけば良いのです。"""


def generate_comedian_message(dishes, calories):
    """コメディアンメッセージ生成"""
    if calories > 1000:
        return f"""🎭 コメディアンとして:
{calories:.0f}kcal！？
パワフルな食事ですね（笑）
次はもう少し控えめでいきましょう！"""
    elif calories < 300:
        return f"""🎭 コメディアンとして:
{calories:.0f}kcal...
ダイエット頑張りすぎてませんか？（笑）
もう少し食べても大丈夫ですよ！"""
    else:
        return """🎭 コメディアンとして:
いい感じのカロリーですね！
美味しく食べて健康的に痩せましょう！"""
