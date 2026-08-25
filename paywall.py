"""
paywall.py

簡易「授權碼」付費驗證模組
========================

目前先用最簡單的方式做付費控管：
    使用者付款（目前為人工方式：轉帳 / LINE Pay / 其他）
        -> 你手動提供一組「本月授權碼」給付款的人
        -> 使用者在網站輸入授權碼即可解鎖使用
        -> 解鎖狀態只存在「這次瀏覽器 session」，不記錄使用者身分

授權碼清單放在 Streamlit 的 st.secrets 裡（不會進版控、不會被看到），
設定方式請見同目錄下的 `.streamlit/secrets.toml.example`。

授權碼支援兩種格式：
    1) "ANYCODE"              -> 只要清單裡有這組字串，永久有效
    2) "ANYCODE:2026-08"      -> 只在 2026-08 這個月有效，過月即失效
                                   （適合「每月 99」的訂閱情境，
                                    你只要每個月把新的碼加進清單就好）

之後要接 Stripe / 綠界等真金流時，
只需要把 `require_access()` 內「輸入授權碼」這段，
換成「金流付款成功後自動核發 code / 寫入 st.session_state」即可，
其他頁面的呼叫方式完全不用改。
"""

from datetime import datetime
from pathlib import Path

import streamlit as st


DEFAULT_PRICE_LABEL = "NT$99 / 月"

# 授權碼檔案：放在專案根目錄，不放在 .streamlit 資料夾裡
# 一行一組授權碼，# 開頭的行當作註解忽略
CODES_FILE = Path(__file__).parent / "access_codes.txt"


# ============================================================
# 讀取合法授權碼清單
#
# 優先順序：
#   1) Streamlit Cloud 後台的 Secrets（部署到雲端時建議用這個，
#      在網站 Settings -> Secrets 貼上即可，不需要任何檔案）
#   2) 專案根目錄的 access_codes.txt（本機測試方便用，
#      這個檔案已加進 .gitignore，不會被上傳到 GitHub）
# ============================================================

def _get_valid_codes():

    codes = []

    # 1) Streamlit Cloud 後台 Secrets（若有設定就優先採用）
    try:
        raw = st.secrets.get("ACCESS_CODES", None)
    except Exception:
        raw = None

    if raw:
        if isinstance(raw, str):
            codes = [c.strip() for c in raw.split(",") if c.strip()]
        else:
            codes = [str(c).strip() for c in raw if str(c).strip()]

        return codes

    # 2) 根目錄 access_codes.txt（本機測試用，不放在 .streamlit 裡）
    if CODES_FILE.exists():

        for line in CODES_FILE.read_text(encoding="utf-8").splitlines():

            line = line.strip()

            if not line or line.startswith("#"):
                continue

            codes.append(line)

    return codes


# ============================================================
# 驗證授權碼
# ============================================================

def _code_is_valid(user_code, valid_codes):

    user_code = (user_code or "").strip()

    if not user_code:
        return False

    current_month = datetime.now().strftime("%Y-%m")

    for raw_code in valid_codes:

        raw_code = raw_code.strip()

        if ":" in raw_code:

            base, expiry_month = raw_code.split(":", 1)

            base = base.strip()
            expiry_month = expiry_month.strip()

            if user_code == base and current_month == expiry_month:
                return True

        else:

            if user_code == raw_code:
                return True

    return False


# ============================================================
# 付費牆主要函式
# 回傳 True  -> 已解鎖，可以繼續顯示主要功能
# 回傳 False -> 尚未解鎖，呼叫端應該 st.stop()
# ============================================================

def require_access(price_label=DEFAULT_PRICE_LABEL):

    if st.session_state.get("paywall_unlocked", False):
        return True

    st.markdown(
        """
        <div style="text-align:center; padding: 32px 0 8px 0;">
            <div style="font-size:36px; font-weight:800;">
                🎵 JianpuTool Professional
            </div>
            <div style="font-size:17px; color:#777; margin-top:6px;">
                MP3 / WAV → 主旋律 MIDI → 數字簡譜 PDF
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown(
            f"""
            <div style="text-align:center; padding: 24px; border-radius:16px;
                        border:1px solid rgba(128,128,128,0.25);
                        margin-bottom:20px;">
                <div style="font-size:20px; font-weight:700;">
                    🔓 訂閱制存取
                </div>
                <div style="font-size:34px; font-weight:800; margin:10px 0;">
                    {price_label}
                </div>
                <div style="color:#777;">
                    付款後將提供本月專屬授權碼
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 💳 如何取得授權碼？")

        st.markdown(
            f"""
            1. 完成每月 **{price_label}** 付款
               （目前為人工收款：轉帳 / LINE Pay / 其他，
               之後可升級為 Stripe 或綠界自動收款）
            2. 我們會提供**本月專屬授權碼**給你
            3. 在下方輸入授權碼即可解鎖使用
            """
        )

        st.divider()

        with st.form("paywall_form"):

            code_input = st.text_input(
                "🔑 請輸入授權碼",
                type="password",
                placeholder="例如：JIANPU-2026-08",
            )

            submitted = st.form_submit_button(
                "✅ 解鎖使用",
                use_container_width=True,
                type="primary",
            )

        if submitted:

            valid_codes = _get_valid_codes()

            if not valid_codes:

                st.error(
                    "⚠️ 系統尚未設定授權碼，"
                    "請聯絡管理員完成設定。"
                )

            elif _code_is_valid(code_input, valid_codes):

                st.session_state["paywall_unlocked"] = True

                st.success("🎉 解鎖成功，正在進入工具...")

                st.rerun()

            else:

                st.error(
                    "❌ 授權碼錯誤或已過期，"
                    "請確認付款狀態或聯絡管理員取得本月授權碼。"
                )

        st.caption(
            "如需付款方式、發票或授權碼，請聯絡管理員。"
        )

    return False


# ============================================================
# 側邊欄：顯示訂閱狀態 + 登出（方便測試 / 換人使用同一台電腦）
# ============================================================

def render_sidebar_status():

    if not st.session_state.get("paywall_unlocked", False):
        return

    with st.sidebar:

        st.divider()

        st.success("✅ 已解鎖本月使用權限")

        if st.button(
            "🔒 鎖定（登出）",
            use_container_width=True,
        ):

            st.session_state["paywall_unlocked"] = False

            st.rerun()
