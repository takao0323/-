#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定期レポートハンドラー
週間レポート・月間レポートを生成・配信
"""

from datetime import datetime, timedelta
from linebot.models import TextSendMessage, FlexSendMessage
import statistics


def generate_weekly_report(user_id, user_name, weight_data, meal_data, profile):
    """
    週間レポートを生成

    Args:
        user_id: ユーザーID
        user_name: ユーザー名
        weight_data: 過去7日間の体重データ [{date, weight}, ...]
        meal_data: 過去7日間の食事データ [{date, calories, protein, fat, carbs}, ...]
        profile: ユーザープロフィール（目標など）

    Returns:
        TextSendMessage: レポートメッセージ
    """
    # 体重分析
    weight_analysis = analyze_weight(weight_data, period='週間')

    # カロリー分析
    calorie_analysis = analyze_calories(meal_data, profile)

    # 現状評価
    current_status = evaluate_current_status(weight_analysis, calorie_analysis, profile)

    # 未来展望
    future_outlook = generate_future_outlook(weight_analysis, profile, period='週間')

    # 関口の4要素メッセージ
    philosophy_message = generate_philosophy_message_for_report(
        user_name, weight_analysis, current_status
    )

    # レポート作成
    report = f"""📊 週間レポート
{datetime.now().strftime('%Y年%m月%d日')}
━━━━━━━━━━━━━━━

{user_name}さん、この1週間お疲れ様でした！
今週の結果を振り返りましょう。

━━━━━━━━━━━━━━━
【📈 体重の推移】
━━━━━━━━━━━━━━━

{weight_analysis['summary']}

開始時: {weight_analysis['start_weight']:.1f}kg
現在: {weight_analysis['current_weight']:.1f}kg
変化: {weight_analysis['change']:+.1f}kg

週間平均: {weight_analysis['average']:.1f}kg
最大: {weight_analysis['max']:.1f}kg
最小: {weight_analysis['min']:.1f}kg

━━━━━━━━━━━━━━━
【🍽️ カロリー分析】
━━━━━━━━━━━━━━━

{calorie_analysis['summary']}

週間平均: {calorie_analysis['average_calories']:.0f}kcal/日
目標カロリー: {calorie_analysis['target_calories']:.0f}kcal/日
達成率: {calorie_analysis['achievement_rate']:.0f}%

記録日数: {calorie_analysis['record_days']}日/7日

PFCバランス（週間平均）:
  P: {calorie_analysis['avg_protein']:.0f}g ({calorie_analysis['p_ratio']:.0f}%)
  F: {calorie_analysis['avg_fat']:.0f}g ({calorie_analysis['f_ratio']:.0f}%)
  C: {calorie_analysis['avg_carbs']:.0f}g ({calorie_analysis['c_ratio']:.0f}%)

━━━━━━━━━━━━━━━
【💡 現状評価】
━━━━━━━━━━━━━━━

{current_status}

━━━━━━━━━━━━━━━
【🔮 未来の展望】
━━━━━━━━━━━━━━━

{future_outlook}

━━━━━━━━━━━━━━━
【関口の指導哲学メッセージ】
100%のトレーナー = 25%チアリーダー×25%コメディアン×25%バーテンダー×25%専門家
━━━━━━━━━━━━━━━

🎺 チアリーダー（応援する）:
{philosophy_message['cheerleader']}

🎭 コメディアン（楽しませる）:
{philosophy_message['comedian']}

🍸 バーテンダー（傾聴する）:
{philosophy_message['bartender']}

🎓 専門家（科学的根拠）:
{philosophy_message['expert']}

━━━━━━━━━━━━━━━

来週も一緒に頑張りましょう！💪
毎日の積み重ねが、未来のあなたを作ります。

━━━━━━━━━━━━━━━"""

    return TextSendMessage(text=report)


def generate_monthly_report(user_id, user_name, weight_data, meal_data, profile):
    """
    月間レポートを生成

    Args:
        user_id: ユーザーID
        user_name: ユーザー名
        weight_data: 過去30日間の体重データ
        meal_data: 過去30日間の食事データ
        profile: ユーザープロフィール

    Returns:
        TextSendMessage: レポートメッセージ
    """
    # 体重分析
    weight_analysis = analyze_weight(weight_data, period='月間')

    # カロリー分析
    calorie_analysis = analyze_calories(meal_data, profile)

    # 達成率
    achievement = calculate_achievement(weight_analysis, profile)

    # 現状評価
    current_status = evaluate_current_status(weight_analysis, calorie_analysis, profile)

    # 未来展望
    future_outlook = generate_future_outlook(weight_analysis, profile, period='月間')

    # 関口の4要素メッセージ
    philosophy_message = generate_philosophy_message_for_report(
        user_name, weight_analysis, current_status
    )

    # レポート作成
    report = f"""📊 月間レポート
{datetime.now().strftime('%Y年%m月')}
━━━━━━━━━━━━━━━

