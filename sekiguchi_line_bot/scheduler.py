#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定期実行スケジューラー
週間レポート・月間レポートを自動配信
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging

from handlers.report_handler import generate_weekly_report, generate_monthly_report

# ロガー設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportScheduler:
    """レポート配信スケジューラー"""

    def __init__(self, line_bot_api):
        """
        Args:
            line_bot_api: LINE Bot APIインスタンス
        """
        self.line_bot_api = line_bot_api
        self.scheduler = BackgroundScheduler()

    def start(self):
        """スケジューラーを開始"""
        # 週間レポート：毎週日曜日 20:00
        self.scheduler.add_job(
            func=self.send_weekly_reports,
            trigger=CronTrigger(day_of_week='sun', hour=20, minute=0),
            id='weekly_report',
            name='週間レポート配信',
            replace_existing=True
        )

        # 月間レポート：毎月最終日 20:00
        self.scheduler.add_job(
            func=self.send_monthly_reports,
            trigger=CronTrigger(day='last', hour=20, minute=0),
            id='monthly_report',
            name='月間レポート配信',
            replace_existing=True
        )

        # コラム配信：毎日20:00
        self.scheduler.add_job(
            func=self.send_daily_column,
            trigger=CronTrigger(hour=20, minute=0),
            id='daily_column',
            name='コラム配信',
            replace_existing=True
        )

        # グループ励ましメッセージ：毎日10:00
        self.scheduler.add_job(
            func=self.send_group_encouragement,
            trigger=CronTrigger(hour=10, minute=0),
            id='group_encouragement',
            name='グループ励ましメッセージ',
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("スケジューラーを開始しました")

    def stop(self):
        """スケジューラーを停止"""
        self.scheduler.shutdown()
        logger.info("スケジューラーを停止しました")

    def send_weekly_reports(self):
        """
        週間レポートを全ユーザーに配信
        """
        logger.info("週間レポート配信開始")

        # ユーザーリストを取得（実際はDBから）
        users = self.get_active_users()

        for user in users:
            try:
                # 過去7日間のデータを取得
                weight_data = self.get_user_weight_data(
                    user['user_id'],
                    days=7
                )
                meal_data = self.get_user_meal_data(
                    user['user_id'],
                    days=7
                )

                # レポート生成
                report_message = generate_weekly_report(
                    user['user_id'],
                    user['name'],
                    weight_data,
                    meal_data,
                    user['profile']
                )

                # 配信
                self.line_bot_api.push_message(
                    user['user_id'],
                    report_message
                )

                logger.info(f"週間レポート配信成功: {user['name']}")

            except Exception as e:
                logger.error(f"週間レポート配信失敗: {user['name']}, {e}")

        logger.info("週間レポート配信完了")

    def send_monthly_reports(self):
        """
        月間レポートを全ユーザーに配信
        """
        logger.info("月間レポート配信開始")

        # ユーザーリストを取得
        users = self.get_active_users()

        for user in users:
            try:
                # 過去30日間のデータを取得
                weight_data = self.get_user_weight_data(
                    user['user_id'],
                    days=30
                )
                meal_data = self.get_user_meal_data(
                    user['user_id'],
                    days=30
                )

                # レポート生成
                report_message = generate_monthly_report(
                    user['user_id'],
                    user['name'],
                    weight_data,
                    meal_data,
                    user['profile']
                )

                # 配信
                self.line_bot_api.push_message(
                    user['user_id'],
                    report_message
                )

                logger.info(f"月間レポート配信成功: {user['name']}")

            except Exception as e:
                logger.error(f"月間レポート配信失敗: {user['name']}, {e}")

        logger.info("月間レポート配信完了")

    def send_daily_column(self):
        """
        毎日のコラムを配信
        """
        from handlers.column_handler import send_daily_column

        logger.info("コラム配信開始")

        users = self.get_active_users()
        user_ids = [u['user_id'] for u in users]

        try:
            send_daily_column(self.line_bot_api, user_ids)
            logger.info(f"コラム配信成功: {len(user_ids)}名")
        except Exception as e:
            logger.error(f"コラム配信失敗: {e}")

    def send_group_encouragement(self):
        """
        グループに励ましメッセージを配信
        """
        from handlers.group_handler import send_group_encouragement
        import os

        logger.info("グループ励ましメッセージ配信開始")

        # グループIDを取得（環境変数から）
        group_id = os.getenv('GROUP_LINE_ID', None)

        if not group_id:
            logger.warning("グループIDが設定されていません")
            return

        try:
            send_group_encouragement(self.line_bot_api, group_id)
            logger.info("グループ励ましメッセージ配信成功")
        except Exception as e:
            logger.error(f"グループ励ましメッセージ配信失敗: {e}")

    def get_active_users(self):
        """
        アクティブユーザーリストを取得

        Returns:
            list: ユーザー情報のリスト
                [{
                    'user_id': 'U1234...',
                    'name': '太郎',
                    'profile': {...}
                }, ...]
        """
        # TODO: 実際はDBから取得
        # 仮実装：テストデータを返す
        return [
            {
                'user_id': 'U_test_001',
                'name': 'テスト太郎',
                'profile': {
                    'monthly_target_kg': 2.0,
                    'target_weight': 70,
                    'target_calories': 1800,
                    'plan': 'light'
                }
            }
        ]

    def get_user_weight_data(self, user_id, days=7):
        """
        ユーザーの体重データを取得

        Args:
            user_id: ユーザーID
            days: 取得する日数

        Returns:
            list: 体重データ [{date, weight}, ...]
        """
        # TODO: 実際はDBから取得
        # 仮実装：ダミーデータを返す
        today = datetime.now()
        data = []

        for i in range(days):
            date = today - timedelta(days=days-i-1)
            # ダミーデータ：徐々に減少
            weight = 75.0 - (i * 0.2)
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'weight': weight
            })

        return data

    def get_user_meal_data(self, user_id, days=7):
        """
        ユーザーの食事データを取得

        Args:
            user_id: ユーザーID
            days: 取得する日数

        Returns:
            list: 食事データ [{date, calories, protein, fat, carbs}, ...]
        """
        # TODO: 実際はDBから取得
        # 仮実装：ダミーデータを返す
        today = datetime.now()
        data = []

        for i in range(days):
            date = today - timedelta(days=days-i-1)
            # ダミーデータ
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'calories': 1800,
                'protein': 135,
                'fat': 40,
                'carbs': 225
            })

        return data


def create_scheduler(line_bot_api):
    """
    スケジューラーインスタンスを作成して起動

    Args:
        line_bot_api: LINE Bot APIインスタンス

    Returns:
        ReportScheduler: スケジューラーインスタンス
    """
    scheduler = ReportScheduler(line_bot_api)
    scheduler.start()
    return scheduler
