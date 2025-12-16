#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
関口の指導哲学の状況別最適化メッセージシステム

個別の状況に合わせて、4要素（チアリーダー×コメディアン×バーテンダー×専門家）を
戦略的に組み合わせて最適解を送信します。
"""

import random


def analyze_user_situation(weight_data, achievement_data, consistency_data):
    """
    ユーザーの詳細な状況を分析して、最適な指導スタイルを決定

    Args:
        weight_data (dict): 体重データ
            - recent_trend: "up", "down", "plateau" (最近の傾向)
            - days_plateau: 停滞日数
            - total_progress: 総進捗率 (%)
        achievement_data (dict): 達成度データ
            - calorie_achievement: カロリー目標達成率 (%)
            - pfc_balance: PFCバランス達成率 (%)
            - exercise_frequency: 運動頻度 (週あたり回数)
        consistency_data (dict): 継続性データ
            - reporting_streak: 連続報告日数
            - total_days: 開始からの経過日数
            - consistency_rate: 報告継続率 (%)

    Returns:
        str: 状況カテゴリー
            - "excellent_progress": 順調に進捗中
            - "struggling_plateau": 停滞期で苦しんでいる
            - "struggling_regression": 後退して苦しんでいる
            - "inconsistent_motivated": 不安定だがやる気あり
            - "inconsistent_demotivated": 不安定でモチベーション低下
            - "excellent_achievement": 目標大幅達成
            - "good_steady": 堅実に継続中
            - "needs_encouragement": 励ましが必要
    """
    # 体重の傾向
    trend = weight_data.get('recent_trend', 'plateau')
    days_plateau = weight_data.get('days_plateau', 0)
    total_progress = weight_data.get('total_progress', 0)

    # 達成度
    calorie_achievement = achievement_data.get('calorie_achievement', 100)
    exercise_frequency = achievement_data.get('exercise_frequency', 0)

    # 継続性
    consistency_rate = consistency_data.get('consistency_rate', 100)
    reporting_streak = consistency_data.get('reporting_streak', 1)

    # 状況判定ロジック
    if trend == "down" and total_progress > 0 and consistency_rate >= 80:
        if total_progress >= 80:
            return "excellent_achievement"  # 目標大幅達成
        else:
            return "excellent_progress"  # 順調に進捗中

    elif trend == "plateau" and days_plateau >= 7:
        if consistency_rate >= 70:
            return "struggling_plateau"  # 停滞期で苦しんでいる（頑張っている）
        else:
            return "inconsistent_demotivated"  # 不安定でモチベーション低下

    elif trend == "up":
        if consistency_rate >= 70:
            return "struggling_regression"  # 後退して苦しんでいる（でも継続）
        else:
            return "inconsistent_demotivated"  # 不安定でモチベーション低下

    elif consistency_rate >= 80 and reporting_streak >= 7:
        return "good_steady"  # 堅実に継続中

    elif consistency_rate >= 50 and reporting_streak >= 3:
        return "inconsistent_motivated"  # 不安定だがやる気あり

    else:
        return "needs_encouragement"  # 励ましが必要


def get_optimized_philosophy_message(name, situation_category, weight_data=None):
    """
    状況に応じて最適化された4要素メッセージを生成

    各状況で重点的に伝えるべき要素を組み合わせます：
    - 苦しい時: バーテンダー（傾聴）60% + チアリーダー（応援）30% + 専門家（根拠）10%
    - 順調な時: チアリーダー（祝福）50% + 専門家（検証）30% + コメディアン（楽しむ）20%
    - 停滞期: 専門家（説明）40% + バーテンダー（理解）40% + チアリーダー（励まし）20%
    - 不安定: バーテンダー（傾聴）50% + 専門家（指導）30% + チアリーダー（励まし）20%

    Args:
        name (str): ユーザー名
        situation_category (str): analyze_user_situation()で判定された状況カテゴリー
        weight_data (dict, optional): 体重データ（具体的な数値を表示する場合）

    Returns:
        dict: 4要素を含む最適化メッセージ
            - message: 統合メッセージ（要素を組み合わせたもの）
            - primary_element: 主要要素名
            - emphasis: 各要素の強調度 {element: percentage}
            - breakdown: 各要素の内容（デバッグ用）
    """
    # 状況別メッセージ定義
    messages = {
        "excellent_progress": {
            "primary": "cheerleader",
            "emphasis": {"cheerleader": 50, "expert": 30, "comedian": 15, "bartender": 5},
            "templates": [
                {
                    "cheerleader": f"{name}さん、素晴らしい進捗です！この調子で一緒に進んでいきましょう！",
                    "expert": "この減量ペースは科学的に理想的です。筋肉を維持しながら脂肪を落とせている証拠です。",
                    "comedian": "体重計が喜んでる音が聞こえてきそうですね！この調子で楽しく続けましょう！",
                    "bartender": f"{name}さんの努力が報われて、私も本当に嬉しいです。",
                },
                {
                    "cheerleader": f"{name}さんの努力が数字にはっきり表れていますね！継続の力です！",
                    "expert": "基礎代謝を維持しながらの減量ができています。リバウンドしにくい理想的な状態です。",
                    "comedian": f"{name}さんと体重計、今日は最高の関係ですね（笑）！",
                    "bartender": "結果が出ると、モチベーション上がりますよね。その気持ちを大切にしてください。",
                }
            ]
        },

        "struggling_plateau": {
            "primary": "expert",
            "emphasis": {"expert": 40, "bartender": 40, "cheerleader": 20, "comedian": 0},
            "templates": [
                {
                    "expert": "停滞期は体が新しい体重に慣れようとしている時期です。ここで諦めずに続けると、必ず突然ストンと落ちる日が来ます。これは科学的に証明されています。",
                    "bartender": f"{name}さん、2週間変化がないと本当に不安になりますよね。その気持ち、よくわかります。でも、報告を続けている時点で前進しています。",
                    "cheerleader": f"{name}さん、停滞期こそが成長のチャンス！ここを乗り越えれば大きな変化が待っています！諦めずに一緒に乗り越えましょう！",
                    "comedian": "",  # この状況ではコメディアン要素は使わない
                },
                {
                    "expert": "体重は階段状に落ちるものです。停滞期の後、急に落ちることが多いです。筋肉が増えて脂肪が減っていれば、体重は変わらなくても体脂肪率は改善しています。",
                    "bartender": f"{name}さん、数字が変わらなくても、体の中では確実に変化が起きていますよ。目に見えない変化もあります。焦らず、今のペースを信じてください。",
                    "cheerleader": f"{name}さん、変化がなくても継続していることが素晴らしい！その姿勢が必ず結果を生みます！",
                    "comedian": "",
                }
            ]
        },

        "struggling_regression": {
            "primary": "bartender",
            "emphasis": {"bartender": 50, "cheerleader": 30, "expert": 20, "comedian": 0},
            "templates": [
                {
                    "bartender": f"{name}さん、体重が増えた時って本当に不安になりますよね。頑張ってるのに増えると、モチベーション下がりますよね。その気持ち、心からわかります。でも、それでもここに報告してくれた。それが本当に素晴らしいんです。",
                    "cheerleader": f"{name}さん、この壁を乗り越えたら、もっと強い自分に会えますよ！停滞や増加は体が変化に慣れようとしている証拠。諦めずに続ければ必ず突破できます！",
                    "expert": "体重は1日で1-2kg変動します。体脂肪1kg減らすには7200kcalの消費が必要なので、1日で脂肪が増えることはほぼありません。多くは水分やグリコーゲンの一時的な蓄積です。",
                    "comedian": "",
                },
                {
                    "bartender": f"{name}さんの頑張り、ちゃんと見えてますよ。数字だけが全てじゃありません。増えた時こそ、自分を責めないでください。体は複雑です。",
                    "cheerleader": f"{name}さん、体重が増えても落ち込む必要はありません！むしろここからが本番です！一緒に頑張りましょう！",
                    "expert": "ホメオスタシス（恒常性）で体が現状維持しようとしている時期かもしれません。ここで諦めずに続けることが成功の鍵です。",
                    "comedian": "",
                }
            ]
        },

        "inconsistent_motivated": {
            "primary": "bartender",
            "emphasis": {"bartender": 40, "expert": 30, "cheerleader": 25, "comedian": 5},
            "templates": [
                {
                    "bartender": f"{name}さん、完璧じゃなくても大丈夫です。続けられる時に続ける。それがあなたのペースです。無理して続けて燃え尽きるより、マイペースで長く続ける方が大切です。",
                    "expert": "継続は完璧さより重要です。週に3-4回の報告でも十分効果はあります。大切なのは、完全にやめないこと。それだけで体は変化します。",
                    "cheerleader": f"{name}さん、報告できた日があるだけでも前進です！完璧を目指さず、できる範囲で一緒に続けていきましょう！",
                    "comedian": "人生、波があるのが普通ですよ（笑）。ロボットじゃないんですから！",
                },
                {
                    "bartender": f"{name}さんのペースで大丈夫。焦らず、一緒に進んでいきましょう。できる日にできることをやる。それで十分です。",
                    "expert": "不規則でも、月単位で見れば効果は出ます。週7日完璧より、週3日でも3ヶ月続ける方が成果が出ます。",
                    "cheerleader": f"{name}さん、継続できていますね。その姿勢が何より大切です！",
                    "comedian": "",
                }
            ]
        },

        "inconsistent_demotivated": {
            "primary": "bartender",
            "emphasis": {"bartender": 60, "cheerleader": 30, "expert": 10, "comedian": 0},
            "templates": [
                {
                    "bartender": f"{name}さん、辛い時期なんですね。無理に頑張ろうとしなくて大丈夫です。今は心と体を休めることも大切です。でも、完全にやめる必要はありません。気が向いた時にまた報告してくれれば、それだけで十分です。",
                    "cheerleader": f"{name}さん、今ここにいてくれるだけで素晴らしいです。ゼロにならなければ、いつでもまた始められます。一緒に少しずつ進んでいきましょう。",
                    "expert": "休息も戦略の一つです。燃え尽きて完全にやめるより、ペースを落として続ける方が長期的には効果的です。",
                    "comedian": "",
                },
                {
                    "bartender": f"{name}さん、今は苦しい時期かもしれませんね。でも、このメッセージを読んでくれている。それだけで、まだ諦めていない証拠です。私はそれを信じています。",
                    "cheerleader": f"{name}さん、今日できなくても明日があります。焦らず、あなたのペースで大丈夫です。",
                    "expert": "完全に中断するより、週1回でも続ける方が効果は圧倒的に高いです。ハードルを下げて続けましょう。",
                    "comedian": "",
                }
            ]
        },

        "excellent_achievement": {
            "primary": "cheerleader",
            "emphasis": {"cheerleader": 60, "expert": 25, "comedian": 10, "bartender": 5},
            "templates": [
                {
                    "cheerleader": f"{name}さん、本当に素晴らしい！目標達成おめでとうございます！この努力と継続力、心から尊敬します！あなたは本当にやり遂げました！",
                    "expert": "この成果は科学的にも完璧です。急激すぎず、遅すぎず、理想的なペースで体が変化しています。筋肉を維持しながら脂肪を落とせた証拠です。自信を持ってください。",
                    "comedian": f"{name}さん、体重計が「お疲れ様でした！」って言ってますよ（笑）！最高の結果ですね！",
                    "bartender": f"{name}さんの努力が報われて、私も本当に嬉しいです。",
                },
                {
                    "cheerleader": f"{name}さん、やりましたね！目標達成です！この継続力があれば、これからも何でも達成できます！",
                    "expert": "この減量ペースとPFCバランス、教科書通りの完璧な成果です。リバウンドのリスクは極めて低いです。",
                    "comedian": "完璧すぎて、私の出番がありませんね（笑）！素晴らしいです！",
                    "bartender": "ここまで続けられた自分を、たくさん褒めてあげてくださいね。",
                }
            ]
        },

        "good_steady": {
            "primary": "expert",
            "emphasis": {"expert": 35, "cheerleader": 35, "bartender": 20, "comedian": 10},
            "templates": [
                {
                    "expert": "この継続性は素晴らしいです。体は継続に対して必ず応えます。堅実なペースで進めていますね。",
                    "cheerleader": f"{name}さん、この堅実な継続、本当に素晴らしいです！地道な努力が必ず結果を生みます！",
                    "bartender": f"{name}さん、毎日の報告、本当にお疲れ様です。その習慣が何より価値があります。",
                    "comedian": f"{name}さん、真面目すぎて逆に心配ですよ（笑）！たまには息抜きも忘れずに！",
                },
                {
                    "expert": "堅実な継続は、短期間の集中より圧倒的に効果的です。科学的にも証明されています。",
                    "cheerleader": f"{name}さん、この調子で一歩一歩進んでいきましょう！",
                    "bartender": "焦らず、今のペースを信じてください。順調です。",
                    "comedian": "",
                }
            ]
        },

        "needs_encouragement": {
            "primary": "cheerleader",
            "emphasis": {"cheerleader": 50, "bartender": 40, "expert": 10, "comedian": 0},
            "templates": [
                {
                    "cheerleader": f"{name}さん、大丈夫です！今日ここに来てくれた、それだけで十分です！一緒に少しずつ進んでいきましょう！",
                    "bartender": f"{name}さん、今は辛い時期かもしれませんね。でも、完全に諦めてはいない。このメッセージを読んでいるということは、まだ前を向いている証拠です。",
                    "expert": "小さな一歩でも、続ければ必ず体は変化します。ゼロじゃなければ、効果はあります。",
                    "comedian": "",
                },
                {
                    "cheerleader": f"{name}さん、今日報告できなくても明日があります！焦らず、できる時にできることを。それで十分です！",
                    "bartender": f"{name}さんのペースで大丈夫。無理する必要はありません。",
                    "expert": "完璧を目指すより、継続を目指す方が効果的です。",
                    "comedian": "",
                }
            ]
        }
    }

    # 状況に応じたメッセージテンプレートを取得
    situation_msg = messages.get(situation_category, messages["good_steady"])
    template = random.choice(situation_msg["templates"])

    # 統合メッセージを構築（強調度に応じて組み合わせ）
    emphasis = situation_msg["emphasis"]
    primary_element = situation_msg["primary"]

    # 強調度が高い順に要素を並べる
    sorted_elements = sorted(emphasis.items(), key=lambda x: x[1], reverse=True)

    # 統合メッセージ生成
    integrated_message_parts = []
    icons = {
        "cheerleader": "🎺",
        "comedian": "🎭",
        "bartender": "🍸",
        "expert": "🎓"
    }

    for element, percentage in sorted_elements:
        if percentage > 0 and template[element]:
            integrated_message_parts.append(f"{icons[element]} {template[element]}")

    integrated_message = "\n\n".join(integrated_message_parts)

    return {
        "message": integrated_message,
        "primary_element": primary_element,
        "emphasis": emphasis,
        "breakdown": template,
        "situation_category": situation_category
    }


def get_simple_optimized_message(name, weight_change=None, consistency_rate=100, days_plateau=0):
    """
    簡易版：基本的なパラメータから最適化メッセージを生成

    Args:
        name (str): ユーザー名
        weight_change (float, optional): 体重変化（kg）。Noneの場合は初回
        consistency_rate (float): 報告継続率（%）
        days_plateau (int): 停滞日数

    Returns:
        dict: 最適化メッセージ
    """
    # 簡易的な状況判定
    if weight_change is None:
        # 初回
        situation = "needs_encouragement"
        trend = "plateau"
    elif weight_change < -0.3:
        # 順調
        situation = "excellent_progress"
        trend = "down"
    elif weight_change > 0.3:
        # 増加
        if consistency_rate >= 70:
            situation = "struggling_regression"
        else:
            situation = "inconsistent_demotivated"
        trend = "up"
    elif days_plateau >= 10:
        # 長期停滞
        situation = "struggling_plateau"
        trend = "plateau"
    elif consistency_rate >= 80:
        # 堅実
        situation = "good_steady"
        trend = "plateau"
    elif consistency_rate >= 50:
        # やる気あり
        situation = "inconsistent_motivated"
        trend = "plateau"
    else:
        # 励まし必要
        situation = "needs_encouragement"
        trend = "plateau"

    # ダミーデータ作成
    weight_data = {"recent_trend": trend, "days_plateau": days_plateau, "total_progress": 0}
    achievement_data = {"calorie_achievement": 100, "pfc_balance": 100, "exercise_frequency": 3}
    consistency_data = {"reporting_streak": 7, "total_days": 30, "consistency_rate": consistency_rate}

    return get_optimized_philosophy_message(name, situation, weight_data)


# 使用例とテスト
if __name__ == "__main__":
    print("=" * 80)
    print("関口の指導哲学 - 状況別最適化メッセージシステム")
    print("=" * 80)

    # テストケース1: 順調に進捗中
    print("\n【テストケース1: 順調に進捗中】")
    print("-" * 80)
    result = get_simple_optimized_message("太郎", weight_change=-0.8, consistency_rate=90, days_plateau=0)
    print(f"状況: {result['situation_category']}")
    print(f"主要要素: {result['primary_element']}")
    print(f"強調度: {result['emphasis']}")
    print(f"\n統合メッセージ:\n{result['message']}")

    # テストケース2: 停滞期で苦しんでいる
    print("\n\n【テストケース2: 停滞期で苦しんでいる】")
    print("-" * 80)
    result = get_simple_optimized_message("花子", weight_change=0.0, consistency_rate=85, days_plateau=14)
    print(f"状況: {result['situation_category']}")
    print(f"主要要素: {result['primary_element']}")
    print(f"強調度: {result['emphasis']}")
    print(f"\n統合メッセージ:\n{result['message']}")

    # テストケース3: 後退して苦しんでいる
    print("\n\n【テストケース3: 後退して苦しんでいる】")
    print("-" * 80)
    result = get_simple_optimized_message("次郎", weight_change=0.8, consistency_rate=75, days_plateau=0)
    print(f"状況: {result['situation_category']}")
    print(f"主要要素: {result['primary_element']}")
    print(f"強調度: {result['emphasis']}")
    print(f"\n統合メッセージ:\n{result['message']}")

    # テストケース4: 不安定だがやる気あり
    print("\n\n【テストケース4: 不安定だがやる気あり】")
    print("-" * 80)
    result = get_simple_optimized_message("三郎", weight_change=-0.2, consistency_rate=60, days_plateau=3)
    print(f"状況: {result['situation_category']}")
    print(f"主要要素: {result['primary_element']}")
    print(f"強調度: {result['emphasis']}")
    print(f"\n統合メッセージ:\n{result['message']}")

    # テストケース5: モチベーション低下
    print("\n\n【テストケース5: モチベーション低下】")
    print("-" * 80)
    result = get_simple_optimized_message("四郎", weight_change=0.5, consistency_rate=30, days_plateau=7)
    print(f"状況: {result['situation_category']}")
    print(f"主要要素: {result['primary_element']}")
    print(f"強調度: {result['emphasis']}")
    print(f"\n統合メッセージ:\n{result['message']}")