{user_name}さん、1ヶ月お疲れ様でした！
この1ヶ月の成果を振り返りましょう。

━━━━━━━━━━━━━━━
【📈 体重の推移】
━━━━━━━━━━━━━━━

{weight_analysis['summary']}

開始時: {weight_analysis['start_weight']:.1f}kg
現在: {weight_analysis['current_weight']:.1f}kg
変化: {weight_analysis['change']:+.1f}kg

目標ペース: {profile.get('monthly_target_kg', 2.0):.1f}kg/月
実績: {abs(weight_analysis['change']):.1f}kg/月
達成率: {achievement:.0f}%

月間平均: {weight_analysis['average']:.1f}kg
最大: {weight_analysis['max']:.1f}kg
最小: {weight_analysis['min']:.1f}kg

━━━━━━━━━━━━━━━
【🍽️ カロリー分析】
━━━━━━━━━━━━━━━

{calorie_analysis['summary']}

月間平均: {calorie_analysis['average_calories']:.0f}kcal/日
目標カロリー: {calorie_analysis['target_calories']:.0f}kcal/日
達成率: {calorie_analysis['achievement_rate']:.0f}%

記録日数: {calorie_analysis['record_days']}日/30日
記録率: {calorie_analysis['record_days']/30*100:.0f}%

PFCバランス（月間平均）:
  P: {calorie_analysis['avg_protein']:.0f}g ({calorie_analysis['p_ratio']:.0f}%)
  F: {calorie_analysis['avg_fat']:.0f}g ({calorie_analysis['f_ratio']:.0f}%)
  C: {calorie_analysis['avg_carbs']:.0f}g ({calorie_analysis['c_ratio']:.0f}%)

━━━━━━━━━━━━━━━
【🏆 この1ヶ月の成果】
━━━━━━━━━━━━━━━

{get_achievements(weight_analysis, calorie_analysis)}

━━━━━━━━━━━━━━━
【💡 現状評価】
━━━━━━━━━━━━━━━

{current_status}

━━━━━━━━━━━━━━━
【🔮 未来の展望】
━━━━━━━━━━━━━━━

{future_outlook}

━━━━━━━━━━━━━━━
【関口の指導哲学メッセージ】
100%のトレーナー = 25%チアリーダー×25%コメディアン×25%バーテンダー×25%専門家
━━━━━━━━━━━━━━━

🎺 チアリーダー（応援する）:
{philosophy_message['cheerleader']}

🎭 コメディアン（楽しませる）:
{philosophy_message['comedian']}

🍸 バーテンダー（傾聴する）:
{philosophy_message['bartender']}

🎓 専門家（科学的根拠）:
{philosophy_message['expert']}

━━━━━━━━━━━━━━━

来月もこの調子で頑張りましょう！💪
継続は力なり。あなたは確実に成長しています。

