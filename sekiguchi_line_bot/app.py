#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
関口式ダイエットメンター LINE Bot
メインアプリケーション
"""

import os
import sys
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    ImageMessage, TemplateSendMessage, ButtonsTemplate,
    MessageAction, URIAction, FlexSendMessage
)
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# Flask app初期化
app = Flask(__name__)

# LINE Bot API初期化
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# ハンドラーをインポート
sys.path.append(os.path.dirname(__file__))
from handlers import weight_handler, meal_handler, lp_handler
from handlers import column_handler, group_handler, qa_handler

# スケジューラーをインポート
from scheduler import create_scheduler

# スケジューラーを起動（定期レポート配信用）
report_scheduler = create_scheduler(line_bot_api)


@app.route("/")
def index():
    """ヘルスチェック用"""
    return "関口式ダイエットメンター LINE Bot is running! 🏃‍♂️"


@app.route("/callback", methods=['POST'])
def callback():
    """LINE Webhookエンドポイント"""
    # 署名検証
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """
    テキストメッセージ処理
    リッチメニューからのメッセージを振り分け
    """
    user_id = event.source.user_id
    text = event.message.text

    # リッチメニューのメッセージに応じて処理を振り分け
    if text == "①今日の体重":
        weight_handler.handle_weight_menu(line_bot_api, event)

    elif text == "②今日の食事":
        meal_handler.handle_meal_menu(line_bot_api, event)

    elif text == "③サービス説明":
        lp_handler.handle_lp(line_bot_api, event)

    elif text == "④関口コラム":
        column_handler.handle_column_menu(line_bot_api, event)

    elif text == "⑤交流の場":
        group_handler.handle_group_menu(line_bot_api, event)

    elif text == "⑥困ったとき":
        qa_handler.handle_qa_menu(line_bot_api, event)

    # 体重入力モード（数値が送られてきた場合）
    elif weight_handler.is_weight_input_mode(user_id) and is_number(text):
        weight_handler.handle_weight_input(line_bot_api, event, float(text))

    # 食事記録モード
    elif meal_handler.is_meal_input_mode(user_id):
        meal_handler.handle_meal_input(line_bot_api, event, text)

    # Q&A個別質問モード
    elif qa_handler.is_question_mode(user_id):
        qa_handler.handle_individual_question(line_bot_api, event, text)

    # その他のメッセージ
    else:
        handle_general_message(line_bot_api, event, text)


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """
    画像メッセージ処理
    食事写真の受信
    """
    user_id = event.source.user_id

    if meal_handler.is_meal_input_mode(user_id):
        meal_handler.handle_meal_image(line_bot_api, event)
    else:
        # 食事記録モードではない場合
        reply_text = "食事の写真ですか？\n「②今日の食事」から記録してくださいね！"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )


def handle_general_message(line_bot_api, event, text):
    """
    一般的なメッセージへの応答
    関口の4要素を反映
    """
    # 挨拶など
    if text in ["こんにちは", "おはよう", "こんばんは", "Hello", "Hi"]:
        reply = """🎺 こんにちは！関口です！

今日も一緒に頑張りましょう！

下のメニューから選んでくださいね：
・体重を記録する
・食事を記録する
・今日のコラムを読む"""

    # 応援を求められた時
    elif any(word in text for word in ["頑張", "応援", "励まし", "やる気"]):
        reply = """🎺 いいですね！その気持ち！

🎭 やる気スイッチ、ONになりましたね（笑）

🍸 頑張ろうと思えること自体が素晴らしいです

🎓 継続すれば必ず結果が出ます。それが科学的事実です！

一緒に頑張りましょう💪"""

    # 困っている時
    elif any(word in text for word in ["困", "わから", "難しい", "できない"]):
        reply = """🍸 困っているんですね。大丈夫ですよ

🎺 一緒に解決しましょう！

下のメニューから「⑥困ったとき」を
タップしてください。

よくある質問や、個別相談ができます！"""

    # デフォルト
    else:
        reply = """メッセージありがとうございます！

下のメニューから選んでくださいね：

⚖️ ①今日の体重
🍽️ ②今日の食事
📱 ③サービス説明
📰 ④関口コラム
👥 ⑤交流の場
❓ ⑥困ったとき"""

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )


def is_number(text):
    """文字列が数値かどうか判定"""
    try:
        float(text)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
