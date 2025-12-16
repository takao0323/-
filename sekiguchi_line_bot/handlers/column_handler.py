#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
④関口コラム（毎日配信） ハンドラー
"""

from datetime import datetime
from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction


# コラムコンテンツ（日替わり）
COLUMN_CONTENTS = {
    0: {  # 月曜
        "title": "年齢は関係ない！",
        "content": """【関口コラム #1】
━━━━━━━━━━━━━━━
🎺 年齢は関係ない！
━━━━━━━━━━━━━━━

おはようございます、関口です！

今日は「年齢」について話します。

🎭 よく「もう歳だから...」って
言う人いますよね。でも待って！
私は49歳で世界一になりました（笑）

🍸 諦めたくなる気持ち、
よくわかります。でもね...

🎓 科学的に証明されています。
80代でも筋肉は成長します。
大切なのは「続けること」だけ。

今日も一緒に頑張りましょう！
━━━━━━━━━━━━━━━"""
    },
    1: {  # 火曜
        "title": "タンパク質の重要性",
        "content": """【関口コラム #2】
━━━━━━━━━━━━━━━
🍖 タンパク質の重要性
━━━━━━━━━━━━━━━

🎺 今日はタンパク質の話！
筋肉の材料ですよ！

🎭 タンパク質って、
「プロテイン」のことです。
難しく考えなくてOK（笑）

🍸 忙しいと、つい炭水化物
ばかりになりがちですよね

🎓 体重1kgあたり1.5-2gの
タンパク質が理想です。
肉、魚、卵、大豆製品を
意識的に摂りましょう！
━━━━━━━━━━━━━━━"""
    },
    # ... 残りの曜日も同様に実装
}


def handle_column_menu(line_bot_api, event):
    """
    コラムメニューがタップされた時の処理
    """
    # 今日の曜日を取得（0=月曜）
    weekday = datetime.now().weekday()

    column = COLUMN_CONTENTS.get(weekday, COLUMN_CONTENTS[0])

    # クイックリプライでアーカイブへのリンクを追加
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="過去のコラムを見る", text="コラムアーカイブ")),
        QuickReplyButton(action=MessageAction(label="今日の体重を記録", text="①今日の体重"))
    ])

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=column['content'], quick_reply=quick_reply)
    )


def send_daily_column(line_bot_api, user_ids):
    """
    毎朝8時にコラムを配信
    APSchedulerから呼び出される
    """
    weekday = datetime.now().weekday()
    column = COLUMN_CONTENTS.get(weekday, COLUMN_CONTENTS[0])

    for user_id in user_ids:
        line_bot_api.push_message(
            user_id,
            TextSendMessage(text=column['content'])
        )