━━━━━━━━━━━━━━━"""

    return TextSendMessage(text=report)


def analyze_weight(weight_data, period='週間'):
    """体重データを分析"""
    if not weight_data or len(weight_data) == 0:
        return {
            'summary': f'{period}の体重データがありません',
            'start_weight': 0,
            'current_weight': 0,
            'change': 0,
            'average': 0,
            'max': 0,
            'min': 0
        }

    weights = [d['weight'] for d in weight_data]
    start_weight = weights[0]
    current_weight = weights[-1]
    change = current_weight - start_weight

    # サマリー文章生成
    if change < -0.5:
        summary = f"順調に減量できています！{period}で{abs(change):.1f}kg減少しました。"
    elif change > 0.5:
        summary = f"{period}で{change:.1f}kg増加しています。生活習慣を見直しましょう。"
    else:
        summary = f"{period}で体重はほぼ変化していません。停滞期かもしれません。"

    return {
        'summary': summary,
        'start_weight': start_weight,
        'current_weight': current_weight,
        'change': change,
        'average': statistics.mean(weights),
        'max': max(weights),
        'min': min(weights)
    }


def analyze_calories(meal_data, profile):
    """カロリーデータを分析"""
    if not meal_data or len(meal_data) == 0:
        return {
            'summary': '食事記録がありません',
            'average_calories': 0,
            'target_calories': profile.get('target_calories', 2000),
            'achievement_rate': 0,
            'record_days': 0,
            'avg_protein': 0,
            'avg_fat': 0,
            'avg_carbs': 0,
            'p_ratio': 0,
            'f_ratio': 0,
            'c_ratio': 0
        }

    calories_list = [d['calories'] for d in meal_data]
    protein_list = [d.get('protein', 0) for d in meal_data]
    fat_list = [d.get('fat', 0) for d in meal_data]
    carbs_list = [d.get('carbs', 0) for d in meal_data]

    avg_calories = statistics.mean(calories_list)
    avg_protein = statistics.mean(protein_list)
    avg_fat = statistics.mean(fat_list)
    avg_carbs = statistics.mean(carbs_list)

    target_calories = profile.get('target_calories', 2000)
    achievement_rate = (avg_calories / target_calories) * 100

    # PFC比率計算
    total_calories = (avg_protein * 4) + (avg_fat * 9) + (avg_carbs * 4)
    if total_calories > 0:
        p_ratio = (avg_protein * 4 / total_calories) * 100
        f_ratio = (avg_fat * 9 / total_calories) * 100
        c_ratio = (avg_carbs * 4 / total_calories) * 100
    else:
        p_ratio = f_ratio = c_ratio = 0

    # サマリー文章
    if 95 <= achievement_rate <= 105:
        summary = "目標カロリーを守れています！素晴らしい！"
    elif achievement_rate > 105:
        summary = f"目標より{achievement_rate-100:.0f}%多めです。少し調整しましょう。"
    else:
        summary = f"目標より{100-achievement_rate:.0f}%少なめです。栄養不足に注意。"

    return {
        'summary': summary,
        'average_calories': avg_calories,
        'target_calories': target_calories,
        'achievement_rate': achievement_rate,
        'record_days': len(meal_data),
        'avg_protein': avg_protein,
        'avg_fat': avg_fat,
        'avg_carbs': avg_carbs,
        'p_ratio': p_ratio,
        'f_ratio': f_ratio,
        'c_ratio': c_ratio
    }


def calculate_achievement(weight_analysis, profile):
    """目標達成率を計算"""
    target = profile.get('monthly_target_kg', 2.0)
    actual = abs(weight_analysis['change'])

    if target == 0:
        return 0

    return (actual / target) * 100


def evaluate_current_status(weight_analysis, calorie_analysis, profile):
    """現状を評価"""
    weight_change = weight_analysis['change']
    target_kg = profile.get('monthly_target_kg', 2.0)

    status_parts = []

    # 体重評価
    if weight_change < 0:
        if abs(weight_change) >= target_kg * 0.8:
            status_parts.append("✅ 体重は目標ペースで減少しています")
        else:
            status_parts.append("📉 体重は減少していますが、目標ペースより遅めです")
    elif weight_change > 0:
        status_parts.append("⚠️ 体重が増加しています。生活習慣の見直しが必要です")
    else:
        status_parts.append("➡️ 体重は変化していません。停滞期の可能性があります")

    # カロリー評価
    if 95 <= calorie_analysis['achievement_rate'] <= 105:
        status_parts.append("✅ カロリー管理は完璧です")
    elif calorie_analysis['achievement_rate'] > 105:
        status_parts.append("📊 カロリーが目標より多めです")
    else:
        status_parts.append("📊 カロリーが目標より少なめです")

    # PFC評価
    p_ok = 25 <= calorie_analysis['p_ratio'] <= 35
    f_ok = 15 <= calorie_analysis['f_ratio'] <= 25
    c_ok = 45 <= calorie_analysis['c_ratio'] <= 55

    if p_ok and f_ok and c_ok:
        status_parts.append("✅ PFCバランスは理想的です")
    else:
        status_parts.append("📊 PFCバランスを意識しましょう")

    # 記録率評価
    if calorie_analysis['record_days'] >= 25:
        status_parts.append("✅ 記録習慣が定着しています")
    elif calorie_analysis['record_days'] >= 15:
        status_parts.append("📝 記録をもう少し増やしましょう")
    else:
        status_parts.append("📝 記録を継続することが大切です")

    return "\n".join(status_parts)


def generate_future_outlook(weight_analysis, profile, period='週間'):
    """未来の展望を生成"""
    change_per_period = weight_analysis['change']
    current_weight = weight_analysis['current_weight']
    target_weight = profile.get('target_weight', current_weight - 5)

    if period == '週間':
        multiplier = 4  # 4週間 = 1ヶ月
        future_period = "1ヶ月後"
    else:
        multiplier = 3  # 3ヶ月後
        future_period = "3ヶ月後"

    predicted_weight = current_weight + (change_per_period * multiplier)
    predicted_change = predicted_weight - current_weight
    remaining = target_weight - predicted_weight

    outlook = f"""このペースで続けると...

