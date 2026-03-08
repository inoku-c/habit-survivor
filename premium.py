"""
premium.py - 習慣サバイバー フリーミアム認証モジュール

【使い方】
1. このファイルをapp.pyと同じディレクトリに置く
2. app.pyの先頭でインポート: from premium import check_premium, show_upgrade_banner, show_sidebar_auth
3. Railway環境変数に PREMIUM_CODE_HASH を設定（下記スクリプトで生成）
"""

import hashlib
import os
import streamlit as st

# ─────────────────────────────────────────────
# 環境変数から取得（Railwayダッシュボードで設定）
# 例: PREMIUM_CODE_HASH = sha256("your-secret-code")
# ─────────────────────────────────────────────
PREMIUM_CODE_HASH = os.environ.get("PREMIUM_CODE_HASH", "")

# Stripe Payment Link（後で差し替え）
STRIPE_PAYMENT_URL = os.environ.get("STRIPE_PAYMENT_URL", "https://buy.stripe.com/XXXXXXXX")

# 価格表示
PREMIUM_PRICE = os.environ.get("PREMIUM_PRICE", "¥500/月")


def _hash(code: str) -> str:
    return hashlib.sha256(code.strip().encode()).hexdigest()


def check_premium() -> bool:
    """セッション内のアクセスコードを検証してpremiumかどうか返す"""
    if not PREMIUM_CODE_HASH:
        # 環境変数未設定の場合は開発モード（全機能開放）
        return True
    code = st.session_state.get("access_code", "")
    return bool(code) and _hash(code) == PREMIUM_CODE_HASH


def show_sidebar_auth():
    """サイドバーにプレミアム認証UIを表示"""
    st.sidebar.markdown("---")
    is_premium = check_premium()

    if is_premium:
        st.sidebar.success("👑 プレミアムプラン有効")
    else:
        st.sidebar.markdown("### 🔑 プレミアムアクセス")
        code = st.sidebar.text_input(
            "アクセスコード",
            type="password",
            placeholder="購入後に届くコードを入力",
            key="access_code_input",
        )
        if code:
            st.session_state["access_code"] = code
            if _hash(code) == PREMIUM_CODE_HASH:
                st.sidebar.success("✅ 認証成功！プレミアム機能が解放されました")
            else:
                st.sidebar.error("❌ コードが正しくありません")
        else:
            st.session_state["access_code"] = ""

        st.sidebar.markdown(f"""
        <div style="background:#1a1a2e;padding:12px;border-radius:8px;margin-top:8px;border:1px solid #4a4a8a;">
            <div style="font-size:0.85rem;color:#aaa;margin-bottom:8px;">🆓 無料プラン</div>
            <div style="font-size:0.8rem;color:#ccc;">✅ 論文エビデンス閲覧<br>✅ デモデータKM曲線<br>✅ 基本生存予測</div>
            <div style="font-size:0.85rem;color:#aaa;margin:10px 0 6px;">👑 プレミアム {{PREMIUM_PRICE}}</div>
            <div style="font-size:0.8rem;color:#ccc;">✅ 自分のデータで分析<br>✅ 習慣比較・ログランク検定<br>✅ Cox回帰フォレストプロット<br>✅ リスク診断＋改善アドバイス</div>
        </div>
        """, unsafe_allow_html=True)

        st.sidebar.markdown(
            f'<a href="{{STRIPE_PAYMENT_URL}}" target="_blank">'
            f'<button style="width:100%;margin-top:10px;padding:10px;background:#635bff;'
            f'color:white;border:none;border-radius:6px;cursor:pointer;font-size:0.95rem;">'
            f'🚀 プレミアムにアップグレード</button></a>',
            unsafe_allow_html=True,
        )


def show_upgrade_banner(feature_name: str):
    """プレミアム機能のロックバナーを表示"""
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);
         padding:24px;border-radius:12px;text-align:center;
         border:1px solid #4a4a8a;margin:16px 0;">
        <div style="font-size:2rem;margin-bottom:8px;">🔒</div>
        <div style="font-size:1.1rem;font-weight:700;color:#e0e0ff;margin-bottom:6px;">
            {{feature_name}} はプレミアム機能です
        </div>
        <div style="font-size:0.85rem;color:#aaa;margin-bottom:16px;">
            アクセスコードを取得してサイドバーに入力すると解放されます
        </div>
        <a href="{{STRIPE_PAYMENT_URL}}" target="_blank"
           style="background:#635bff;color:white;padding:10px 24px;
                  border-radius:6px;text-decoration:none;font-weight:600;">
            👑 プレミアムにアップグレード ({{PREMIUM_PRICE}})
        </a>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# アクセスコード生成スクリプト（ローカルで実行）
# python -c "import hashlib; print(hashlib.sha256('あなたのコード'.encode()).hexdigest())"
# ─────────────────────────────────────────────
