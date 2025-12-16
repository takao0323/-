#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
①今日の体重 ハンドラー
"""

import os
import sys
from datetime import datetime
from linebot.models import TextSendMessage, ImageSendMessage

# 既存のmain.pyからロジックをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from sekiguchi_bot.main import (
    get_previous_weight,
    save_weight_record,
    generate_weight_graph,
    get_sekiguchi_philosophy_message
)

# ユーザーの入力モード管理（実際は DBやRedisで管理）
user_modes = {}


def handle_weight_menu(line_bot_api, event):
    """
    体重メニューがタップされた時の処理
    """
    user_id = event.source.user_id

    # 体重入力モードをON
    user_modes[user_id] = 'weight_input'

    reply_text = """⚖️ 今日の体重を記録しましょう！

体重を数値で入力してください
（例: 65.5）

小数点第一位まで入力できます"""

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


def is_weight_input_mode(user_id):
    """
    ユーザーが体重入力モードかどうか確認
    """
    return user_modes.get(user_id) == 'weight_input'


def handle_weight_input(line_bot_api, event, weight):
    """
    体重が入力された時の処理
    """
    user_id = event.source.user_id
    name = get_user_name(user_id)  # LINEプロフィールから名前取得

    # 体重入力モードをOFF
    if user_id in user_modes:
        del user_modes[user_id]

    # 前回の体重を取得
    previous_weight = get_previous_weight(name)

    # 体重を記録
    save_weight_record(name, weight)

    # グラフ生成
    generate_weight_graph(name)
    graph_path = f"weight_graph_{name}.png"

    # 体重変化を判定
    if previous_weight is not None:
        weight_change = weight - previous_weight
        if weight_change > 0:
            situation = "weight_up"
            change_text = f"前日: {previous_weight:.1f}kg (+{weight_change:.1f}kg)"
        elif weight_change < 0:
            situation = "weight_down"
            change_text = f"前日: {previous_weight:.1f}kg ({weight_change:.1f}kg)"
        else:
            situation = "weight_same"
            change_text = f"前日: {previous_weight:.1f}kg (変化なし)"
    else:
        situation = "general"
        change_text = "初回記録"

    # 関口の4要素メッセージ取得
    philosophy_msg = get_sekiguchi_philosophy_message(name, situation)

    # メッセージ作成
    reply_text = f"""📊 体重記録完了！

今日: {weight:.1f}kg
{change_text}

{"=" * 30}
【関口の指導哲学メッセージ】
100%のトレーナー = 25%チアリーダー×25%コメディアン×25%バーテンダー×25%専門家
{"=" * 30}

🎺 チアリーダー（応援する）:
{philosophy_msg['cheerleader']}

🎭 コメディアン（楽しませる）:
{philosophy_msg['comedian']}

🍸 バーテンダー（傾聴する）:
{philosophy_msg['bartender']}

🎓 専門家（科学的根拠）:
{philosophy_msg['expert']}

{"=" * 30}

グラフを送信します...📈"""

    # メッセージとグラフを送信
    messages = [TextSendMessage(text=reply_text)]

    # グラフが生成されていれば送信
    if os.path.exists(graph_path):
        # グラフをLINEにアップロードして送信
        # （実際の実装では画像をLINE Content APIにアップロード）
        messages.append(
            TextSendMessage(text="※本番環境ではグラフ画像が表示されます")
        )

    line_bot_api.reply_message(
        event.reply_token,
        messages
    )


def get_user_name(user_id):
    """
    ユーザー名を取得
    実際はDBから取得 or LINEプロフィールAPIを使用
    """
    # 仮実装：user_idをそのまま使用
    # 本番環境ではDBから取得
    return f"user_{user_id[:8]}"
