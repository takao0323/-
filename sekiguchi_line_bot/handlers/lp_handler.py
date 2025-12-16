#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
③サービス説明（LP） ハンドラー
"""

from linebot.models import (
    TextSendMessage, TemplateSendMessage,
    CarouselTemplate, CarouselColumn,
    MessageAction, URIAction
)


def handle_lp(line_bot_api, event):
    """
    サービス説明（LP）を表示
    カルーセル形式で訴求
    """

    # カルーセルメッセージ作成
    carousel_template = CarouselTemplate(columns=[
        # カード1: サービス概要
        CarouselColumn(
            title='関口式ダイエットメンター',
            text='フィジークマスターズ世界一×指導歴30年×人格搭載AI',
            actions=[
                MessageAction(label='次へ >', text='LP_次へ_2')
            ]
        ),
        # カード2: 指導哲学
        CarouselColumn(
            title='関口の指導哲学',
            text='100%のトレーナー=25%チアリーダー×コメディアン×バーテンダー×専門家',
            actions=[
                MessageAction(label='次へ >', text='LP_次へ_3')
            ]
        ),
        # カード3: プラン説明
        CarouselColumn(
            title='2つのプラン',
            text='ライト(2%/月)とハード(4%/月)から選択。どちらも科学的に安全',
            actions=[
                MessageAction(label='次へ >', text='LP_次へ_4')
            ]
        ),
        # カード4: 料金
        CarouselColumn(
            title='料金プラン',
            text='月額990円で理想の体を手に入れましょう！',
            actions=[
                URIAction(label='申し込む', uri='https://example.com/signup')
            ]
        )
    ])

    template_message = TemplateSendMessage(
        alt_text='関口式ダイエットメンター サービス説明',
        template=carousel_template
    )

    line_bot_api.reply_message(
        event.reply_token,
        template_message
    )
