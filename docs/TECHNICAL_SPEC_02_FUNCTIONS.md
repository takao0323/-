# 関口式ダイエットメンター - 機能仕様書（Part 2）

**Document Version:** 1.0
**Last Updated:** 2025-12-21
**対象:** 実装エンジニア

---

## 目次

1. [体重記録・グラフ生成機能](#1-体重記録グラフ生成機能)
2. [食事報告・PFC分析機能](#2-食事報告pfc分析機能)
3. [4要素哲学メッセージ機能](#3-4要素哲学メッセージ機能)
4. [状況別最適化メッセージ機能](#4-状況別最適化メッセージ機能)
5. [週次レポート機能](#5-週次レポート機能)
6. [月次レポート機能](#6-月次レポート機能)
7. [関口コラム配信機能](#7-関口コラム配信機能)
8. [コミュニティ機能](#8-コミュニティ機能)

---

## 1. 体重記録・グラフ生成機能

### 1.1 機能概要
ユーザーが送信した体重データを記録し、推移グラフを生成してLINEで返信する。

### 1.2 入力仕様

**ユーザー入力形式:**
```
70.5
```
または
```
体重70.5kg
```

**入力バリデーション:**
- 数値部分を正規表現で抽出: `r'[\d.]+kg|^[\d.]+$'`
- 範囲チェック: 30.0kg ≤ 体重 ≤ 200.0kg
- エラー時: 「正しい体重を入力してください（例: 70.5）」

### 1.3 処理フロー

```
1. テキストメッセージ受信
   ↓
2. 数値抽出・バリデーション
   ↓
3. ユーザーID取得 (event.source.user_id)
   ↓
4. プロフィールデータ読み込み (data/profile_{user_id}.json)
   ↓
5. 体重データ保存 (data/weight_data_{user_id}.csv)
   ├─ 存在しない場合: 新規作成（ヘッダー: date,weight）
   └─ 存在する場合: 追記
   ↓
6. グラフ生成 (matplotlib)
   ├─ サイズ: 10x6 inch
   ├─ 線色: #2E86AB (青)
   ├─ マーカー: 'o'
   ├─ X軸: 日付 (rotation=45)
   └─ Y軸: 体重 (kg)
   ↓
7. 画像保存 (temp/weight_graph_{user_id}.png)
   ↓
8. LINE ImageMessage で送信
   ↓
9. フィードバックメッセージ生成
   ├─ 目標カロリー・PFC計算
   ├─ 体重変化分析（前回比）
   └─ 4要素哲学メッセージ
   ↓
10. TextMessage で送信
```

### 1.4 データ構造

**weight_data_{user_id}.csv:**
```csv
date,weight
2025-12-01,72.5
2025-12-02,72.3
2025-12-03,72.0
```

**保存ロジック:**
```python
import csv
from datetime import datetime

def save_weight_data(user_id, weight):
    filepath = f'data/weight_data_{user_id}.csv'
    today = datetime.now().strftime('%Y-%m-%d')

    # ファイル存在チェック
    file_exists = os.path.isfile(filepath)

    with open(filepath, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['date', 'weight'])
        writer.writerow([today, weight])
```

### 1.5 グラフ生成仕様

**実装（matplotlib）:**
```python
import matplotlib.pyplot as plt
import pandas as pd

def generate_weight_graph(user_id):
    df = pd.read_csv(f'data/weight_data_{user_id}.csv')
    df['date'] = pd.to_datetime(df['date'])

    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['weight'],
             marker='o',
             color='#2E86AB',
             linewidth=2)
    plt.xlabel('日付')
    plt.ylabel('体重 (kg)')
    plt.title('体重推移グラフ')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    filepath = f'temp/weight_graph_{user_id}.png'
    plt.savefig(filepath, dpi=100)
    plt.close()

    return filepath
```

### 1.6 実装ファイル
- `sekiguchi_line_bot/handlers/weight_handler.py`
- `sekiguchi_line_bot/handlers/message_handler.py` (ルーティング)

---

## 2. 食事報告・PFC分析機能（Gemini AI 自動解析）

### 2.1 機能概要
ユーザーが送信した食事の写真をGoogle Gemini AIで自動解析し、料理名・カロリー・PFCバランス（タンパク質・脂質・炭水化物）を推定して評価とアドバイスを返信する。

### 2.2 入力仕様

**ユーザー入力:**
- **画像のみ**（写真撮影またはアップロード）
- 推奨: 料理全体が写るように撮影

**画像形式:**
- JPEG、PNG対応
- ファイルサイズ: LINE Messaging API の制限内（10MB以下推奨）

### 2.3 処理フロー

```
1. リッチメニュー「②今日の食事」タップ
   ↓
2. 食事記録モード ON
   ↓
3. ユーザーが食事写真を送信（ImageMessage）
   ↓
4. LINE APIから画像ダウンロード
   ↓
5. Gemini API に画像を送信
   ├─ モデル: gemini-1.5-flash
   ├─ プロンプト: 料理名、カロリー、PFC推定を依頼
   └─ レスポンス: JSON形式で取得
   ↓
6. Gemini解析結果パース
   ├─ dishes: 料理名
   ├─ total_calories: 総カロリー (kcal)
   ├─ protein_g: タンパク質 (g)
   ├─ fat_g: 脂質 (g)
   ├─ carbs_g: 炭水化物 (g)
   └─ balance_evaluation: バランス評価
   ↓
7. PFC比率計算
   ├─ タンパク質比率 = (protein_g × 4 / 総カロリー) × 100
   ├─ 脂質比率 = (fat_g × 9 / 総カロリー) × 100
   └─ 炭水化物比率 = (carbs_g × 4 / 総カロリー) × 100
   ↓
8. 4要素哲学メッセージ生成
   ├─ 専門家メッセージ（PFC評価に基づく）
   ├─ チアリーダーメッセージ
   ├─ バーテンダーメッセージ
   └─ コメディアンメッセージ
   ↓
9. フィードバックメッセージ送信
   ↓
10. 食事記録モード OFF
```

### 2.4 Gemini AI 解析仕様

**Gemini API 設定:**
- **モデル:** `gemini-1.5-flash`（高速・コスト効率重視）
- **入力:** 食事画像 + プロンプト
- **出力:** JSON形式

**プロンプト例:**
```
この食事画像を分析して、以下の情報をJSON形式で返してください：

1. dishes: 料理名（複数ある場合はカンマ区切り）
2. total_calories: 総カロリー（kcal）の推定値（数値のみ）
3. protein_g: タンパク質（g）の推定値（数値のみ）
4. fat_g: 脂質（g）の推定値（数値のみ）
5. carbs_g: 炭水化物（g）の推定値（数値のみ）
6. balance_evaluation: PFCバランスの評価（「良好」「タンパク質不足」「炭水化物過多」など）

必ずJSON形式で返してください。
```

**レスポンス例:**
```json
{
  "dishes": "鶏胸肉のグリル、ブロッコリー、玄米",
  "total_calories": 650,
  "protein_g": 45,
  "fat_g": 15,
  "carbs_g": 70,
  "balance_evaluation": "良好"
}
```

### 2.5 フィードバックメッセージ生成

**実装例:**
```python
def generate_meal_feedback(analysis_result):
    dishes = analysis_result.get('dishes', '不明')
    calories = analysis_result.get('total_calories', 0)
    protein = analysis_result.get('protein_g', 0)
    fat = analysis_result.get('fat_g', 0)
    carbs = analysis_result.get('carbs_g', 0)
    balance = analysis_result.get('balance_evaluation', '')

    # PFC比率計算
    total_kcal_from_pfc = (protein * 4) + (fat * 9) + (carbs * 4)
    protein_ratio = (protein * 4 / total_kcal_from_pfc) * 100
    fat_ratio = (fat * 9 / total_kcal_from_pfc) * 100
    carbs_ratio = (carbs * 4 / total_kcal_from_pfc) * 100

    # 4要素メッセージ生成
    expert_msg = generate_expert_message(protein, fat, carbs, balance)
    cheerleader_msg = generate_cheerleader_message(balance)
    bartender_msg = generate_bartender_message(balance)
    comedian_msg = generate_comedian_message(dishes, calories)

    # 結合
    feedback = f"""🍽️ 食事記録完了！

【AI解析結果】
📋 料理: {dishes}

【栄養情報】
🔥 カロリー: {calories:.0f} kcal

タンパク質: {protein:.1f}g ({protein_ratio:.1f}%)
脂質: {fat:.1f}g ({fat_ratio:.1f}%)
炭水化物: {carbs:.1f}g ({carbs_ratio:.1f}%)

PFCバランス: {balance}

【関口からのフィードバック】

{expert_msg}

{cheerleader_msg}

{bartender_msg}

{comedian_msg}

この調子で頑張りましょう💪"""

    return feedback
```

### 2.6 4要素別メッセージロジック

**専門家メッセージ（状態別）:**
```python
def generate_expert_message(protein, fat, carbs, balance):
    if "タンパク質不足" in balance or protein < 20:
        return """🎓 専門家として:
タンパク質が少し不足しています。
1食あたり20g以上を目安に、
鶏肉・魚・卵などを追加しましょう。"""
    elif "炭水化物過多" in balance or carbs > 100:
        return """🎓 専門家として:
炭水化物がやや多めです。
減量中は1食40-60gを目安に
調整していきましょう。"""
    # ... 他の条件
```

**チアリーダーメッセージ:**
```python
def generate_cheerleader_message(balance):
    if "良好" in balance:
        return """🎺 チアリーダーとして:
完璧なバランスですね！
この調子で継続していきましょう！"""
    # ... 他の条件
```

**バーテンダーメッセージ:**
```python
def generate_bartender_message(balance):
    if "良好" in balance:
        return """🍸 バーテンダーとして:
バランスを意識できていますね。
素晴らしいです。"""
    # ... 他の条件
```

**コメディアンメッセージ:**
```python
def generate_comedian_message(dishes, calories):
    if calories > 1000:
        return f"""🎭 コメディアンとして:
{calories:.0f}kcal！？
パワフルな食事ですね（笑）
次はもう少し控えめでいきましょう！"""
    # ... 他の条件
```

### 2.7 エラーハンドリング

**Gemini API エラー:**
- タイムアウト: 10秒でリトライ
- 解析失敗: 「⚠️ 画像の解析に失敗しました。もう一度撮影してください。」

**画像ダウンロード失敗:**
- LINE API エラー: 「⚠️ エラーが発生しました。もう一度お試しください。」

### 2.8 環境変数

**必須:**
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

**取得方法:**
1. Google AI Studio にアクセス
2. API Key を生成
3. .env に設定

### 2.9 実装ファイル
- `sekiguchi_line_bot/handlers/meal_handler.py` - Gemini連携メインロジック
- `sekiguchi_line_bot/app.py` - 画像メッセージハンドラー
- `requirements.txt` - `google-generativeai==0.3.2` 追加

---

## 3. 4要素哲学メッセージ機能

### 3.1 機能概要
専門家・チアリーダー・バーテンダー・コメディアンの4要素を組み合わせた多様なメッセージを生成する。

### 3.2 4要素の定義

| 要素 | 絵文字 | 役割 | メッセージ特性 |
|-----|------|-----|-------------|
| 専門家 | 🎓 | Expert | 科学的根拠、データ、具体的数値 |
| チアリーダー | 🎺 | Cheerleader | 承認、励まし、ポジティブ強化 |
| バーテンダー | 🍸 | Bartender | 共感、傾聴、心理的サポート |
| コメディアン | 🎭 | Comedian | ユーモア、軽い冗談、緊張緩和 |

### 3.3 メッセージ生成ロジック

**基本構造:**
```python
def generate_philosophy_message(situation):
    # 4要素からランダム選択（均等または重み付け）
    elements = random.sample(['expert', 'cheerleader', 'bartender', 'comedian'],
                            k=random.randint(1, 4))

    message_parts = []

    for element in elements:
        if element == 'expert':
            message_parts.append(get_expert_message(situation))
        elif element == 'cheerleader':
            message_parts.append(get_cheerleader_message(situation))
        elif element == 'bartender':
            message_parts.append(get_bartender_message(situation))
        elif element == 'comedian':
            message_parts.append(get_comedian_message(situation))

    return '\n\n'.join(message_parts)
```

### 3.4 パターン数計算

**要素別パターン数:**
- 専門家: 35パターン/状況
- チアリーダー: 35パターン/状況
- バーテンダー: 35パターン/状況
- コメディアン: 35パターン/状況

**組み合わせ数:**
```
単一要素: 4通り × 35パターン = 140
2要素組合せ: C(4,2) × 35² = 6 × 1,225 = 7,350
3要素組合せ: C(4,3) × 35³ = 4 × 42,875 = 171,500
4要素組合せ: C(4,4) × 35⁴ = 1 × 1,500,625 = 1,500,625

合計: 1,679,615パターン/状況
```

### 3.5 実装ファイル
- `sekiguchi_bot/advice_data.py` (全4900パターン)
- `sekiguchi_bot/philosophy.py` (メッセージ生成ロジック)

---

## 4. 状況別最適化メッセージ機能

### 4.1 機能概要
ユーザーの状況を8カテゴリーに分類し、4要素の比率を動的に調整して最適なメッセージを生成する。

### 4.2 8つの状況カテゴリー

| カテゴリーID | 状況 | 判定条件 | 要素比率 |
|-----------|-----|---------|---------|
| 1 | excellent_progress | 体重減少率 > 目標 × 1.2 | 🎺50% 🎭30% 🎓20% 🍸0% |
| 2 | struggling_plateau | 7日以上体重変化なし | 🎓40% 🍸40% 🎺20% 🎭0% |
| 3 | struggling_regression | 体重増加 > 0.5kg | 🍸40% 🎓40% 🎺20% 🎭0% |
| 4 | inconsistent_motivated | 記録率 < 50% かつ 最近報告あり | 🎺40% 🎭30% 🎓20% 🍸10% |
| 5 | inconsistent_demotivated | 記録率 < 50% かつ 最近報告なし | 🍸50% 🎺30% 🎓20% 🎭0% |
| 6 | excellent_achievement | 目標達成 | 🎺60% 🎭30% 🎓10% 🍸0% |
| 7 | good_steady | 順調に推移 | 🎓30% 🎺30% 🍸20% 🎭20% |
| 8 | needs_encouragement | その他低調時 | 🎺40% 🍸30% 🎓20% 🎭10% |

### 4.3 状況分析ロジック

**実装例:**
```python
def analyze_user_situation(weight_data, achievement_data, consistency_data):
    """
    ユーザー状況を分析し、カテゴリーを返す

    Args:
        weight_data: DataFrame (date, weight)
        achievement_data: dict (target_weight, current_weight, etc.)
        consistency_data: dict (reporting_rate, last_report_days, etc.)

    Returns:
        str: カテゴリー名
    """

    # 1. 目標達成チェック
    if achievement_data['achieved']:
        return 'excellent_achievement'

    # 2. 体重変化分析（直近7日間）
    recent_7days = weight_data.tail(7)
    if len(recent_7days) >= 2:
        weight_change = recent_7days.iloc[-1]['weight'] - recent_7days.iloc[0]['weight']

        # 優秀な進捗（目標の1.2倍以上）
        expected_change = achievement_data['weekly_target'] * 1.2
        if weight_change <= expected_change:
            return 'excellent_progress'

        # 停滞（7日以上変化なし）
        if abs(weight_change) < 0.2:
            return 'struggling_plateau'

        # 逆行（増加）
        if weight_change > 0.5:
            return 'struggling_regression'

    # 3. 記録継続性チェック
    reporting_rate = consistency_data['rate']
    last_report_days = consistency_data['days_since_last']

    if reporting_rate < 0.5:  # 50%未満
        if last_report_days <= 3:
            return 'inconsistent_motivated'
        else:
            return 'inconsistent_demotivated'

    # 4. 順調な推移
    if weight_change < 0 and reporting_rate >= 0.7:
        return 'good_steady'

    # 5. デフォルト（励まし）
    return 'needs_encouragement'
```

### 4.4 メッセージ生成（重み付け）

**実装例:**
```python
def get_optimized_philosophy_message(name, situation_category, weight_data=None):
    """
    状況に最適化された4要素メッセージを生成
    """

    # カテゴリー別の要素比率
    emphasis_map = {
        'excellent_progress': {'cheerleader': 50, 'comedian': 30, 'expert': 20, 'bartender': 0},
        'struggling_plateau': {'expert': 40, 'bartender': 40, 'cheerleader': 20, 'comedian': 0},
        'struggling_regression': {'bartender': 40, 'expert': 40, 'cheerleader': 20, 'comedian': 0},
        'inconsistent_motivated': {'cheerleader': 40, 'comedian': 30, 'expert': 20, 'bartender': 10},
        'inconsistent_demotivated': {'bartender': 50, 'cheerleader': 30, 'expert': 20, 'comedian': 0},
        'excellent_achievement': {'cheerleader': 60, 'comedian': 30, 'expert': 10, 'bartender': 0},
        'good_steady': {'expert': 30, 'cheerleader': 30, 'bartender': 20, 'comedian': 20},
        'needs_encouragement': {'cheerleader': 40, 'bartender': 30, 'expert': 20, 'comedian': 10}
    }

    emphasis = emphasis_map.get(situation_category, emphasis_map['good_steady'])

    # 重み付けランダム選択
    elements = []
    weights = []
    for element, weight in emphasis.items():
        if weight > 0:
            elements.append(element)
            weights.append(weight)

    selected = random.choices(elements, weights=weights, k=random.randint(2, 3))

    # メッセージ生成
    messages = []
    for element in selected:
        msg = get_element_message(element, situation_category, name)
        messages.append(msg)

    return '\n\n'.join(messages)
```

### 4.5 実装ファイル
- `sekiguchi_bot/optimized_philosophy.py` (600+ lines)
- `sekiguchi_line_bot/handlers/report_handler.py` (統合)

---

## 5. 週次レポート機能

### 5.1 機能概要
毎週日曜日20:00に、過去7日間のデータを分析してレポートを自動送信する。

### 5.2 配信スケジュール

**Cron設定:**
```python
scheduler.add_job(
    func=send_weekly_report,
    trigger=CronTrigger(day_of_week='sun', hour=20, minute=0),
    id='weekly_report'
)
```

### 5.3 レポート内容

**構成:**
```
📊 週次レポート（12/15〜12/21）

【体重変化】
開始: 72.5kg → 現在: 71.3kg
変化: -1.2kg 🎺

【目標達成率】
目標: -0.8kg/週
実績: -1.2kg
達成率: 150% ✨

【記録継続性】
報告日数: 7/7日
継続率: 100% 🎺

【PFCバランス】
タンパク質: 良好 ✓
炭水化物: やや多め △
脂質: 適量 ✓

【来週のアドバイス】
🎓 専門家として:
素晴らしいペースです。ただし急激な減量は
リバウンドリスクがあるため、来週は-0.8kg
を目標にペースを調整しましょう。

🎺 チアリーダーとして:
7日間毎日報告！完璧な継続力です！
この調子で来週も頑張りましょう！
```

### 5.4 データ集計ロジック

**実装例:**
```python
def generate_weekly_report(user_id):
    # 1. プロフィール読み込み
    profile = load_profile(user_id)

    # 2. 体重データ取得（直近7日間）
    weight_df = pd.read_csv(f'data/weight_data_{user_id}.csv')
    weight_df['date'] = pd.to_datetime(weight_df['date'])

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    weekly_data = weight_df[
        (weight_df['date'] >= start_date) &
        (weight_df['date'] <= end_date)
    ]

    # 3. 体重変化計算
    if len(weekly_data) >= 2:
        weight_start = weekly_data.iloc[0]['weight']
        weight_end = weekly_data.iloc[-1]['weight']
        weight_change = weight_end - weight_start
    else:
        return "データ不足のためレポート生成不可"

    # 4. 目標達成率計算
    plan = profile.get('plan', 'light')
    current_weight = weight_end

    if plan == 'light':
        monthly_target_rate = 0.02  # 2%/月
    else:
        monthly_target_rate = 0.04  # 4%/月

    weekly_target_kg = current_weight * monthly_target_rate / 4
    achievement_rate = (abs(weight_change) / weekly_target_kg) * 100

    # 5. 記録継続性計算
    reporting_days = len(weekly_data)
    consistency_rate = (reporting_days / 7) * 100

    # 6. レポート生成
    report = f"""📊 週次レポート（{start_date.strftime('%m/%d')}〜{end_date.strftime('%m/%d')}）

【体重変化】
開始: {weight_start}kg → 現在: {weight_end}kg
変化: {weight_change:+.1f}kg {"🎺" if weight_change < 0 else "⚠️"}

【目標達成率】
目標: -{weekly_target_kg:.1f}kg/週
実績: {weight_change:.1f}kg
達成率: {achievement_rate:.0f}% {"✨" if achievement_rate >= 100 else ""}

【記録継続性】
報告日数: {reporting_days}/7日
継続率: {consistency_rate:.0f}% {"🎺" if consistency_rate >= 80 else ""}
"""

    # 7. 状況別メッセージ追加
    situation = analyze_situation_from_weekly_data(weekly_data, achievement_rate)
    optimized_msg = get_optimized_philosophy_message(
        profile['name'],
        situation,
        weekly_data
    )

    report += f"\n\n【来週のアドバイス】\n{optimized_msg}"

    return report
```

### 5.5 実装ファイル
- `sekiguchi_line_bot/handlers/report_handler.py`
- `sekiguchi_line_bot/scheduler.py`

---

## 6. 月次レポート機能

### 6.1 機能概要
毎月最終日20:00に、月間の総括レポートを自動送信する。

### 6.2 配信スケジュール

**Cron設定:**
```python
from apscheduler.triggers.cron import CronTrigger

scheduler.add_job(
    func=send_monthly_report,
    trigger=CronTrigger(day='last', hour=20, minute=0),
    id='monthly_report'
)
```

### 6.3 レポート内容

**構成:**
```
📅 月次レポート（12月）

【月間体重変化】
開始: 75.0kg → 現在: 71.3kg
変化: -3.7kg 🎺

【プラン別評価】
プラン: ハードプラン
目標: -3.0kg/月（4%）
実績: -3.7kg
達成率: 123% ✨

【記録継続性】
報告日数: 28/30日
継続率: 93% 🎺

【体重推移グラフ】
（グラフ画像送信）

【月間ハイライト】
✓ 最大減量週: 12/8週（-1.5kg）
✓ 最長連続記録: 14日間
⚠️ 停滞期: 12/15〜12/18（4日間）

【来月の目標設定】
🎓 専門家として:
月間-3.7kgは優秀ですが、5%ルールの上限に
近づいています。来月は-2.5kg程度に抑え、
筋肉量維持を優先しましょう。

🎺 チアリーダーとして:
1ヶ月で-3.7kg！素晴らしい成果です！
来月も無理なく継続していきましょう！
```

### 6.4 月間統計計算

**実装例:**
```python
def generate_monthly_report(user_id):
    profile = load_profile(user_id)

    # 月間データ取得
    end_date = datetime.now()
    start_date = end_date.replace(day=1)

    weight_df = pd.read_csv(f'data/weight_data_{user_id}.csv')
    weight_df['date'] = pd.to_datetime(weight_df['date'])

    monthly_data = weight_df[
        (weight_df['date'] >= start_date) &
        (weight_df['date'] <= end_date)
    ]

    # 体重変化
    weight_start = monthly_data.iloc[0]['weight']
    weight_end = monthly_data.iloc[-1]['weight']
    total_change = weight_end - weight_start

    # 目標計算
    plan = profile.get('plan', 'light')
    target_rate = 0.02 if plan == 'light' else 0.04
    target_kg = weight_start * target_rate
    achievement_rate = (abs(total_change) / target_kg) * 100

    # 5%ルールチェック
    max_safe_loss = weight_start * 0.05
    is_safe = abs(total_change) <= max_safe_loss

    # 週別分析
    weekly_changes = []
    for i in range(0, len(monthly_data), 7):
        week_data = monthly_data.iloc[i:i+7]
        if len(week_data) >= 2:
            change = week_data.iloc[-1]['weight'] - week_data.iloc[0]['weight']
            weekly_changes.append(change)

    max_loss_week = min(weekly_changes) if weekly_changes else 0

    # 停滞期検出（体重変化 < 0.2kg が3日以上連続）
    plateau_periods = detect_plateau_periods(monthly_data)

    # レポート生成
    report = f"""📅 月次レポート（{start_date.strftime('%m月')}）

【月間体重変化】
開始: {weight_start}kg → 現在: {weight_end}kg
変化: {total_change:+.1f}kg {"🎺" if total_change < 0 else "⚠️"}

【プラン別評価】
プラン: {"ライトプラン" if plan == 'light' else "ハードプラン"}
目標: -{target_kg:.1f}kg/月（{int(target_rate*100)}%）
実績: {total_change:.1f}kg
達成率: {achievement_rate:.0f}% {"✨" if achievement_rate >= 100 else ""}

【5%ルールチェック】
月間上限: -{max_safe_loss:.1f}kg
実績: {abs(total_change):.1f}kg
評価: {"✓ 安全範囲内" if is_safe else "⚠️ 上限超過"}

【月間ハイライト】
✓ 最大減量週: {max_loss_week:.1f}kg
"""

    if plateau_periods:
        report += f"⚠️ 停滞期: {len(plateau_periods)}回検出\n"

    return report
```

### 6.5 グラフ送信

月次レポートでは、月間全体のグラフ画像も送信する。

```python
def send_monthly_report(line_bot_api, user_id):
    # レポートテキスト生成
    report_text = generate_monthly_report(user_id)

    # グラフ生成
    graph_path = generate_weight_graph(user_id)

    # 送信
    line_bot_api.push_message(
        user_id,
        [
            TextSendMessage(text=report_text),
            ImageSendMessage(
                original_content_url=f"https://your-domain.com/{graph_path}",
                preview_image_url=f"https://your-domain.com/{graph_path}"
            )
        ]
    )
```

### 6.6 実装ファイル
- `sekiguchi_line_bot/handlers/report_handler.py`
- `sekiguchi_line_bot/scheduler.py`

---

## 7. 関口コラム配信機能

### 7.1 機能概要
毎日20:00に、曜日別テーマの関口コラムを全ユーザーに配信する。

### 7.2 配信スケジュール

**Cron設定:**
```python
scheduler.add_job(
    func=send_daily_column,
    trigger=CronTrigger(hour=20, minute=0),
    id='daily_column'
)
```

### 7.3 曜日別テーマ

| 曜日 | テーマ | 内容例 |
|-----|-------|-------|
| 月曜 | 筋トレの基本 | フォームの重要性、BIG3解説 |
| 火曜 | 栄養学 | PFCバランス、タンパク質の重要性 |
| 水曜 | モチベーション | 継続の秘訣、目標設定法 |
| 木曜 | 科学的根拠 | 最新研究、エビデンス紹介 |
| 金曜 | 成功事例・Q&A | 実際の成功例、よくある質問 |
| 土曜 | 実践テクニック | 外食の選び方、時短レシピ |
| 日曜 | 週間振り返り | 1週間の総括、来週の準備 |

### 7.4 コンテンツ構造

**データ構造:**
```python
COLUMN_CONTENTS = {
    0: [  # Monday
        """📚 関口コラム - 月曜日
【筋トレの基本 #1】「フォームが全て」

🎓 専門家として:
重量よりもフォームが重要です。正しいフォームで
行うことで、ターゲット筋肉に確実に効かせられ、
怪我のリスクも最小限に抑えられます。

💡 今日のポイント:
- 鏡で自分のフォームをチェック
- 重量は後からついてくる
- まずは10回×3セットを正確に

明日も頑張りましょう！ 関口""",

        """📚 関口コラム - 月曜日
【筋トレの基本 #2】「BIG3の重要性」
...
"""
    ],
    1: [  # Tuesday - 2 variations
        "...",
        "..."
    ],
    # ... 6までの7曜日分
}
```

### 7.5 配信ロジック

**実装例:**
```python
def send_daily_column(line_bot_api, user_ids):
    """
    全登録ユーザーに日次コラムを配信

    Args:
        line_bot_api: LINE Bot APIインスタンス
        user_ids: list of str (登録ユーザーのLINE ID一覧)
    """
    from datetime import datetime
    import random

    # 曜日取得（0=月曜, 6=日曜）
    weekday = datetime.now().weekday()

    # 該当曜日のコラム取得
    columns = COLUMN_CONTENTS.get(weekday, COLUMN_CONTENTS[0])

    # バリエーションからランダム選択
    column_text = random.choice(columns)

    # 全ユーザーに送信
    for user_id in user_ids:
        try:
            line_bot_api.push_message(
                user_id,
                TextSendMessage(text=column_text)
            )
        except Exception as e:
            print(f"Failed to send column to {user_id}: {e}")
```

### 7.6 ユーザーID管理

登録ユーザーのID一覧を管理するファイル:

**data/registered_users.json:**
```json
{
    "users": [
        "U1234567890abcdef",
        "U2345678901bcdefg",
        "U3456789012cdefgh"
    ]
}
```

### 7.7 実装ファイル
- `sekiguchi_line_bot/handlers/column_handler.py` (557 lines)
- `sekiguchi_line_bot/scheduler.py`

---

## 8. コミュニティ機能

### 8.1 機能概要
LINEグループで交流の場を提供し、毎日10:00に励ましメッセージを配信、キーワードに反応して自動返信する。

### 8.2 配信スケジュール

**Cron設定:**
```python
scheduler.add_job(
    func=send_group_encouragement,
    trigger=CronTrigger(hour=10, minute=0),
    id='group_encouragement'
)
```

### 8.3 グループ招待（Flex Message）

**実装例:**
```python
def handle_group_menu(line_bot_api, event):
    """
    リッチメニューから「交流の場」選択時に招待メッセージ送信
    """
    from linebot.models import FlexSendMessage, BubbleContainer, BoxComponent

    flex_message = FlexSendMessage(
        alt_text='🤝 交流の場への招待',
        contents=BubbleContainer(
            hero=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(
                        text='🤝 交流の場',
                        size='xl',
                        weight='bold',
                        color='#1DB446'
                    )
                ],
                background_color='#F0F8F0'
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='仲間と一緒に頑張りましょう！'),
                    TextComponent(text='・励まし合える仲間'),
                    TextComponent(text='・成功体験のシェア'),
                    TextComponent(text='・質問し合える環境'),
                    SeparatorComponent(margin='lg'),
                    TextComponent(
                        text='📌 グループルール',
                        weight='bold',
                        margin='lg'
                    ),
                    TextComponent(text='1. 互いを尊重する'),
                    TextComponent(text='2. ポジティブな発言'),
                    TextComponent(text='3. 勧誘・宣伝禁止')
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                contents=[
                    ButtonComponent(
                        style='primary',
                        color='#1DB446',
                        action=URIComponentAction(
                            label='グループに参加',
                            uri=os.getenv('GROUP_INVITE_URL', 'https://line.me/R/ti/g/xxx')
                        )
                    )
                ]
            )
        )
    )

    line_bot_api.reply_message(event.reply_token, flex_message)
```

### 8.4 定時励ましメッセージ

**5パターンをローテーション:**
```python
ENCOURAGEMENT_MESSAGES = [
    """🎺 関口からのメッセージ

おはようございます！
今日も小さな一歩を積み重ねていきましょう。

完璧じゃなくていい。
継続することが何より大切です。

今日も応援しています！""",

    """🍸 関口からのメッセージ

他人と比べることじゃなく、
昨日の自分と比べてください。

少しでも前進していれば、
それは立派な成功です。

焦らず、自分のペースで。""",

    # ... 5パターン
]

def send_group_encouragement(line_bot_api, group_id):
    """毎日10:00に励ましメッセージ配信"""
    import random
    message = random.choice(ENCOURAGEMENT_MESSAGES)

    line_bot_api.push_message(
        group_id,
        TextSendMessage(text=message)
    )
```

### 8.5 キーワード自動返信

**実装例:**
```python
def handle_group_post(line_bot_api, event):
    """
    グループ内の投稿にキーワード反応
    """
    text = event.message.text.lower()

    # 成功・達成キーワード
    if any(word in text for word in ['達成', '成功', '減った', 'できた']):
        reply = """🎺 おめでとうございます！

素晴らしい成果ですね！
その調子で継続していきましょう！

他のメンバーの励みにもなります✨"""

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

    # 悩み・停滞キーワード
    elif any(word in text for word in ['停滞', '辛い', '難しい', '悩み']):
        reply = """🍸 その気持ち、よくわかります。

停滞期は誰にでも訪れるものです。
ここを乗り越えたら、また必ず体重は落ち始めます。

諦めずに継続することが大切です。
一緒に頑張りましょう！"""

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )

    # 質問キーワード
    elif any(word in text for word in ['質問', '教えて', 'どうすれば']):
        reply = """🎓 関口がお答えします！

具体的な状況を教えていただければ、
より詳しいアドバイスができます。

・現在の体重と目標体重
・どのくらいの期間取り組んでいるか
・現在の食事内容や運動状況

など、詳細をシェアしてください！"""

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
```

### 8.6 環境変数設定

**必要な環境変数:**
```bash
# .env
GROUP_LINE_ID=C1234567890abcdef     # グループID
GROUP_INVITE_URL=https://line.me/R/ti/g/xxx  # 招待URL
```

### 8.7 実装ファイル
- `sekiguchi_line_bot/handlers/group_handler.py` (370 lines)
- `sekiguchi_line_bot/scheduler.py`

---

## 付録A: エラーハンドリング

### A.1 共通エラー処理

**全ハンドラーで実装すべきエラー処理:**

```python
try:
    # メイン処理
    process_user_input(event)
except ValueError as e:
    # 入力値エラー
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"⚠️ 入力エラー: {str(e)}")
    )
except FileNotFoundError:
    # データファイル未作成
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="まず初回登録を完了してください。")
    )
except Exception as e:
    # 予期しないエラー
    logger.error(f"Unexpected error: {e}")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="エラーが発生しました。時間をおいて再度お試しください。")
    )
```

### A.2 LINE API エラー

```python
from linebot.exceptions import LineBotApiError

try:
    line_bot_api.push_message(user_id, message)
except LineBotApiError as e:
    if e.status_code == 400:
        logger.error(f"Invalid request: {e.message}")
    elif e.status_code == 401:
        logger.error(f"Invalid access token")
    elif e.status_code == 429:
        logger.warning(f"Rate limit exceeded")
    else:
        logger.error(f"LINE API Error: {e}")
```

---

## 付録B: パフォーマンス最適化

### B.1 CSV読み込み最適化

大量データの場合、pandas のチャンク読み込みを使用:

```python
import pandas as pd

def load_weight_data_optimized(user_id, limit=100):
    """直近N件のみ読み込み"""
    df = pd.read_csv(
        f'data/weight_data_{user_id}.csv',
        parse_dates=['date']
    )
    return df.tail(limit)  # 直近100件のみ
```

### B.2 グラフ生成キャッシュ

同日内の重複生成を避ける:

```python
from functools import lru_cache
from datetime import date

@lru_cache(maxsize=100)
def generate_weight_graph_cached(user_id, today):
    """日付をキーにキャッシュ"""
    return generate_weight_graph(user_id)

# 使用例
graph_path = generate_weight_graph_cached(user_id, date.today())
```

---

**以上、全8機能の詳細仕様**
