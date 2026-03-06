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

## ライセンス

MIT
