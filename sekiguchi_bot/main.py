#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
関口式ダイエットメンター
フィジークマスターズ世界一×指導歴30年×人格搭載AI
ダイエットや健康維持をサポートする、関口貴夫さん風のメンターbotです。
"""

import random
import csv
import os
import json
import base64
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# プラン定義
PLANS = {
    "1": {
        "name": "月額プラン",
        "price": "月額990円",
        "days": 30,
        "description": "関口式ダイエットメンターで理想の体を手に入れましょう！"
    }
}


def print_welcome():
    """ウェルカムメッセージを表示する"""
    print("=" * 60)
    print("       関口式ダイエットメンターへようこそ！")
    print("    フィジークマスターズ世界一×指導歴30年×人格搭載AI")
    print("=" * 60)
    print("\n【関口の指導哲学】")
    print("100%のトレーナー = 25%チアリーダー（応援）×25%コメディアン（楽しませる）")
    print("                   ×25%バーテンダー（傾聴）×25%専門家（科学的根拠）")
    print("\nこの4つの要素で、あなたのダイエットを楽しく、確実にサポートします！")
    print("=" * 60)
    print()


def select_plan():
    """
    プランを選択してもらう

    Returns:
        dict: 選択されたプラン情報
    """
    print("\n" + "=" * 60)
    print("【プラン選択】")
    print("=" * 60)
    print("\nまずは、あなたに合ったプランを選びましょう！\n")

    # プランを表示
    for key, plan in PLANS.items():
        print(f"【{key}】{plan['name']} - {plan['price']}")
        print(f"    {plan['description']}")
        print()

    # プランを選択
    while True:
        choice = input("始めるには「1」を入力してください\n> ").strip()
        if choice in PLANS:
            selected_plan = PLANS[choice].copy()
            selected_plan["start_date"] = datetime.now().strftime('%Y-%m-%d')
            print(f"\n{selected_plan['name']}を選択しました！")
            print(f"期間: {selected_plan['days']}日間")
            print(f"料金: {selected_plan['price']}")
            return selected_plan
        else:
            print("「1」を入力してください。")


def conduct_preparation_period(profile):
    """
    準備期間（3日間）の食事記録を行う

    Args:
        profile (dict): ユーザーのプロフィール情報

    Returns:
        list: 3日間の食事記録のリスト
    """
    print("\n" + "=" * 60)
    print("【準備期間：3日間の食事記録】")
    print("=" * 60)

    # バーテンダー要素（傾聴・理解）
    print(f"\n🍸 {profile['name']}さん、まずはあなたの普段の食生活を教えてください。")
    print(f"   3日間、いつも通りの食事を記録するだけで大丈夫です。")

    # 専門家要素（科学的根拠）
    print(f"\n🎓 この記録から、マニュアルではなく{profile['name']}さん専用の")
    print(f"   目標カロリーとPFCバランスを科学的に算出します！")

    # コメディアン要素（楽しませる）
    print(f"\n🎭 完璧な食事じゃなくても大丈夫！")
    print(f"   むしろ「いつもの」を知りたいんです（笑）")

    # チアリーダー要素（応援）
    print(f"\n🎺 記録すること自体が、もう第一歩です！頑張りましょう！")

    print("\n食事の写真がある場合は画像パスを入力してください。")
    print("画像がない場合はスキップして、食事内容を直接入力できます。")
    print("-" * 60)

    meal_records = []

    for day in range(1, 4):
        print(f"\n📅 {day}日目の食事記録")
        print("-" * 60)

        # 画像パスの入力（オプション）
        image_path = input("\n食事の画像ファイルパス（スキップする場合はEnter）\n> ").strip()

        # 食事内容の入力
        meal_description = input("\n食事内容を教えてください（例：朝：パン、卵、サラダ／昼：定食／夜：魚、野菜）\n> ").strip()

        # カロリーとPFCの入力
        print("\nカロリーとPFC（タンパク質・脂質・炭水化物）を入力してください。")
        print("概算でOKです！わからない場合は推定値を入力してください。")

        while True:
            try:
                calories = float(input("\n総カロリー（kcal）\n> "))
                protein = float(input("タンパク質（g）\n> "))
                fat = float(input("脂質（g）\n> "))
                carbs = float(input("炭水化物（g）\n> "))
                break
            except ValueError:
                print("数字で入力してください。")

        # 記録を保存
        meal_record = {
            "day": day,
            "image_path": image_path if image_path else None,
            "meal_description": meal_description,
            "calories": calories,
            "protein": protein,
            "fat": fat,
            "carbs": carbs
        }
        meal_records.append(meal_record)

        print(f"\n✅ {day}日目の記録が完了しました！")

    # 準備期間完了メッセージ
    print("\n" + "=" * 60)
    print("🎉 3日間の準備期間が完了しました！")
    print("=" * 60)

    # チアリーダー要素（応援）
    print(f"\n🎺 {profile['name']}さん、3日間お疲れ様でした！素晴らしいです！")

    # コメディアン要素（楽しませる）
    print(f"\n🎭 記録を続けるって、思ったより大変だったかもしれませんね（笑）")
    print(f"   でも、ここまでやれた{profile['name']}さんなら絶対大丈夫です！")

    # バーテンダー要素（傾聴・理解）
    print(f"\n🍸 {profile['name']}さんの普段の食生活、よく理解できました。")
    print(f"   これをもとに、無理のない目標を一緒に作っていきましょう。")

    # 専門家要素（科学的根拠）
    print(f"\n🎓 このデータから、{profile['name']}さん専用の目標を科学的に算出します！")

    return meal_records


def calculate_nutrition_baseline(meal_records):
    """
    3日間の食事記録から平均カロリーとPFCを計算する

    Args:
        meal_records (list): 3日間の食事記録

    Returns:
        dict: 平均カロリーとPFC
    """
    total_calories = sum(record['calories'] for record in meal_records)
    total_protein = sum(record['protein'] for record in meal_records)
    total_fat = sum(record['fat'] for record in meal_records)
    total_carbs = sum(record['carbs'] for record in meal_records)

    avg_calories = total_calories / len(meal_records)
    avg_protein = total_protein / len(meal_records)
    avg_fat = total_fat / len(meal_records)
    avg_carbs = total_carbs / len(meal_records)

    return {
        "avg_calories": avg_calories,
        "avg_protein": avg_protein,
        "avg_fat": avg_fat,
        "avg_carbs": avg_carbs
    }


def calculate_target_nutrition(profile, baseline):
    """
    ユーザーの希望減量ペースに基づいて目標カロリーとPFCを計算する

    Args:
        profile (dict): ユーザーのプロフィール情報
        baseline (dict): 準備期間の平均栄養データ

    Returns:
        dict: 目標カロリーとPFC

    Note:
        - ユーザーが設定した月間減量目標（kg/月）を使用
        - 最大で体重の5%/月まで
    """
    baseline_calories = baseline['avg_calories']

    # カロリー調整量を決定（ユーザーの希望減量ペースベース）
    calorie_adjustment = 0
    monthly_weight_loss_kg = 0

    if profile.get('monthly_target_kg'):
        monthly_weight_loss_kg = profile['monthly_target_kg']

        # 1日あたりの目標減量（kg/日）
        daily_weight_loss_kg = monthly_weight_loss_kg / 30

        # 1kgの体脂肪 = 約7200kcal
        # 1日あたりの必要カロリー削減
        calorie_adjustment = -(daily_weight_loss_kg * 7200)

    # 目標カロリーを計算
    target_calories = baseline_calories + calorie_adjustment

    # 目標PFCを計算（P:30%, F:20%, C:50%）
    # 1gあたりのカロリー：タンパク質=4kcal, 脂質=9kcal, 炭水化物=4kcal
    protein_calories = target_calories * 0.30
    fat_calories = target_calories * 0.20
    carbs_calories = target_calories * 0.50

    target_protein = protein_calories / 4
    target_fat = fat_calories / 9
    target_carbs = carbs_calories / 4

    return {
        "target_calories": target_calories,
        "target_protein": target_protein,
        "target_fat": target_fat,
        "target_carbs": target_carbs,
        "calorie_adjustment": calorie_adjustment,
        "monthly_weight_loss_kg": monthly_weight_loss_kg
    }


def get_user_profile(plan):
    """
    ユーザーのプロフィール情報を入力してもらう

    Args:
        plan (dict): 選択されたプラン情報

    Returns:
        dict: ユーザーのプロフィール情報（名前、性別、目的、目標体重、カロリー調整モード、プラン情報）
    """
    print("\nそれでは、あなたのことを教えてください！\n")

    # 名前を入力してもらう
    name = input("【お名前】何とお呼びすればよいですか？（例：太郎、花子など）\n> ").strip()
    if not name:
        name = "あなた"  # 入力がない場合はデフォルト

    # 性別を入力してもらう
    while True:
        gender = input("\n【性別】性別を教えてください（男性 または 女性）\n> ").strip()
        if gender in ["男性", "女性"]:
            break
        else:
            print("「男性」または「女性」と入力してください。")

    # 年齢を入力してもらう
    age = None
    while True:
        try:
            age_input = input("\n【年齢】年齢を教えてください\n> ")
            age = int(age_input)
            if age > 0 and age < 150:
                break
            else:
                print("正しい年齢を入力してください。")
        except ValueError:
            print("数字で入力してください。")

    # 目的を入力してもらう
    purpose = input("\n【目的】目標は何ですか？（例：ダイエット、増量、健康維持など）\n> ")

    # 現在の体重を入力してもらう
    current_weight_kg = None
    while True:
        try:
            current_weight = input("\n【現在の体重】現在の体重は何kgですか？\n> ")
            current_weight_kg = float(current_weight)
            break
        except ValueError:
            print("数字で入力してください（小数点もOKです）。")

    # 目標体重を入力してもらう
    while True:
        try:
            target_weight = input("\n【目標体重】目標体重は何kgですか？\n> ")
            target_weight_kg = float(target_weight)
            break
        except ValueError:
            print("数字で入力してください（小数点もOKです）。")

    # 関口からの提案（ダイエット目的の場合のみ）
    monthly_target_kg = None
    if 'ダイエット' in purpose or '減量' in purpose or '痩せ' in purpose:
        print("\n" + "=" * 60)
        print("【関口からの提案】")
        print("=" * 60)

        # プラン期間を取得
        plan_months = plan['days'] / 30

        # ライトプラン（2%）とハードプラン（4%）のペースを計算
        light_monthly_kg = current_weight_kg * 0.02
        hard_monthly_kg = current_weight_kg * 0.04
        light_total_kg = light_monthly_kg * plan_months
        hard_total_kg = hard_monthly_kg * plan_months

        # 関口からのメッセージ（4要素を反映）
        print(f"\n{'='*60}")
        print(f"【関口からの提案】")
        print(f"{'='*60}")

        # バーテンダー要素（傾聴・理解）
        print(f"\n🍸 {name}さん、{plan['days']}日間のプランですね。")
        print(f"   現在の体重{current_weight_kg}kgから目標に向かって、一緒に計画を立てましょう。")

        # 専門家要素（科学的根拠）
        print(f"\n🎓 科学的に安全な2つのプランをご用意しました：")

        print(f"\n【1】ライトプラン（体重の2%/月）")
        print(f"    月に{light_monthly_kg:.1f}kgずつ、{plan['days']}日間で約{light_total_kg:.1f}kg減")
        print(f"    → 基礎代謝を維持し、リバウンドリスクが最も低い")

        print(f"\n【2】ハードプラン（体重の4%/月）")
        print(f"    月に{hard_monthly_kg:.1f}kgずつ、{plan['days']}日間で約{hard_total_kg:.1f}kg減")
        print(f"    → 5%以内の安全範囲で、最大限の効果を目指す")

        # コメディアン要素（楽しませる）
        print(f"\n🎭 どちらのプランも、体が「おっと、これは無理だ」って")
        print(f"   思わない範囲で設定してあります！安心してください（笑）")

        # チアリーダー要素（応援）
        print(f"\n🎺 {name}さんなら、どちらのプランでも必ず成功できます！")
        print(f"   あなたに合ったペースで、一緒に理想の体を手に入れましょう！")

        # ユーザーの希望を聞く
        print("\n" + "-" * 60)
        while True:
            plan_choice = input(f"\nどちらのプランで進めますか？（1 または 2）\n> ").strip()

            if plan_choice == "1":
                monthly_target_kg = light_monthly_kg
                print(f"\nライトプランを選択しました！月{monthly_target_kg:.1f}kgペースで進めます。")
                break
            elif plan_choice == "2":
                monthly_target_kg = hard_monthly_kg
                print(f"\nハードプランを選択しました！月{monthly_target_kg:.1f}kgペースで進めます。")
                break
            else:
                print("「1」または「2」を入力してください。")

    print("\n" + "-" * 60)
    print(f"{name}さん、よろしくお願いします！")
    print(f"目標は「{purpose}」ですね。")
    if current_weight_kg and target_weight_kg:
        weight_diff = current_weight_kg - target_weight_kg
        print(f"現在{current_weight_kg}kg → 目標{target_weight_kg}kg（-{weight_diff:.1f}kg）")
        print(f"{plan['days']}日間で達成を目指しましょう！")
    if monthly_target_kg:
        print(f"月{monthly_target_kg:.1f}kgペースで進めます！")
    print("一緒に頑張りましょう💪")
    print("-" * 60 + "\n")

    # プロフィール情報を辞書形式で返す
    return {
        "name": name,
        "gender": gender,
        "age": age,
        "purpose": purpose,
        "current_weight": current_weight_kg,
        "target_weight": target_weight_kg,
        "monthly_target_kg": monthly_target_kg,
        "plan": plan
    }


def get_daily_report(with_nutrition=False):
    """
    今日の報告を入力してもらう

    Args:
        with_nutrition (bool): カロリーとPFCも記録するかどうか

    Returns:
        dict or None: 今日の報告内容（体重、運動、食事、カロリー、PFC）。終了の場合はNone
    """
    print("\n" + "=" * 60)
    print("今日の報告をお願いします！")
    print("=" * 60)

    # 体重を入力してもらう（exitや終了で終了できる）
    weight_input = input("\n【今日の体重】体重は何kgでしたか？（終了する場合は「exit」または「終了」と入力）\n> ")

    # 終了コマンドのチェック
    if weight_input.lower() in ["exit", "終了", "quit"]:
        return None

    # 体重を数値に変換
    try:
        today_weight = float(weight_input)
    except ValueError:
        print("数字で入力してください。今回の報告をスキップします。")
        return get_daily_report(with_nutrition)  # もう一度入力を求める

    # 運動内容を入力してもらう
    exercise = input("\n【今日の運動】今日はどんな運動をしましたか？\n> ")

    # 食事内容を入力してもらう
    meal = input("\n【今日の食事】今日食べたものを教えてください（ざっくりでOK）\n> ")

    # カロリーとPFCの記録（オプション）
    calories = None
    protein = None
    fat = None
    carbs = None

    if with_nutrition:
        print("\n【栄養記録】今日のカロリーとPFCを記録しましょう（概算でOK）")
        try:
            calories = float(input("総カロリー（kcal）\n> "))
            protein = float(input("タンパク質（g）\n> "))
            fat = float(input("脂質（g）\n> "))
            carbs = float(input("炭水化物（g）\n> "))
        except ValueError:
            print("数値の入力に失敗しました。栄養記録はスキップします。")

    # 報告内容を辞書形式で返す
    return {
        "weight": today_weight,
        "exercise": exercise,
        "meal": meal,
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs
    }


def save_weight_data(name, weight):
    """
    体重データをCSVファイルに保存する

    Args:
        name (str): ユーザーの名前
        weight (float): 体重（kg）
    """
    # ファイル名を生成（名前ごとに別ファイル）
    filename = f"weight_data_{name}.csv"

    # ファイルが存在しない場合はヘッダーを書き込む
    file_exists = os.path.exists(filename)

    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # 新規ファイルの場合はヘッダーを追加
        if not file_exists:
            writer.writerow(['日付', '体重(kg)'])

        # データを追加
        today = datetime.now().strftime('%Y-%m-%d')
        writer.writerow([today, weight])


def get_previous_weight(name):
    """
    前回の体重を取得する

    Args:
        name (str): ユーザーの名前

    Returns:
        float or None: 前回の体重（データがない場合はNone）
    """
    filename = f"weight_data_{name}.csv"

    if not os.path.exists(filename):
        return None

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # ヘッダーをスキップ

            weights = []
            for row in reader:
                if len(row) >= 2:
                    weights.append(float(row[1]))

            if len(weights) > 0:
                return weights[-1]  # 最後の体重を返す
    except:
        pass

    return None


def analyze_meal(meal_text):
    """
    食事内容から良い点を見つける

    Args:
        meal_text (str): 食事内容のテキスト

    Returns:
        list: 見つかった良い点のリスト
    """
    good_points = []
    meal_lower = meal_text.lower()

    # タンパク質関連
    protein_foods = ['鶏肉', '鶏胸肉', 'ささみ', '魚', 'サーモン', '卵', 'プロテイン', '豆腐', '納豆', 'チキン']
    if any(food in meal_text for food in protein_foods):
        good_points.append("タンパク質をしっかり摂取されていますね")

    # 野菜関連
    vegetable_words = ['サラダ', '野菜', 'ブロッコリー', 'ほうれん草', 'キャベツ', 'トマト']
    if any(word in meal_text for word in vegetable_words):
        good_points.append("野菜を意識されていて素晴らしいです")

    # 健康的な炭水化物
    healthy_carbs = ['玄米', 'オートミール', '全粒粉', 'さつまいも']
    if any(carb in meal_text for carb in healthy_carbs):
        good_points.append("質の良い炭水化物を選んでいますね")

    # 小分け・バランス
    if '、' in meal_text or '小分け' in meal_text:
        good_points.append("バランスよく食べられていますね")

    return good_points


def get_purpose_specific_message(purpose, weight_change):
    """
    目的に応じた個別カスタマイズメッセージを生成

    Args:
        purpose (str): ユーザーの目的
        weight_change (float or None): 体重変化

    Returns:
        str: 目的に応じたメッセージ
    """
    purpose_lower = purpose.lower()

    # ダイエット向けメッセージ
    if 'ダイエット' in purpose or '減量' in purpose or '痩せ' in purpose:
        if weight_change is not None:
            if weight_change < 0:
                return f"ダイエット順調ですね！無理なく続けていきましょう"
            elif weight_change > 0:
                return "体重が増えても焦る必要はありません。筋肉が増えている可能性もありますよ"
            else:
                return "停滞期かもしれませんね。続ければ必ず突破できます"
        return "ダイエットは焦らず、着実に進めていきましょう"

    # 増量向けメッセージ
    elif '増量' in purpose or '筋肉' in purpose or 'バルク' in purpose:
        if weight_change is not None:
            if weight_change > 0:
                return f"増量順調です！タンパク質摂取を意識して続けましょう"
            elif weight_change < 0:
                return "もう少しカロリー摂取を増やしても良いかもしれませんね"
            else:
                return "体重を増やすには、少し食事量を増やしてみましょう"
        return "筋肉をつけながら健康的に体重を増やしていきましょう"

    # 健康維持向けメッセージ
    elif '健康' in purpose or '維持' in purpose or '体型' in purpose:
        if weight_change is not None:
            if abs(weight_change) < 0.5:
                return f"体重を上手に維持できていますね。素晴らしいです"
            else:
                return "多少の変動は気にせず、今のペースで続けましょう"
        return "健康的な生活習慣を継続することが大切です"

    # その他
    else:
        return "あなたの目標に向かって、一緒に頑張っていきましょう"


def get_purpose_specific_tips(purpose):
    """
    目的に応じた改善ポイントを返す

    Args:
        purpose (str): ユーザーの目的

    Returns:
        list: 目的に応じた改善ポイントのリスト
    """
    purpose_lower = purpose.lower()
    tips = []

    # ダイエット向けアドバイス
    if 'ダイエット' in purpose or '減量' in purpose or '痩せ' in purpose:
        tips = [
            "夕食は軽めにして、寝る3時間前には済ませましょう",
            "有酸素運動を20分以上続けると脂肪燃焼効果が高まります",
            "間食を減らして、1日3食を規則正しく摂りましょう",
            "水分をしっかり摂って代謝を上げましょう",
            "食事の記録をつけると、食べ過ぎを防げますよ",
        ]

    # 増量向けアドバイス
    elif '増量' in purpose or '筋肉' in purpose or 'バルク' in purpose:
        tips = [
            "筋トレ後30分以内にタンパク質を摂取しましょう",
            "1日5-6回に分けて食事を摂ると吸収効率が上がります",
            "炭水化物もしっかり摂って、筋肉の材料を確保しましょう",
            "筋トレは週3-4回、しっかり休息を取りながら行いましょう",
            "プロテインを活用して、タンパク質を補給しましょう",
        ]

    # 健康維持向けアドバイス
    elif '健康' in purpose or '維持' in purpose or '体型' in purpose:
        tips = [
            "バランスの良い食事を心がけましょう",
            "適度な運動習慣を維持することが大切です",
            "睡眠時間を確保して、体を休めましょう",
            "ストレス管理も健康維持には重要ですよ",
            "定期的な健康チェックを忘れずに",
        ]

    # その他
    else:
        tips = [
            "無理なく続けられるペースを見つけましょう",
            "自分に合った方法を探していきましょう",
        ]

    return tips


def generate_weight_graph(name):
    """
    体重データからグラフを生成する

    Args:
        name (str): ユーザーの名前
    """
    filename = f"weight_data_{name}.csv"

    # ファイルが存在しない場合は何もしない
    if not os.path.exists(filename):
        return

    # CSVファイルからデータを読み込む
    dates = []
    weights = []

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダーをスキップ

        for row in reader:
            dates.append(datetime.strptime(row[0], '%Y-%m-%d'))
            weights.append(float(row[1]))

    # データが1件もない場合は何もしない
    if len(dates) == 0:
        return

    # 日本語フォント設定（環境によって調整が必要）
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    # グラフを生成
    plt.figure(figsize=(10, 6))
    plt.plot(dates, weights, marker='o', linestyle='-', linewidth=2, markersize=8)

    # グラフの装飾
    plt.title(f'{name}san no Weight Progress', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Weight (kg)', fontsize=12)
    plt.grid(True, alpha=0.3)

    # x軸の日付フォーマット
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()  # 日付ラベルを斜めに表示

    # y軸の範囲を少し広げる
    if len(weights) > 0:
        weight_min = min(weights)
        weight_max = max(weights)
        margin = (weight_max - weight_min) * 0.1 if weight_max != weight_min else 1
        plt.ylim(weight_min - margin, weight_max + margin)

    # グラフを保存
    graph_filename = f"weight_graph_{name}.png"
    plt.tight_layout()
    plt.savefig(graph_filename, dpi=100, bbox_inches='tight')
    plt.close()

    print(f"\n📊 体重グラフを更新しました: {graph_filename}")


def save_profile(profile):
    """
    プロフィール情報をJSONファイルに保存する

    Args:
        profile (dict): ユーザーのプロフィール情報
    """
    filename = f"profile_{profile['name']}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def load_profile(name):
    """
    プロフィール情報をJSONファイルから読み込む

    Args:
        name (str): ユーザーの名前

    Returns:
        dict or None: プロフィール情報（ファイルがない場合はNone）
    """
    filename = f"profile_{name}.json"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def calculate_remaining_days(profile):
    """
    プラン残り日数を計算する

    Args:
        profile (dict): ユーザーのプロフィール情報

    Returns:
        int: 残り日数
    """
    plan = profile.get('plan', {})
    start_date = datetime.strptime(plan['start_date'], '%Y-%m-%d')
    total_days = plan['days']
    today = datetime.now()
    elapsed_days = (today - start_date).days
    remaining = total_days - elapsed_days
    return max(0, remaining)  # マイナスにならないようにする


def get_sekiguchi_philosophy_message(name, situation):
    """
    関口の指導哲学「100%のトレーナー = 25%チアリーダー×25%コメディアン×25%バーテンダー×25%専門家」
    を具現化したメッセージを生成する

    Args:
        name (str): ユーザーの名前
        situation (str): 状況（"weight_up", "weight_down", "weight_same", "general"）

    Returns:
        dict: 4つの要素を含むメッセージ
    """
    messages = {
        "weight_up": {
            "cheerleader": [
                f"{name}さん、体重が増えても落ち込む必要はありません！むしろここからが本番です！",
                f"{name}さん、停滞や増加は体が変化に慣れようとしている証拠。諦めずに続ければ必ず突破できます！",
                f"{name}さん、この壁を乗り越えたら、もっと強い自分に会えますよ！一緒に頑張りましょう！",
            ],
            "comedian": [
                "体重計が壊れたかと思いましたか？笑　違いますよ、体が一時的に水分を溜め込んでるだけです！",
                "増えた分は「貯金」みたいなもの。明日からストンと落ちる可能性大です！楽しみにしていてください！",
                "体重計に「調子乗るなよ」って言われた気分ですよね（笑）。でも大丈夫、これは通過点です！",
            ],
            "bartender": [
                f"{name}さん、増えた時って本当に不安になりますよね。その気持ち、よくわかります",
                "頑張ってるのに増えると、モチベーション下がりますよね。でも、それでもここに報告してくれた。それが素晴らしいんです",
                f"{name}さんの頑張り、ちゃんと見えてますよ。数字だけが全てじゃありません",
            ],
            "expert": [
                "科学的には、体重は1日で1-2kg変動します。体脂肪1kg減らすには7200kcalの消費が必要なので、1日で脂肪が増えることはほぼありません",
                "体重増加の多くは水分やグリコーゲンの一時的な蓄積。継続すれば必ず突然ストンと落ちる日が来ます",
                "ホメオスタシス（恒常性）で体が現状維持しようとしている時期。ここで諦めずに続けることが成功の鍵です",
            ]
        },
        "weight_down": {
            "cheerleader": [
                f"{name}さん、素晴らしい！この調子で一緒に進んでいきましょう！",
                f"{name}さんの努力が数字に表れていますね！この調子です！",
                f"{name}さん、やりましたね！継続の成果が出ています！",
            ],
            "comedian": [
                "体重計が喜んでる音が聞こえてきそうですね！この調子で楽しく続けましょう！",
                "順調すぎて、私も嬉しくなっちゃいました！一緒に喜びましょう！",
                f"{name}さんと体重計、今日は良い関係ですね（笑）。明日も仲良くしてください！",
            ],
            "bartender": [
                f"{name}さん、頑張ってきた甲斐がありましたね。本当に嬉しいです",
                "結果が出ると、モチベーション上がりますよね。その気持ちを大切にしてください",
                f"{name}さんの努力が報われて、私も本当に嬉しいです",
            ],
            "expert": [
                "この減量ペースは理想的です。急激な減量ではなく、持続可能なペースで体が順応しています",
                "筋肉を維持しながら脂肪を落とせている証拠です。PFCバランスを保ちながら続けましょう",
                "基礎代謝を維持しながらの減量ができています。リバウンドしにくい理想的な状態です",
            ]
        },
        "weight_same": {
            "cheerleader": [
                f"{name}さん、変化がなくても継続していることが素晴らしい！その姿勢が結果を生みます！",
                f"{name}さん、停滞期こそが成長のチャンス！ここを乗り越えれば大きな変化が待っています！",
                f"{name}さん、諦めない心が何より大切。一緒に乗り越えましょう！",
            ],
            "comedian": [
                "体重計が「今日はお休み」って言ってるみたいですね（笑）。明日は働いてもらいましょう！",
                "体重、現状維持の名人ですね！でも明日はきっと動きますよ！",
                f"{name}さんと体重、今日は仲良く「様子見」タイムですね。明日が楽しみです！",
            ],
            "bartender": [
                "変化がないと、不安になりますよね。でも、報告を続けている時点で前進しています",
                f"{name}さん、数字が変わらなくても、体の中では確実に変化が起きていますよ",
                "目に見えない変化もあります。焦らず、今のペースを信じてください",
            ],
            "expert": [
                "体重は階段状に落ちるもの。停滞期の後、急に落ちることが多いです。科学的にも証明されています",
                "筋肉が増えて脂肪が減っていれば、体重は変わらなくても体脂肪率は改善しています",
                "停滞期は体が新しい体重に慣れようとしている時期。ここで諦めずに続けることが重要です",
            ]
        },
        "general": {
            "cheerleader": [
                f"{name}さん、今日も報告してくれてありがとう！その継続が力になります！",
                f"{name}さん、毎日の積み重ねが結果を生みます！一緒に頑張りましょう！",
                f"{name}さんの前向きな姿勢、本当に素晴らしいです！",
            ],
            "comedian": [
                "今日も元気にやっていきましょう！楽しみながら続けるのが関口流です！",
                f"{name}さん、笑顔で続ければ、体も喜んで応えてくれますよ！",
                "真面目すぎると疲れちゃいます。たまには笑って、リラックスしながら進みましょう！",
            ],
            "bartender": [
                f"{name}さん、今日はどんな一日でしたか？頑張った自分を褒めてあげてくださいね",
                "日々の努力、ちゃんと見えています。あなたは確実に成長していますよ",
                f"{name}さんのペースで大丈夫。焦らず、一緒に進んでいきましょう",
            ],
            "expert": [
                "継続することで、体は確実に変化します。それが科学的に証明されている事実です",
                "年齢に関係なく、筋肉は成長します。80代でも筋肥大は可能です。今日が一番若い日です",
                "PFCバランス（P:30% F:20% C:50%）を意識することで、健康的に体重をコントロールできます",
            ]
        }
    }

    # 状況に応じたメッセージを取得
    situation_messages = messages.get(situation, messages["general"])

    return {
        "cheerleader": random.choice(situation_messages["cheerleader"]),
        "comedian": random.choice(situation_messages["comedian"]),
        "bartender": random.choice(situation_messages["bartender"]),
        "expert": random.choice(situation_messages["expert"])
    }


def generate_feedback(profile, report):
    """
    関口貴夫さん風のフィードバックを生成する
    関口の指導哲学「100%のトレーナー = 25%チアリーダー×25%コメディアン×25%バーテンダー×25%専門家」を具現化

    Args:
        profile (dict): ユーザーのプロフィール
        report (dict): 今日の報告内容
    """
    # 名前を取得（デフォルトは「あなた」）
    name = profile.get("name", "あなた")

    # 前回の体重を取得
    previous_weight = get_previous_weight(name)
    current_weight = report["weight"]
    weight_change = None
    if previous_weight is not None:
        weight_change = current_weight - previous_weight

    print("\n" + "-" * 60)
    print("【関口メンターからのフィードバック】")
    print("-" * 60)

    # カロリーとPFCの比較（目標が設定されている場合）
    if report.get('calories') and profile.get('nutrition_target'):
        target = profile['nutrition_target']
        print("\n📊 栄養バランス:")
        print(f"  カロリー: {report['calories']:.0f}kcal / 目標 {target['target_calories']:.0f}kcal")

        cal_diff = report['calories'] - target['target_calories']
        if abs(cal_diff) <= 100:
            print(f"  → 目標ピッタリです！素晴らしい👍")
        elif cal_diff > 0:
            print(f"  → 目標より{cal_diff:.0f}kcal多めです。明日調整しましょう")
        else:
            print(f"  → 目標より{abs(cal_diff):.0f}kcal少なめです")

        if report.get('protein') and report.get('fat') and report.get('carbs'):
            print(f"\n  タンパク質: {report['protein']:.1f}g / 目標 {target['target_protein']:.1f}g")
            print(f"  脂質: {report['fat']:.1f}g / 目標 {target['target_fat']:.1f}g")
            print(f"  炭水化物: {report['carbs']:.1f}g / 目標 {target['target_carbs']:.1f}g")

            # PFCバランスをチェック
            total_pfc = report['protein'] + report['fat'] + report['carbs']
            if total_pfc > 0:
                p_ratio = (report['protein'] * 4 / report['calories']) * 100
                f_ratio = (report['fat'] * 9 / report['calories']) * 100
                c_ratio = (report['carbs'] * 4 / report['calories']) * 100
                print(f"\n  PFCバランス: P{p_ratio:.0f}% F{f_ratio:.0f}% C{c_ratio:.0f}%")
                print(f"  目標バランス: P30% F20% C50%")

    # 体重変化のメッセージ + 関口の指導哲学（4要素）
    if weight_change is not None:
        # 状況を判定
        if weight_change > 0:
            situation = "weight_up"
            print(f"\n📊 体重変化: +{weight_change:.1f}kg")
        elif weight_change < 0:
            situation = "weight_down"
            print(f"\n📊 体重変化: {weight_change:.1f}kg")
        else:
            situation = "weight_same"
            print(f"\n📊 体重変化: 変化なし")
    else:
        situation = "general"

    # 関口の指導哲学（4要素）を反映したメッセージを取得
    philosophy_msg = get_sekiguchi_philosophy_message(name, situation)

    print("\n" + "=" * 60)
    print("【関口の指導哲学メッセージ】")
    print("100%のトレーナー = 25%チアリーダー×25%コメディアン×25%バーテンダー×25%専門家")
    print("=" * 60)

    print(f"\n🎺 チアリーダー（応援する）:")
    print(f"  {philosophy_msg['cheerleader']}")

    print(f"\n🎭 コメディアン（楽しませる）:")
    print(f"  {philosophy_msg['comedian']}")

    print(f"\n🍸 バーテンダー（傾聴する）:")
    print(f"  {philosophy_msg['bartender']}")

    print(f"\n🎓 専門家（科学的根拠）:")
    print(f"  {philosophy_msg['expert']}")

    # 目的別カスタマイズメッセージ
    purpose_message = get_purpose_specific_message(profile.get('purpose', ''), weight_change)
    print(f"\n🎯 {name}さんへ: {purpose_message}")

    # 良かった点を生成
    print("\n✨ 良かった点:")
    good_points = []

    # このメッセージを読んでいること自体を褒める
    good_points.append(f"{name}さん、このメッセージを読んでくれただけでも前向きな気持ちの表れです")

    # 運動したかチェック
    if report["exercise"].strip():
        good_points.append(f"「{report['exercise']}」をやったこと、素晴らしいです")
        # 頑張り過ぎない大切さを伝える
        if random.random() < 0.3:  # 30%の確率で表示
            good_points.append("頑張り過ぎると続かなかったりしますから、今のペースがかえって良いんですよ")

    # 食事内容から良い点を見つける
    meal_good_points = analyze_meal(report["meal"])
    if meal_good_points:
        good_points.extend(meal_good_points[:1])  # 最初の1つだけ追加

    # できたことに目を向けるメッセージ
    good_points.append("人間、できなかったことに目が向きがちですが、意外とできたことも多いものですよ")

    # 体重報告のチェック
    good_points.append("毎日体重を測って記録する習慣、これがとても大切です！")

    # 少しの進歩を認める追加メッセージ（ランダムで1つ追加）
    progress_praise = [
        f"{name}さん、今日も継続できていますね。それが何より大切です",
        "小さな一歩でも、積み重ねが結果を生みます",
        f"{name}さん、完璧じゃなくても前に進んでいますね",
        "記録を続けること自体が、成果につながります",
        f"{name}さん、昨日より今日、着実に前進していますよ",
    ]
    good_points.append(random.choice(progress_praise))

    for point in good_points:
        print(f"  • {point}")

    # 改善ポイントを生成（1つだけ）
    print("\n💡 改善ポイント（1つだけ！）:")

    # 目的別の改善ポイントを取得
    purpose_tips = get_purpose_specific_tips(profile.get('purpose', ''))

    improvement_tips = purpose_tips + [
        # 運動関連（1-15）
        "明日は運動の時間を少しだけ増やしてみましょう！",
        "ストレッチを5分追加するだけでも効果的です！",
        "階段を使う機会を増やしてみましょう！",
        "朝起きたら軽い体操をしてみてください！",
        "運動前のウォームアップを丁寧にやってみましょう！",
        "運動後のクールダウンも忘れずに！",
        "インターバルトレーニングを取り入れてみましょう！",
        "週に1回は違う種類の運動にチャレンジしてみてください！",
        "筋トレと有酸素運動をバランスよく組み合わせましょう！",
        "歩く時は姿勢を意識してみてください！",
        "運動は無理せず、自分のペースで続けましょう！",
        "通勤時に一駅歩いてみるのもおすすめです！",
        "休憩時間に軽くストレッチしてみましょう！",
        "運動の記録をつけると、モチベーションが上がりますよ！",
        "好きな音楽を聴きながら運動すると楽しいですよ！",

        # 食事関連（16-30）
        "タンパク質をもう少し意識して摂ってみましょう！",
        "野菜をあと一皿増やしてみましょう！色とりどりの野菜がベストです！",
        "朝食はしっかり食べましょう！一日の活力源です！",
        "夜遅い食事は控えめにしてみましょう！",
        "よく噛んで食べることを意識してみてください！",
        "間食は果物やナッツにしてみましょう！",
        "食事の時間を規則正しくすると良いですよ！",
        "炭水化物は適量を心がけましょう！",
        "揚げ物より蒸し料理や焼き料理を選んでみてください！",
        "食物繊維を意識して摂りましょう！",
        "塩分控えめを心がけてみてください！",
        "食事の記録をつけると気づきがありますよ！",
        "ゆっくり食べることで満腹感が得られます！",
        "お菓子は小分けにして食べましょう！",
        "食事のバランスを意識してみてください！",

        # 水分補給関連（31-38）
        "水分補給を意識してみてください。1日2リットルが目安です！",
        "起床後にコップ一杯の水を飲む習慣をつけましょう！",
        "運動中はこまめに水分補給しましょう！",
        "水筒を持ち歩くと水分補給しやすいですよ！",
        "ジュースより水やお茶を選びましょう！",
        "カフェインの摂り過ぎに注意しましょう！",
        "アルコールは控えめにしてみましょう！",
        "炭酸飲料を減らしてみましょう！",

        # 睡眠・休養関連（39-46）
        "睡眠も大事！7時間以上の睡眠を心がけてみてください！",
        "寝る前のスマホ時間を減らしてみましょう！",
        "就寝時間を規則正しくすると良いですよ！",
        "リラックスする時間を意識的に作りましょう！",
        "疲れを感じたら無理せず休むことも大切です！",
        "お風呂でゆっくり体を温めましょう！",
        "深呼吸を意識してみてください。リラックス効果があります！",
        "休息日も計画的に取り入れましょう！",

        # メンタル・モチベーション関連（47-50）
        "小さな成功を祝うことを忘れずに！",
        "目標を細分化して、達成感を味わいましょう！",
        "ポジティブな言葉を自分にかけてあげましょう！",
        "仲間を見つけると続けやすいですよ！",

        # 関口貴夫さん風：年齢・可能性に関するメッセージ（51-55）
        "年齢は関係ありません！今日から始めれば、今日が一番若い日です！",
        "体は正直です。やった分だけ必ず応えてくれますよ！",
        "80代でも筋肉は成長します。あなたにできないわけがありません！",
        "小さな変化を見逃さないで。それが確実な成長の証です！",
        "今の自分を超えることだけを考えましょう。比べるのは昨日の自分だけ！",

        # 関口貴夫さん風：継続・実践に関するメッセージ（56-60）
        "完璧を目指さず、継続を目指しましょう！それが成功の秘訣です！",
        "筋トレも食事も、バランスが大切。無理なく続けられる方法を見つけましょう！",
        "結果を焦らないでください。体は必ず変化します！",
        "トレーニングの質も大事ですが、続けることがもっと大事です！",
        "毎日の小さな努力が、やがて大きな変化を生み出します！",

        # 少しの進歩を認めて褒める（61-70）
        f"{name}さん、0.1kgの変化でも、それは確実な前進です",
        "今日も報告してくれましたね。その継続が大切です",
        f"{name}さん、少しずつでも前に進んでいる。それが一番大事なことです",
        "完璧じゃなくても大丈夫。続けていることが素晴らしいです",
        "小さな変化を積み重ねる。それがプロも実践する王道です",
        f"{name}さん、昨日より少しでも良くなっていれば、それは成功です",
        "今日できたことに目を向けましょう。できなかったことは明日の課題に",
        "小さな一歩でも、歩みを止めなければゴールに辿り着けます",
        f"{name}さん、体重計に乗ること、それ自体が成長の証です",
        "記録を続けているだけで、習慣化できています",
    ]

    # 運動していない場合は運動を勧める
    if not report["exercise"].strip():
        tip = "まずは軽い散歩やストレッチから始めてみましょう！10分でもOKです！"
    else:
        tip = random.choice(improvement_tips)

    print(f"  • {tip}")

    # 明日への一言メッセージ
    print("\n🔥 明日への一言:")
    encouragement_messages = [
        # 継続・習慣化を応援（1-10）
        "継続は力なり！明日も一緒に頑張りましょう！",
        "完璧じゃなくていい、続けることが何より大切です！",
        "小さな積み重ねが大きな成果を生みます！明日も楽しみにしています！",
        "一歩一歩、確実に前進していますよ！",
        "今日の努力は、未来のあなたへの最高のプレゼントです！",
        "毎日続けているあなた、本当に素晴らしいです！",
        "習慣は第二の天性。続けることで必ず結果が出ます！",
        "今日できたことを、明日も続けていきましょう！",
        "諦めなければ、必ず目標に到達できます！",
        "あなたの継続力、本当に尊敬します！",

        # 成長・進歩を讃える（11-20）
        "あなたなら絶対できます！その調子で行きましょう！",
        "昨日より今日、今日より明日。少しずつ前進していきましょう！",
        "成長は階段のように、一段ずつ上がっていくものです！",
        "あなたは確実に成長しています！自信を持ってください！",
        "小さな変化も、立派な成長です！",
        "今のあなたは、昨日のあなたより強くなっています！",
        "一日一日が、新しいあなたを作っています！",
        "変化を恐れず、前に進み続けましょう！",
        "あなたの可能性は無限大です！",
        "成長の過程を楽しんでいきましょう！",

        # モチベーション維持（21-30）
        "あなたの努力、ちゃんと見ていますよ！明日も応援しています！",
        "頑張っているあなたを、私は全力で応援します！",
        "あなたの決意、素晴らしいです！私も一緒に頑張ります！",
        "明日もあなたと一緒に、目標に向かって進みたいです！",
        "あなたのチャレンジ精神、本当に素敵です！",
        "一緒に理想の自分を目指しましょう！",
        "あなたの熱意が、私にも伝わってきます！",
        "その調子で、楽しみながら続けていきましょう！",
        "あなたの笑顔のために、私も全力でサポートします！",
        "明日もあなたの報告を楽しみに待っています！",

        # ポジティブ思考（31-40）
        "できることに目を向ければ、可能性は無限に広がります！",
        "失敗は成功のもと。すべてが学びです！",
        "今日という日は、二度と来ません。大切に過ごしましょう！",
        "自分を信じることが、成功への第一歩です！",
        "ポジティブな気持ちが、良い結果を引き寄せます！",
        "楽しむ心を忘れずに！それが長続きの秘訣です！",
        "あなたには、目標を達成する力があります！",
        "明日は明日の風が吹く。今日を大切にしましょう！",
        "笑顔で過ごせば、良いことが起こりますよ！",
        "前向きな気持ちが、あなたを強くします！",

        # 実践的アドバイス（41-50）
        "体は正直です。良い習慣は必ず結果に表れます！",
        "無理せず、自分のペースで進んでいきましょう！",
        "小さな目標をクリアして、達成感を味わいましょう！",
        "今日の反省を明日に活かしていきましょう！",
        "バランスが大切。無理なく楽しく続けましょう！",
        "自分を褒めることも忘れずに！",
        "休むことも、頑張ることと同じくらい大切です！",
        "健康は一日にしてならず。コツコツと積み重ねましょう！",
        "今日の努力が、明日の自信になります！",
        "あなたのペースで大丈夫。焦らず進みましょう！",

        # 関口貴夫さん風：年齢・挑戦（51-55）
        "何歳からでも体は変わります！49歳で世界一になった私が保証します！",
        "体づくりに遅すぎることはありません！今日が人生で一番若い日です！",
        "年齢は数字に過ぎません。大切なのは、挑戦する気持ちです！",
        "限界を決めているのは、自分自身。年齢ではありません！",
        "今日の一歩が、10年後のあなたを作ります！",

        # 関口貴夫さん風：継続・結果（56-60）
        "大切なのは、今日の一歩。その積み重ねが未来を変えます！",
        "継続こそが、最強のトレーニング法です！",
        "結果は必ず出ます。信じて続けましょう！",
        "やった分だけ、体は応えてくれます。それが体づくりの真実です！",
        "毎日コツコツ。それが世界一への道でした。あなたも同じです！",

        # 少しの進歩を認めて褒める（61-70）
        f"{name}さん、今日も報告してくれましたね。その継続が結果を生みます",
        "小さな前進を積み重ねている。それが大切です",
        f"{name}さん、0.1kgでも、100gでも、変化は変化。確実に前進していますよ",
        "完璧な一日じゃなくても、報告したこと自体が成長です",
        f"{name}さん、できなかったことより、できたことに目を向けましょう",
        "昨日より、少しでも成長していれば十分です",
        "記録を続けること、それ自体が成果につながります",
        f"{name}さん、今日の小さな努力が、明日の自信に変わります",
        f"{name}さん、一歩ずつで大丈夫。私は伴走者として、見守っています",
        "小さな成功を積み重ねる。それが目標達成への確実な道です",

        # 関口さん実際のメッセージ風（71-80）
        "明日も積み上げていきましょう！",
        "できたことに目を向ければ、前進していることがわかりますよ",
        "頑張ってる感を出さないのも大切なポイントです",
        "今のペースがかえって良いんですよ",
        "突然ストンと落ちる日がありますから、焦らず続けましょう",
        "人間、できなかったことに目が向きがちですが、できたことも多いものですよ",
        "あきらめる必要は全くありません！そこから加速させていきましょう",
        "前向きな気持ちで続けていけば、必ず結果が出ます",
        "この調子で無理なく続けていきましょう",
        "できたことを数えて、明日につなげていきましょう",
    ]
    print(f"  {random.choice(encouragement_messages)}")
    print("-" * 60)


def main():
    """メイン関数：プログラムの実行の流れを制御する"""
    # ウェルカムメッセージを表示
    print_welcome()

    # プランを選択
    selected_plan = select_plan()

    # ユーザーのプロフィールを取得
    user_profile = get_user_profile(selected_plan)

    # 準備期間を実施（ダイエット目的の場合のみ）
    enable_nutrition_tracking = False
    if user_profile.get('monthly_target_kg'):
        # 3日間の食事記録を実施
        meal_records = conduct_preparation_period(user_profile)

        # 平均カロリーとPFCを計算
        baseline = calculate_nutrition_baseline(meal_records)

        # 目標カロリーとPFCを計算
        nutrition_target = calculate_target_nutrition(user_profile, baseline)

        # プロフィールに目標栄養データを追加
        user_profile['nutrition_target'] = nutrition_target
        user_profile['nutrition_baseline'] = baseline

        # 栄養記録を有効化
        enable_nutrition_tracking = True

        # 目標を表示
        print("\n" + "=" * 60)
        print("【あなた専用の栄養目標が設定されました！】")
        print("=" * 60)

        # 体重ベースの目標を表示
        if nutrition_target.get('monthly_weight_loss_kg'):
            monthly_loss = nutrition_target['monthly_weight_loss_kg']
            print(f"\n⚖️  月間目標減量: {monthly_loss:.1f}kg/月")
            print(f"   1日あたり: 約{monthly_loss/30:.3f}kg/日")

        print(f"\n📊 準備期間の平均摂取カロリー: {baseline['avg_calories']:.0f}kcal/日")
        print(f"📉 カロリー調整: {nutrition_target['calorie_adjustment']:+.0f}kcal/日")
        print(f"🎯 目標カロリー: {nutrition_target['target_calories']:.0f}kcal/日")

        print(f"\n【目標PFCバランス（P:30% F:20% C:50%）】")
        print(f"  タンパク質: {nutrition_target['target_protein']:.1f}g")
        print(f"  脂質: {nutrition_target['target_fat']:.1f}g")
        print(f"  炭水化物: {nutrition_target['target_carbs']:.1f}g")

        print("\nこの目標に向かって、一緒に頑張りましょう！")
        print("=" * 60)

    # プロフィールを保存
    save_profile(user_profile)

    # 報告ループ開始のメッセージ
    print("\nそれでは、日々の報告を始めましょう！")
    if enable_nutrition_tracking:
        print("※ カロリーとPFCの記録もお願いします")
    print("（いつでも体重入力で「exit」または「終了」と入力すると終了できます）\n")

    # 日々の報告ループ
    day_count = 1  # 何日目かをカウント
    while True:
        # 残り日数を確認
        remaining_days = calculate_remaining_days(user_profile)

        # プラン期間が終了した場合
        if remaining_days <= 0:
            print("\n" + "=" * 60)
            print(f"🎉 {user_profile['plan']['name']}が終了しました！")
            print("=" * 60)
            print(f"\n{user_profile['name']}さん、お疲れさまでした！")
            print(f"{user_profile['plan']['days']}日間、よく頑張りました💪")
            print("\n目標に向かって一緒に走り続けた日々、素晴らしかったです！")
            print("これからも、この習慣を続けていってくださいね。")
            print("\n引き続きサポートが必要な場合は、新しいプランをご検討ください。")
            print("=" * 60)
            break

        print(f"\n📅 {day_count}日目の報告（残り{remaining_days}日）")

        # 今日の報告を取得（栄養記録の有無を指定）
        daily_report = get_daily_report(with_nutrition=enable_nutrition_tracking)

        # Noneが返ってきたら終了
        if daily_report is None:
            print("\n" + "=" * 60)
            print("今日もお疲れさまでした！")
            print("また明日も頑張りましょう！💪")
            print(f"\nプラン残り日数: {remaining_days}日")
            print("=" * 60)
            break

        # 体重データを保存
        name = user_profile.get("name", "あなた")
        save_weight_data(name, daily_report["weight"])

        # フィードバックを生成・表示
        generate_feedback(user_profile, daily_report)

        # グラフを生成・更新
        generate_weight_graph(name)

        # 日数をカウントアップ
        day_count += 1


# このスクリプトが直接実行された場合のみmain()を実行
if __name__ == "__main__":
    main()
