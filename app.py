"""
🩺 健康寿命サバイバー v3.0
生存分析で「健康寿命」を科学的に予測するアプリ
厚生労働省データ・疫学研究のエビデンスに基づく
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test
import warnings
import io
import hashlib
warnings.filterwarnings("ignore")

st.set_page_config(page_title="健康寿命サバイバー", page_icon="🩺", layout="wide")

# ─── プラン設定 ──────────────────────────────────────────────────────────────
PLANS = {
    "free": {
        "name": "無料プラン",
        "price": "¥0",
        "tabs": [0],          # Tab index: 0=evidence only
        "features": ["疫学エビデンス閲覧", "日本・国際統計グラフ", "8大リスク因子の解説"],
        "locked":   ["生存曲線グループ比較", "コックス回帰分析（多変量）",
                     "あなたの個人健康寿命予測", "解析手法の数理的詳細", "CSVエクスポート"],
    },
    "pro": {
        "name": "プロプラン",
        "price": "¥100/月",
        "tabs": [0, 1, 2, 3, 4],  # All tabs
        "features": ["無料プランの全機能", "生存曲線グループ比較 + ログランク検定",
                     "コックス回帰分析（多変量・フォレストプロット）",
                     "個人健康寿命予測（コックスモデル）",
                     "解析手法の数理的詳細（LaTeX数式）", "CSVデータエクスポート"],
        "locked":   [],
    },
}

# 決済リンク（Gumroad / LemonSqueezy / 任意のサービスのURLをsecretsに設定）
PAYMENT_LINK = st.secrets.get("payment_link", "https://your-payment-link-here")

def _valid_codes() -> set:
    """st.secrets からアクセスコードを取得（なければデモ用コードを使用）"""
    try:
        codes = st.secrets["access_codes"]
        if isinstance(codes, str):
            return {c.strip().upper() for c in codes.split(",")}
        return {str(c).strip().upper() for c in codes}
    except Exception:
        return {"HEALTH2024PRO", "DEMO_PRO"}   # デモ用（本番では secrets で管理）

def verify_access_code(code: str) -> bool:
    return code.strip().upper() in _valid_codes()

# ─── ランディング / 料金ページ ────────────────────────────────────────────────
def show_landing():
    st.markdown("""
    <style>
        .landing-hero {
            text-align: center; padding: 3rem 1rem 2rem; margin-bottom: 1rem;
        }
        .hero-title {
            font-size: 3.5rem; font-weight: 900; line-height: 1.1;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        .hero-sub { font-size: 1.2rem; color: #555; margin-bottom: 2rem; }
        .pricing-card {
            border-radius: 16px; padding: 2rem; text-align: center;
            box-shadow: 0 8px 30px rgba(0,0,0,0.10); margin: 0.5rem;
        }
        .card-free {
            background: #fff; border: 2px solid #e2e8f0;
        }
        .card-pro {
            background: linear-gradient(160deg, #11998e 0%, #38ef7d 100%);
            border: none; color: white;
        }
        .plan-name { font-size: 1.4rem; font-weight: 800; margin-bottom: 0.5rem; }
        .plan-price { font-size: 2.8rem; font-weight: 900; margin-bottom: 0.3rem; }
        .plan-period { font-size: 0.9rem; opacity: 0.75; margin-bottom: 1.5rem; }
        .feature-item { font-size: 0.95rem; margin: 0.4rem 0; }
        .badge-popular {
            background: #f6ad55; color: #744210; font-size: 0.75rem; font-weight: 700;
            padding: 2px 10px; border-radius: 20px; display: inline-block; margin-bottom: 0.8rem;
        }
        .cta-free {
            background: #edf2f7; color: #2d3748; border: none;
            padding: 0.8rem 2rem; border-radius: 8px; font-size: 1rem; font-weight: 600;
            cursor: pointer; width: 100%; margin-top: 1.5rem;
        }
        .cta-pro {
            background: white; color: #11998e; border: none;
            padding: 0.8rem 2rem; border-radius: 8px; font-size: 1rem; font-weight: 700;
            cursor: pointer; width: 100%; margin-top: 1.5rem;
        }
        .divider { border: none; border-top: 1px solid #e2e8f0; margin: 2rem 0; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="landing-hero">
        <div class="hero-title">🩺 健康寿命サバイバー</div>
        <div class="hero-sub">
            生存分析 × 疫学エビデンスで、<b>あなたの健康寿命</b>を科学的に予測する<br>
            厚生労働省データ・WHO・JPHC Study に基づく国内唯一のインタラクティブ解析ツール
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 料金カード ────────────────────────────────
    col_free, col_pro = st.columns(2)

    with col_free:
        st.markdown("""
        <div class="pricing-card card-free">
            <div class="plan-name">🌱 無料プラン</div>
            <div class="plan-price">¥0</div>
            <div class="plan-period">永久無料</div>
            <hr style="border-color:#e2e8f0; margin:1rem 0;">
            <div class="feature-item">✅ 疫学エビデンス閲覧</div>
            <div class="feature-item">✅ 日本・国際健康寿命統計</div>
            <div class="feature-item">✅ 8大リスク因子の解説</div>
            <div class="feature-item" style="color:#aaa;">🔒 生存曲線グループ比較</div>
            <div class="feature-item" style="color:#aaa;">🔒 コックス回帰分析</div>
            <div class="feature-item" style="color:#aaa;">🔒 個人健康寿命予測</div>
            <div class="feature-item" style="color:#aaa;">🔒 解析手法の詳細</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("無料で始める", key="btn_free", use_container_width=True):
            st.session_state["plan"] = "free"
            st.rerun()

    with col_pro:
        st.markdown("""
        <div class="pricing-card card-pro">
            <div class="badge-popular">⭐ 最もご好評</div>
            <div class="plan-name" style="color:white;">🚀 プロプラン</div>
            <div class="plan-price" style="color:white;">¥100</div>
            <div class="plan-period" style="color:rgba(255,255,255,0.8);">/ 月（税込）</div>
            <hr style="border-color:rgba(255,255,255,0.3); margin:1rem 0;">
            <div class="feature-item" style="color:white;">✅ 無料プランの全機能</div>
            <div class="feature-item" style="color:white;">✅ 生存曲線グループ比較</div>
            <div class="feature-item" style="color:white;">✅ コックス回帰分析（多変量）</div>
            <div class="feature-item" style="color:white;">✅ 個人健康寿命予測</div>
            <div class="feature-item" style="color:white;">✅ 解析手法の数理的詳細</div>
            <div class="feature-item" style="color:white;">✅ CSVデータエクスポート</div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button(
            "💳 今すぐ購入（¥100/月）",
            url=PAYMENT_LINK,
            use_container_width=True,
        )

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── アクセスコード入力（購入後） ────────────────
    st.markdown("#### 🔑 購入済みの方：アクセスコードを入力")
    col_code, col_submit = st.columns([3, 1])
    with col_code:
        code_input = st.text_input(
            "アクセスコード",
            placeholder="例：HEALTH2024PRO",
            label_visibility="collapsed",
        )
    with col_submit:
        if st.button("認証", use_container_width=True, type="primary"):
            if verify_access_code(code_input):
                st.session_state["plan"] = "pro"
                st.session_state["code"] = code_input.upper().strip()
                st.success("✅ 認証成功！プロプランが有効化されました。")
                st.rerun()
            else:
                st.error("❌ アクセスコードが正しくありません。")

    st.markdown("""
    <div style="text-align:center;color:#aaa;font-size:0.8rem;margin-top:2rem;">
        購入後にメールで送付されるアクセスコードを入力してください。<br>
        お問い合わせ：support@example.com
    </div>
    """, unsafe_allow_html=True)

# ─── 認証チェック ─────────────────────────────────────────────────────────────
if "plan" not in st.session_state:
    show_landing()
    st.stop()

CURRENT_PLAN = st.session_state["plan"]

def locked_tab(feature_name: str):
    """プロプランでのみ使える機能をロック表示"""
    st.markdown(f"""
    <div style="text-align:center; padding: 4rem 2rem;">
        <div style="font-size:4rem;">🔒</div>
        <div style="font-size:1.5rem; font-weight:700; color:#2d3748; margin:1rem 0;">
            {feature_name}
        </div>
        <div style="color:#718096; margin-bottom:2rem;">
            この機能はプロプラン限定です。
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 プロプランにアップグレード", type="primary", key=f"upgrade_{feature_name}"):
        st.session_state["plan"] = None
        del st.session_state["plan"]
        st.rerun()

st.markdown("""
<style>
    .main-title {
        font-size: 3rem; font-weight: 900;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; padding: 1rem 0;
    }
    .subtitle { text-align: center; color: #555; font-size: 1.1rem; margin-bottom: 0.5rem; }
    .data-badge { text-align: center; margin-bottom: 1.5rem; }
    .metric-card {
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
        border-radius: 12px; padding: 1.2rem; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin: 0.5rem 0;
        border: 1px solid #9ae6b4;
    }
    .metric-value { font-size: 2.5rem; font-weight: 800; color: #22543d; }
    .metric-label { font-size: 0.85rem; color: #555; margin-top: 0.3rem; line-height: 1.4; }
    .bad-card {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        border-radius: 12px; padding: 1.2rem; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin: 0.5rem 0;
        border: 1px solid #fc8181;
    }
    .bad-value { font-size: 2.5rem; font-weight: 800; color: #742a2a; }
    .insight-box {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        border-radius: 10px; padding: 1rem 1.5rem; margin: 0.8rem 0;
        border-left: 4px solid #fc8181;
    }
    .good-box {
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
        border-radius: 10px; padding: 1rem 1.5rem; margin: 0.8rem 0;
        border-left: 4px solid #38a169;
    }
    .info-box {
        background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
        border-radius: 10px; padding: 1rem 1.5rem; margin: 0.8rem 0;
        border-left: 4px solid #3182ce; font-size: 0.92rem;
    }
    .warning-box {
        background: linear-gradient(135deg, #fffff0 0%, #fefcbf 100%);
        border-radius: 10px; padding: 1rem 1.5rem; margin: 0.8rem 0;
        border-left: 4px solid #d69e2e;
    }
    .method-box {
        background: linear-gradient(135deg, #faf5ff 0%, #e9d8fd 100%);
        border-radius: 10px; padding: 1.2rem 1.5rem; margin: 0.8rem 0;
        border-left: 4px solid #805ad5;
    }
    .formula-box {
        background: #1a202c; color: #e2e8f0;
        border-radius: 8px; padding: 1rem 1.5rem; margin: 0.8rem 0;
        font-family: monospace; font-size: 0.9rem;
    }
    .disclaimer-box {
        background: linear-gradient(135deg, #fffff0 0%, #fefcbf 100%);
        border-radius: 8px; padding: 0.8rem 1.2rem; margin: 0.5rem 0;
        border: 1px solid #d69e2e; font-size: 0.8rem; color: #744210;
    }
</style>
""", unsafe_allow_html=True)

# ─── 定数・エビデンス ──────────────────────────────────────────────────────────
JAPAN_STATS = {
    "men_healthy": 72.68, "women_healthy": 75.38,
    "men_total": 81.41,   "women_total": 87.45,
    "men_unhealthy": 8.73, "women_unhealthy": 12.07,
}

RISK_FACTOR_EVIDENCE = [
    ("🚬", "喫煙", "HR 1.5〜2.0",
     "ニコチンによる血管障害・炎症・がんリスクが複合的に作用。健康寿命を平均3〜5年短縮。禁煙後5年で非喫煙者レベルに近づく。",
     "Jha et al. (2013) NEJM; JPHC Study"),
    ("🏃", "運動不足", "HR 1.3〜1.5",
     "週150分以上の中強度有酸素運動で健康寿命を2〜4年延長。筋力・心肺機能・骨密度維持に加え、うつ・認知症の予防効果も実証。",
     "Lee et al. (2012) Lancet; JAGES研究"),
    ("⚖️", "肥満 (BMI≥30)", "HR 1.2〜1.5",
     "糖尿病・高血圧・関節疾患等の複合リスクで健康寿命2〜4年短縮。腹部肥満（内臓脂肪型）が特に高リスク。",
     "Global BMI Mortality Collaboration (2016) Lancet"),
    ("🍺", "多量飲酒", "HR 1.3〜1.4",
     "純アルコール換算60g/日超は肝疾患・がん・脳卒中リスクを増加。「少量は健康に良い」説は大規模研究で否定されている。",
     "GBD 2016 Alcohol Collaborators (2018) Lancet"),
    ("👥", "社会的孤立", "HR 1.5〜1.8",
     "孤立は死亡リスクを29%増加。孤独感がメンタル・免疫・心血管系に影響。日本では孤独死・孤立の社会問題化が深刻。",
     "Holt-Lunstad et al. (2015) PLOS Med"),
    ("😴", "睡眠不足 (<6時間)", "HR 1.3〜1.4",
     "6時間未満は代謝障害・免疫低下・認知機能障害のリスク。7〜8時間が最適。9時間超もリスク増加（逆U字型関係）。",
     "Cappuccio et al. (2011) Sleep"),
    ("🥗", "食事の質（不良）", "HR 1.2〜1.3",
     "地中海食・日本食（魚・野菜・発酵食品）が有利。超加工食品・塩分過多は不利。DASH食は高血圧改善に有効。",
     "Willett et al. (2019) Lancet; NIPPON DATA"),
    ("🏥", "慢性疾患（高血圧・糖尿病等）", "HR 1.5〜2.5",
     "糖尿病は健康寿命を平均6〜8年短縮。高血圧・脂質異常症は適切な管理でリスク大幅低減。早期発見・治療が鍵。",
     "GBD 2019 Collaborators; 日本糖尿病学会"),
]

GLOBAL_STATS = pd.DataFrame({
    "国": ["🇯🇵 日本（女性）", "🇯🇵 日本（男性）", "🇫🇷 フランス", "🇩🇪 ドイツ",
           "🇬🇧 イギリス", "🇦🇺 オーストラリア", "🇺🇸 アメリカ", "🇨🇳 中国"],
    "健康寿命（年）": [75.4, 72.7, 73.4, 70.9, 70.1, 71.3, 66.1, 68.5],
    "平均寿命（年）": [87.5, 81.4, 85.1, 80.9, 81.4, 83.3, 78.5, 77.4],
})
GLOBAL_STATS["不健康期間（年）"] = (GLOBAL_STATS["平均寿命（年）"] - GLOBAL_STATS["健康寿命（年）"]).round(1)

# ─── デモデータ生成（論文パラメータ反映）────────────────────────────────────────
@st.cache_data
def generate_health_data():
    np.random.seed(42)
    n = 800

    sex      = np.random.choice(["男性", "女性"],                  n, p=[0.50, 0.50])
    smoking  = np.random.choice(["あり", "なし"],                  n, p=[0.20, 0.80])
    exercise = np.random.choice(["週3回以上", "週1〜2回", "ほぼしない"], n, p=[0.30, 0.35, 0.35])
    bmi_cat  = np.random.choice(["低体重", "適正", "過体重", "肥満"],   n, p=[0.05, 0.65, 0.20, 0.10])
    alcohol  = np.random.choice(["ほとんど飲まない", "適度", "多量"],    n, p=[0.35, 0.50, 0.15])
    diet     = np.random.choice(["良好", "普通", "不良"],             n, p=[0.25, 0.50, 0.25])
    sleep_hr = np.random.choice(["7〜8時間", "6時間未満", "9時間超"],   n, p=[0.55, 0.30, 0.15])
    social   = np.random.choice(["豊富", "普通", "乏しい"],            n, p=[0.30, 0.45, 0.25])
    chronic  = np.random.choice(["なし", "あり"],                   n, p=[0.80, 0.20])

    # 個人ハザード比（論文エビデンスベース）
    hr = np.ones(n)
    hr[smoking == "あり"]      *= 1.80
    hr[exercise == "ほぼしない"] *= 1.40
    hr[exercise == "週1〜2回"]  *= 1.15
    hr[bmi_cat == "過体重"]     *= 1.20
    hr[bmi_cat == "肥満"]       *= 1.50
    hr[bmi_cat == "低体重"]     *= 1.15
    hr[alcohol == "多量"]       *= 1.40
    hr[diet == "不良"]          *= 1.20
    hr[diet == "普通"]          *= 1.05
    hr[sleep_hr == "6時間未満"] *= 1.30
    hr[sleep_hr == "9時間超"]   *= 1.20
    hr[social == "乏しい"]      *= 1.60
    hr[social == "普通"]        *= 1.10
    hr[chronic == "あり"]       *= 2.00
    hr[sex == "男性"]           *= 1.15

    # Weibull 分布による健康寿命シミュレーション（基準：40歳からの健康年数）
    # BASE_SCALE=35 → 理想的プロフィールの中央値≈29年（= 69歳まで健康）
    BASE_SCALE, SHAPE = 35.0, 2.0
    scale_i = BASE_SCALE / (hr ** (1.0 / SHAPE))
    u = np.random.random(n)
    true_dur = scale_i * (-np.log(u)) ** (1.0 / SHAPE)

    # 打ち切り（フォローアップ上限40年 + 15%途中脱落）
    MAX_FOLLOW = 40.0
    censor_mask = np.random.random(n) < 0.15
    censor_time = np.random.uniform(8, MAX_FOLLOW, n)

    dur_obs = true_dur.copy()
    event = np.ones(n, dtype=int)

    m1 = true_dur > MAX_FOLLOW
    dur_obs[m1] = MAX_FOLLOW
    event[m1] = 0

    m2 = censor_mask & (censor_time < true_dur)
    dur_obs[m2] = censor_time[m2]
    event[m2] = 0

    dur_obs = np.clip(dur_obs, 1.0, MAX_FOLLOW)

    records = []
    for i in range(n):
        records.append({
            "性別": sex[i], "喫煙": smoking[i], "運動習慣": exercise[i],
            "BMI区分": bmi_cat[i], "飲酒": alcohol[i], "食事の質": diet[i],
            "睡眠時間": sleep_hr[i], "社会的つながり": social[i], "慢性疾患": chronic[i],
            "健康期間（年）": round(dur_obs[i], 2),
            "健康終了": event[i],
        })
    return pd.DataFrame(records)


@st.cache_data
def fit_cox_model():
    df = generate_health_data()
    cdf = df.copy()
    cdf["喫煙あり"]    = (cdf["喫煙"] == "あり").astype(int)
    cdf["運動不足"]    = (cdf["運動習慣"] == "ほぼしない").astype(int)
    cdf["過体重以上"]  = cdf["BMI区分"].isin(["過体重", "肥満"]).astype(int)
    cdf["多量飲酒"]    = (cdf["飲酒"] == "多量").astype(int)
    cdf["食事不良"]    = (cdf["食事の質"] == "不良").astype(int)
    cdf["睡眠異常"]    = (cdf["睡眠時間"] != "7〜8時間").astype(int)
    cdf["社会的孤立"]  = (cdf["社会的つながり"] == "乏しい").astype(int)
    cdf["慢性疾患あり"] = (cdf["慢性疾患"] == "あり").astype(int)
    cdf["男性"]        = (cdf["性別"] == "男性").astype(int)

    features = ["喫煙あり", "運動不足", "過体重以上", "多量飲酒", "食事不良",
                "睡眠異常", "社会的孤立", "慢性疾患あり", "男性"]
    cox_input = cdf[features + ["健康期間（年）", "健康終了"]].copy()
    cph = CoxPHFitter(penalizer=0.1)
    cph.fit(cox_input, duration_col="健康期間（年）", event_col="健康終了")
    return cph, features


# ─── ヘッダー ─────────────────────────────────────────────────────────────────
plan_badge_color = "#276749" if CURRENT_PLAN == "pro" else "#718096"
plan_badge_label = "🚀 プロプラン" if CURRENT_PLAN == "pro" else "🌱 無料プラン"
st.markdown('<div class="main-title">🩺 健康寿命サバイバー</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">生存分析が「健康寿命」の真実を暴く — 疫学研究エビデンス搭載</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="data-badge">'
    f'<span style="background:#276749;color:white;padding:3px 14px;border-radius:20px;font-size:0.8rem;font-weight:600;">'
    f'📊 厚生労働省 令和元年(2019)データ · WHO · JPHC Study · JAGES研究 · n=800シミュレーションコホート'
    f'</span>'
    f'&nbsp;&nbsp;'
    f'<span style="background:{plan_badge_color};color:white;padding:3px 14px;border-radius:20px;font-size:0.8rem;font-weight:700;">'
    f'{plan_badge_label}'
    f'</span></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="disclaimer-box">⚠️ <b>注意：</b> '
    '本アプリは疫学研究の手法を学ぶための教育目的シミュレーションです。'
    '実際の医療診断・予後予測ではありません。健康上の判断は医師にご相談ください。'
    '</div>', unsafe_allow_html=True)
st.markdown("---")

# ─── サイドバー ───────────────────────────────────────────────────────────────
with st.sidebar:
    # ── プラン表示 ──────────────────────────────────
    if CURRENT_PLAN == "pro":
        st.markdown(
            '<div style="background:linear-gradient(135deg,#11998e,#38ef7d);'
            'color:white;border-radius:10px;padding:0.8rem 1rem;text-align:center;margin-bottom:0.5rem;">'
            '<b>🚀 プロプラン 有効</b><br><small>全機能が利用可能です</small>'
            '</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="background:#edf2f7;border-radius:10px;padding:0.8rem 1rem;'
            'text-align:center;margin-bottom:0.5rem;">'
            '<b>🌱 無料プラン</b><br><small>疫学エビデンスのみ閲覧可</small>'
            '</div>', unsafe_allow_html=True)
        if st.button("🚀 プロプランにアップグレード", use_container_width=True, type="primary"):
            del st.session_state["plan"]
            st.rerun()

    if st.button("🚪 ログアウト / プラン変更", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("## ⚙️ 設定")
    st.markdown("---")
    st.markdown("### 📥 データエクスポート")
    df_export = generate_health_data()
    if CURRENT_PLAN == "pro":
        csv_buf = io.StringIO()
        df_export.to_csv(csv_buf, index=False, encoding="utf-8-sig")
        st.download_button(
            "📊 シミュレーションデータをCSV",
            data=csv_buf.getvalue().encode("utf-8-sig"),
            file_name="health_longevity_data.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.button("📊 CSVエクスポート（🔒 プロプラン）", disabled=True, use_container_width=True)
    st.markdown("---")
    st.markdown("### 📄 主要データソース")
    st.info(
        "**厚生労働省 (2019)**\n健康寿命の算定方法の指針\n\n"
        "**JPHC Study**\n日本公衆衛生センターコホート研究\n\n"
        "**WHO Global Health Observatory**\n国際健康寿命比較データ"
    )
    st.markdown("---")
    st.markdown("### 🔬 使用解析手法")
    st.markdown("- カプランマイヤー法\n- ログランク検定\n- コックス比例ハザード回帰\n- Weibull分布シミュレーション")

# ─── データ・モデルのロード ───────────────────────────────────────────────────
df = generate_health_data()
cph, cox_features = fit_cox_model()

# ─── タブ ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 疫学エビデンス",
    "📈 生存曲線比較",
    "🧬 コックス回帰分析",
    "🎯 あなたの健康寿命予測",
    "🔬 解析手法の詳細",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: 疫学エビデンス
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 📊 日本の健康寿命 — 最新統計")

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, JAPAN_STATS["men_healthy"],   "歳", "男性の健康寿命",   False),
        (c2, JAPAN_STATS["women_healthy"], "歳", "女性の健康寿命",   False),
        (c3, JAPAN_STATS["men_unhealthy"], "年", "男性の不健康期間", True),
        (c4, JAPAN_STATS["women_unhealthy"],"年","女性の不健康期間", True),
    ]
    for col, val, unit, label, is_bad in stats:
        cls = "bad-card" if is_bad else "metric-card"
        vcls = "bad-value" if is_bad else "metric-value"
        with col:
            st.markdown(
                f'<div class="{cls}">'
                f'<div class="{vcls}">{val}<span style="font-size:1.2rem;">{unit}</span></div>'
                f'<div class="metric-label">{label}<br><small>厚労省 2019</small></div>'
                f'</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="insight-box">⚠️ <b>不健康期間（日常生活が制限される期間）</b>は男性約9年・女性約12年。'
        '「長生き」だけでなく、いかに健康に生きるかが重要です。</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🌍 国際比較（WHO 2019）")
    fig_global = go.Figure()
    fig_global.add_trace(go.Bar(
        x=GLOBAL_STATS["国"], y=GLOBAL_STATS["健康寿命（年）"],
        name="健康寿命", marker_color="#38a169",
        text=GLOBAL_STATS["健康寿命（年）"].astype(str),
        textposition="outside",
    ))
    fig_global.add_trace(go.Bar(
        x=GLOBAL_STATS["国"], y=GLOBAL_STATS["不健康期間（年）"],
        name="不健康期間", marker_color="#fc8181",
        text=GLOBAL_STATS["不健康期間（年）"].astype(str),
        textposition="outside",
    ))
    fig_global.update_layout(
        barmode="stack", title="健康寿命と不健康期間の国際比較",
        yaxis_title="年", height=420,
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig_global.update_xaxes(showgrid=False)
    fig_global.update_yaxes(showgrid=True, gridcolor="#eee")
    st.plotly_chart(fig_global, use_container_width=True)

    st.markdown("---")
    st.markdown("## 🔑 健康寿命を左右する8大リスク因子（論文エビデンス）")
    for icon, factor, effect, detail, source in RISK_FACTOR_EVIDENCE:
        with st.expander(f"{icon} **{factor}** — ハザード比: **{effect}**"):
            st.markdown(f"**メカニズム：** {detail}")
            st.markdown(f"**出典：** _{source}_")

    st.markdown(
        '<div class="info-box">📄 <b>ハザード比（HR）とは：</b> '
        'HR=1.5 は「そのリスク因子を持つ人は、持たない人より健康終了リスクが50%高い」ことを意味します。'
        '詳しくは「🔬 解析手法の詳細」タブを参照。'
        '</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: 生存曲線比較
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
  if CURRENT_PLAN != "pro":
    locked_tab("生存曲線グループ比較")
  else:
    st.markdown("## 📈 リスク因子別 カプランマイヤー生存曲線")
    st.markdown("リスク因子ごとにグループを分け、**健康を維持できる確率の推移**を比較します。")

    col_opt, _ = st.columns([1, 2])
    with col_opt:
        factor_options = {
            "喫煙": ("喫煙", ["あり", "なし"]),
            "運動習慣": ("運動習慣", ["週3回以上", "週1〜2回", "ほぼしない"]),
            "BMI区分": ("BMI区分", ["適正", "過体重", "肥満"]),
            "飲酒": ("飲酒", ["ほとんど飲まない", "適度", "多量"]),
            "社会的つながり": ("社会的つながり", ["豊富", "普通", "乏しい"]),
            "睡眠時間": ("睡眠時間", ["7〜8時間", "6時間未満", "9時間超"]),
            "慢性疾患": ("慢性疾患", ["なし", "あり"]),
            "性別": ("性別", ["女性", "男性"]),
        }
        selected_factor = st.selectbox("比較するリスク因子", list(factor_options.keys()))
        show_ci = st.checkbox("95%信頼区間を表示", value=True)

    col_name, groups = factor_options[selected_factor]
    groups = [g for g in groups if g in df[col_name].values]

    fig2 = go.Figure()
    colors = px.colors.qualitative.Set2
    kmf = KaplanMeierFitter()
    median_rows = []

    for i, grp in enumerate(groups):
        sub = df[df[col_name] == grp]
        if len(sub) < 5:
            continue
        kmf.fit(sub["健康期間（年）"], sub["健康終了"], label=grp)
        t = kmf.survival_function_.index
        s = kmf.survival_function_[grp].values
        ci_lo = kmf.confidence_interval_[f"{grp}_lower_0.95"].values
        ci_hi = kmf.confidence_interval_[f"{grp}_upper_0.95"].values
        color = colors[i % len(colors)]

        if show_ci:
            fig2.add_trace(go.Scatter(
                x=list(t) + list(t[::-1]),
                y=list(ci_hi) + list(ci_lo[::-1]),
                fill="toself",
                fillcolor=color.replace("rgb", "rgba").replace(")", ", 0.12)"),
                line=dict(width=0), showlegend=False, hoverinfo="skip",
            ))
        fig2.add_trace(go.Scatter(
            x=t, y=s, mode="lines", name=grp,
            line=dict(color=color, width=2.5, shape="hv"),
            hovertemplate=f"<b>{grp}</b><br>%{{x:.1f}}年<br>健康維持率: %{{y:.1%}}<extra></extra>",
        ))
        med = kmf.median_survival_time_
        med_age = f"{40 + int(med)}歳頃" if (not np.isnan(med) and not np.isinf(med)) else "40年超"
        median_rows.append({
            "グループ": grp, "中央健康期間（年）": round(med, 1) if (not np.isnan(med) and not np.isinf(med)) else "40年超",
            "推定健康限界年齢": med_age,
        })

    fig2.add_hline(y=0.5, line_dash="dash", line_color="red",
                   annotation_text="50%（半数が健康終了）", annotation_position="right")
    fig2.update_layout(
        title=f"「{selected_factor}」別 健康維持率の推移（40歳基準）",
        xaxis_title="40歳からの年数", yaxis_title="健康維持率",
        yaxis=dict(tickformat=".0%", range=[0, 1.05]),
        height=520, hovermode="x unified", plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig2.update_xaxes(showgrid=True, gridcolor="#eee",
                      tickvals=list(range(0, 41, 5)),
                      ticktext=[f"{40+v}歳\n(+{v}年)" for v in range(0, 41, 5)])
    fig2.update_yaxes(showgrid=True, gridcolor="#eee")
    st.plotly_chart(fig2, use_container_width=True)

    # ログランク検定
    if len(groups) == 2:
        g1 = df[df[col_name] == groups[0]]
        g2 = df[df[col_name] == groups[1]]
        lr = logrank_test(g1["健康期間（年）"], g2["健康期間（年）"], g1["健康終了"], g2["健康終了"])
        p = lr.p_value
        cls = "good-box" if p < 0.05 else "warning-box"
        sig = "**統計的に有意な差あり**（α=0.05）" if p < 0.05 else "統計的な有意差は検出されず"
        st.markdown(f'<div class="{cls}">🔬 <b>ログランク検定</b> p = {p:.4f} — {sig}</div>', unsafe_allow_html=True)
    elif len(groups) > 2:
        pairs = [(groups[i], groups[j]) for i in range(len(groups)) for j in range(i+1, len(groups))]
        results = []
        for a, b in pairs:
            ga = df[df[col_name] == a]; gb = df[df[col_name] == b]
            lr = logrank_test(ga["健康期間（年）"], gb["健康期間（年）"], ga["健康終了"], gb["健康終了"])
            results.append({"比較": f"{a} vs {b}", "p値": f"{lr.p_value:.4f}", "有意差": "✅" if lr.p_value < 0.05 else "❌"})
        st.markdown("**ペアワイズ ログランク検定（α=0.05）**")
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

    st.markdown("### ⏱️ グループ別 中央健康期間")
    st.dataframe(pd.DataFrame(median_rows), use_container_width=True, hide_index=True)
    st.markdown(
        '<div class="info-box">📌 <b>読み方：</b> 縦軸は「40歳時点で健康な人のうち、X年後もまだ健康な割合」。'
        '縦軸50%の位置での横軸の値が中央健康期間（半数が健康を終える年数）です。</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: コックス回帰分析
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
  if CURRENT_PLAN != "pro":
    locked_tab("コックス回帰分析（多変量）")
  else:
    st.markdown("## 🧬 コックス比例ハザードモデル")
    st.markdown("8大リスク因子を同時投入し、**他因子を調整した上での独立した影響**を定量化します。")

    summary = cph.summary.copy()
    label_map = {
        "喫煙あり":    "喫煙 🚬",
        "運動不足":    "運動不足 🛋️",
        "過体重以上":  "過体重/肥満 ⚖️",
        "多量飲酒":    "多量飲酒 🍺",
        "食事不良":    "食事の質（不良）🥗",
        "睡眠異常":    "睡眠異常 😴",
        "社会的孤立":  "社会的孤立 👤",
        "慢性疾患あり": "慢性疾患あり 🏥",
        "男性":        "男性 👨",
    }
    summary.index = [label_map.get(i, i) for i in summary.index]
    summary["HR"]    = np.exp(summary["coef"])
    summary["HR_lo"] = np.exp(summary["coef lower 95%"])
    summary["HR_hi"] = np.exp(summary["coef upper 95%"])

    # フォレストプロット
    fig3 = go.Figure()
    for var, row in summary.iterrows():
        hr, lo, hi, p = row["HR"], row["HR_lo"], row["HR_hi"], row["p"]
        color = "#e53e3e" if hr > 1 else "#38a169"
        fig3.add_trace(go.Scatter(
            x=[hr], y=[var], mode="markers",
            marker=dict(size=14, color=color,
                        symbol="circle" if p < 0.05 else "circle-open",
                        line=dict(width=2, color=color)),
            error_x=dict(type="data", symmetric=False,
                         array=[hi - hr], arrayminus=[hr - lo],
                         color=color, thickness=2),
            hovertemplate=(f"<b>{var}</b><br>"
                           f"HR = {hr:.3f}<br>95%CI [{lo:.3f} – {hi:.3f}]<br>"
                           f"p = {p:.4f}<extra></extra>"),
            showlegend=False,
        ))

    fig3.add_vline(x=1, line_dash="dash", line_color="#718096", line_width=1.5)
    fig3.add_vrect(x0=0.8, x1=1.0, fillcolor="#c6f6d5", opacity=0.2, line_width=0)
    fig3.add_vrect(x0=1.0, x1=3.0, fillcolor="#fed7d7", opacity=0.15, line_width=0)
    fig3.update_layout(
        title="ハザード比（HR）フォレストプロット — 多変量調整済み",
        xaxis_title="ハザード比（HR）— 右：健康終了リスク増加 / 左：保護的",
        xaxis=dict(type="log", range=[-0.3, 0.7]),
        height=480, showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
    )
    fig3.update_yaxes(showgrid=True, gridcolor="#eee")
    st.plotly_chart(fig3, use_container_width=True)

    # 結果テーブル
    disp = summary[["HR", "HR_lo", "HR_hi", "p"]].copy()
    disp.columns = ["HR", "95%CI 下限", "95%CI 上限", "p値"]
    disp["有意"] = disp["p値"].apply(
        lambda p: "★★★" if p < 0.001 else "★★" if p < 0.01 else "★" if p < 0.05 else "n.s.")
    disp["解釈"] = disp["HR"].apply(
        lambda h: f"リスク {(h-1)*100:+.0f}%"  if abs(h-1) > 0.01 else "影響なし")
    st.dataframe(
        disp.style.format({"HR": "{:.3f}", "95%CI 下限": "{:.3f}", "95%CI 上限": "{:.3f}", "p値": "{:.4f}"}),
        use_container_width=True)

    # CSV エクスポート
    csv_cox = io.StringIO()
    disp.to_csv(csv_cox, encoding="utf-8-sig")
    st.download_button(
        "📥 Cox回帰結果をCSVでダウンロード",
        data=csv_cox.getvalue().encode("utf-8-sig"),
        file_name="cox_regression_results.csv",
        mime="text/csv",
    )

    st.markdown(
        '<div class="info-box">📌 <b>見方：</b> '
        '● = p&lt;0.05（統計的有意）、○ = n.s.（非有意）。'
        'HR&gt;1（赤）は健康終了リスクを増加させる因子、HR&lt;1（緑）は保護的因子。'
        '95%信頼区間が HR=1 をまたがない場合に有意。'
        '</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: あなたの健康寿命予測
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
  if CURRENT_PLAN != "pro":
    locked_tab("あなたの個人健康寿命予測")
  else:
    st.markdown("## 🎯 あなたの健康寿命を予測する")
    st.markdown("現在の生活習慣・健康状態を入力して、コックス回帰モデルによる**個人化された生存曲線**を確認しましょう。")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**👤 基本情報**")
        pred_age  = st.slider("現在の年齢", 40, 80, 45)
        pred_sex  = st.radio("性別", ["女性", "男性"])
        pred_chr  = st.radio("慢性疾患（高血圧・糖尿病等）", ["なし", "あり"])
    with c2:
        st.markdown("**🏃 生活習慣**")
        pred_smk  = st.radio("喫煙", ["なし", "あり"])
        pred_ex   = st.radio("運動習慣", ["週3回以上", "週1〜2回", "ほぼしない"])
        pred_alc  = st.radio("飲酒", ["ほとんど飲まない", "適度", "多量"])
    with c3:
        st.markdown("**🧠 その他**")
        pred_bmi  = st.radio("BMI区分", ["適正", "低体重", "過体重", "肥満"])
        pred_diet = st.radio("食事の質", ["良好", "普通", "不良"])
        pred_slp  = st.radio("睡眠時間", ["7〜8時間", "6時間未満", "9時間超"])
        pred_soc  = st.radio("社会的つながり", ["豊富", "普通", "乏しい"])

    # ユーザープロフィール作成
    user_profile = pd.DataFrame([{
        "喫煙あり":    int(pred_smk == "あり"),
        "運動不足":    int(pred_ex == "ほぼしない"),
        "過体重以上":  int(pred_bmi in ["過体重", "肥満"]),
        "多量飲酒":    int(pred_alc == "多量"),
        "食事不良":    int(pred_diet == "不良"),
        "睡眠異常":    int(pred_slp != "7〜8時間"),
        "社会的孤立":  int(pred_soc == "乏しい"),
        "慢性疾患あり": int(pred_chr == "あり"),
        "男性":        int(pred_sex == "男性"),
    }])

    # 個人生存曲線の予測
    sf = cph.predict_survival_function(user_profile)
    times = sf.index.values
    surv  = sf.iloc[:, 0].values

    # 現在年齢からの条件付き確率
    current_years = max(pred_age - 40, 0)
    surv_now = float(np.interp(current_years, times, surv))

    def cond_prob(target_age):
        t = target_age - 40
        if t <= current_years or surv_now <= 0:
            return 1.0 if t <= current_years else 0.0
        return float(np.interp(t, times, surv)) / surv_now

    # 中央健康寿命の推定（生存率50%を下回る時点）
    below50 = np.where(surv <= 0.5)[0]
    if len(below50) > 0:
        median_healthy_years = float(times[below50[0]])
        median_healthy_age = 40 + median_healthy_years
    else:
        median_healthy_age = 80

    st.markdown("### 📊 あなたの予測結果")
    c1, c2, c3, c4 = st.columns(4)
    targets = [(65, c1), (70, c2), (75, c3), (80, c4)]
    for target, col in targets:
        p = cond_prob(target)
        with col:
            cls = "metric-card" if p >= 0.5 else "bad-card"
            vcls = "metric-value" if p >= 0.5 else "bad-value"
            st.markdown(
                f'<div class="{cls}">'
                f'<div class="{vcls}">{p:.0%}</div>'
                f'<div class="metric-label">{target}歳まで<br>健康でいられる確率</div>'
                f'</div>', unsafe_allow_html=True)

    # 予測中央健康年齢
    age_color = "#276749" if median_healthy_age >= 75 else "#744210" if median_healthy_age >= 65 else "#742a2a"
    st.markdown(
        f'<div style="text-align:center;margin:1rem 0;">'
        f'<span style="font-size:1rem;color:#555;">推定中央健康年齢（50%確率で健康を維持できる年齢）：</span><br>'
        f'<span style="font-size:2.8rem;font-weight:900;color:{age_color};">'
        f'約 {median_healthy_age:.0f} 歳</span>'
        f'</div>', unsafe_allow_html=True)

    # 生存曲線プロット
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=times + 40, y=surv,
        mode="lines", name="あなたの生存曲線",
        line=dict(color="#38a169", width=3, shape="hv"),
        fill="tozeroy", fillcolor="rgba(56,161,105,0.1)",
        hovertemplate="<b>%{x:.0f}歳</b><br>健康維持率: %{y:.1%}<extra></extra>",
    ))

    # 現在地マーカー
    surv_now_plot = float(np.interp(current_years, times, surv))
    fig4.add_trace(go.Scatter(
        x=[pred_age], y=[surv_now_plot], mode="markers+text",
        marker=dict(size=16, color="#e53e3e", symbol="star"),
        text=[f"  ← 現在（{pred_age}歳）"],
        textposition="middle right", textfont=dict(size=12, color="#e53e3e"), name="現在地",
    ))

    # 日本平均の参照線
    avg_healthy = JAPAN_STATS["women_healthy"] if pred_sex == "女性" else JAPAN_STATS["men_healthy"]
    fig4.add_vline(x=avg_healthy, line_dash="dot", line_color="#805ad5", line_width=2,
                   annotation_text=f"日本人{pred_sex}平均\n健康寿命 {avg_healthy}歳",
                   annotation_position="top left", annotation_font_color="#805ad5")
    fig4.add_hline(y=0.5, line_dash="dash", line_color="#e53e3e",
                   annotation_text="50%", annotation_position="right")

    fig4.update_layout(
        title="あなたの健康維持率の予測（コックス回帰モデル）",
        xaxis_title="年齢", yaxis_title="健康維持率",
        yaxis=dict(tickformat=".0%", range=[0, 1.05]),
        xaxis=dict(range=[40, 90]),
        height=450, plot_bgcolor="white", paper_bgcolor="white",
    )
    fig4.update_xaxes(showgrid=True, gridcolor="#eee")
    fig4.update_yaxes(showgrid=True, gridcolor="#eee")
    st.plotly_chart(fig4, use_container_width=True)

    # リスク診断と改善アドバイス
    risk_factors_present = []
    if pred_smk == "あり":        risk_factors_present.append(("🚬", "喫煙", "禁煙で健康寿命3〜5年延長の可能性"))
    if pred_ex == "ほぼしない":   risk_factors_present.append(("🏃", "運動不足", "週150分の中強度運動で2〜4年延長"))
    if pred_bmi in ["過体重", "肥満"]: risk_factors_present.append(("⚖️", "過体重/肥満", "5〜10%の体重減少でリスク大幅低下"))
    if pred_alc == "多量":        risk_factors_present.append(("🍺", "多量飲酒", "適度な飲酒に変えることでリスク低減"))
    if pred_soc == "乏しい":      risk_factors_present.append(("👥", "社会的孤立", "地域活動・友人との交流でリスク低減"))
    if pred_slp != "7〜8時間":    risk_factors_present.append(("😴", "睡眠異常", "7〜8時間の睡眠確保が目標"))
    if pred_diet == "不良":       risk_factors_present.append(("🥗", "食事不良", "野菜・魚・発酵食品の摂取増加"))
    if pred_chr == "あり":        risk_factors_present.append(("🏥", "慢性疾患", "薬物療法・生活習慣改善で進行を抑制"))

    if risk_factors_present:
        risk_score = len(risk_factors_present)
        level = "高リスク 🔴" if risk_score >= 4 else "中リスク 🟡" if risk_score >= 2 else "低リスク 🟢"
        st.markdown(f"### 🩺 リスク因子診断：**{level}**（{risk_score}項目該当）")
        for icon, factor, advice in risk_factors_present:
            st.markdown(f"- {icon} **{factor}** — {advice}")
    else:
        st.markdown(
            '<div class="good-box">✅ <b>すべての因子が最適です！</b> '
            '現在の生活習慣を維持することで、長く健康でいられる可能性が高いです。</div>',
            unsafe_allow_html=True)

    st.markdown(
        '<div class="info-box">📄 <b>予測の仕組み：</b> '
        'コックス比例ハザードモデルであなたのリスクプロフィールを評価し、個人化された生存関数を推定しています。'
        '疫学的ハザード比（論文値ベース）で生成したシミュレーションデータで学習しています。'
        '</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: 解析手法の詳細
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
  if CURRENT_PLAN != "pro":
    locked_tab("解析手法の数理的詳細")
  else:
    st.markdown("## 🔬 解析手法の詳細")
    st.markdown("本アプリで使用している統計解析手法の数理的背景と実装方法を解説します。")

    # ─── 1. 生存分析とは ───────────────────────────────────────────────────
    with st.expander("📖 1. 生存分析（Survival Analysis）とは", expanded=True):
        st.markdown(
            '<div class="method-box">'
            '<b>生存分析</b>とは、「ある事象が発生するまでの時間」を統計的に分析する手法です。'
            '医学では死亡・疾患発症・健康終了までの時間を扱います。'
            '</div>', unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**🎯 分析の目的**")
            st.markdown("""
- 集団の生存率・健康維持率の推定
- リスク因子の同定と効果量の定量化
- 個人レベルでの予後予測
- 介入効果の評価（臨床試験）
            """)
        with col_b:
            st.markdown("**📌 重要な概念**")
            st.markdown("""
- **イベント (Event)**: 分析対象の事象（本アプリ: 健康終了）
- **継続時間 (Duration)**: イベント発生までの時間
- **打ち切り (Censoring)**: フォローアップ終了時点でイベント未発生
- **生存関数 S(t)**: 時刻 t までイベントが発生しない確率
- **ハザード関数 h(t)**: 時刻 t における瞬間的なイベント発生率
            """)
        st.markdown("**⚠️ なぜ通常の回帰分析ではダメなのか？**")
        st.markdown(
            '<div class="warning-box">'
            '打ち切りデータ（フォローアップ中にまだイベントが起きていない人）を無視すると推定が偏ります。'
            '生存分析は打ち切りを正しく扱うことで不偏な推定を実現します。'
            '</div>', unsafe_allow_html=True)
        st.markdown("**生存関数とハザード関数の関係**")
        st.latex(r"S(t) = P(T > t) = \exp\!\left(-\int_0^t h(u)\,du\right)")
        st.markdown("累積ハザード関数 $H(t) = -\ln S(t)$ を用いて相互変換できます。")

    # ─── 2. カプランマイヤー法 ────────────────────────────────────────────────
    with st.expander("📈 2. カプランマイヤー法（Kaplan-Meier Estimator）"):
        st.markdown(
            '<div class="method-box">'
            'カプランマイヤー法（1958）は生存関数の<b>ノンパラメトリック推定量</b>です。'
            'モデルの仮定なしに、観測データだけから生存曲線を推定できます。'
            '</div>', unsafe_allow_html=True)

        st.markdown("**数式**")
        st.latex(r"\hat{S}(t) = \prod_{t_i \le t} \left(1 - \frac{d_i}{n_i}\right)")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown("""
| 記号 | 意味 |
|------|------|
| $t_i$ | イベント発生時刻 |
| $d_i$ | 時刻 $t_i$ でのイベント数 |
| $n_i$ | 時刻 $t_i$ 直前のリスク集合数 |
            """)
        with col_f2:
            st.markdown("""
**例: 6人のコホート**

| 時刻 | イベント | リスク集合 | $1-d/n$ | $\hat{S}$ |
|------|--------|--------|---------|-------|
| 2年  | 1      | 6      | 5/6     | 0.833 |
| 5年  | 1      | 5      | 4/5     | 0.667 |
| 8年  | 1      | 3      | 2/3     | 0.444 |
            """)

        st.markdown("**95%信頼区間（グリーンウッド公式）**")
        st.latex(r"\widehat{\text{Var}}[\hat{S}(t)] = \hat{S}(t)^2 \sum_{t_i \le t} \frac{d_i}{n_i(n_i - d_i)}")
        st.markdown("""
**特徴と注意点**
- ✅ パラメトリックモデルの仮定不要（柔軟）
- ✅ 打ち切りデータを正しく処理
- ✅ 直感的で解釈しやすい階段状グラフ
- ⚠️ 複数の共変量（リスク因子）の同時調整には不向き → Cox回帰が必要
- ⚠️ フォローアップ後半で信頼区間が広くなる（少数からの推定）
        """)

    # ─── 3. ログランク検定 ────────────────────────────────────────────────────
    with st.expander("🔬 3. ログランク検定（Log-rank Test）"):
        st.markdown(
            '<div class="method-box">'
            'ログランク検定（Mantel 1966）は2群以上の生存曲線を比較し、'
            '統計的に有意な差があるかを検定するノンパラメトリック検定です。'
            '</div>', unsafe_allow_html=True)

        st.markdown("**帰無仮説と検定統計量**")
        st.latex(r"H_0: S_1(t) = S_2(t) \quad \forall t")
        st.latex(r"\chi^2 = \frac{\left(\sum_j (O_j - E_j)\right)^2}{\mathrm{Var}\left(\sum_j (O_j - E_j)\right)}")
        st.markdown("""
| 記号 | 意味 |
|------|------|
| $O_j$ | 各時点 $t_j$ での群1の観測イベント数 |
| $E_j$ | $H_0$ 下での群1の期待イベント数 $= n_{1j} \cdot d_j / n_j$ |
| $d_j$ | 全体のイベント数、$n_j$ = 全リスク集合数 |
        """)
        st.latex(r"E_j = \frac{n_{1j}}{n_j} \cdot d_j")
        st.markdown("""
検定統計量は自由度 $k-1$（$k$: 群数）のカイ二乗分布に従います。

**p値の解釈**
- $p < 0.05$: 2群間に統計的有意な生存差あり（有意水準5%）
- $p \ge 0.05$: 有意差検出されず（差がないことの証明ではない）

**注意**: ログランク検定は比例ハザード仮定の下で最も検出力が高いです。交差する生存曲線には不向きで、その場合は Wilcoxon 検定等を検討します。
        """)

    # ─── 4. コックス比例ハザード回帰 ────────────────────────────────────────────
    with st.expander("🧬 4. コックス比例ハザード回帰（Cox Proportional Hazards Regression）"):
        st.markdown(
            '<div class="method-box">'
            'コックス回帰（Cox 1972）は複数のリスク因子を同時に調整しながら、'
            '各因子の独立した影響を定量化できる<b>セミパラメトリックモデル</b>です。'
            '</div>', unsafe_allow_html=True)

        st.markdown("**モデル式**")
        st.latex(r"h(t \mid \mathbf{X}) = h_0(t) \cdot \exp(\beta_1 X_1 + \beta_2 X_2 + \cdots + \beta_p X_p)")
        col_cx1, col_cx2 = st.columns(2)
        with col_cx1:
            st.markdown("""
| 記号 | 意味 |
|------|------|
| $h_0(t)$ | ベースラインハザード（未特定化） |
| $X_1, \ldots, X_p$ | 共変量（リスク因子） |
| $\beta_1, \ldots, \beta_p$ | 回帰係数 |
            """)
        with col_cx2:
            st.markdown("""
**セミパラメトリックの意味**
- $h_0(t)$: ノンパラメトリック（形を仮定しない）
- $\exp(\boldsymbol{\beta}^\top \mathbf{X})$: パラメトリック

これにより柔軟性と解釈可能性を両立しています。
            """)

        st.markdown("**ハザード比（Hazard Ratio, HR）の解釈**")
        st.latex(r"\text{HR} = \frac{h(t \mid X_j = 1)}{h(t \mid X_j = 0)} = e^{\beta_j}")
        st.markdown("""
| HR | 解釈 |
|----|------|
| HR = 1.5 | その因子を持つ人は持たない人より健康終了リスクが **50% 高い** |
| HR = 0.7 | その因子を持つ人は持たない人より健康終了リスクが **30% 低い** |
| HR = 1.0 | 影響なし |
        """)

        st.markdown("**比例ハザード仮定（Proportional Hazards Assumption）**")
        st.latex(r"\frac{h(t \mid X_j = 1)}{h(t \mid X_j = 0)} = e^{\beta_j} = \text{const.} \quad \forall t")
        st.markdown(
            '<div class="warning-box">⚠️ <b>重要な仮定：</b> '
            'ハザード比が時間に依存しないことを仮定します。'
            'Schoenfeld残差プロット等で確認が必要です。仮定が成立しない場合は時間依存Cox回帰を使用します。'
            '</div>', unsafe_allow_html=True)

        st.markdown("**パーシャル尤度による推定**")
        st.latex(
            r"\mathcal{L}(\boldsymbol{\beta}) = \prod_{i:\,\delta_i=1} "
            r"\frac{\exp(\boldsymbol{\beta}^\top \mathbf{X}_i)}{\sum_{j \in \mathcal{R}(t_i)} \exp(\boldsymbol{\beta}^\top \mathbf{X}_j)}"
        )
        st.markdown("$\mathcal{R}(t_i)$: 時刻 $t_i$ でのリスク集合。$h_0(t)$ を消去できるのがこの手法の優れた点です。")
        st.markdown("""
**本アプリでの設定**
- ペナライザー（L2正則化）: 0.1 — 過学習防止、不安定な推定の抑制
- ライブラリ: `lifelines.CoxPHFitter`（Python）
        """)

    # ─── 5. 個人予測（条件付き生存確率） ─────────────────────────────────────
    with st.expander("🎯 5. 個人予測 — 条件付き生存確率"):
        st.markdown(
            '<div class="method-box">'
            '予測タブでは、コックス回帰モデルの推定結果から個人の生存関数を計算し、'
            '現在年齢を条件とした<b>条件付き生存確率</b>を算出しています。'
            '</div>', unsafe_allow_html=True)

        st.markdown("**個人化された生存関数**")
        st.latex(r"\hat{S}(t \mid \mathbf{X}) = \hat{S}_0(t)^{\exp(\hat{\boldsymbol{\beta}}^\top \mathbf{X})}")
        st.markdown("$\hat{S}_0(t)$: Breslow推定によるベースライン生存関数")

        st.markdown("**条件付き生存確率**")
        st.latex(
            r"P(T > t \mid T > t_{\text{now}}, \mathbf{X}) = "
            r"\frac{\hat{S}(t \mid \mathbf{X})}{\hat{S}(t_{\text{now}} \mid \mathbf{X})}"
        )
        st.markdown("""
| 記号 | 意味 |
|------|------|
| $t_{\text{now}}$ | 現在年齢 − 40歳（40歳基準からの年数） |
| $t$ | 目標年齢 − 40歳 |
        """)
        st.markdown(
            '<div class="warning-box">⚠️ <b>予測の不確実性：</b> '
            '個人レベルの予測には95%信頼区間が非常に広くなります。'
            '提示される確率は点推定値であり、個人の将来を確定的に予測するものではありません。'
            '</div>', unsafe_allow_html=True)

    # ─── 6. デモデータの生成方法 ──────────────────────────────────────────────
    with st.expander("🎲 6. シミュレーションデータの生成方法（Weibull分布）"):
        st.markdown(
            '<div class="method-box">'
            '本アプリのデモデータは、論文のハザード比に基づいたWeibull分布シミュレーションで生成しています。'
            'n=800名の仮想コホート研究です。'
            '</div>', unsafe_allow_html=True)

        st.markdown("**Weibull分布による生存時間の生成**")
        st.latex(r"T \sim \text{Weibull}(\lambda_i,\, k) \quad \Rightarrow \quad f(t) = \frac{k}{\lambda_i}\left(\frac{t}{\lambda_i}\right)^{k-1} e^{-(t/\lambda_i)^k}")
        st.markdown("**個人スケールパラメータ（ハザード比の適用）**")
        st.latex(r"\lambda_i = \frac{\lambda_0}{HR_i^{1/k}}")

        st.markdown("""
| パラメータ | 値 | 意味 |
|------------|----|----|
| $\lambda_0$ | 35年 | 理想プロフィールの特性スケール（中央値 ≈ 29年 = 69歳） |
| $k$ | 2.0 | 形状パラメータ（加齢とともにリスク増加） |
| $HR_i$ | 個人別 | 各リスク因子のHR積（論文値ベース） |
        """)
        st.markdown("""
**打ち切りの実装**
1. **管理的打ち切り**: 40年（80歳）でフォローアップ終了
2. **途中脱落**: 15%の参加者が無作為な時点で脱落（U(8, 40)年）

**使用リスク因子のHR設定**
        """)
        hr_table = pd.DataFrame({
            "因子": ["喫煙", "運動不足（ほぼしない）", "肥満", "過体重", "多量飲酒",
                     "食事不良", "睡眠異常（6h未満）", "睡眠異常（9h超）",
                     "社会的孤立", "慢性疾患", "男性"],
            "HR設定値": [1.80, 1.40, 1.50, 1.20, 1.40, 1.20, 1.30, 1.20, 1.60, 2.00, 1.15],
            "文献値範囲": ["1.5〜2.0", "1.3〜1.5", "1.2〜1.5", "1.1〜1.3", "1.3〜1.4",
                           "1.2〜1.3", "1.3〜1.4", "1.1〜1.3", "1.5〜1.8", "1.5〜2.5", "1.1〜1.2"],
        })
        st.dataframe(hr_table, use_container_width=True, hide_index=True)

    # ─── 7. 本アプリの限界と注意事項 ──────────────────────────────────────────
    with st.expander("⚠️ 7. 本アプリの限界と注意事項"):
        st.markdown("""
**統計モデルの限界**
1. **比例ハザード仮定**: コックス回帰はリスク因子の効果が時間に依存しないと仮定します。実際には年齢とともに効果が変化する可能性があります。
2. **未観測交絡因子**: シミュレーションデータには遺伝的要因・SES（社会経済的地位）・環境要因等が含まれていません。
3. **因果推論の限界**: 観察研究のデータに基づくため、関連性を示すものであり因果関係を証明するものではありません。
4. **個人レベル予測の不確実性**: 集団レベルのモデルを個人に適用すると予測精度が低下します。

**データの限界**
1. **シミュレーションデータ**: 実際の患者データではなく、論文のパラメータで生成した仮想データです。
2. **日本人特有の要因**: 本アプリは一般的なエビデンスに基づいており、民族・地域差は十分に考慮されていません。
3. **経時変化**: リスク因子が追跡中に変化することは考慮していません（固定共変量モデル）。

**推奨事項**
- 本アプリの結果を医療診断・治療方針の決定に用いないでください。
- 健康上の懸念がある場合は、医療機関を受診してください。
- 生活習慣の改善については、医師・管理栄養士・健康運動指導士にご相談ください。
        """)
        st.markdown(
            '<div class="info-box">📚 <b>より詳しく学びたい方へ：</b><br>'
            'Kleinbaum DG, Klein M. <i>Survival Analysis: A Self-Learning Text</i>. 3rd ed. Springer, 2012.<br>'
            'Harrell FE. <i>Regression Modeling Strategies</i>. 2nd ed. Springer, 2015.<br>'
            '浜田知久馬. 生存時間解析. 朝倉書店, 2009.'
            '</div>', unsafe_allow_html=True)

# ─── フッター ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#aaa;font-size:0.8rem;'>"
    "🩺 健康寿命サバイバー v2.0 | KM法・ログランク検定・Cox比例ハザード回帰 | "
    "Data: 厚生労働省(2019) · WHO · JPHC Study · Weibull Simulation (n=800)"
    "</div>", unsafe_allow_html=True)
