#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
関口ポケットメンターbot（ライト版）
ダイエットや健康維持をサポートする、関口貴夫さん風のメンターbotです。
"""

import random
import csv
import os
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# プラン定義
PLANS = {
    "1": {
        "name": "３日間お試しプラン",
        "price": "550円",
        "days": 3,
        "description": "まずは3日間、気軽に試してみましょう！"
    },
    "2": {
        "name": "３ヵ月プラン",
        "price": "月額990円",
        "days": 90,
        "description": "じっくり体質改善！3ヶ月でしっかり結果を出しましょう"
    },
    "3": {
        "name": "６ヵ月プラン",
        "price": "月額880円",
        "days": 180,
        "description": "最もお得！半年かけて理想の体を手に入れましょう"
    }
}


def print_welcome():
    """ウェルカムメッセージを表示する"""
    print("=" * 60)
    print("    関口ポケットメンターbot（ライト版）へようこそ！")
    print("=" * 60)
    print("あなたの健康とボディメイクをサポートします！")
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
        choice = input("プランを選択してください（1, 2, 3）\n> ").strip()
        if choice in PLANS:
            selected_plan = PLANS[choice].copy()
            selected_plan["start_date"] = datetime.now().strftime('%Y-%m-%d')
            print(f"\n{selected_plan['name']}を選択しました！")
            print(f"期間: {selected_plan['days']}日間")
            print(f"料金: {selected_plan['price']}")
            return selected_plan
        else:
            print("1, 2, 3のいずれかを入力してください。")


def get_user_profile(plan):
    """
    ユーザーのプロフィール情報を入力してもらう

    Args:
        plan (dict): 選択されたプラン情報

    Returns:
        dict: ユーザーのプロフィール情報（名前、目的、目標体重、プラン情報）
    """
    print("\nそれでは、あなたのことを教えてください！\n")

    # 名前を入力してもらう
    name = input("【お名前】何とお呼びすればよいですか？（例：太郎、花子など）\n> ").strip()
    if not name:
        name = "あなた"  # 入力がない場合はデフォルト

    # 目的を入力してもらう
    purpose = input("\n【目的】目標は何ですか？（例：ダイエット、増量、健康維持など）\n> ")

    # 目標体重を入力してもらう
    while True:
        try:
            target_weight = input("\n【目標体重】目標体重は何kgですか？\n> ")
            target_weight_kg = float(target_weight)
            break
        except ValueError:
            print("数字で入力してください（小数点もOKです）。")

    print("\n" + "-" * 60)
    print(f"{name}さん、よろしくお願いします！")
    print(f"目標は「{purpose}」ですね。")
    print(f"{plan['days']}日間で{target_weight_kg}kgを目指しましょう！")
    print("一緒に頑張りましょう💪")
    print("-" * 60 + "\n")

    # プロフィール情報を辞書形式で返す
    return {
        "name": name,
        "purpose": purpose,
        "target_weight": target_weight_kg,
        "plan": plan
    }


def get_daily_report():
    """
    今日の報告を入力してもらう

    Returns:
        dict or None: 今日の報告内容（体重、運動、食事）。終了の場合はNone
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
        return get_daily_report()  # もう一度入力を求める

    # 運動内容を入力してもらう
    exercise = input("\n【今日の運動】今日はどんな運動をしましたか？\n> ")

    # 食事内容を入力してもらう
    meal = input("\n【今日の食事】今日食べたものを教えてください（ざっくりでOK）\n> ")

    # 報告内容を辞書形式で返す
    return {
        "weight": today_weight,
        "exercise": exercise,
        "meal": meal
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


def generate_feedback(profile, report):
    """
    関口貴夫さん風のフィードバックを生成する

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

    # 体重変化のメッセージ
    if weight_change is not None:
        if weight_change > 0:
            print(f"\n📊 体重変化: +{weight_change:.1f}kg")
            print(f"停滞しても、逆に増えていてもあきらめる必要は全くありません！")
            print(f"突然ストンと落ちる日がありますから、そこから加速させていきましょう。")
        elif weight_change < 0:
            print(f"\n📊 体重変化: {weight_change:.1f}kg")
            print(f"順調ですね！この調子で続けていきましょう。")
        else:
            print(f"\n📊 体重変化: 変化なし")
            print(f"体重は毎日変動するものです。焦らず継続していきましょう。")

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

    # プロフィールを保存
    save_profile(user_profile)

    # 報告ループ開始のメッセージ
    print("\nそれでは、日々の報告を始めましょう！")
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

        # 今日の報告を取得
        daily_report = get_daily_report()

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
