#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⑤交流の場（グループライン） ハンドラー
"""

import os
from linebot.models import TextSendMessage, TemplateSendMessage, ButtonsTemplate, URIAction


def handle_group_menu(line_bot_api, event):
    """
    グループメニューがタップされた時の処理
    """
    group_invite_url = os.getenv('GROUP_LINE_INVITE_URL', 'https://line.me/R/ti/g/xxxxx')

    reply_text = """🤝 交流の場へようこそ！

関口式ダイエットメンターを
利用している仲間たちと
励まし合いましょう！

【グループでできること】
✅ 体重報告を共有
✅ 成功体験を投稿
✅ 悩み相談
✅ 関口botからの応援コメント

━━━━━━━━━━━━━━━

※グループ参加は任意です
※ニックネームでの参加も可能
※関口botも定期的にコメントします"""

    # ボタンテンプレートで招待リンクを送信
    buttons_template = ButtonsTemplate(
        title='交流の場',
        text='グループLINEで仲間と励まし合おう！',
        actions=[
            URIAction(label='グループに参加する', uri=group_invite_url)
        ]
    )

    template_message = TemplateSendMessage(
        alt_text='交流の場への招待',
        template=buttons_template
    )

    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=reply_text),
            template_message
        ]
    )
