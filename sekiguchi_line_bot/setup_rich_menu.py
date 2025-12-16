#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リッチメニューセットアップスクリプト
"""

import os
import json
import requests
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
RICH_MENU_IMAGE_PATH = 'rich_menu_image.png'  # 準備した画像ファイル


def create_rich_menu():
    """リッチメニューを作成"""
    url = 'https://api.line.me/v2/bot/richmenu'
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    # rich_menu_config.jsonを読み込み
    with open('rich_menu_config.json', 'r', encoding='utf-8') as f:
        rich_menu_data = json.load(f)

    response = requests.post(url, headers=headers, json=rich_menu_data)

    if response.status_code == 200:
        rich_menu_id = response.json()['richMenuId']
        print(f'✅ リッチメニュー作成成功！')
        print(f'Rich Menu ID: {rich_menu_id}')
        return rich_menu_id
    else:
        print(f'❌ リッチメニュー作成失敗: {response.text}')
        return None


def upload_rich_menu_image(rich_menu_id):
    """リッチメニュー画像をアップロード"""
    url = f'https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content'
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'image/png'
    }

    if not os.path.exists(RICH_MENU_IMAGE_PATH):
        print(f'❌ 画像ファイルが見つかりません: {RICH_MENU_IMAGE_PATH}')
        print('📝 2500x1686pxの画像を準備してください')
        return False

    with open(RICH_MENU_IMAGE_PATH, 'rb') as f:
        response = requests.post(url, headers=headers, data=f)

    if response.status_code == 200:
        print('✅ リッチメニュー画像アップロード成功！')
        return True
    else:
        print(f'❌ 画像アップロード失敗: {response.text}')
        return False


def set_default_rich_menu(rich_menu_id):
    """リッチメニューをデフォルトに設定"""
    url = f'https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}'
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        print('✅ リッチメニューをデフォルトに設定しました！')
        return True
    else:
        print(f'❌ デフォルト設定失敗: {response.text}')
        return False


def list_rich_menus():
    """登録済みリッチメニューの一覧を表示"""
    url = 'https://api.line.me/v2/bot/richmenu/list'
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        menus = response.json().get('richmenus', [])
        print(f'\n📋 登録済みリッチメニュー: {len(menus)}件')
        for menu in menus:
            print(f"  - {menu['name']} (ID: {menu['richMenuId']})")
        return menus
    else:
        print(f'❌ リッチメニュー一覧取得失敗: {response.text}')
        return []


def delete_rich_menu(rich_menu_id):
    """リッチメニューを削除"""
    url = f'https://api.line.me/v2/bot/richmenu/{rich_menu_id}'
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        print(f'✅ リッチメニュー削除成功: {rich_menu_id}')
        return True
    else:
        print(f'❌ リッチメニュー削除失敗: {response.text}')
        return False


def main():
    """メイン処理"""
    print('='*60)
    print('関口式ダイエットメンター リッチメニューセットアップ')
    print('='*60)

    if not CHANNEL_ACCESS_TOKEN:
        print('❌ LINE_CHANNEL_ACCESS_TOKENが設定されていません')
        print('📝 .envファイルを確認してください')
        return

    # 既存のリッチメニューを表示
    print('\n【STEP 1】既存のリッチメニュー確認')
    existing_menus = list_rich_menus()

    # 既存メニューを削除するか確認
    if existing_menus:
        print('\n既存のリッチメニューを削除しますか？ (y/n)')
        choice = input('> ').strip().lower()
        if choice == 'y':
            for menu in existing_menus:
                delete_rich_menu(menu['richMenuId'])

    # 新しいリッチメニューを作成
    print('\n【STEP 2】リッチメニュー作成')
    rich_menu_id = create_rich_menu()

    if not rich_menu_id:
        print('\n❌ リッチメニューの作成に失敗しました')
        return

    # 画像をアップロード
    print('\n【STEP 3】リッチメニュー画像アップロード')
    if not upload_rich_menu_image(rich_menu_id):
        print('\n❌ 画像のアップロードに失敗しました')
        return

    # デフォルトに設定
    print('\n【STEP 4】デフォルトリッチメニューに設定')
    if set_default_rich_menu(rich_menu_id):
        print('\n' + '='*60)
        print('🎉 リッチメニューのセットアップが完了しました！')
        print('='*60)
        print(f'\nRich Menu ID: {rich_menu_id}')
        print('\nLINE公式アカウントを友だち追加して確認してください。')
    else:
        print('\n❌ デフォルト設定に失敗しました')


if __name__ == '__main__':
    main()
