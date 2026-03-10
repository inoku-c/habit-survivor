# ⚰️ 習慣サバイバー (Habit Survivor)

生存分析で「習慣の寿命」を予測するWebアプリ。

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## 概要

あなたの習慣は何日続くのか？生物統計学の手法を使って科学的に予測します。

**使用手法：**
- カプランマイヤー生存曲線
- ログランク検定
- コックス比例ハザードモデル

**論文エビデンス：**
> Singh B, et al. Time to Form a Habit: A Systematic Review and Meta-Analysis.
> *Healthcare (Basel).* 2024;12(23):2488. doi: 10.3390/healthcare12232488

---

## スクリーンショット

| 論文エビデンス | KM生存曲線 | コックス回帰 |
|---|---|---|
| 21日神話を破壊 | 習慣ごとの継続率 | 脱落リスク因子 |

---

## ローカル実行

```bash
git clone https://github.com/YOUR_USERNAME/habit-survivor.git
cd habit-survivor
pip install -r requirements.txt
streamlit run app.py
```

---

## 技術スタック

- **Frontend/App**: Streamlit
- **生存分析**: lifelines
- **可視化**: Plotly
- **データ処理**: pandas, numpy

---

## Railway デプロイ設定

### 環境変数（Railway Variables）

| 変数名 | 説明 | 例 |
|---|---|---|
| `payjp_public_key` | PAY.JP 公開キー | `pk_live_xxxxxxxxxxxx` |
| `payjp_secret_key` | PAY.JP 秘密キー | `sk_live_xxxxxxxxxxxx` |
| `payjp_plan_id` | PAY.JP サブスクリプションプランID | `pln_xxxxxxxxxxxx` |

### PAY.JP での設定手順

1. [pay.jp](https://pay.jp) でアカウント作成・本人確認
2. ダッシュボード → 「API」から公開キー・秘密キーを取得
3. ダッシュボード → 「プラン」→ 「プランを作成」で ¥100/月のプランを作成しプランIDを取得
4. 上記3つをRailwayの環境変数に設定

### 決済フロー（ユーザー視点）

1. ユーザーが「クレジットカードで支払う」ボタンをクリック
2. PAY.JP のカード入力ポップアップが表示される
3. カード情報入力・支払い完了 → 自動でプロプランが有効化
4. 次回アクセス時は **カスタマーID（`cus_xxxx`）** を「アクセスコード」として入力してログイン

> **テスト用カード番号**: `4242 4242 4242 4242`（PAY.JPテストモード）

---

## ライセンス

MIT
