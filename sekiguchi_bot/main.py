#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
関口ポケットメンターbot（ライト版）
ダイエットや健康維持をサポートする、関口貴夫さん風のメンターbotです。
"""

import random


def print_welcome():
    """ウェルカムメッセージを表示する"""
    print("=" * 60)
    print("    関口ポケットメンターbot（ライト版）へようこそ！")
    print("=" * 60)
    print("あなたの健康とボディメイクをサポートします！")
    print()


def get_user_profile():
    """
    ユーザーのプロフィール情報を入力してもらう

    Returns:
        dict: ユーザーのプロフィール情報（目的、期間、目標体重）
    """
    print("まずは、あなたのことを教えてください！\n")

    # 目的を入力してもらう
    purpose = input("【目的】あなたの目標は何ですか？（例：ダイエット、増量、健康維持など）\n> ")

    # 期間を入力してもらう（数字として受け取る）
    while True:
        try:
            period = input("\n【期間】何ヶ月で達成したいですか？（数字で入力）\n> ")
            period_months = int(period)
            break
        except ValueError:
            print("数字で入力してください。")

    # 目標体重を入力してもらう
    while True:
        try:
            target_weight = input("\n【目標体重】目標体重は何kgですか？\n> ")
            target_weight_kg = float(target_weight)
            break
        except ValueError:
            print("数字で入力してください（小数点もOKです）。")

    print("\n" + "-" * 60)
    print(f"素晴らしい！目標は「{purpose}」ですね！")
    print(f"{period_months}ヶ月で{target_weight_kg}kgを目指しましょう！")
    print("一緒に頑張りましょう！💪")
    print("-" * 60 + "\n")

    # プロフィール情報を辞書形式で返す
    return {
        "purpose": purpose,
        "period_months": period_months,
        "target_weight": target_weight_kg
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


def generate_feedback(profile, report):
    """
    関口貴夫さん風のフィードバックを生成する

    Args:
        profile (dict): ユーザーのプロフィール
        report (dict): 今日の報告内容
    """
    print("\n" + "-" * 60)
    print("【関口メンターからのフィードバック】")
    print("-" * 60)

    # 良かった点を生成
    print("\n✨ 良かった点:")
    good_points = []

    # 運動したかチェック
    if report["exercise"].strip():
        good_points.append(f"「{report['exercise']}」をやったこと、素晴らしいです！")
    else:
        good_points.append("報告をしっかりしてくれたこと、それ自体が素晴らしい一歩です！")

    # 体重報告のチェック
    good_points.append("毎日体重を測って記録する習慣、これがとても大切です！")

    for point in good_points:
        print(f"  • {point}")

    # 改善ポイントを生成（1つだけ）
    print("\n💡 改善ポイント（1つだけ！）:")
    improvement_tips = [
        "明日は運動の時間を少しだけ増やしてみましょう！",
        "水分補給を意識してみてください。1日2リットルが目安です！",
        "タンパク質をもう少し意識して摂ってみましょう！",
        "睡眠も大事！7時間以上の睡眠を心がけてみてください！",
        "野菜をあと一皿増やしてみましょう！色とりどりの野菜がベストです！",
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
        "継続は力なり！明日も一緒に頑張りましょう！",
        "あなたなら絶対できます！その調子で行きましょう！",
        "小さな積み重ねが大きな成果を生みます！明日も楽しみにしています！",
        "昨日より今日、今日より明日。少しずつ前進していきましょう！",
        "完璧じゃなくていい、続けることが何より大切です！",
        "あなたの努力、ちゃんと見ていますよ！明日も応援しています！",
    ]
    print(f"  {random.choice(encouragement_messages)}")
    print("-" * 60)


def main():
    """メイン関数：プログラムの実行の流れを制御する"""
    # ウェルカムメッセージを表示
    print_welcome()

    # ユーザーのプロフィールを取得
    user_profile = get_user_profile()

    # 報告ループ開始のメッセージ
    print("\nそれでは、日々の報告を始めましょう！")
    print("（いつでも体重入力で「exit」または「終了」と入力すると終了できます）\n")

    # 日々の報告ループ
    day_count = 1  # 何日目かをカウント
    while True:
        print(f"\n📅 {day_count}日目の報告")

        # 今日の報告を取得
        daily_report = get_daily_report()

        # Noneが返ってきたら終了
        if daily_report is None:
            print("\n" + "=" * 60)
            print("今日もお疲れさまでした！")
            print("また明日も頑張りましょう！💪")
            print("=" * 60)
            break

        # フィードバックを生成・表示
        generate_feedback(user_profile, daily_report)

        # 日数をカウントアップ
        day_count += 1


# このスクリプトが直接実行された場合のみmain()を実行
if __name__ == "__main__":
    main()
