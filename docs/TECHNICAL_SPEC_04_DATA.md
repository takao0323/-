# 関口式ダイエットメンター - データ仕様書（Part 4）

**Document Version:** 1.0
**Last Updated:** 2025-12-21
**対象:** 実装エンジニア

---

## 目次

1. [データストレージ概要](#1-データストレージ概要)
2. [プロフィールデータ（JSON）](#2-プロフィールデータjson)
3. [体重データ（CSV）](#3-体重データcsv)
4. [登録ユーザー管理（JSON）](#4-登録ユーザー管理json)
5. [カロリー計算式](#5-カロリー計算式)
6. [PFCバランス計算式](#6-pfcバランス計算式)
7. [5%ルール計算](#7-5ルール計算)
8. [基礎代謝計算（Harris-Benedict式）](#8-基礎代謝計算harris-benedict式)
9. [データバリデーション](#9-データバリデーション)
10. [データ移行・バックアップ](#10-データ移行バックアップ)

---

## 1. データストレージ概要

### 1.1 ストレージ方式

**ファイルベースストレージ（軽量・シンプル）**
- ユーザー数が少ない場合に最適（〜1000ユーザー）
- データベース不要
- バックアップが容易

### 1.2 ディレクトリ構造

```
project_root/
├── data/
│   ├── profile_{user_id}.json          # ユーザープロフィール
│   ├── weight_data_{user_id}.csv       # 体重記録
│   └── registered_users.json           # 登録ユーザー一覧
├── temp/
│   └── weight_graph_{user_id}.png      # 一時グラフ画像
└── logs/
    └── bot.log                          # アプリケーションログ
```

### 1.3 ファイル命名規則

| ファイルタイプ | 命名形式 | 例 |
|------------|---------|---|
| プロフィール | `profile_{user_id}.json` | `profile_U1234567890abcdef.json` |
| 体重データ | `weight_data_{user_id}.csv` | `weight_data_U1234567890abcdef.csv` |
| グラフ画像 | `weight_graph_{user_id}.png` | `weight_graph_U1234567890abcdef.png` |

**user_id の形式:**
- LINE User ID: `U` + 16文字の英数字
- 例: `U1234567890abcdef`

### 1.4 文字エンコーディング

**全ファイル共通:**
- エンコーディング: **UTF-8**
- 改行コード: **LF** (Unix形式)

---

## 2. プロフィールデータ（JSON）

### 2.1 ファイル名

`data/profile_{user_id}.json`

### 2.2 データスキーマ

```json
{
  "user_id": "U1234567890abcdef",
  "name": "山田太郎",
  "age": 30,
  "gender": "male",
  "current_weight": 70.5,
  "target_weight": 65.0,
  "plan": "hard",
  "preparation_days": 7,
  "preparation_start_date": "2025-12-01",
  "main_start_date": "2025-12-08",
  "created_at": "2025-12-01T10:30:00",
  "updated_at": "2025-12-21T15:45:00"
}
```

### 2.3 フィールド定義

| フィールド | 型 | 必須 | 説明 | 制約 |
|----------|---|-----|------|------|
| `user_id` | string | ✓ | LINE User ID | `U` + 16文字 |
| `name` | string | ✓ | 表示名 | 1-50文字 |
| `age` | integer | ✓ | 年齢 | 18-100 |
| `gender` | string | ✓ | 性別 | `"male"` または `"female"` |
| `current_weight` | float | ✓ | 現在体重 (kg) | 30.0-200.0 |
| `target_weight` | float | ✓ | 目標体重 (kg) | 30.0-200.0 |
| `plan` | string | ✓ | プラン | `"light"` または `"hard"` |
| `preparation_days` | integer | ✓ | 準備期間 (日) | 7 (固定) |
| `preparation_start_date` | string | ✓ | 準備期間開始日 | `YYYY-MM-DD` |
| `main_start_date` | string | ✓ | 本格開始日 | `YYYY-MM-DD` |
| `created_at` | string | ✓ | 作成日時 | ISO 8601形式 |
| `updated_at` | string | ✓ | 更新日時 | ISO 8601形式 |

### 2.4 プラン定義

| プラン | 月間減量率 | 週間減量率 | 対象 |
|------|----------|----------|------|
| `light` | 2% | 0.5% | 緩やかに減量したい方 |
| `hard` | 4% | 1.0% | 短期集中で減量したい方 |

### 2.5 CRUD操作実装

**作成（Create）:**
```python
import json
from datetime import datetime, timedelta

def create_profile(user_id, name, age, gender, current_weight, target_weight, plan):
    """
    新規プロフィール作成

    Args:
        user_id: str (LINE User ID)
        name: str
        age: int
        gender: str ("male" or "female")
        current_weight: float
        target_weight: float
        plan: str ("light" or "hard")

    Returns:
        dict: 作成されたプロフィール
    """
    # 準備期間計算
    preparation_start = datetime.now()
    main_start = preparation_start + timedelta(days=7)

    profile = {
        "user_id": user_id,
        "name": name,
        "age": age,
        "gender": gender,
        "current_weight": current_weight,
        "target_weight": target_weight,
        "plan": plan,
        "preparation_days": 7,
        "preparation_start_date": preparation_start.strftime('%Y-%m-%d'),
        "main_start_date": main_start.strftime('%Y-%m-%d'),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    # ファイル保存
    filepath = f'data/profile_{user_id}.json'
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    return profile
```

**読み込み（Read）:**
```python
def load_profile(user_id):
    """
    プロフィール読み込み

    Args:
        user_id: str

    Returns:
        dict or None
    """
    filepath = f'data/profile_{user_id}.json'

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            profile = json.load(f)
        return profile
    except FileNotFoundError:
        return None
```

**更新（Update）:**
```python
def update_profile(user_id, updates):
    """
    プロフィール更新

    Args:
        user_id: str
        updates: dict (更新するフィールド)

    Returns:
        dict: 更新後のプロフィール
    """
    profile = load_profile(user_id)

    if profile is None:
        raise ValueError(f"Profile not found: {user_id}")

    # フィールド更新
    for key, value in updates.items():
        if key in profile:
            profile[key] = value

    # 更新日時を自動更新
    profile['updated_at'] = datetime.now().isoformat()

    # ファイル保存
    filepath = f'data/profile_{user_id}.json'
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    return profile
```

**削除（Delete）:**
```python
import os

def delete_profile(user_id):
    """
    プロフィール削除

    Args:
        user_id: str

    Returns:
        bool: 削除成功
    """
    filepath = f'data/profile_{user_id}.json'

    try:
        os.remove(filepath)
        return True
    except FileNotFoundError:
        return False
```

---

## 3. 体重データ（CSV）

### 3.1 ファイル名

`data/weight_data_{user_id}.csv`

### 3.2 データスキーマ

**CSV形式:**
```csv
date,weight
2025-12-01,72.5
2025-12-02,72.3
2025-12-03,72.0
2025-12-04,71.8
2025-12-05,71.5
```

### 3.3 フィールド定義

| カラム | 型 | 説明 | 制約 |
|-------|---|------|------|
| `date` | string | 記録日 | `YYYY-MM-DD` 形式 |
| `weight` | float | 体重 (kg) | 30.0-200.0, 小数第1位まで |

### 3.4 CRUD操作実装

**追記（Append）:**
```python
import csv
from datetime import datetime

def save_weight_data(user_id, weight):
    """
    体重データを追記

    Args:
        user_id: str
        weight: float

    Returns:
        None
    """
    filepath = f'data/weight_data_{user_id}.csv'
    today = datetime.now().strftime('%Y-%m-%d')

    # ファイル存在チェック
    file_exists = os.path.isfile(filepath)

    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # 新規ファイルの場合、ヘッダー書き込み
        if not file_exists:
            writer.writerow(['date', 'weight'])

        # データ書き込み
        writer.writerow([today, weight])
```

**読み込み（Read）:**
```python
import pandas as pd

def load_weight_data(user_id, limit=None):
    """
    体重データを読み込み

    Args:
        user_id: str
        limit: int or None (取得件数制限)

    Returns:
        DataFrame: columns=['date', 'weight']
    """
    filepath = f'data/weight_data_{user_id}.csv'

    try:
        df = pd.read_csv(filepath, parse_dates=['date'])

        if limit:
            df = df.tail(limit)

        return df
    except FileNotFoundError:
        # 空のDataFrameを返す
        return pd.DataFrame(columns=['date', 'weight'])
```

**最新データ取得:**
```python
def get_latest_weight(user_id):
    """
    最新の体重を取得

    Args:
        user_id: str

    Returns:
        float or None
    """
    df = load_weight_data(user_id)

    if df.empty:
        return None

    return df.iloc[-1]['weight']
```

**期間指定取得:**
```python
from datetime import datetime, timedelta

def get_weight_range(user_id, start_date, end_date):
    """
    期間を指定して体重データを取得

    Args:
        user_id: str
        start_date: datetime
        end_date: datetime

    Returns:
        DataFrame
    """
    df = load_weight_data(user_id)

    if df.empty:
        return df

    # 期間フィルタ
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    return df[mask]
```

**同日データの上書き処理:**
```python
def save_weight_data_with_overwrite(user_id, weight):
    """
    同日の体重データがある場合は上書き

    Args:
        user_id: str
        weight: float
    """
    filepath = f'data/weight_data_{user_id}.csv'
    today = datetime.now().strftime('%Y-%m-%d')

    # 既存データ読み込み
    df = load_weight_data(user_id)

    if df.empty:
        # 新規作成
        df = pd.DataFrame({'date': [today], 'weight': [weight]})
    else:
        # 同日データチェック
        today_dt = pd.to_datetime(today)
        if today_dt in df['date'].values:
            # 上書き
            df.loc[df['date'] == today_dt, 'weight'] = weight
        else:
            # 追加
            new_row = pd.DataFrame({'date': [today_dt], 'weight': [weight]})
            df = pd.concat([df, new_row], ignore_index=True)

    # ソート（日付昇順）
    df = df.sort_values('date')

    # ファイル保存
    df.to_csv(filepath, index=False, date_format='%Y-%m-%d')
```

---

## 4. 登録ユーザー管理（JSON）

### 4.1 ファイル名

`data/registered_users.json`

### 4.2 データスキーマ

```json
{
  "users": [
    {
      "user_id": "U1234567890abcdef",
      "registered_at": "2025-12-01T10:30:00",
      "active": true
    },
    {
      "user_id": "U2345678901bcdefg",
      "registered_at": "2025-12-05T14:20:00",
      "active": true
    }
  ]
}
```

### 4.3 フィールド定義

| フィールド | 型 | 説明 |
|----------|---|------|
| `user_id` | string | LINE User ID |
| `registered_at` | string | 登録日時（ISO 8601） |
| `active` | boolean | アクティブ状態（ブロック時false） |

### 4.4 操作実装

**ユーザー追加:**
```python
def add_user_to_registry(user_id):
    """
    登録ユーザーリストに追加

    Args:
        user_id: str
    """
    filepath = 'data/registered_users.json'

    # 既存リスト読み込み
    if os.path.isfile(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {'users': []}

    # 重複チェック
    if any(u['user_id'] == user_id for u in data['users']):
        return

    # 追加
    data['users'].append({
        'user_id': user_id,
        'registered_at': datetime.now().isoformat(),
        'active': True
    })

    # 保存
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

**アクティブユーザー取得:**
```python
def get_active_user_ids():
    """
    アクティブなユーザーIDリストを取得

    Returns:
        list[str]
    """
    filepath = 'data/registered_users.json'

    if not os.path.isfile(filepath):
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return [u['user_id'] for u in data['users'] if u['active']]
```

---

## 5. カロリー計算式

### 5.1 目標カロリー計算フロー

```
1. 基礎代謝（BMR）計算
   ↓
2. 活動代謝（TDEE）計算
   ↓
3. 目標減量カロリー計算
   ↓
4. 準備期間/本格期間の調整
   ↓
5. 最終目標カロリー
```

### 5.2 基礎代謝（BMR）計算

**Harris-Benedict式（改訂版）:**

**男性:**
```
BMR = 13.397 × 体重(kg) + 4.799 × 身長(cm) - 5.677 × 年齢 + 88.362
```

**女性:**
```
BMR = 9.247 × 体重(kg) + 3.098 × 身長(cm) - 4.330 × 年齢 + 447.593
```

**実装:**
```python
def calculate_bmr(weight, height, age, gender):
    """
    基礎代謝（BMR）を計算

    Args:
        weight: float (kg)
        height: float (cm)
        age: int
        gender: str ("male" or "female")

    Returns:
        float: BMR (kcal/日)
    """
    if gender == "male":
        bmr = 13.397 * weight + 4.799 * height - 5.677 * age + 88.362
    elif gender == "female":
        bmr = 9.247 * weight + 3.098 * height - 4.330 * age + 447.593
    else:
        raise ValueError(f"Invalid gender: {gender}")

    return round(bmr, 2)
```

**計算例:**
```
男性、30歳、70kg、170cm の場合:
BMR = 13.397 × 70 + 4.799 × 170 - 5.677 × 30 + 88.362
    = 937.79 + 815.83 - 170.31 + 88.362
    = 1,671.66 kcal/日
```

### 5.3 活動代謝（TDEE）計算

**活動レベル係数:**

| レベル | 係数 | 説明 |
|-------|-----|------|
| 座りがち | 1.2 | デスクワーク中心 |
| 軽い運動 | 1.375 | 週1-3回の運動 |
| 中程度の運動 | 1.55 | 週3-5回の運動 |
| 激しい運動 | 1.725 | 週6-7回の運動 |
| 非常に激しい運動 | 1.9 | 1日2回の運動 |

**デフォルト設定:**
- 本システムでは **1.2（座りがち）** を使用
- 理由: 保守的な設定で確実な減量を促す

**実装:**
```python
def calculate_tdee(bmr, activity_level=1.2):
    """
    活動代謝（TDEE）を計算

    Args:
        bmr: float (kcal/日)
        activity_level: float (活動係数)

    Returns:
        float: TDEE (kcal/日)
    """
    tdee = bmr * activity_level
    return round(tdee, 2)
```

**計算例:**
```
BMR 1,671.66 kcal/日 の場合:
TDEE = 1,671.66 × 1.2 = 2,005.99 kcal/日
```

### 5.4 目標減量カロリー計算

**基本式:**
```
1kg の体脂肪 = 7,200 kcal
```

**プラン別計算:**

**ライトプラン（月間2%減量）:**
```
月間減量kg = 現在体重 × 0.02
週間減量kg = 月間減量kg ÷ 4
日間減量kg = 週間減量kg ÷ 7

カロリー調整 = 日間減量kg × 7,200 kcal
目標カロリー = TDEE - カロリー調整
```

**ハードプラン（月間4%減量）:**
```
月間減量kg = 現在体重 × 0.04
週間減量kg = 月間減量kg ÷ 4
日間減量kg = 週間減量kg ÷ 7

カロリー調整 = 日間減量kg × 7,200 kcal
目標カロリー = TDEE - カロリー調整
```

**実装:**
```python
def calculate_target_nutrition(profile):
    """
    目標カロリーとPFCを計算

    Args:
        profile: dict (ユーザープロフィール)

    Returns:
        dict: {
            'bmr': float,
            'tdee': float,
            'target_calories': float,
            'protein_g': float,
            'fat_g': float,
            'carbs_g': float
        }
    """
    # 身長はデフォルト170cm（プロフィールにない場合）
    height = profile.get('height', 170)

    # BMR計算
    bmr = calculate_bmr(
        profile['current_weight'],
        height,
        profile['age'],
        profile['gender']
    )

    # TDEE計算
    tdee = calculate_tdee(bmr, activity_level=1.2)

    # プラン別減量率
    plan = profile.get('plan', 'light')
    if plan == 'light':
        monthly_rate = 0.02  # 2%
    else:
        monthly_rate = 0.04  # 4%

    # 日間減量kg
    daily_weight_loss_kg = (profile['current_weight'] * monthly_rate) / 30

    # カロリー調整
    calorie_adjustment = daily_weight_loss_kg * 7200

    # 目標カロリー
    target_calories = tdee - calorie_adjustment

    # 準備期間中は-200kcal のみ
    from datetime import datetime
    today = datetime.now().date()
    main_start = datetime.strptime(profile['main_start_date'], '%Y-%m-%d').date()

    if today < main_start:
        # 準備期間
        target_calories = tdee - 200

    # PFC計算（後述）
    protein_g = calculate_protein(profile['current_weight'])
    fat_g = calculate_fat(target_calories)
    carbs_g = calculate_carbs(target_calories, protein_g, fat_g)

    return {
        'bmr': round(bmr, 2),
        'tdee': round(tdee, 2),
        'target_calories': round(target_calories, 2),
        'protein_g': round(protein_g, 2),
        'fat_g': round(fat_g, 2),
        'carbs_g': round(carbs_g, 2)
    }
```

### 5.5 計算例

**ライトプラン（70kg、30歳、男性）:**
```
BMR = 1,671.66 kcal/日
TDEE = 2,005.99 kcal/日

月間減量 = 70kg × 0.02 = 1.4kg
日間減量 = 1.4kg ÷ 30 = 0.0467kg/日

カロリー調整 = 0.0467kg × 7,200kcal = 336kcal

目標カロリー = 2,005.99 - 336 = 1,670kcal/日
```

**ハードプラン（70kg、30歳、男性）:**
```
BMR = 1,671.66 kcal/日
TDEE = 2,005.99 kcal/日

月間減量 = 70kg × 0.04 = 2.8kg
日間減量 = 2.8kg ÷ 30 = 0.0933kg/日

カロリー調整 = 0.0933kg × 7,200kcal = 672kcal

目標カロリー = 2,005.99 - 672 = 1,334kcal/日
```

---

## 6. PFCバランス計算式

### 6.1 PFC比率

**理想比率:**
- **P（Protein / タンパク質）:** 30%
- **F（Fat / 脂質）:** 20%
- **C（Carbohydrate / 炭水化物）:** 50%

### 6.2 カロリー換算係数

| 栄養素 | カロリー/g |
|-------|----------|
| タンパク質 | 4 kcal/g |
| 脂質 | 9 kcal/g |
| 炭水化物 | 4 kcal/g |

### 6.3 タンパク質計算

**基本式:**
```
タンパク質(g) = 体重(kg) × 1.5 〜 2.0
```

**本システムの採用値:**
```
タンパク質(g) = 体重(kg) × 1.5
```

**実装:**
```python
def calculate_protein(weight):
    """
    目標タンパク質量を計算

    Args:
        weight: float (kg)

    Returns:
        float: タンパク質 (g/日)
    """
    return weight * 1.5
```

**計算例:**
```
70kg の場合:
タンパク質 = 70kg × 1.5 = 105g/日
カロリー = 105g × 4kcal/g = 420kcal
```

### 6.4 脂質計算

**基本式:**
```
脂質カロリー = 目標カロリー × 0.20
脂質(g) = 脂質カロリー ÷ 9
```

**実装:**
```python
def calculate_fat(target_calories):
    """
    目標脂質量を計算

    Args:
        target_calories: float (kcal/日)

    Returns:
        float: 脂質 (g/日)
    """
    fat_calories = target_calories * 0.20
    return fat_calories / 9
```

**計算例:**
```
目標カロリー 1,670kcal の場合:
脂質カロリー = 1,670 × 0.20 = 334kcal
脂質 = 334 ÷ 9 = 37.1g/日
```

### 6.5 炭水化物計算

**基本式:**
```
炭水化物カロリー = 目標カロリー - タンパク質カロリー - 脂質カロリー
炭水化物(g) = 炭水化物カロリー ÷ 4
```

**実装:**
```python
def calculate_carbs(target_calories, protein_g, fat_g):
    """
    目標炭水化物量を計算

    Args:
        target_calories: float (kcal/日)
        protein_g: float (g/日)
        fat_g: float (g/日)

    Returns:
        float: 炭水化物 (g/日)
    """
    protein_calories = protein_g * 4
    fat_calories = fat_g * 9
    carbs_calories = target_calories - protein_calories - fat_calories
    return carbs_calories / 4
```

**計算例:**
```
目標カロリー 1,670kcal、タンパク質 105g、脂質 37.1g の場合:

タンパク質カロリー = 105 × 4 = 420kcal
脂質カロリー = 37.1 × 9 = 334kcal
炭水化物カロリー = 1,670 - 420 - 334 = 916kcal
炭水化物 = 916 ÷ 4 = 229g/日
```

### 6.6 PFC計算統合

**完全実装:**
```python
def calculate_pfc_balance(target_calories, weight):
    """
    PFCバランスを計算

    Args:
        target_calories: float (kcal/日)
        weight: float (kg)

    Returns:
        dict: {
            'protein_g': float,
            'protein_kcal': float,
            'protein_ratio': float,
            'fat_g': float,
            'fat_kcal': float,
            'fat_ratio': float,
            'carbs_g': float,
            'carbs_kcal': float,
            'carbs_ratio': float,
            'total_kcal': float
        }
    """
    # タンパク質
    protein_g = weight * 1.5
    protein_kcal = protein_g * 4

    # 脂質
    fat_kcal = target_calories * 0.20
    fat_g = fat_kcal / 9

    # 炭水化物
    carbs_kcal = target_calories - protein_kcal - fat_kcal
    carbs_g = carbs_kcal / 4

    # 比率計算
    total_kcal = protein_kcal + fat_kcal + carbs_kcal
    protein_ratio = (protein_kcal / total_kcal) * 100
    fat_ratio = (fat_kcal / total_kcal) * 100
    carbs_ratio = (carbs_kcal / total_kcal) * 100

    return {
        'protein_g': round(protein_g, 1),
        'protein_kcal': round(protein_kcal, 1),
        'protein_ratio': round(protein_ratio, 1),
        'fat_g': round(fat_g, 1),
        'fat_kcal': round(fat_kcal, 1),
        'fat_ratio': round(fat_ratio, 1),
        'carbs_g': round(carbs_g, 1),
        'carbs_kcal': round(carbs_kcal, 1),
        'carbs_ratio': round(carbs_ratio, 1),
        'total_kcal': round(total_kcal, 1)
    }
```

---

## 7. 5%ルール計算

### 7.1 5%ルールとは

**定義:**
- 月間の体重減少は **現在体重の5%まで**
- これを超えると **ホメオスタシス（恒常性）** が働く
- リバウンドリスクが高まる

### 7.2 計算式

```
月間上限減量kg = 現在体重(kg) × 0.05
```

### 7.3 実装

```python
def calculate_5_percent_limit(current_weight):
    """
    5%ルール上限を計算

    Args:
        current_weight: float (kg)

    Returns:
        float: 月間上限減量 (kg)
    """
    return current_weight * 0.05
```

**計算例:**
```
70kg の場合:
月間上限 = 70kg × 0.05 = 3.5kg
```

### 7.4 プラン妥当性チェック

**ハードプランの検証:**
```python
def validate_plan_against_5_percent_rule(profile):
    """
    選択プランが5%ルールに違反していないか確認

    Args:
        profile: dict

    Returns:
        dict: {
            'valid': bool,
            'plan_loss': float,
            'max_safe_loss': float,
            'message': str
        }
    """
    current_weight = profile['current_weight']
    plan = profile.get('plan', 'light')

    # プラン別月間減量
    if plan == 'light':
        monthly_rate = 0.02  # 2%
    else:
        monthly_rate = 0.04  # 4%

    plan_loss = current_weight * monthly_rate
    max_safe_loss = current_weight * 0.05

    valid = plan_loss <= max_safe_loss

    if valid:
        message = f"✓ 安全範囲内です（計画: {plan_loss:.1f}kg、上限: {max_safe_loss:.1f}kg）"
    else:
        message = f"⚠️ 5%ルール超過（計画: {plan_loss:.1f}kg、上限: {max_safe_loss:.1f}kg）"

    return {
        'valid': valid,
        'plan_loss': round(plan_loss, 1),
        'max_safe_loss': round(max_safe_loss, 1),
        'message': message
    }
```

**計算例:**
```
70kg、ハードプラン（4%）の場合:
計画減量 = 70kg × 0.04 = 2.8kg
上限減量 = 70kg × 0.05 = 3.5kg

2.8kg ≤ 3.5kg → ✓ 安全範囲内
```

### 7.5 月次レポートでのチェック

```python
def check_monthly_weight_loss(user_id):
    """
    月間実績が5%ルール内か確認

    Args:
        user_id: str

    Returns:
        dict
    """
    # 月初・月末の体重取得
    from datetime import datetime
    end_date = datetime.now()
    start_date = end_date.replace(day=1)

    weight_df = get_weight_range(user_id, start_date, end_date)

    if len(weight_df) < 2:
        return {'valid': None, 'message': 'データ不足'}

    weight_start = weight_df.iloc[0]['weight']
    weight_end = weight_df.iloc[-1]['weight']
    actual_loss = weight_start - weight_end
    max_safe_loss = weight_start * 0.05

    valid = actual_loss <= max_safe_loss

    return {
        'valid': valid,
        'actual_loss': round(actual_loss, 1),
        'max_safe_loss': round(max_safe_loss, 1),
        'message': "✓ 安全範囲内" if valid else "⚠️ 5%ルール超過"
    }
```

---

## 8. 基礎代謝計算（Harris-Benedict式）

### 8.1 式の詳細

**Harris-Benedict式（改訂版、1984年）**

**男性:**
```
BMR = 13.397W + 4.799H - 5.677A + 88.362
```

**女性:**
```
BMR = 9.247W + 3.098H - 4.330A + 447.593
```

**変数:**
- `W` = 体重 (kg)
- `H` = 身長 (cm)
- `A` = 年齢 (歳)

### 8.2 年齢・性別による違い

**年齢別BMR（70kg、170cm の場合）:**

| 年齢 | 男性 BMR | 女性 BMR | 差 |
|-----|---------|---------|---|
| 20歳 | 1,728 kcal | 1,433 kcal | 295 kcal |
| 30歳 | 1,672 kcal | 1,390 kcal | 282 kcal |
| 40歳 | 1,615 kcal | 1,347 kcal | 268 kcal |
| 50歳 | 1,558 kcal | 1,304 kcal | 254 kcal |

**傾向:**
- 年齢が上がるとBMRは低下
- 男性の方が女性より約15-20%高い

### 8.3 身長による調整

**身長データがない場合のデフォルト値:**
- 男性: **170 cm**
- 女性: **158 cm**

**実装:**
```python
def get_default_height(gender):
    """
    性別に応じたデフォルト身長

    Args:
        gender: str

    Returns:
        float: 身長 (cm)
    """
    if gender == "male":
        return 170.0
    else:
        return 158.0
```

---

## 9. データバリデーション

### 9.1 体重バリデーション

**制約:**
- 範囲: **30.0kg 〜 200.0kg**
- 小数第1位まで
- 前回比の異常値チェック（±10kg/日）

**実装:**
```python
def validate_weight(weight, previous_weight=None):
    """
    体重データを検証

    Args:
        weight: float
        previous_weight: float or None

    Returns:
        dict: {'valid': bool, 'message': str}

    Raises:
        ValueError: バリデーションエラー
    """
    # 範囲チェック
    if weight < 30.0 or weight > 200.0:
        return {
            'valid': False,
            'message': '体重は30.0kg〜200.0kgの範囲で入力してください'
        }

    # 前回比チェック
    if previous_weight is not None:
        diff = abs(weight - previous_weight)
        if diff > 10.0:
            return {
                'valid': False,
                'message': f'前回比{diff:.1f}kgは異常値です。入力を確認してください'
            }

    return {'valid': True, 'message': 'OK'}
```

### 9.2 年齢バリデーション

**制約:**
- 範囲: **18歳 〜 100歳**

**実装:**
```python
def validate_age(age):
    """
    年齢を検証

    Args:
        age: int

    Returns:
        dict: {'valid': bool, 'message': str}
    """
    if age < 18 or age > 100:
        return {
            'valid': False,
            'message': '年齢は18歳〜100歳の範囲で入力してください'
        }

    return {'valid': True, 'message': 'OK'}
```

### 9.3 性別バリデーション

**許可値:**
- `"male"` (男性)
- `"female"` (女性)

**実装:**
```python
def validate_gender(gender):
    """
    性別を検証

    Args:
        gender: str

    Returns:
        dict: {'valid': bool, 'message': str}
    """
    if gender not in ['male', 'female']:
        return {
            'valid': False,
            'message': '性別は"male"または"female"を指定してください'
        }

    return {'valid': True, 'message': 'OK'}
```

### 9.4 プランバリデーション

**許可値:**
- `"light"` (ライトプラン)
- `"hard"` (ハードプラン)

**実装:**
```python
def validate_plan(plan):
    """
    プランを検証

    Args:
        plan: str

    Returns:
        dict: {'valid': bool, 'message': str}
    """
    if plan not in ['light', 'hard']:
        return {
            'valid': False,
            'message': 'プランは"light"または"hard"を指定してください'
        }

    return {'valid': True, 'message': 'OK'}
```

### 9.5 総合バリデーション

**プロフィール作成時の一括検証:**
```python
def validate_profile_data(data):
    """
    プロフィールデータを一括検証

    Args:
        data: dict

    Returns:
        dict: {'valid': bool, 'errors': list}
    """
    errors = []

    # 体重チェック
    result = validate_weight(data.get('current_weight'))
    if not result['valid']:
        errors.append(result['message'])

    result = validate_weight(data.get('target_weight'))
    if not result['valid']:
        errors.append(result['message'])

    # 年齢チェック
    result = validate_age(data.get('age'))
    if not result['valid']:
        errors.append(result['message'])

    # 性別チェック
    result = validate_gender(data.get('gender'))
    if not result['valid']:
        errors.append(result['message'])

    # プランチェック
    result = validate_plan(data.get('plan'))
    if not result['valid']:
        errors.append(result['message'])

    # 目標体重の妥当性チェック
    if data.get('target_weight') >= data.get('current_weight'):
        errors.append('目標体重は現在体重より低く設定してください')

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }
```

---

## 10. データ移行・バックアップ

### 10.1 バックアップ戦略

**日次バックアップ:**
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="backups/$DATE"

mkdir -p $BACKUP_DIR
cp -r data/* $BACKUP_DIR/

# 30日以上前のバックアップを削除
find backups/* -mtime +30 -exec rm -rf {} \;
```

**Cron設定（毎日3:00）:**
```bash
0 3 * * * /path/to/backup.sh
```

### 10.2 データエクスポート

**全ユーザーデータをJSON形式で出力:**
```python
import json
import glob

def export_all_data(output_path='export.json'):
    """
    全ユーザーデータをエクスポート

    Args:
        output_path: str

    Returns:
        None
    """
    export_data = {
        'exported_at': datetime.now().isoformat(),
        'users': []
    }

    # 全プロフィール取得
    profile_files = glob.glob('data/profile_*.json')

    for profile_file in profile_files:
        with open(profile_file, 'r', encoding='utf-8') as f:
            profile = json.load(f)

        user_id = profile['user_id']

        # 体重データ取得
        weight_df = load_weight_data(user_id)
        weight_data = weight_df.to_dict('records') if not weight_df.empty else []

        # 統合
        export_data['users'].append({
            'profile': profile,
            'weight_data': weight_data
        })

    # JSON出力
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(export_data['users'])} users to {output_path}")
```

### 10.3 データインポート

**エクスポートしたJSONからデータ復元:**
```python
def import_all_data(input_path='export.json'):
    """
    エクスポートデータをインポート

    Args:
        input_path: str

    Returns:
        None
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        import_data = json.load(f)

    for user_data in import_data['users']:
        profile = user_data['profile']
        weight_data = user_data['weight_data']

        user_id = profile['user_id']

        # プロフィール保存
        profile_path = f'data/profile_{user_id}.json'
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

        # 体重データ保存
        if weight_data:
            weight_df = pd.DataFrame(weight_data)
            weight_df['date'] = pd.to_datetime(weight_df['date'])
            weight_path = f'data/weight_data_{user_id}.csv'
            weight_df.to_csv(weight_path, index=False, date_format='%Y-%m-%d')

    print(f"Imported {len(import_data['users'])} users")
```

### 10.4 データベース移行（将来拡張）

**SQLiteスキーマ例:**
```sql
-- users テーブル
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    current_weight REAL NOT NULL,
    target_weight REAL NOT NULL,
    plan TEXT NOT NULL,
    preparation_days INTEGER NOT NULL,
    preparation_start_date TEXT NOT NULL,
    main_start_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- weight_records テーブル
CREATE TABLE weight_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date TEXT NOT NULL,
    weight REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE(user_id, date)
);

-- インデックス
CREATE INDEX idx_weight_user_date ON weight_records(user_id, date);
```

---

## 付録A: データ計算クイックリファレンス

### BMR（基礎代謝）
```
男性: 13.397W + 4.799H - 5.677A + 88.362
女性: 9.247W + 3.098H - 4.330A + 447.593
```

### TDEE（活動代謝）
```
TDEE = BMR × 1.2（座りがち）
```

### 目標カロリー
```
ライト: TDEE - (体重 × 0.02 ÷ 30 × 7200)
ハード: TDEE - (体重 × 0.04 ÷ 30 × 7200)
準備期間: TDEE - 200
```

### PFC
```
タンパク質: 体重 × 1.5 (g)
脂質: 目標カロリー × 0.20 ÷ 9 (g)
炭水化物: (目標カロリー - P*4 - F*9) ÷ 4 (g)
```

### 5%ルール
```
月間上限 = 体重 × 0.05 (kg)
```

---

**以上、データ仕様書（CSV/JSON構造、計算式）**
