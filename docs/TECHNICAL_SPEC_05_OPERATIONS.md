# 関口式ダイエットメンター - 運用仕様書（Part 5）

**Document Version:** 1.0
**Last Updated:** 2025-12-21
**対象:** インフラ・運用エンジニア

---

## 目次

1. [運用概要](#1-運用概要)
2. [開発環境セットアップ](#2-開発環境セットアップ)
3. [本番環境デプロイ](#3-本番環境デプロイ)
4. [環境変数管理](#4-環境変数管理)
5. [監視・ログ管理](#5-監視ログ管理)
6. [バックアップ・復旧](#6-バックアップ復旧)
7. [スケーリング](#7-スケーリング)
8. [トラブルシューティング](#8-トラブルシューティング)
9. [メンテナンス](#9-メンテナンス)
10. [セキュリティ対策](#10-セキュリティ対策)

---

## 1. 運用概要

### 1.1 システム構成

```
┌─────────────────┐
│  LINE Platform  │
└────────┬────────┘
         │ HTTPS Webhook
         ↓
┌─────────────────┐
│   Web Server    │
│  (Flask/Gunicorn)│
│   Port: 5000    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Scheduler     │
│  (APScheduler)  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  File Storage   │
│  (data/*.json)  │
│  (data/*.csv)   │
└─────────────────┘
```

### 1.2 必要なリソース

**推奨スペック（~1000ユーザー）:**
- **CPU:** 1 vCPU
- **メモリ:** 1 GB RAM
- **ストレージ:** 10 GB SSD
- **帯域:** 100 Mbps

**推奨スペック（~10,000ユーザー）:**
- **CPU:** 2 vCPU
- **メモリ:** 4 GB RAM
- **ストレージ:** 50 GB SSD
- **帯域:** 1 Gbps

### 1.3 運用時間

**サービス稼働時間:**
- **24時間365日稼働**

**定期メンテナンス:**
- 毎週日曜日 2:00-4:00（影響最小時間帯）

**自動配信スケジュール:**
- 週次レポート: 毎週日曜 20:00
- 月次レポート: 毎月最終日 20:00
- 日次コラム: 毎日 20:00
- グループ励まし: 毎日 10:00
- データクリーンアップ: 毎日 3:00

---

## 2. 開発環境セットアップ

### 2.1 ローカル開発環境

**必要な環境:**
- Python 3.11+
- pip
- virtualenv
- ngrok（Webhook テスト用）

**セットアップ手順:**

```bash
# 1. リポジトリクローン
git clone https://github.com/your-org/sekiguchi-mentor-bot.git
cd sekiguchi-mentor-bot

# 2. 仮想環境作成
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存パッケージインストール
pip install -r requirements.txt

# 4. ディレクトリ作成
mkdir -p data temp logs

# 5. 環境変数設定
cp .env.example .env
# .env を編集してLINE認証情報を設定

# 6. ローカルサーバー起動
python app.py
```

### 2.2 requirements.txt

**依存パッケージ一覧:**
```txt
# Web Framework
Flask==3.0.0
gunicorn==21.2.0

# LINE Bot SDK
line-bot-sdk==3.5.0

# Data Processing
pandas==2.1.3
numpy==1.26.2

# Visualization
matplotlib==3.8.2

# Scheduler
APScheduler==3.10.4

# Environment Variables
python-dotenv==1.0.0

# Utilities
requests==2.31.0
pytz==2023.3
```

### 2.3 ngrok によるWebhookテスト

**ngrok起動:**
```bash
# ngrok インストール（初回のみ）
# https://ngrok.com/download

# HTTPSトンネル作成
ngrok http 5000
```

**出力例:**
```
Forwarding  https://abcd1234.ngrok.io -> http://localhost:5000
```

**LINE Developers設定:**
1. Webhook URL: `https://abcd1234.ngrok.io/webhook`
2. 「検証」ボタンで疎通確認

### 2.4 開発時の注意点

**デバッグモード:**
```python
# app.py
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**ログレベル:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)  # 開発時
# logging.basicConfig(level=logging.INFO)  # 本番時
```

---

## 3. 本番環境デプロイ

### 3.1 デプロイ方式の選択

**推奨デプロイ先:**

| プラットフォーム | メリット | デメリット | コスト |
|-------------|---------|----------|-------|
| **AWS EC2** | 柔軟性高い、フルコントロール | 運用負荷大 | ~$10/月 |
| **Heroku** | 簡単デプロイ、自動スケール | やや高コスト | ~$25/月 |
| **Google Cloud Run** | サーバーレス、自動スケール | コールドスタート問題 | ~$5/月 |
| **さくらVPS** | 低コスト、日本リージョン | 運用負荷中 | ~$5/月 |

### 3.2 AWS EC2 デプロイ手順

**3.2.1 EC2インスタンス作成**

```bash
# インスタンスタイプ: t3.micro または t3.small
# OS: Ubuntu 22.04 LTS
# セキュリティグループ:
#   - SSH (22): 管理者IPのみ
#   - HTTPS (443): 0.0.0.0/0
#   - HTTP (80): 0.0.0.0/0（HTTPS リダイレクト用）
```

**3.2.2 サーバー初期設定**

```bash
# SSH接続
ssh -i your-key.pem ubuntu@your-ec2-ip

# システムアップデート
sudo apt update && sudo apt upgrade -y

# Python 3.11 インストール
sudo apt install -y python3.11 python3.11-venv python3-pip

# Git インストール
sudo apt install -y git

# Nginx インストール
sudo apt install -y nginx

# Certbot（Let's Encrypt）インストール
sudo apt install -y certbot python3-certbot-nginx
```

**3.2.3 アプリケーションデプロイ**

```bash
# アプリケーション配置
cd /opt
sudo git clone https://github.com/your-org/sekiguchi-mentor-bot.git
cd sekiguchi-mentor-bot

# 仮想環境作成
sudo python3.11 -m venv venv
sudo venv/bin/pip install -r requirements.txt

# ディレクトリ作成
sudo mkdir -p data temp logs

# 環境変数設定
sudo nano .env
# LINE認証情報を設定

# 所有権変更
sudo chown -R ubuntu:ubuntu /opt/sekiguchi-mentor-bot
```

**3.2.4 Systemd サービス設定**

**ファイル: `/etc/systemd/system/sekiguchi-bot.service`**
```ini
[Unit]
Description=Sekiguchi Diet Mentor Bot
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/sekiguchi-mentor-bot
Environment="PATH=/opt/sekiguchi-mentor-bot/venv/bin"
ExecStart=/opt/sekiguchi-mentor-bot/venv/bin/gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile /opt/sekiguchi-mentor-bot/logs/access.log \
    --error-logfile /opt/sekiguchi-mentor-bot/logs/error.log \
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**サービス起動:**
```bash
# サービス有効化
sudo systemctl enable sekiguchi-bot

# サービス起動
sudo systemctl start sekiguchi-bot

# 状態確認
sudo systemctl status sekiguchi-bot
```

**3.2.5 Nginx 設定**

**ファイル: `/etc/nginx/sites-available/sekiguchi-bot`**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Let's Encrypt 検証用
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # HTTPS リダイレクト
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL証明書（Let's Encrypt）
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL設定
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ログ
    access_log /var/log/nginx/sekiguchi-bot-access.log;
    error_log /var/log/nginx/sekiguchi-bot-error.log;

    # Webhook エンドポイント
    location /webhook {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # タイムアウト設定
        proxy_connect_timeout 10s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }

    # 静的ファイル（画像）
    location /images/ {
        alias /opt/sekiguchi-mentor-bot/temp/;
        expires 1h;
    }
}
```

**Nginx有効化:**
```bash
# シンボリックリンク作成
sudo ln -s /etc/nginx/sites-available/sekiguchi-bot /etc/nginx/sites-enabled/

# 設定テスト
sudo nginx -t

# Nginx再起動
sudo systemctl restart nginx
```

**3.2.6 SSL証明書取得（Let's Encrypt）**

```bash
# 証明書取得
sudo certbot --nginx -d your-domain.com

# 自動更新設定（Cron）
sudo crontab -e
# 追加: 0 3 * * * certbot renew --quiet
```

### 3.3 Heroku デプロイ手順

**3.3.1 必要なファイル**

**Procfile:**
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**runtime.txt:**
```
python-3.11.6
```

**3.3.2 デプロイコマンド**

```bash
# Heroku CLI インストール
# https://devcenter.heroku.com/articles/heroku-cli

# ログイン
heroku login

# アプリ作成
heroku create sekiguchi-diet-mentor

# 環境変数設定
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=your_token
heroku config:set LINE_CHANNEL_SECRET=your_secret
heroku config:set GROUP_LINE_ID=your_group_id
heroku config:set GROUP_INVITE_URL=your_invite_url

# デプロイ
git push heroku main

# ログ確認
heroku logs --tail
```

**3.3.3 Heroku Scheduler設定**

```bash
# アドオン追加
heroku addons:create scheduler:standard

# ダッシュボードから設定
# https://dashboard.heroku.com/apps/your-app/scheduler
```

### 3.4 Docker デプロイ（オプション）

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 依存パッケージインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコピー
COPY . .

# ディレクトリ作成
RUN mkdir -p data temp logs

# ポート公開
EXPOSE 5000

# 起動コマンド
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  bot:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./temp:/app/temp
      - ./logs:/app/logs
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**起動:**
```bash
docker-compose up -d
```

---

## 4. 環境変数管理

### 4.1 必須環境変数

| 変数名 | 説明 | 例 |
|-------|------|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINEチャンネルアクセストークン | `xxxxx...` |
| `LINE_CHANNEL_SECRET` | LINEチャンネルシークレット | `xxxxx...` |
| `GROUP_LINE_ID` | グループID（コミュニティ機能） | `C1234567890abcdef` |
| `GROUP_INVITE_URL` | グループ招待URL | `https://line.me/R/ti/g/xxx` |

### 4.2 オプション環境変数

| 変数名 | 説明 | デフォルト |
|-------|------|----------|
| `FLASK_ENV` | 実行環境 | `production` |
| `LOG_LEVEL` | ログレベル | `INFO` |
| `WEBHOOK_URL` | WebhookベースURL | - |
| `AWS_ACCESS_KEY_ID` | AWS認証（S3使用時） | - |
| `AWS_SECRET_ACCESS_KEY` | AWS認証（S3使用時） | - |
| `S3_BUCKET_NAME` | S3バケット名 | - |

### 4.3 環境別設定

**.env.development:**
```bash
FLASK_ENV=development
LOG_LEVEL=DEBUG
LINE_CHANNEL_ACCESS_TOKEN=your_dev_token
LINE_CHANNEL_SECRET=your_dev_secret
```

**.env.production:**
```bash
FLASK_ENV=production
LOG_LEVEL=INFO
LINE_CHANNEL_ACCESS_TOKEN=your_prod_token
LINE_CHANNEL_SECRET=your_prod_secret
```

### 4.4 秘密情報の管理

**推奨ツール:**
- **AWS Secrets Manager**
- **HashiCorp Vault**
- **Doppler**

**AWS Secrets Manager 使用例:**
```python
import boto3
import json

def get_secret(secret_name):
    """
    AWS Secrets Manager から秘密情報を取得
    """
    client = boto3.client('secretsmanager', region_name='ap-northeast-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# 使用例
secrets = get_secret('sekiguchi-bot-secrets')
LINE_CHANNEL_ACCESS_TOKEN = secrets['LINE_CHANNEL_ACCESS_TOKEN']
```

---

## 5. 監視・ログ管理

### 5.1 ログレベル

| レベル | 用途 | 例 |
|-------|-----|---|
| DEBUG | 開発デバッグ | 変数の値、処理フロー |
| INFO | 通常動作 | ユーザー登録、メッセージ送信成功 |
| WARNING | 警告 | リトライ発生、タイムアウト |
| ERROR | エラー | API呼び出し失敗、データ不整合 |
| CRITICAL | 致命的 | サービス停止、データ損失 |

### 5.2 ログ設定

**logging.conf:**
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    ロギング設定
    """
    # ログレベル
    log_level = os.getenv('LOG_LEVEL', 'INFO')

    # フォーマッター
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # ファイルハンドラー（ローテーション）
    file_handler = RotatingFileHandler(
        'logs/bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)

    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # ルートロガー設定
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
```

### 5.3 重要メトリクス

**監視すべき指標:**

| メトリクス | 閾値 | アラート条件 |
|----------|------|------------|
| CPU使用率 | 80% | 5分間継続 |
| メモリ使用率 | 85% | 5分間継続 |
| ディスク使用率 | 90% | - |
| エラー率 | 5% | 1時間あたり |
| レスポンスタイム | 3秒 | 平均値 |
| Webhook失敗率 | 1% | 1時間あたり |

### 5.4 CloudWatch 監視（AWS）

**CloudWatch Logs エージェント設定:**

```bash
# CloudWatch Logs エージェントインストール
sudo apt install -y amazon-cloudwatch-agent

# 設定ファイル作成
sudo nano /opt/aws/amazon-cloudwatch-agent/etc/config.json
```

**config.json:**
```json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/opt/sekiguchi-mentor-bot/logs/bot.log",
            "log_group_name": "/aws/ec2/sekiguchi-bot",
            "log_stream_name": "{instance_id}/bot.log",
            "timestamp_format": "%Y-%m-%d %H:%M:%S"
          },
          {
            "file_path": "/var/log/nginx/sekiguchi-bot-error.log",
            "log_group_name": "/aws/ec2/sekiguchi-bot",
            "log_stream_name": "{instance_id}/nginx-error.log"
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "SekiguchiBot",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {"name": "cpu_usage_idle", "rename": "CPU_IDLE", "unit": "Percent"}
        ],
        "totalcpu": false
      },
      "disk": {
        "measurement": [
          {"name": "used_percent", "rename": "DISK_USED", "unit": "Percent"}
        ],
        "resources": ["/"]
      },
      "mem": {
        "measurement": [
          {"name": "mem_used_percent", "rename": "MEM_USED", "unit": "Percent"}
        ]
      }
    }
  }
}
```

**エージェント起動:**
```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config \
    -m ec2 \
    -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

### 5.5 アラート設定

**CloudWatch Alarm 例（CPU使用率）:**
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name sekiguchi-bot-high-cpu \
    --alarm-description "CPU usage > 80% for 5 minutes" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:ap-northeast-1:123456789012:admin-alerts
```

### 5.6 ヘルスチェックエンドポイント

**実装:**
```python
@app.route('/health', methods=['GET'])
def health_check():
    """
    ヘルスチェックエンドポイント
    """
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }

    # ディスク容量チェック
    disk_usage = shutil.disk_usage('data')
    disk_percent = (disk_usage.used / disk_usage.total) * 100
    status['checks']['disk'] = {
        'status': 'ok' if disk_percent < 90 else 'warning',
        'usage_percent': round(disk_percent, 2)
    }

    # データディレクトリチェック
    status['checks']['data_dir'] = {
        'status': 'ok' if os.path.isdir('data') else 'error'
    }

    # スケジューラーチェック
    status['checks']['scheduler'] = {
        'status': 'ok' if scheduler.running else 'error'
    }

    # 総合ステータス
    if any(c['status'] == 'error' for c in status['checks'].values()):
        status['status'] = 'unhealthy'
        return jsonify(status), 503
    elif any(c['status'] == 'warning' for c in status['checks'].values()):
        status['status'] = 'degraded'
        return jsonify(status), 200
    else:
        return jsonify(status), 200
```

---

## 6. バックアップ・復旧

### 6.1 バックアップ戦略

**3-2-1ルール:**
- **3** つのコピー
- **2** 種類の異なるメディア
- **1** つはオフサイト

### 6.2 日次バックアップスクリプト

**backup.sh:**
```bash
#!/bin/bash

# 設定
BACKUP_DIR="/backup/sekiguchi-bot"
DATA_DIR="/opt/sekiguchi-mentor-bot/data"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# バックアップディレクトリ作成
mkdir -p "${BACKUP_DIR}/${DATE}"

# データファイルコピー
cp -r "${DATA_DIR}"/* "${BACKUP_DIR}/${DATE}/"

# 圧縮
cd "${BACKUP_DIR}"
tar -czf "backup_${DATE}.tar.gz" "${DATE}"
rm -rf "${DATE}"

# 古いバックアップ削除（30日以上前）
find "${BACKUP_DIR}" -name "backup_*.tar.gz" -mtime +${RETENTION_DAYS} -delete

# ログ出力
echo "[$(date)] Backup completed: backup_${DATE}.tar.gz"
```

**実行権限付与:**
```bash
chmod +x /opt/sekiguchi-mentor-bot/scripts/backup.sh
```

**Cron設定（毎日3:00）:**
```bash
sudo crontab -e
# 追加: 0 3 * * * /opt/sekiguchi-mentor-bot/scripts/backup.sh >> /var/log/backup.log 2>&1
```

### 6.3 S3へのバックアップ

**s3-backup.sh:**
```bash
#!/bin/bash

# AWS設定
S3_BUCKET="s3://sekiguchi-bot-backups"
DATA_DIR="/opt/sekiguchi-mentor-bot/data"
DATE=$(date +%Y%m%d_%H%M%S)

# 一時圧縮ファイル作成
TEMP_FILE="/tmp/backup_${DATE}.tar.gz"
tar -czf "${TEMP_FILE}" -C "${DATA_DIR}" .

# S3アップロード
aws s3 cp "${TEMP_FILE}" "${S3_BUCKET}/daily/backup_${DATE}.tar.gz"

# 一時ファイル削除
rm "${TEMP_FILE}"

# 古いバックアップ削除（S3ライフサイクルポリシーで管理推奨）
# aws s3 rm "${S3_BUCKET}/daily/" --recursive --exclude "*" --include "backup_$(date -d '31 days ago' +%Y%m%d)*.tar.gz"

echo "[$(date)] S3 backup completed"
```

### 6.4 復旧手順

**ローカルバックアップからの復旧:**
```bash
# 1. サービス停止
sudo systemctl stop sekiguchi-bot

# 2. 現在のデータをバックアップ
mv /opt/sekiguchi-mentor-bot/data /opt/sekiguchi-mentor-bot/data.old

# 3. バックアップファイル展開
cd /backup/sekiguchi-bot
tar -xzf backup_YYYYMMDD_HHMMSS.tar.gz
cp -r YYYYMMDD_HHMMSS /opt/sekiguchi-mentor-bot/data

# 4. 所有権修正
sudo chown -R ubuntu:ubuntu /opt/sekiguchi-mentor-bot/data

# 5. サービス再起動
sudo systemctl start sekiguchi-bot

# 6. 動作確認
sudo systemctl status sekiguchi-bot
```

**S3からの復旧:**
```bash
# S3からダウンロード
aws s3 cp s3://sekiguchi-bot-backups/daily/backup_YYYYMMDD_HHMMSS.tar.gz /tmp/

# 展開
sudo systemctl stop sekiguchi-bot
sudo rm -rf /opt/sekiguchi-mentor-bot/data
sudo mkdir /opt/sekiguchi-mentor-bot/data
sudo tar -xzf /tmp/backup_YYYYMMDD_HHMMSS.tar.gz -C /opt/sekiguchi-mentor-bot/data
sudo chown -R ubuntu:ubuntu /opt/sekiguchi-mentor-bot/data
sudo systemctl start sekiguchi-bot
```

### 6.5 災害復旧計画（DRP）

**目標復旧時間（RTO）:** 2時間
**目標復旧時点（RPO）:** 24時間

**復旧手順書:**
1. 新しいEC2インスタンス起動（10分）
2. アプリケーションデプロイ（20分）
3. S3からデータ復元（15分）
4. DNS切り替え（5分）
5. 動作確認（30分）
6. ユーザー通知（10分）

---

## 7. スケーリング

### 7.1 垂直スケーリング（Scale Up）

**インスタンスタイプ変更:**
```bash
# AWS EC2の場合
# t3.micro → t3.small → t3.medium

# 手順:
# 1. インスタンス停止
# 2. インスタンスタイプ変更
# 3. インスタンス起動
```

### 7.2 水平スケーリング（Scale Out）

**ロードバランサー構成:**

```
        ┌─────────────┐
        │     ALB     │
        │ (443/HTTPS) │
        └──────┬──────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼─────┐   ┌──────▼─────┐
│  Instance1 │   │ Instance2  │
│ (Flask)    │   │ (Flask)    │
└──────┬─────┘   └──────┬─────┘
       │                │
       └───────┬────────┘
               │
        ┌──────▼──────┐
        │  EFS/NFS    │
        │ (共有data/) │
        └─────────────┘
```

**共有ストレージ設定（AWS EFS）:**
```bash
# EFS マウント
sudo apt install -y nfs-common
sudo mkdir /efs
sudo mount -t nfs4 -o nfsvers=4.1 fs-xxxxx.efs.ap-northeast-1.amazonaws.com:/ /efs

# fstab 追加（自動マウント）
echo "fs-xxxxx.efs.ap-northeast-1.amazonaws.com:/ /efs nfs4 defaults,_netdev 0 0" | sudo tee -a /etc/fstab

# アプリからEFS使用
ln -s /efs/data /opt/sekiguchi-mentor-bot/data
```

### 7.3 データベース移行（スケール対応）

**ファイル → PostgreSQL移行:**

```sql
-- テーブル作成
CREATE TABLE users (
    user_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(10) NOT NULL,
    current_weight DECIMAL(5,2) NOT NULL,
    target_weight DECIMAL(5,2) NOT NULL,
    plan VARCHAR(10) NOT NULL,
    preparation_days INTEGER NOT NULL,
    preparation_start_date DATE NOT NULL,
    main_start_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE weight_records (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL REFERENCES users(user_id),
    date DATE NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

CREATE INDEX idx_weight_user_date ON weight_records(user_id, date);
```

**移行スクリプト:**
```python
import psycopg2
import json
import pandas as pd

def migrate_to_postgres():
    """
    ファイルベースデータをPostgreSQLに移行
    """
    conn = psycopg2.connect(
        host="localhost",
        database="sekiguchi_bot",
        user="postgres",
        password="password"
    )
    cur = conn.cursor()

    # プロフィール移行
    for profile_file in glob.glob('data/profile_*.json'):
        with open(profile_file) as f:
            profile = json.load(f)

        cur.execute("""
            INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (
            profile['user_id'], profile['name'], profile['age'],
            profile['gender'], profile['current_weight'], profile['target_weight'],
            profile['plan'], profile['preparation_days'],
            profile['preparation_start_date'], profile['main_start_date'],
            profile['created_at'], profile['updated_at']
        ))

    # 体重データ移行
    for weight_file in glob.glob('data/weight_data_*.csv'):
        user_id = weight_file.split('_')[-1].replace('.csv', '')
        df = pd.read_csv(weight_file)

        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO weight_records (user_id, date, weight)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, date) DO UPDATE SET weight = EXCLUDED.weight
            """, (user_id, row['date'], row['weight']))

    conn.commit()
    cur.close()
    conn.close()
```

---

## 8. トラブルシューティング

### 8.1 よくある問題と対処

| 問題 | 原因 | 対処方法 |
|-----|------|---------|
| Webhook応答なし | サービス停止 | `systemctl status sekiguchi-bot` で確認、再起動 |
| 画像送信失敗 | URL公開されていない | Nginx設定確認、ファイアウォール確認 |
| スケジューラー動作しない | タイムゾーン設定 | `pytz` でタイムゾーン明示 |
| メモリ不足エラー | matplotlib メモリリーク | `plt.close()` 確実に実行 |
| データファイル破損 | ディスク満杯 | バックアップから復元 |

### 8.2 ログ確認コマンド

```bash
# アプリケーションログ（リアルタイム）
tail -f /opt/sekiguchi-mentor-bot/logs/bot.log

# エラーログのみ抽出
grep ERROR /opt/sekiguchi-mentor-bot/logs/bot.log

# 特定ユーザーのログ
grep "U1234567890abcdef" /opt/sekiguchi-mentor-bot/logs/bot.log

# Nginx エラーログ
tail -f /var/log/nginx/sekiguchi-bot-error.log

# Systemd サービスログ
journalctl -u sekiguchi-bot -f
```

### 8.3 デバッグモード起動

```bash
# サービス停止
sudo systemctl stop sekiguchi-bot

# 手動起動（デバッグモード）
cd /opt/sekiguchi-mentor-bot
source venv/bin/activate
export LOG_LEVEL=DEBUG
python app.py

# 別ターミナルでテストリクエスト送信
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{"events": []}'
```

---

## 9. メンテナンス

### 9.1 定期メンテナンス項目

**日次:**
- [ ] ログファイルサイズ確認
- [ ] ディスク使用率確認
- [ ] エラーログ確認

**週次:**
- [ ] バックアップ確認
- [ ] パフォーマンスメトリクス確認
- [ ] セキュリティパッチ確認

**月次:**
- [ ] システムアップデート
- [ ] 不要ファイル削除
- [ ] データベース最適化（DB使用時）
- [ ] SSL証明書期限確認

### 9.2 システムアップデート

```bash
# パッケージアップデート
sudo apt update && sudo apt upgrade -y

# Python パッケージアップデート
cd /opt/sekiguchi-mentor-bot
source venv/bin/activate
pip list --outdated
pip install --upgrade package-name

# requirements.txt 更新
pip freeze > requirements.txt

# サービス再起動
sudo systemctl restart sekiguchi-bot
```

### 9.3 ログローテーション

**/etc/logrotate.d/sekiguchi-bot:**
```
/opt/sekiguchi-mentor-bot/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload sekiguchi-bot > /dev/null 2>&1 || true
    endscript
}
```

---

## 10. セキュリティ対策

### 10.1 ファイアウォール設定

**UFW設定（Ubuntu）:**
```bash
# UFW有効化
sudo ufw enable

# SSH許可（管理者IPのみ）
sudo ufw allow from YOUR_IP_ADDRESS to any port 22

# HTTP/HTTPS許可
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 状態確認
sudo ufw status
```

### 10.2 Fail2Ban設定

**Fail2Ban インストール:**
```bash
sudo apt install -y fail2ban
```

**/etc/fail2ban/jail.local:**
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/sekiguchi-bot-error.log
```

### 10.3 定期的なセキュリティスキャン

```bash
# Lynis（セキュリティ監査ツール）
sudo apt install -y lynis
sudo lynis audit system

# 不要なポート確認
sudo netstat -tulpn

# 不審なプロセス確認
ps aux | grep -v "ubuntu\|root"
```

### 10.4 データ暗号化

**保存時暗号化（EFS使用時）:**
- AWS EFS 作成時に暗号化オプション有効化

**通信時暗号化:**
- HTTPS（TLS 1.2+）使用
- LINE Platform との通信は自動的にHTTPS

---

## 付録A: 運用チェックリスト

### デプロイ前チェックリスト

- [ ] 環境変数設定完了
- [ ] SSL証明書取得
- [ ] Webhook URL 設定・検証
- [ ] バックアップスクリプト設定
- [ ] 監視・アラート設定
- [ ] ログローテーション設定
- [ ] ファイアウォール設定
- [ ] ヘルスチェック動作確認
- [ ] スケジューラー動作確認

### 運用開始後チェックリスト

**毎日:**
- [ ] エラーログ確認
- [ ] ディスク使用率確認

**毎週:**
- [ ] バックアップ確認
- [ ] パフォーマンスメトリクス確認

**毎月:**
- [ ] セキュリティパッチ適用
- [ ] SSL証明書期限確認
- [ ] データクリーンアップ

---

## 付録B: 緊急連絡先・エスカレーション

| レベル | 担当 | 連絡先 | 対応時間 |
|-------|-----|-------|---------|
| Level 1 | 運用担当 | ops@example.com | 24時間 |
| Level 2 | 開発担当 | dev@example.com | 平日9-18時 |
| Level 3 | システム管理者 | admin@example.com | オンコール |

**エスカレーション条件:**
- サービス停止が30分以上継続
- データ損失の可能性
- セキュリティインシデント検知

---

**以上、運用仕様書（デプロイ、監視、バックアップ）**