{future_period}の予測体重: {predicted_weight:.1f}kg
（{predicted_change:+.1f}kg）

目標体重: {target_weight:.1f}kg
残り: {abs(remaining):.1f}kg"""

    if remaining > 0:
        outlook += f"\n\n目標達成まで、あと{abs(remaining):.1f}kgです！\nこのペースなら、確実に近づいています。"
    elif remaining < -2:
        outlook += f"\n\n目標を{abs(remaining):.1f}kg超えて減量する計算です。\nペースを緩めても大丈夫ですよ。"
    else:
        outlook += f"\n\n🎉 目標達成が見えてきました！\nこの調子で頑張りましょう！"

    return outlook


def generate_philosophy_message_for_report(user_name, weight_analysis, current_status):
    """レポート用の関口4要素メッセージ"""
    change = weight_analysis['change']

    if change < -0.5:
        # 順調な場合
        return {
            'cheerleader': f"{user_name}さん、素晴らしい！目に見える成果が出ていますね。この調子で一緒に進みましょう！",
            'comedian': f"体重計が喜んでる音が聞こえてきそうです（笑）。{user_name}さんの努力が数字に表れてますね！",
            'bartender': f"{user_name}さん、頑張ってきた甲斐がありましたね。この成果を一緒に喜びましょう。",
            'expert': f"科学的に理想的なペースです。筋肉を維持しながら脂肪を落とせている証拠。リバウンドしにくい健康的な減量ができています。"
        }
    elif change > 0.5:
        # 増加した場合
        return {
            'cheerleader': f"{user_name}さん、増えても諦める必要はありません！ここからが本番です。一緒に乗り越えましょう！",
            'comedian': f"体重計が「ちょっと待った！」って言ってますね（笑）。でも大丈夫、明日から巻き返しましょう！",
            'bartender': f"増えた時って本当に落ち込みますよね。{user_name}さんの気持ち、よくわかります。でも、ここで報告できたこと自体が素晴らしいです。",
            'expert': f"体重増加の多くは一時的な水分やグリコーゲンの蓄積です。食事と運動を見直せば、必ず改善します。ここで諦めないことが成功の鍵です。"
        }
    else:
        # 変化なしの場合
        return {
            'cheerleader': f"{user_name}さん、変化がなくても継続できていることが素晴らしい！停滞期を抜ければ大きな変化が待っています！",
            'comedian': f"体重計が「今週はお休みモード」ですね（笑）。でも明日突然動き出す可能性大です！",
            'bartender': f"変化がないと不安になりますよね。{user_name}さん、その気持ちよくわかります。でも、体の中では確実に変化が起きていますよ。",
            'expert': f"停滞期は体が新しい体重に慣れようとしている時期。科学的には正常な反応です。ここで諦めずに続けると、必ず突然ストンと落ちる日が来ます。"
        }


def get_achievements(weight_analysis, calorie_analysis):
    """達成事項をリストアップ"""
    achievements = []

    # 体重関連
    if weight_analysis['change'] < -2:
        achievements.append("🏆 1ヶ月で2kg以上の減量に成功")
    elif weight_analysis['change'] < -1:
        achievements.append("🏆 1ヶ月で1kg以上の減量に成功")

    # 記録関連
    if calorie_analysis['record_days'] >= 28:
        achievements.append("🏆 ほぼ毎日記録を継続（素晴らしい！）")
    elif calorie_analysis['record_days'] >= 20:
        achievements.append("🏆 20日以上の記録を達成")

    # カロリー管理
    if 95 <= calorie_analysis['achievement_rate'] <= 105:
        achievements.append("🏆 カロリー管理が完璧")

    # PFCバランス
    p_ok = 25 <= calorie_analysis['p_ratio'] <= 35
    f_ok = 15 <= calorie_analysis['f_ratio'] <= 25
    c_ok = 45 <= calorie_analysis['c_ratio'] <= 55
    if p_ok and f_ok and c_ok:
        achievements.append("🏆 理想的なPFCバランスを維持")

    if not achievements:
        achievements.append("継続できていること自体が成果です！")

    return "\n".join(achievements)
