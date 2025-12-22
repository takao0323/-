# 関口式ダイエットメンター - API仕様書（Part 3）

**Document Version:** 1.0
**Last Updated:** 2025-12-21
**対象:** 実装エンジニア

---

## 目次

1. [LINE Messaging API 基本設定](#1-line-messaging-api-基本設定)
2. [Webhook 仕様](#2-webhook-仕様)
3. [イベントタイプ別処理](#3-イベントタイプ別処理)
4. [メッセージ送信API](#4-メッセージ送信api)
5. [リッチメニュー設定](#5-リッチメニュー設定)
6. [Flex Message 仕様](#6-flex-message-仕様)
7. [画像送信仕様](#7-画像送信仕様)
8. [プロフィールAPI](#8-プロフィールapi)
9. [エラーハンドリング](#9-エラーハンドリング)
10. [レート制限対応](#10-レート制限対応)
11. [セキュリティ](#11-セキュリティ)

---

## 1. LINE Messaging API 基本設定

### 1.1 必要な認証情報

**環境変数（.env）:**
```bash
# LINE Messaging API
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
LINE_CHANNEL_SECRET=your_channel_secret_here

# Webhook URL
WEBHOOK_URL=https://your-domain.com/webhook

# グループ機能
GROUP_LINE_ID=C1234567890abcdef
GROUP_INVITE_URL=https://line.me/R/ti/g/xxx
```

### 1.2 LINE Bot SDK for Python

**インストール:**
```bash
pip install line-bot-sdk==3.5.0
```

**初期化コード:**
```python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
import os

# API初期化
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
```

### 1.3 LINE Developers コンソール設定

**必須設定項目:**

| 項目 | 設定値 | 説明 |
|-----|-------|-----|
| Webhook URL | `https://your-domain.com/webhook` | イベント受信エンドポイント |
| Webhookの利用 | ON | 必須 |
| 応答メッセージ | OFF | Botが自動応答を制御するため |
| あいさつメッセージ | OFF | カスタムメッセージで対応 |
| 友だち追加時あいさつ | ON | 初回登録フロー用 |
| グループ・複数人トークへの参加 | ON | コミュニティ機能用 |

---

## 2. Webhook 仕様

### 2.1 エンドポイント定義

**Flask アプリケーション:**
```python
from flask import Flask, request, abort

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    LINE Platform からのWebhookを受信
    """
    # 署名検証
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK', 200
```

### 2.2 リクエスト仕様

**HTTPリクエスト:**
```
POST /webhook HTTP/1.1
Host: your-domain.com
Content-Type: application/json
X-Line-Signature: {signature}

{
  "destination": "Uxxxxx",
  "events": [
    {
      "type": "message",
      "message": {
        "type": "text",
        "id": "123456789",
        "text": "70.5"
      },
      "timestamp": 1640000000000,
      "source": {
        "type": "user",
        "userId": "U1234567890abcdef"
      },
      "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA",
      "mode": "active"
    }
  ]
}
```

### 2.3 署名検証

**検証アルゴリズム:**
```python
import hmac
import hashlib
import base64

def validate_signature(body, signature, channel_secret):
    """
    LINE Platform からのリクエストを検証

    Args:
        body (str): リクエストボディ
        signature (str): X-Line-Signature ヘッダーの値
        channel_secret (str): Channel Secret

    Returns:
        bool: 検証結果
    """
    hash_obj = hmac.new(
        channel_secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    )
    expected_signature = base64.b64encode(hash_obj.digest()).decode('utf-8')

    return hmac.compare_digest(signature, expected_signature)
```

**SDK による自動検証:**
```python
# WebhookHandler が自動的に検証
handler.handle(body, signature)
# 検証失敗時は InvalidSignatureError を raise
```

### 2.4 タイムアウト設定

LINE Platform は **10秒以内** にレスポンスを要求します。

**対応方法:**
```python
import threading

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    # 署名検証のみ同期処理
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    # すぐに200を返す
    return 'OK', 200

# ハンドラー内で重い処理は非同期化
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    # 重い処理はバックグラウンドで実行
    thread = threading.Thread(
        target=process_message_async,
        args=(event,)
    )
    thread.start()
```

---

## 3. イベントタイプ別処理

### 3.1 サポートするイベントタイプ

| イベントタイプ | 用途 | ハンドラー |
|------------|-----|----------|
| message (text) | テキストメッセージ受信 | `handle_text_message()` |
| message (image) | 画像受信（将来拡張用） | - |
| postback | リッチメニューのアクション | `handle_postback()` |
| follow | 友だち追加 | `handle_follow()` |
| unfollow | ブロック | `handle_unfollow()` |
| join | グループ参加 | `handle_join()` |

### 3.2 テキストメッセージハンドラー

**実装例:**
```python
from linebot.models import MessageEvent, TextMessage, TextSendMessage

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """
    テキストメッセージを処理してルーティング
    """
    user_id = event.source.user_id
    text = event.message.text.strip()

    # 体重入力判定（数値のみ、または「XX.Xkg」形式）
    import re
    weight_pattern = r'^[\d.]+$|[\d.]+kg'
    if re.search(weight_pattern, text):
        handle_weight_input(line_bot_api, event, text)
        return

    # 食事報告判定（キーワード検出）
    meal_keywords = ['朝食', '昼食', '夕食', '間食', '朝', '昼', '夜', '食べた']
    if any(kw in text for kw in meal_keywords):
        handle_meal_report(line_bot_api, event, text)
        return

    # その他のテキスト
    handle_general_message(line_bot_api, event, text)
```

### 3.3 Postback ハンドラー

**実装例:**
```python
from linebot.models import PostbackEvent

@handler.add(PostbackEvent)
def handle_postback(event):
    """
    リッチメニューからのPostbackを処理
    """
    user_id = event.source.user_id
    data = event.postback.data

    # data 形式: "action=xxx&param=yyy"
    params = dict(param.split('=') for param in data.split('&'))
    action = params.get('action')

    if action == 'weight':
        # 体重記録画面へ誘導
        reply_message = "体重を入力してください（例: 70.5）"

    elif action == 'meal':
        # 食事報告画面へ誘導
        reply_message = "今日の食事内容を教えてください"

    elif action == 'graph':
        # グラフ送信
        send_weight_graph(line_bot_api, user_id)
        return

    elif action == 'column':
        # 今日のコラム送信
        send_today_column(line_bot_api, user_id)
        return

    elif action == 'community':
        # コミュニティ招待
        handle_group_menu(line_bot_api, event)
        return

    elif action == 'report':
        # レポート送信
        send_latest_report(line_bot_api, user_id)
        return

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )
```

### 3.4 Follow イベントハンドラー

**実装例:**
```python
from linebot.models import FollowEvent

@handler.add(FollowEvent)
def handle_follow(event):
    """
    友だち追加時の初回登録フロー
    """
    user_id = event.source.user_id

    # ユーザープロフィール取得
    profile = line_bot_api.get_profile(user_id)
    display_name = profile.display_name

    # 登録ユーザーリストに追加
    add_user_to_registry(user_id)

    # ウェルカムメッセージ
    welcome_message = f"""{display_name}さん、友だち追加ありがとうございます！

🎺 関口式ダイエットメンターへようこそ！

まずは以下の情報を教えてください：

1️⃣ 現在の体重（kg）
2️⃣ 目標体重（kg）
3️⃣ 年齢
4️⃣ 性別（男/女）
5️⃣ プラン（ライト/ハード）

例）
70.5
65
30
男
ハード

※改行で区切って送信してください"""

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_message)
    )
```

### 3.5 Unfollow イベントハンドラー

**実装例:**
```python
from linebot.models import UnfollowEvent

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    """
    ブロック時の処理（ログのみ）
    """
    user_id = event.source.user_id

    # ログ記録
    import logging
    logging.info(f"User {user_id} unfollowed the bot")

    # ユーザーデータは保持（再フォロー時に復元可能）
    # 削除する場合は以下を実装
    # remove_user_from_registry(user_id)
```

---

## 4. メッセージ送信API

### 4.1 Reply Message API

**用途:** Webhook で受信したイベントに対する返信（1回のみ）

**実装例:**
```python
from linebot.models import TextSendMessage

def send_reply(event, text):
    """
    Reply Token を使った返信
    """
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text)
    )
```

**制限事項:**
- Reply Token は **1回のみ** 使用可能
- Reply Token の有効期限は **1分間**
- 最大 **5件** のメッセージを送信可能

**複数メッセージ送信:**
```python
from linebot.models import TextSendMessage, ImageSendMessage

line_bot_api.reply_message(
    event.reply_token,
    [
        TextSendMessage(text="体重を記録しました！"),
        ImageSendMessage(
            original_content_url="https://example.com/graph.png",
            preview_image_url="https://example.com/graph.png"
        ),
        TextSendMessage(text="今日のフィードバック...")
    ]
)
```

### 4.2 Push Message API

**用途:** 能動的なメッセージ送信（定時配信など）

**実装例:**
```python
def send_push_message(user_id, text):
    """
    Push API でメッセージ送信
    """
    line_bot_api.push_message(
        user_id,
        TextSendMessage(text=text)
    )
```

**複数メッセージ送信:**
```python
line_bot_api.push_message(
    user_id,
    [
        TextSendMessage(text="週次レポート"),
        TextSendMessage(text="詳細データ...")
    ]
)
```

**料金:**
- Push Message API は **従量課金**（無料枠あり）
- 月間 **500通まで無料**（2024年1月時点）
- 超過分は有料

### 4.3 Multicast API

**用途:** 複数ユーザーに一斉送信（最大500人）

**実装例:**
```python
def send_daily_column_multicast(user_ids, column_text):
    """
    複数ユーザーに同時配信

    Args:
        user_ids: list[str] (最大500件)
        column_text: str
    """
    # 500件ずつ分割
    for i in range(0, len(user_ids), 500):
        batch = user_ids[i:i+500]

        line_bot_api.multicast(
            batch,
            TextSendMessage(text=column_text)
        )
```

**メリット:**
- Push Message より効率的
- レート制限に引っかかりにくい

### 4.4 Broadcast API

**用途:** 全友だちに一斉送信

**実装例:**
```python
def send_broadcast(message_text):
    """
    全友だちに配信
    """
    line_bot_api.broadcast(
        TextSendMessage(text=message_text)
    )
```

**注意:**
- 公式アカウント（認証済み）のみ利用可能
- 非認証アカウントでは使用不可

---

## 5. リッチメニュー設定

### 5.1 リッチメニュー設計

**レイアウト（6分割）:**

```
┌──────────┬──────────┬──────────┐
│  体重記録  │  食事報告  │  グラフ   │
│  (weight) │  (meal)   │  (graph) │
├──────────┼──────────┼──────────┤
│ コラム    │ 交流の場   │ レポート  │
│ (column)  │(community)│ (report) │
└──────────┴──────────┴──────────┘
```

### 5.2 リッチメニューJSON

**作成API:**
```python
from linebot.models import RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds
from linebot.models.actions import PostbackAction

def create_rich_menu():
    """
    リッチメニューを作成
    """
    rich_menu = RichMenu(
        size=RichMenuSize(width=2500, height=1686),
        selected=True,
        name="関口式ダイエットメンター メニュー",
        chat_bar_text="メニュー",
        areas=[
            # 体重記録（左上）
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
                action=PostbackAction(
                    label="体重記録",
                    data="action=weight"
                )
            ),
            # 食事報告（中央上）
            RichMenuArea(
                bounds=RichMenuBounds(x=833, y=0, width=834, height=843),
                action=PostbackAction(
                    label="食事報告",
                    data="action=meal"
                )
            ),
            # グラフ（右上）
            RichMenuArea(
                bounds=RichMenuBounds(x=1667, y=0, width=833, height=843),
                action=PostbackAction(
                    label="グラフ",
                    data="action=graph"
                )
            ),
            # コラム（左下）
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=843, width=833, height=843),
                action=PostbackAction(
                    label="コラム",
                    data="action=column"
                )
            ),
            # 交流の場（中央下）
            RichMenuArea(
                bounds=RichMenuBounds(x=833, y=843, width=834, height=843),
                action=PostbackAction(
                    label="交流の場",
                    data="action=community"
                )
            ),
            # レポート（右下）
            RichMenuArea(
                bounds=RichMenuBounds(x=1667, y=843, width=833, height=843),
                action=PostbackAction(
                    label="レポート",
                    data="action=report"
                )
            )
        ]
    )

    # リッチメニュー作成
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu)
    return rich_menu_id
```

### 5.3 リッチメニュー画像アップロード

**画像仕様:**
- サイズ: **2500 × 1686 px**
- フォーマット: JPEG または PNG
- ファイルサイズ: 1MB以下

**アップロードコード:**
```python
def upload_rich_menu_image(rich_menu_id, image_path):
    """
    リッチメニュー画像をアップロード

    Args:
        rich_menu_id: str
        image_path: str (画像ファイルパス)
    """
    with open(image_path, 'rb') as f:
        line_bot_api.set_rich_menu_image(
            rich_menu_id,
            'image/png',  # または 'image/jpeg'
            f
        )
```

### 5.4 デフォルトリッチメニュー設定

**全ユーザーに適用:**
```python
def set_default_rich_menu(rich_menu_id):
    """
    デフォルトリッチメニューに設定
    """
    line_bot_api.set_default_rich_menu(rich_menu_id)
```

### 5.5 ユーザー別リッチメニュー設定

**個別設定:**
```python
def link_rich_menu_to_user(user_id, rich_menu_id):
    """
    特定ユーザーにリッチメニューをリンク
    """
    line_bot_api.link_rich_menu_to_user(user_id, rich_menu_id)
```

---

## 6. Flex Message 仕様

### 6.1 Flex Message 概要

**用途:**
- リッチなビジュアル表現
- ボタン付きカード
- グループ招待UI

### 6.2 Bubble Container（基本）

**実装例（コミュニティ招待）:**
```python
from linebot.models import (
    FlexSendMessage, BubbleContainer, BoxComponent,
    TextComponent, ButtonComponent, SeparatorComponent,
    URIAction
)

def create_community_invitation_flex():
    """
    コミュニティ招待用 Flex Message
    """
    bubble = BubbleContainer(
        direction='ltr',
        hero=BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(
                    text='🤝 交流の場',
                    size='xl',
                    weight='bold',
                    color='#1DB446',
                    align='center'
                )
            ],
            background_color='#F0F8F0',
            padding_all='20px'
        ),
        body=BoxComponent(
            layout='vertical',
            contents=[
                TextComponent(
                    text='仲間と一緒に頑張りましょう！',
                    size='md',
                    wrap=True,
                    margin='md'
                ),
                TextComponent(
                    text='✓ 励まし合える仲間',
                    size='sm',
                    color='#666666',
                    margin='md'
                ),
                TextComponent(
                    text='✓ 成功体験のシェア',
                    size='sm',
                    color='#666666',
                    margin='xs'
                ),
                TextComponent(
                    text='✓ 質問し合える環境',
                    size='sm',
                    color='#666666',
                    margin='xs'
                ),
                SeparatorComponent(margin='lg'),
                TextComponent(
                    text='📌 グループルール',
                    size='md',
                    weight='bold',
                    margin='lg'
                ),
                TextComponent(
                    text='1. 互いを尊重する',
                    size='sm',
                    color='#666666',
                    margin='md'
                ),
                TextComponent(
                    text='2. ポジティブな発言',
                    size='sm',
                    color='#666666',
                    margin='xs'
                ),
                TextComponent(
                    text='3. 勧誘・宣伝禁止',
                    size='sm',
                    color='#666666',
                    margin='xs'
                )
            ],
            spacing='md',
            padding_all='20px'
        ),
        footer=BoxComponent(
            layout='vertical',
            contents=[
                ButtonComponent(
                    style='primary',
                    color='#1DB446',
                    action=URIAction(
                        label='グループに参加する',
                        uri=os.getenv('GROUP_INVITE_URL')
                    )
                )
            ],
            spacing='sm',
            padding_all='20px'
        )
    )

    flex_message = FlexSendMessage(
        alt_text='🤝 交流の場への招待',
        contents=bubble
    )

    return flex_message
```

### 6.3 Carousel Container（複数カード）

**実装例（週次レポート）:**
```python
from linebot.models import CarouselContainer

def create_weekly_report_carousel(weekly_data):
    """
    週次レポートを Carousel で表示
    """
    bubbles = []

    # 体重変化カード
    bubbles.append(create_weight_change_bubble(weekly_data))

    # PFCバランスカード
    bubbles.append(create_pfc_balance_bubble(weekly_data))

    # 継続性カード
    bubbles.append(create_consistency_bubble(weekly_data))

    carousel = CarouselContainer(contents=bubbles)

    flex_message = FlexSendMessage(
        alt_text='📊 週次レポート',
        contents=carousel
    )

    return flex_message
```

### 6.4 Flex Message Simulator

**デザインツール:**
- LINE公式: https://developers.line.biz/flex-simulator/
- JSON生成後、Pythonコードに変換

---

## 7. 画像送信仕様

### 7.1 ImageSendMessage

**基本実装:**
```python
from linebot.models import ImageSendMessage

def send_weight_graph(user_id, graph_url):
    """
    体重グラフ画像を送信

    Args:
        user_id: str
        graph_url: str (公開URL、HTTPS必須)
    """
    line_bot_api.push_message(
        user_id,
        ImageSendMessage(
            original_content_url=graph_url,
            preview_image_url=graph_url
        )
    )
```

### 7.2 画像URL要件

**必須条件:**
- **HTTPS** 必須（HTTP不可）
- 公開アクセス可能なURL
- ファイルサイズ: **10MB以下**（推奨1MB以下）
- フォーマット: JPEG または PNG

### 7.3 画像ホスティング方法

**方法1: 自サーバーでホスト**
```python
from flask import send_from_directory

@app.route('/images/<filename>')
def serve_image(filename):
    """
    画像ファイルを配信
    """
    return send_from_directory('temp', filename)

# 使用例
graph_path = generate_weight_graph(user_id)  # temp/weight_graph_xxx.png
graph_url = f"https://your-domain.com/images/weight_graph_{user_id}.png"

send_weight_graph(user_id, graph_url)
```

**方法2: AWS S3にアップロード**
```python
import boto3

def upload_to_s3(local_path, s3_key):
    """
    S3にアップロードして公開URLを返す
    """
    s3 = boto3.client('s3')
    bucket_name = 'your-bucket-name'

    s3.upload_file(
        local_path,
        bucket_name,
        s3_key,
        ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/png'}
    )

    url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
    return url

# 使用例
graph_path = generate_weight_graph(user_id)
s3_url = upload_to_s3(graph_path, f"graphs/{user_id}.png")
send_weight_graph(user_id, s3_url)
```

**方法3: Cloudinary（CDN）**
```python
import cloudinary.uploader

def upload_to_cloudinary(local_path):
    """
    Cloudinary にアップロード
    """
    result = cloudinary.uploader.upload(local_path)
    return result['secure_url']
```

### 7.4 一時ファイル管理

**定期クリーンアップ:**
```python
import os
import time

def cleanup_old_images(directory='temp', max_age_hours=24):
    """
    古い画像ファイルを削除

    Args:
        directory: str
        max_age_hours: int (保持時間)
    """
    now = time.time()
    max_age_seconds = max_age_hours * 3600

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        if os.path.isfile(filepath):
            file_age = now - os.path.getmtime(filepath)

            if file_age > max_age_seconds:
                os.remove(filepath)
                print(f"Deleted old file: {filename}")

# Schedulerで定期実行
scheduler.add_job(
    func=cleanup_old_images,
    trigger=CronTrigger(hour=3, minute=0),  # 毎日3:00
    id='cleanup_images'
)
```

---

## 8. プロフィールAPI

### 8.1 ユーザープロフィール取得

**実装例:**
```python
def get_user_profile(user_id):
    """
    LINE ユーザープロフィールを取得

    Returns:
        dict: {
            'displayName': str,
            'userId': str,
            'pictureUrl': str,
            'statusMessage': str
        }
    """
    try:
        profile = line_bot_api.get_profile(user_id)

        return {
            'display_name': profile.display_name,
            'user_id': profile.user_id,
            'picture_url': profile.picture_url,
            'status_message': profile.status_message
        }
    except LineBotApiError as e:
        print(f"Failed to get profile: {e}")
        return None
```

### 8.2 グループ情報取得

**実装例:**
```python
def get_group_summary(group_id):
    """
    グループ情報を取得

    Returns:
        dict: {
            'groupId': str,
            'groupName': str,
            'pictureUrl': str
        }
    """
    try:
        summary = line_bot_api.get_group_summary(group_id)

        return {
            'group_id': summary.group_id,
            'group_name': summary.group_name,
            'picture_url': summary.picture_url
        }
    except LineBotApiError as e:
        print(f"Failed to get group summary: {e}")
        return None
```

---

## 9. エラーハンドリング

### 9.1 LINE API エラーコード

| HTTPステータス | エラー内容 | 対処方法 |
|-------------|---------|---------|
| 400 | Bad Request | リクエスト内容を確認 |
| 401 | Unauthorized | アクセストークン確認 |
| 403 | Forbidden | 権限不足 |
| 404 | Not Found | ユーザーIDやリソース確認 |
| 429 | Too Many Requests | レート制限超過、待機 |
| 500 | Internal Server Error | LINE側の問題、リトライ |

### 9.2 エラーハンドリング実装

**包括的エラー処理:**
```python
from linebot.exceptions import LineBotApiError
import time

def send_message_with_retry(user_id, message, max_retries=3):
    """
    リトライ付きメッセージ送信

    Args:
        user_id: str
        message: SendMessage
        max_retries: int
    """
    for attempt in range(max_retries):
        try:
            line_bot_api.push_message(user_id, message)
            return True

        except LineBotApiError as e:
            if e.status_code == 400:
                # Bad Request - リトライ不要
                print(f"Invalid request: {e.message}")
                return False

            elif e.status_code == 401:
                # Unauthorized - アクセストークン問題
                print(f"Invalid access token")
                return False

            elif e.status_code == 429:
                # Rate limit - 待機してリトライ
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limit exceeded. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            elif e.status_code >= 500:
                # Server error - リトライ
                wait_time = 2 ** attempt
                print(f"Server error. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue

            else:
                print(f"Unexpected error: {e}")
                return False

        except Exception as e:
            print(f"Unexpected exception: {e}")
            return False

    print(f"Failed after {max_retries} attempts")
    return False
```

### 9.3 ログ記録

**推奨ロギング:**
```python
import logging

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 使用例
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = event.source.user_id
    text = event.message.text

    logger.info(f"Received message from {user_id}: {text}")

    try:
        # 処理
        pass
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
```

---

## 10. レート制限対応

### 10.1 レート制限

**LINE Messaging API の制限:**
- Reply Message: **制限なし**（Reply Token 単位）
- Push Message: **500通/秒**
- Multicast: **制限なし**（推奨）
- Broadcast: **1回/秒**

### 10.2 レート制限回避策

**方法1: バッチ送信（Multicast使用）**
```python
def send_to_multiple_users(user_ids, message):
    """
    複数ユーザーに効率的に送信
    """
    # 500件ずつ分割してMulticast
    for i in range(0, len(user_ids), 500):
        batch = user_ids[i:i+500]

        try:
            line_bot_api.multicast(batch, message)
            time.sleep(0.1)  # 念のため少し待機
        except LineBotApiError as e:
            if e.status_code == 429:
                time.sleep(5)  # Rate limit時は長めに待機
                line_bot_api.multicast(batch, message)
```

**方法2: Queue + Worker パターン**
```python
from queue import Queue
from threading import Thread

message_queue = Queue()

def message_worker():
    """
    バックグラウンドでメッセージ送信
    """
    while True:
        user_id, message = message_queue.get()

        try:
            line_bot_api.push_message(user_id, message)
            time.sleep(0.1)  # レート制限考慮
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
        finally:
            message_queue.task_done()

# Worker起動
worker_thread = Thread(target=message_worker, daemon=True)
worker_thread.start()

# 使用例
def queue_message(user_id, message):
    """メッセージをキューに追加"""
    message_queue.put((user_id, message))
```

---

## 11. セキュリティ

### 11.1 環境変数管理

**推奨方法:**
```python
from dotenv import load_dotenv
import os

# .env ファイル読み込み
load_dotenv()

# 環境変数取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# 必須チェック
if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    raise ValueError("LINE credentials not found in environment variables")
```

**.env ファイル（Gitignore必須）:**
```bash
LINE_CHANNEL_ACCESS_TOKEN=xxxxx
LINE_CHANNEL_SECRET=xxxxx
```

**.gitignore:**
```
.env
*.env
.env.*
```

### 11.2 HTTPS必須

**本番環境:**
- Webhook URL は **HTTPS** 必須
- SSL証明書の設定（Let's Encrypt推奨）

**開発環境（ngrok使用）:**
```bash
# ngrok でローカルサーバーをHTTPS公開
ngrok http 5000

# 表示されたHTTPS URLをWebhook URLに設定
# https://xxxx.ngrok.io/webhook
```

### 11.3 IPホワイトリスト（オプション）

**LINE Platform からのアクセスのみ許可:**
```python
from flask import request, abort

ALLOWED_IPS = [
    '147.92.150.0/25',  # LINE Platform IP範囲
    '147.92.150.128/25'
]

@app.before_request
def check_ip():
    """
    IPアドレス検証（本番環境推奨）
    """
    if request.endpoint == 'webhook':
        client_ip = request.remote_addr

        # IP範囲チェック（簡易版）
        # 本番では ipaddress モジュール使用推奨
        if not is_ip_allowed(client_ip, ALLOWED_IPS):
            abort(403)
```

---

## 付録: APIリファレンス

### LINE Messaging API 公式ドキュメント
- **APIリファレンス:** https://developers.line.biz/ja/reference/messaging-api/
- **SDKドキュメント:** https://github.com/line/line-bot-sdk-python
- **Flex Message Simulator:** https://developers.line.biz/flex-simulator/

### よく使うエンドポイント

| エンドポイント | メソッド | 用途 |
|-----------|---------|-----|
| `/v2/bot/message/reply` | POST | Reply Message送信 |
| `/v2/bot/message/push` | POST | Push Message送信 |
| `/v2/bot/message/multicast` | POST | Multicast送信 |
| `/v2/bot/profile/{userId}` | GET | ユーザープロフィール取得 |
| `/v2/bot/richmenu` | POST | リッチメニュー作成 |

---

**以上、LINE Messaging API 連携仕様**
