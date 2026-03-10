# 🩺 健康寿命サバイバー (Health Longevity Survivor)

生存分析 × 疫学エビデンスで「あなたの健康寿命」を科学的に予測するWebアプリ。

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## 概要

あなたは何歳まで健康でいられるか？コックス比例ハザードモデルと厚生労働省データに基づき、個人の健康寿命を予測します。

**使用手法：**
- カプランマイヤー生存曲線
- ログランク検定
- コックス比例ハザードモデル

**論文・データソース：**
- 厚生労働省 令和元年(2019) 健康寿命の算定データ
- WHO Global Health Observatory（2019）
- JPHC Study（日本公衆衛生センターコホート研究）
- JAGES研究

---

## 機能

| プラン | 機能 |
|---|---|
| 🌱 無料 | **あなたの健康寿命予測**、疫学エビデンス、日本・国際統計、8大リスク因子解説 |
| ☕ サポーター | 上記 + 生存曲線グループ比較、コックス回帰分析、解析手法の詳細、CSVエクスポート |

---

## スクリーンショット

| 健康寿命予測 | 疫学エビデンス | 生存曲線比較 |
|---|---|---|
| コックスモデルで個人予測 | 8大リスク因子 | グループ別KM曲線 |

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

## デプロイ設定（Streamlit Community Cloud / Railway）

### secrets.toml（`.streamlit/secrets.toml`）

```toml
# サポーター向けアクセスコード（カンマ区切り）
access_codes = "CODE1,CODE2"

# Buy Me a Coffee リンク
payment_link = "https://buymeacoffee.com/your-username"
```

### サポーターフロー

1. ユーザーが「☕ Buy Me a Coffee でサポート」ボタンからサポート
2. 支援完了後、管理者がアクセスコードをメールで送付
3. ランディングページでアクセスコードを入力 → サポータープラン有効化

---

## ライセンス

MIT
