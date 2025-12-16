#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⑥困ったとき（Q&A） ハンドラー
"""

from linebot.models import (
    TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageAction,
    QuickReply, QuickReplyButton
)

# ユーザーの質問モード管理
user_question_mode = {}

# FAQ データ
FAQ_DATA = {
    "体重が減らない": """Q. 体重が2週間変わりません

━━━━━━━━━━━━━━━
【関口からの回答】

🎺 大丈夫！諦めないで！
停滞期はみんな経験します。

🎭 体重計が「休憩中」なんです（笑）
でも明日突然動き出しますよ！

🍸 2週間頑張ってるのに変化がないと
不安になりますよね。その気持ち、
よくわかります。

🎓 科学的には「停滞期」と呼ばれ、
体が新しい体重に慣れようとしている
時期です。ここで諦めずに続けると
必ず突然ストンと落ちる日が来ます。
━━━━━━━━━━━━━━━""",

    "外食が多い": """Q. 外食が多いのですが...

━━━━━━━━━━━━━━━
【関口からの回答】

🎺 外食でも大丈夫！
選び方次第ですよ！

🎭 毎日自炊は大変ですよね。
私も外食しますよ（笑）

🍸 仕事が忙しいと、
外食になっちゃいますよね

🎓 外食のコツ：
・定食を選ぶ
・揚げ物より焼き物・蒸し物
・ご飯は少なめに
・野菜を追加注文
・汁物でお腹を満たす
━━━━━━━━━━━━━━━""",

    "運動する時間がない": """Q. 運動する時間がありません

━━━━━━━━━━━━━━━
【関口からの回答】

🎺 時間がなくても大丈夫！
10分でもOKです！

🎭 忙しいあなたに朗報！
「ながら運動」という
便利なものがあります（笑）

🍸 仕事に家事に、
時間がないのは当然ですよね

🎓 隙間時間の活用法：
・通勤で一駅歩く
・階段を使う
・歯磨きしながらスクワット
・テレビ見ながらストレッチ
・寝る前に5分だけ筋トレ
━━━━━━━━━━━━━━━"""
}


def handle_qa_menu(line_bot_api, event):
    """
    Q&Aメニューがタップされた時の処理
    """
    reply_text = """❓ 困ったとき Q&A

カテゴリを選んでください："""

    # クイックリプライでカテゴリ選択
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="📋 プランについて", text="QA_プラン")),
        QuickReplyButton(action=MessageAction(label="🍽️ 食事について", text="QA_食事")),
        QuickReplyButton(action=MessageAction(label="💪 トレーニング", text="QA_トレーニング")),
        QuickReplyButton(action=MessageAction(label="⚖️ 体重が減らない", text="FAQ_体重が減らない")),
        QuickReplyButton(action=MessageAction(label="💬 個別質問", text="QA_個別質問"))
    ])

    # よくある質問TOP3も表示
    faq_list = """
━━━━━━━━━━━━━━━
よくある質問TOP3

Q1. 体重が2週間変わりません
Q2. 外食が多いのですが...
Q3. 運動する時間がありません

タップして回答を見る↓"""

    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=reply_text, quick_reply=quick_reply),
            TextSendMessage(
                text=faq_list,
                quick_reply=QuickReply(items=[
                    QuickReplyButton(action=MessageAction(label="Q1", text="FAQ_体重が減らない")),
                    QuickReplyButton(action=MessageAction(label="Q2", text="FAQ_外食が多い")),
                    QuickReplyButton(action=MessageAction(label="Q3", text="FAQ_運動する時間がない"))
                ])
            )
        ]
    )


def is_question_mode(user_id):
    """個別質問モードかどうか"""
    return user_question_mode.get(user_id, False)


def handle_individual_question(line_bot_api, event, question):
    """
    個別質問が送られた時の処理
    """
    user_id = event.source.user_id

    # 質問モードをOFF
    if user_id in user_question_mode:
        del user_question_mode[user_id]

    reply_text = f"""💬 ご質問ありがとうございます！

「{question}」

━━━━━━━━━━━━━━━

🍸 お困りなんですね。
一緒に解決しましょう！

🎺 ご質問は受け付けました。
できるだけ早くお答えします！

🎓 24時間以内に個別に
回答させていただきます。

しばらくお待ちください。

━━━━━━━━━━━━━━━
※この機能は開発中です
※現在はFAQをご利用ください"""

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


def handle_faq_request(line_bot_api, event, faq_key):
    """
    FAQ回答を表示
    """
    answer = FAQ_DATA.get(faq_key, "申し訳ございません。該当するFAQが見つかりませんでした。")

    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="他の質問を見る", text="⑥困ったとき")),
        QuickReplyButton(action=MessageAction(label="個別質問する", text="QA_個別質問"))
    ])

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=answer, quick_reply=quick_reply)
    )
