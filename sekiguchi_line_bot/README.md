# 関口式ダイエットメンター LINE Bot版

> フィジークマスターズ世界一×指導歴30年×人格搭載AI
>
> LINE上で関口貴夫さんの分身があなたのダイエットをサポート

---

## 📱 概要

「関口式ダイエットメンター」のLINE Bot版実装。
リッチメニューから直感的に操作でき、毎日の体重・食事記録、コラム配信、Q&Aなど充実した機能を提供。

---

## 🎨 リッチメニュー構成

### 上段
- **①今日の体重**: 体重を記録してグラフ化＋関口の4要素メッセージ
- **②今日の食事**: 食事写真 or テキストで記録＋PFC比較
- **③サービス説明**: カルーセル形式のLP表示

### 下段
- **④関口コラム**: 毎日配信される関口のコラム（日替わり）
- **⑤交流の場**: グループLINEへの招待
- **⑥困ったとき**: FAQ＋個別質問受付

---

## 🛠️ セットアップ

### 1. 必要なもの

- Python 3.11+
- LINE Developers アカウント
- LINE Messaging API チャネル

### 2. インストール

```bash
cd sekiguchi_line_bot

# 仮想環境作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存ライブラリインストール
pip install -r requirements.txt
```

### 3. 環境変数設定

```bash
# .env.exampleをコピー
cp .env.example .env

# .envを編集
# LINE_CHANNEL_ACCESS_TOKEN=your_token_here
# LINE_CHANNEL_SECRET=your_secret_here
```

### 4. リッチメニュー作成

```bash
# リッチメニュー画像を準備（2500x1686px）
# rich_menu_image.png

# リッチメニューをLINEに登録
python setup_rich_menu.py
```

### 5. Webhook URL設定

LINE Developers コンソールで Webhook URL を設定：

```
https://your-domain.com/callback
```

### 6. 起動

```bash
# 開発環境
python app.py

# 本番環境（Gunicorn使用）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 📂 ファイル構成

```
sekiguchi_line_bot/
├── app.py                      # メインアプリケーション
├── rich_menu_config.json       # リッチメニュー設定
├── requirements.txt            # 依存ライブラリ
├── .env.example                # 環境変数テンプレート
├── setup_rich_menu.py          # リッチメニューセットアップ
├── handlers/                   # 各機能のハンドラー
│   ├── __init__.py
│   ├── weight_handler.py       # ①体重記録
│   ├── meal_handler.py         # ②食事記録
│   ├── lp_handler.py           # ③LP表示
│   ├── column_handler.py       # ④コラム配信
│   ├── group_handler.py        # ⑤グループ招待
│   └── qa_handler.py           # ⑥Q&A
└── README.md                   # このファイル
```

---

## 🔧 機能詳細

### ①今日の体重

1. ユーザーがタップ
2. 体重を数値入力
3. 前日比を計算＆グラフ生成
4. 関口の4要素メッセージ（状況に応じて）
   - 体重増加時
   - 体重減少時
   - 変化なし時

### ②今日の食事

1. ユーザーがタップ
2. 食事写真 or テキスト入力
3. カロリー・PFC入力
4. 目標値と比較
5. 関口の4要素フィードバック

### ③サービス説明

- カルーセル形式のLP
- サービス概要、指導哲学、プラン説明、料金

### ④関口コラム

- 毎朝8:00に自動配信
- 日替わりテーマ（月:年齢、火:食事、水:メンタル...）
- アーカイブ閲覧可能

### ⑤交流の場

- グループLINE参加案内
- 招待リンク送信
- 関口botも参加

### ⑥困ったとき

- カテゴリ別FAQ
- よくある質問TOP3
- 個別質問受付

---

## 🤖 関口の指導哲学（4要素）

すべてのメッセージに以下の4要素を反映：

1. **🎺 チアリーダー（応援する）25%**
2. **🎭 コメディアン（楽しませる）25%**
3. **🍸 バーテンダー（傾聴する）25%**
4. **🎓 専門家（科学的根拠）25%**

---

## 📅 今後の開発予定

- [ ] LIFF（LINE Front-end Framework）でリッチUI
- [ ] 画像認識AIで食事写真から自動カロリー推定
- [ ] プッシュ通知のパーソナライズ
- [ ] ユーザー間ランキング機能
- [ ] 達成バッジ・報酬システム
- [ ] 関口さん本人の動画メッセージ配信

---

## 🚀 デプロイ

### Heroku

```bash
# Herokuアプリ作成
heroku create sekiguchi-diet-mentor

# 環境変数設定
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=xxxxx
heroku config:set LINE_CHANNEL_SECRET=xxxxx

# デプロイ
git push heroku main

# Webhook URL設定
https://sekiguchi-diet-mentor.herokuapp.com/callback
```

### AWS / GCP / Azure

- Elastic Beanstalk / App Engine / App Service 使用
- 環境変数を適切に設定
- HTTPS必須

---

## 📝 ライセンス

MIT License

---

## 👨‍💻 開発者

関口式ダイエットメンター開発チーム

---

## 📞 サポート

問題が発生した場合：
1. GitHubのIssueを確認
2. 新しいIssueを作成
3. support@sekiguchi-diet.com に連絡

---

以上
