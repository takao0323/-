#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⑤交流の場（グループライン） ハンドラー
コミュニティ機能で仲間と励まし合う
"""

import os
from linebot.models import (
    TextSendMessage, TemplateSendMessage, ButtonsTemplate,
    URIAction, FlexSendMessage, BubbleContainer, BoxComponent,
    TextComponent, ButtonComponent, URIComponentAction
)


def handle_group_menu(line_bot_api, event):
    """
    グループメニューがタップされた時の処理
    """
    group_invite_url = os.getenv('GROUP_LINE_INVITE_URL', 'https://line.me/R/ti/g/xxxxx')

    # Flex Messageでより魅力的な招待画面を作成
    flex_message = FlexSendMessage(
        alt_text='🤝 交流の場への招待',
        contents=BubbleContainer(
            hero=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(
                        text='🤝 交流の場',
                        size='xxl',
                        weight='bold',
                        color='#1DB446',
                        align='center'
                    )
                ],
                background_color='#F0F0F0',
                padding_all='20px'
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(
                        text='仲間と励まし合おう！',
                        size='lg',
                        weight='bold',
                        wrap=True,
                        margin='md'
                    ),
                    TextComponent(
                        text='関口式ダイエットメンターを\n利用している仲間たちと\n一緒に頑張りましょう！',
                        size='sm',
                        color='#666666',
                        wrap=True,
                        margin='md'
                    ),
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            create_feature_row('✅', '体重・食事報告を共有'),
                            create_feature_row('✅', '成功体験を投稿'),
                            create_feature_row('✅', '悩み相談・アドバイス'),
                            create_feature_row('✅', '関口botからの応援'),
                            create_feature_row('✅', 'モチベーション維持'),
                        ]
                    ),
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            TextComponent(
                                text='💬 現在のメンバー',
                                size='md',
                                weight='bold',
                                color='#1DB446'
                            ),
                            TextComponent(
                                text='120名の仲間が参加中！',
                                size='sm',
                                color='#666666',
                                margin='xs'
                            )
                        ]
                    )
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    ButtonComponent(
                        style='primary',
                        height='sm',
                        action=URIComponentAction(
                            label='グループに参加する',
                            uri=group_invite_url
                        ),
                        color='#1DB446'
                    ),
                    TextComponent(
                        text='※参加は任意です\n※ニックネームでの参加も可能',
                        size='xxs',
                        color='#999999',
                        align='center',
                        margin='md'
                    )
                ]
            )
        )
    )

    # コミュニティのルール説明
    rules_message = TextSendMessage(text="""📜 コミュニティのルール

━━━━━━━━━━━━━━━

【大切にしていること】
🎺 お互いを応援し合う
🍸 お互いの頑張りを認め合う
🎭 楽しく、前向きに
🎓 科学的根拠を大切に

【禁止事項】
❌ 他人を否定する発言
❌ 商品・サービスの勧誘
❌ プライバシーの侵害

【投稿例】
✅「今日も1km走れた！」
✅「停滞期で辛いけど頑張る」
✅「おすすめのレシピ教えて」
✅「-2kg達成しました！」

━━━━━━━━━━━━━━━

関口botも定期的に
励ましのメッセージを
投稿します！

一緒に頑張りましょう💪""")

    line_bot_api.reply_message(
        event.reply_token,
        [flex_message, rules_message]
    )


def create_feature_row(icon, text):
    """
    機能一覧の行を作成

    Args:
        icon: アイコン文字
        text: 説明文

    Returns:
        BoxComponent: 行コンポーネント
    """
    return BoxComponent(
        layout='horizontal',
        contents=[
            TextComponent(
                text=icon,
                size='sm',
                color='#1DB446',
                flex=0
            ),
            TextComponent(
                text=text,
                size='sm',
                color='#666666',
                wrap=True,
                flex=1,
                margin='sm'
            )
        ]
    )


def send_group_encouragement(line_bot_api, group_id):
    """
    グループに定期的な励ましメッセージを送信
    スケジューラーから呼び出される

    Args:
        line_bot_api: LINE Bot API インスタンス
        group_id: グループID
    """
    import random
    from datetime import datetime

    messages = [
        """🎺 関口からのメッセージ

おはようございます！
今日も元気にいきましょう！

小さな一歩でも、
昨日より前に進めば
それは成長です。

体重計に乗る。
それだけでも素晴らしい。

みんな、今日も一緒に
頑張りましょう💪

#継続は力なり""",
        """🍸 関口からのメッセージ

こんにちは、関口です。

順調な人も、
苦しんでいる人も、
みんな頑張っていますね。

大切なのは、
他人と比べることじゃなく
昨日の自分と比べること。

少しでも前進していれば
それで十分です。

あなたのペースで大丈夫。
一緒に進んでいきましょう。

#マイペース #自分との戦い""",
        """🎓 関口からのメッセージ

今日は科学的なお話を。

体重は「階段状」に落ちます。

停滞 → 減少 → 停滞 → 減少

これが正常なパターン。

停滞期に入っても
諦めないでください。

次の「落ちる」タイミングが
必ず来ます。

科学が証明しています。
信じて続けましょう！

#科学的ダイエット #停滞期""",
        """🎭 関口からのメッセージ

週の真ん中、
お疲れ様です！

ここで質問です（笑）

「今週、体重計に
何回乗りましたか？」

0回の人→明日から頑張ろう！
1-2回の人→いい感じ！
3回以上の人→完璧です！

大切なのは回数じゃなく
「乗ろうとした気持ち」

その気持ちが、
あなたを変えていきます。

#体重計は友達""",
        """🎺🎭🍸🎓 関口からのメッセージ

金曜日ですね！
今週もお疲れ様でした！

【今週の振り返り】
良かったこと1つ、
書き込んでみてください！

「1kg減った！」
「毎日記録できた！」
「運動を3回した！」

どんな小さなことでもOK。

良かったことを
言葉にすることで
モチベーションが上がります。

みんなの良かったこと、
聞かせてください！

#週間振り返り #ポジティブ思考"""
    ]

    # 曜日に応じてメッセージを選択（または<br/>ランダム）
    weekday = datetime.now().weekday()
    if weekday < len(messages):
        message = messages[weekday]
    else:
        message = random.choice(messages)

    try:
        line_bot_api.push_message(
            group_id,
            TextSendMessage(text=message)
        )
    except Exception as e:
        print(f"Error sending group encouragement: {e}")


def handle_group_post(line_bot_api, event):
    """
    グループ内での投稿に対して自動返信
    特定のキーワードに反応する

    Args:
        line_bot_api: LINE Bot API インスタンス
        event: LINE Bot event
    """
    text = event.message.text.lower()

    # キーワード検出と自動返信
    if any(word in text for word in ['達成', '成功', '減った', 'kg減']):
        reply = """🎺 おめでとうございます！

素晴らしい成果ですね！
その努力、確実に報われています。

この調子で一緒に
頑張りましょう💪"""
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

    elif any(word in text for word in ['停滞', '減らない', '辛い', '苦しい']):
        reply = """🍸 その気持ち、よくわかります。

停滞期は誰にでも来ます。
でも、必ず抜けられます。

ここで諦めずに続けた人は
100%、成功しています。

あなたも必ず乗り越えられます。
一緒に頑張りましょう。"""
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

    elif any(word in text for word in ['教えて', '質問', 'どうすれば']):
        reply = """🎓 質問ですね！

詳しいQ&Aは
リッチメニューの
「⑥困ったとき」から
確認できます。

それでも解決しない場合は
ここで質問してください。

みんなで助け合いましょう！"""
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
