#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
②今日の食事 ハンドラー
"""

from linebot.models import TextSendMessage

# ユーザーの入力モード管理
user_modes = {}
meal_data = {}  # 食事データ一時保存


def handle_meal_menu(line_bot_api, event):
    """
    食事メニューがタップされた時の処理
    """
    user_id = event.source.user_id
    user_modes[user_id] = 'meal_description'

    reply_text = """🍽️ 今日の食事を記録しましょう！

食事の写真を送るか、
内容をテキストで入力してください

（例）
朝：パン、卵、サラダ
昼：定食
夜：魚、野菜炒め"""

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


def is_meal_input_mode(user_id):
    """食事記録モードかどうか"""
    return user_id in user_modes and user_modes[user_id].startswith('meal_')


def handle_meal_input(line_bot_api, event, text):
    """
    食事内容が入力された時の処理
    """
    user_id = event.source.user_id
    mode = user_modes.get(user_id)

    if mode == 'meal_description':
        # 食事内容を保存
        if user_id not in meal_data:
            meal_data[user_id] = {}
        meal_data[user_id]['description'] = text

        # カロリー入力モードへ
        user_modes[user_id] = 'meal_calories'

        reply_text = """📊 栄養情報を入力してください

カロリーを入力（例: 1800）"""

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

    elif mode == 'meal_calories':
        try:
            calories = float(text)
            meal_data[user_id]['calories'] = calories

            # PFC入力モードへ
            user_modes[user_id] = 'meal_pfc'

            reply_text = """続けて PFC を入力してください

タンパク質（g）を入力"""

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
        except ValueError:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="数値で入力してください")
            )

    elif mode == 'meal_pfc':
        # PFC入力処理（簡略化）
        # 実際は3回に分けて入力
        reply_text = """🍽️ 食事記録完了！

【関口からのフィードバック】

🎺 記録を続けていますね！素晴らしい！

🎭 今日も美味しく食べましたか？（笑）

🍸 栄養バランスを意識できていますね

🎓 PFCバランスを保つことで
　　健康的に体重をコントロールできます

この調子で頑張りましょう💪"""

        # モードクリア
        if user_id in user_modes:
            del user_modes[user_id]
        if user_id in meal_data:
            del meal_data[user_id]

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )


def handle_meal_image(line_bot_api, event):
    """
    食事写真が送られた時の処理
    """
    user_id = event.source.user_id

    if user_id not in meal_data:
        meal_data[user_id] = {}

    meal_data[user_id]['has_image'] = True

    reply_text = """📸 写真を受け取りました！

続けてカロリーとPFCを入力してください

カロリーを入力（例: 1800）"""

    user_modes[user_id] = 'meal_calories'

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )
