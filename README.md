# Sekiguchi Pocket Mentor Bot (Lite)

関口ポケットメンターbot（ライト版）

## 概要

関口貴夫さん風のメンタリングで、日々のボディメイクをサポートするPythonプログラムです。

## 主な機能

- 📝 日々の体重・運動・食事の記録
- 💬 関口貴夫さん風の励ましメッセージ（4900通りの組み合わせ）
- 📊 体重の自動グラフ化
- 👤 名前でパーソナライズされたメッセージ

## 実行方法

```bash
cd sekiguchi_bot
python3 main.py
```

## 必要なライブラリ

- matplotlib

インストール:
```bash
pip install matplotlib
```

## 生成されるファイル

- `weight_data_{名前}.csv` - 体重データ
- `weight_graph_{名前}.png` - 体重グラフ
