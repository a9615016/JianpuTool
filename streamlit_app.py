import os
import time
import zipfile
import tempfile
from pathlib import Path

import requests
import streamlit as st


# ============================================================
# 頁面設定
# ============================================================

st.set_page_config(
    page_title="JianpuTool Professional",
    page_icon="🎵",
    layout="centered",
)


# ============================================================
# 載入環境變數
# ============================================================

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


# ============================================================
# FastAPI 後端網址
#
# 本機：
# http://127.0.0.1:8000
#
# Cloudflare：
# https://xxxx.trycloudflare.com
# ============================================================

FASTAPI_BASE_URL = os.getenv(
    "FASTAPI_BASE_URL",
    "https://instructors-donations-prefix-lock.trycloudflare.com",
).strip().rstrip("/")


# ============================================================
# ACCESS_CODE
#
# 對應 main.py 的：
#
# X-Access-Code
# ============================================================

ACCESS_CODE = os.getenv(
    "ACCESS_CODE",
    "",
).strip()


# ============================================================
# Session State
# ============================================================

defaults = {
    "logged_in": False,
    "email": "",
    "session_token": "",
    "code_sent": False,
    "code_email": "",
    "last_code_time": 0.0,
    "payment_url": "",
    "trade_no": "",
    "payment_started": False,
    "member_info": None,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 工具函式
# ============================================================

def api_url(path: str) -> str:

    return (
        FASTAPI_BASE_URL
        + "/"
        + path.lstrip("/")
    )


def api_error_message(response):

    try:
        data = response.json()

        if isinstance(data, dict):

            if "detail" in data:
                return str(data["detail"])

            if "message" in data:
                return str(data["message"])

    except Exception:
        pass

    return response.text or f"HTTP {response.status_code}"


def clear_login():

    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.session_token = ""
    st.session_state.code_sent = False
    st.session_state.code_email = ""
    st.session_state.last_code_time = 0.0
    st.session_state.member_info = None
    st.session_state.payment_url = ""
    st.session_state.trade_no = ""
    st.session_state.payment_started = False


def get_member():

    email = st.session_state.email
    token = st.session_state.session_token

    if not email or not token:
        return None

    try:

        response = requests.get(
            api_url("/api/member"),
            params={
                "email": email,
            },
            headers={
                "X-Session-Token": token,
            },
            timeout=20,
        )

        if response.status_code == 200:

            return response.json()

        return None

    except Exception:

        return None


def is_member_active(member):

    if not member:
        return False

    # 支援目前 membership.py / database.py
    # 可能使用的欄位名稱

    if member.get("active") is True:
        return True

    if member.get("is_active") is True:
        return True

    if member.get("member_active") is True:
        return True

    status = str(
        member.get("status", "")
    ).upper()

    if status in (
        "ACTIVE",
        "PAID",
        "MEMBER",
    ):
        return True

    return False


# ============================================================
# 後端健康檢查
# ============================================================

def check_backend():

    try:

        response = requests.get(
            api_url("/api/health"),
            timeout=10,
        )

        return response

    except Exception as e:

        return e


# ============================================================
# 頁首
# ============================================================

st.title("🎵 JianpuTool Professional")

st.caption(
    "MP3 / WAV → MIDI → 數字簡譜 PDF"
)


# ============================================================
# 側邊欄
# ============================================================

with st.sidebar:

    st.subheader("⚙️ 系統設定")

    st.write(
        "後端 API："
    )

    st.code(
        FASTAPI_BASE_URL
    )

    st.divider()

    if st.button(
        "🔍 測試後端",
        use_container_width=True,
    ):

        result = check_backend()

        if isinstance(result, Exception):

            st.error(
                f"後端無法連線：{result}"
            )

        elif result.status_code == 200:

            st.success(
                "✅ FastAPI 後端正常"
            )

            try:
                st.json(result.json())
            except Exception:
                pass

        else:

            st.error(
                f"後端 HTTP {result.status_code}"
            )


# ============================================================
# 尚未登入
# ============================================================

if not st.session_state.logged_in:

    st.subheader("👤 會員登入")

    st.write(
        "使用 Email 驗證碼登入，不需要設定網站密碼。"
    )

    st.info(
        "登入後即可查看會員狀態並進行 NT$99 / 30天訂閱。"
    )

    # --------------------------------------------------------
    # Email
    # --------------------------------------------------------

    email = st.text_input(
        "📧 Email",
        value=st.session_state.code_email,
        placeholder="請輸入您的 Email",
    ).strip().lower()

    # --------------------------------------------------------
    # 取得驗證碼
    # --------------------------------------------------------

    if st.button(
        "📧 取得驗證碼",
        use_container_width=True,
    ):

        if not email:

            st.error(
                "❌ 請輸入 Email"
            )

        elif "@" not in email:

            st.error(
                "❌ Email 格式不正確"
            )

        else:

            try:

                response = requests.post(
                    api_url(
                        "/api/auth/request-code"
                    ),
                    json={
                        "email": email,
                    },
                    timeout=30,
                )

                if response.status_code == 200:

                    st.session_state.code_sent = True
                    st.session_state.code_email = email
                    st.session_state.last_code_time = time.time()

                    st.success(
                        f"✅ 驗證碼已寄到 {email}"
                    )

                    st.info(
                        "請查看 Gmail，輸入收到的 6 位驗證碼。"
                    )

                else:

                    st.error(
                        f"❌ API 錯誤 "
                        f"({response.status_code})"
                    )

                    st.code(
                        api_error_message(response)
                    )

            except requests.exceptions.RequestException as e:

                st.error(
                    "❌ 無法連線後端 API"
                )

                st.code(
                    str(e)
                )

    # --------------------------------------------------------
    # 驗證碼
    # --------------------------------------------------------

    if st.session_state.code_sent:

        st.divider()

        st.subheader(
            "🔐 Email 驗證"
        )

        code = st.text_input(
            "6 位驗證碼",
            max_chars=6,
            placeholder="請輸入 Gmail 收到的 6 位數字",
        ).strip()

        # ----------------------------------------------------
        # 有效時間
        # ----------------------------------------------------

        elapsed = (
            time.time()
            - st.session_state.last_code_time
        )

        remaining = max(
            0,
            600 - int(elapsed),
        )

        minutes = remaining // 60
        seconds = remaining % 60

        st.caption(
            f"驗證碼有效時間："
            f"{minutes} 分 {seconds:02d} 秒"
        )

        # ----------------------------------------------------
        # 登入
        # ----------------------------------------------------

        if st.button(
            "🔓 登入",
            use_container_width=True,
        ):

            if not code:

                st.error(
                    "❌ 請輸入驗證碼"
                )

            elif len(code) != 6:

                st.error(
                    "❌ 驗證碼必須是 6 位"
                )

            elif remaining <= 0:

                st.error(
                    "❌ 驗證碼已過期，請重新取得。"
                )

                st.session_state.code_sent = False

            else:

                try:

                    response = requests.post(
                        api_url(
                            "/api/auth/verify-code"
                        ),
                        json={
                            "email":
                                st.session_state.code_email,

                            "code":
                                code,
                        },
                        timeout=30,
                    )

                    if response.status_code == 200:

                        data = response.json()

                        token = data.get(
                            "token",
                            "",
                        )

                        if not token:

                            st.error(
                                "❌ 後端沒有回傳 Session Token"
                            )

                        else:

                            st.session_state.logged_in = True

                            st.session_state.email = (
                                st.session_state.code_email
                            )

                            st.session_state.session_token = token

                            st.session_state.code_sent = False

                            st.session_state.member_info = None

                            st.success(
                                "🎉 Email 驗證成功！"
                            )

                            st.rerun()

                    else:

                        st.error(
                            f"❌ 登入失敗 "
                            f"({response.status_code})"
                        )

                        st.code(
                            api_error_message(response)
                        )

                except requests.exceptions.RequestException as e:

                    st.error(
                        "❌ 無法連線後端 API"
                    )

                    st.code(
                        str(e)
                    )

    st.divider()

    st.caption(
        "🎵 JianpuTool Professional"
    )

    st.stop()


# ============================================================
# 登入成功
# ============================================================

email = st.session_state.email
token = st.session_state.session_token

st.success(
    "✅ 登入成功"
)

st.write(
    f"會員 Email：{email}"
)


# ============================================================
# 取得會員資料
# ============================================================

if st.session_state.member_info is None:

    st.session_state.member_info = get_member()

member = st.session_state.member_info


# ============================================================
# 會員中心
# ============================================================

st.divider()

st.subheader("👤 會員中心")


if member is None:

    st.warning(
        "⚠️ 暫時無法取得會員資料。"
    )

    active = False

else:

    active = is_member_active(member)


# ============================================================
# 會員有效
# ============================================================

if active:

    st.success(
        "🟢 會員有效"
    )

    st.write(
        "方案：NT$99 / 30天"
    )

    expire_date = (
        member.get("member_until")
        or member.get("expire_date")
        or member.get("expires_at")
    )

    if expire_date:

        st.info(
            f"會員到期時間：{expire_date}"
        )

    st.divider()

    st.subheader(
        "🎼 JianpuTool 轉換"
    )

    st.write(
        "會員已開通，可以開始將 MP3 / WAV 轉換成數字簡譜 PDF。"
    )

    # --------------------------------------------------------
    # 檢查 ACCESS_CODE
    # --------------------------------------------------------

    if not ACCESS_CODE:

        st.error(
            "❌ 尚未設定 ACCESS_CODE。"
        )

        st.warning(
            "請在本機 `.env` 設定 ACCESS_CODE，"
            "例如："
        )

        st.code(
            "ACCESS_CODE=JianpuTool2026"
        )

        st.stop()

    # --------------------------------------------------------
    # 上傳音檔
    # --------------------------------------------------------

    uploaded_file = st.file_uploader(
        "🎵 上傳 MP3 / WAV",
        type=[
            "mp3",
            "wav",
            "flac",
        ],
    )

    if uploaded_file is not None:

        st.audio(
            uploaded_file
        )

        st.write(
            f"檔案：{uploaded_file.name}"
        )

        st.write(
            f"大小："
            f"{len(uploaded_file.getvalue()) / 1024 / 1024:.2f} MB"
        )

        # ----------------------------------------------------
        # 開始轉換
        # ----------------------------------------------------

        if st.button(
            "🚀 開始轉換",
            type="primary",
            use_container_width=True,
        ):

            progress = st.progress(
                0
            )

            status = st.empty()

            try:

                status.info(
                    "📤 正在上傳音檔..."
                )

                progress.progress(
                    10
                )

                file_bytes = (
                    uploaded_file.getvalue()
                )

                response = requests.post(
                    api_url("/upload"),
                    files={
                        "file": (
                            uploaded_file.name,
                            file_bytes,
                            uploaded_file.type
                            or "audio/mpeg",
                        )
                    },
                    headers={
                        "X-Access-Code":
                            ACCESS_CODE,
                    },
                    timeout=1800,
                )

                progress.progress(
                    90
                )

                if response.status_code == 200:

                    status.success(
                        "✅ PDF 轉換完成！"
                    )

                    progress.progress(
                        100
                    )

                    # ------------------------------------------------
                    # 儲存 PDF
                    # ------------------------------------------------

                    pdf_bytes = response.content

                    base_name = Path(
                        uploaded_file.name
                    ).stem

                    pdf_name = (
                        f"{base_name}_jianpu.pdf"
                    )

                    # ------------------------------------------------
                    # 建立 ZIP
                    # ------------------------------------------------

                    with tempfile.TemporaryDirectory() as tmpdir:

                        pdf_path = (
                            Path(tmpdir)
                            / pdf_name
                        )

                        zip_path = (
                            Path(tmpdir)
                            / f"{base_name}_jianpu.zip"
                        )

                        pdf_path.write_bytes(
                            pdf_bytes
                        )

                        with zipfile.ZipFile(
                            zip_path,
                            "w",
                            zipfile.ZIP_DEFLATED,
                        ) as z:

                            z.write(
                                pdf_path,
                                arcname=pdf_name,
                            )

                        zip_bytes = (
                            zip_path.read_bytes()
                        )

                    st.success(
                        "🎉 JianpuTool 轉換完成！"
                    )

                    st.divider()

                    st.subheader(
                        "📥 下載結果"
                    )

                    st.download_button(
                        label="📄 下載簡譜 PDF",
                        data=pdf_bytes,
                        file_name=pdf_name,
                        mime="application/pdf",
                        use_container_width=True,
                    )

                    st.download_button(
                        label="📦 下載 ZIP",
                        data=zip_bytes,
                        file_name=(
                            f"{base_name}_jianpu.zip"
                        ),
                        mime="application/zip",
                        use_container_width=True,
                    )

                else:

                    progress.progress(
                        100
                    )

                    status.error(
                        f"❌ 轉換失敗 "
                        f"({response.status_code})"
                    )

                    st.code(
                        api_error_message(
                            response
                        )
                    )

            except requests.exceptions.Timeout:

                progress.progress(
                    100
                )

                status.error(
                    "❌ 轉換逾時"
                )

                st.warning(
                    "音檔轉換可能仍在後端處理，"
                    "請檢查 FastAPI 終端機。"
                )

            except requests.exceptions.RequestException as e:

                progress.progress(
                    100
                )

                status.error(
                    "❌ 無法連線後端 API"
                )

                st.code(
                    str(e)
                )

            except Exception as e:

                progress.progress(
                    100
                )

                status.error(
                    "❌ 發生錯誤"
                )

                st.exception(
                    e
                )


# ============================================================
# 尚未訂閱
# ============================================================

else:

    st.warning(
        "🔴 尚未訂閱"
    )

    st.write(
        "目前方案："
    )

    st.markdown(
        """
### 💳 NT$99 / 30天

- 使用 JianpuTool
- MP3 / WAV 音訊轉換
- AI 主旋律分析
- 數字簡譜 PDF
- ZIP 下載
"""
    )

    st.divider()

    st.subheader(
        "💳 訂閱會員"
    )

    st.write(
        "NT$99 / 30天"
    )

    st.write(
        "付款成功後，系統會自動開通 30 天會員。"
    )

    # --------------------------------------------------------
    # 建立 ECPay 訂單
    # --------------------------------------------------------

    if st.button(
        "💳 NT$99 立即訂閱",
        type="primary",
        use_container_width=True,
    ):

        try:

            response = requests.post(
                api_url(
                    "/api/orders"
                ),
                json={
                    "email": email,
                },
                headers={
                    "X-Session-Token":
                        token,
                },
                timeout=30,
            )

            if response.status_code != 200:

                st.error(
                    f"❌ 建立訂單失敗 "
                    f"({response.status_code})"
                )

                st.code(
                    api_error_message(
                        response
                    )
                )

            else:

                data = response.json()

                # ------------------------------------------------
                # 已經是會員
                # ------------------------------------------------

                if data.get(
                    "already_member"
                ):

                    st.success(
                        "🟢 您已經是有效會員。"
                    )

                    st.session_state.member_info = (
                        get_member()
                    )

                    st.rerun()

                else:

                    trade_no = data.get(
                        "trade_no",
                        "",
                    )

                    payment_url = data.get(
                        "payment_url",
                        "",
                    )

                    st.session_state.trade_no = (
                        trade_no
                    )

                    st.session_state.payment_url = (
                        payment_url
                    )

                    st.session_state.payment_started = (
                        True
                    )

                    st.success(
                        "✅ ECPay 訂單建立成功！"
                    )

                    st.write(
                        f"訂單編號：{trade_no}"
                    )

                    if payment_url:

                        st.markdown(
                            f"""
### 💳 前往 ECPay 付款

請按下面按鈕進入綠界付款頁面。
"""
                        )

                        st.link_button(
                            "💳 前往 ECPay 付款",
                            payment_url,
                            use_container_width=True,
                        )

        except requests.exceptions.RequestException as e:

            st.error(
                "❌ 無法連線後端 API"
            )

            st.code(
                str(e)
            )


# ============================================================
# 等待付款 / 查詢訂單
# ============================================================

if (
    st.session_state.payment_started
    and st.session_state.trade_no
):

    st.divider()

    st.subheader(
        "🔄 付款狀態"
    )

    st.write(
        f"訂單：{st.session_state.trade_no}"
    )

    if st.button(
        "🔍 查詢付款狀態",
        use_container_width=True,
    ):

        try:

            response = requests.get(
                api_url(
                    f"/api/orders/"
                    f"{st.session_state.trade_no}"
                ),
                timeout=20,
            )

            if response.status_code == 200:

                order = response.json()

                status = str(
                    order.get(
                        "status",
                        ""
                    )
                ).upper()

                if status == "PAID":

                    st.success(
                        "🎉 付款成功！"
                    )

                    st.success(
                        "🟢 30 天會員已開通。"
                    )

                    st.session_state.member_info = (
                        get_member()
                    )

                    st.session_state.payment_started = (
                        False
                    )

                    st.rerun()

                else:

                    st.info(
                        f"目前訂單狀態：{status or 'PENDING'}"
                    )

                    st.write(
                        "如果您剛完成超商付款，"
                        "請稍候再查詢一次。"
                    )

            else:

                st.error(
                    f"❌ 查詢訂單失敗 "
                    f"({response.status_code})"
                )

                st.code(
                    api_error_message(
                        response
                    )
                )

        except requests.exceptions.RequestException as e:

            st.error(
                "❌ 無法連線後端 API"
            )

            st.code(
                str(e)
            )


# ============================================================
# 登出
# ============================================================

st.divider()

if st.button(
    "🚪 登出",
    use_container_width=True,
):

    try:

        requests.post(
            api_url(
                "/api/auth/logout"
            ),
            headers={
                "X-Session-Token":
                    token,
            },
            timeout=10,
        )

    except Exception:
        pass

    clear_login()

    st.rerun()


# ============================================================
# Footer
# ============================================================

st.divider()

st.caption(
    "🎵 JianpuTool Professional"
)

st.caption(
    "Email 登入 → NT$99 / 30天 → ECPay → "
    "自動開通 → MP3/WAV → 簡譜 PDF → ZIP"
)