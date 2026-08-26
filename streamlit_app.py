import streamlit as st

st.set_page_config(
    page_title="JianpuTool 測試",
    page_icon="🎵"
)

st.title("🎵 JianpuTool 測試網站")
st.success("✅ Streamlit 網頁啟動成功！")

st.write("GitHub → Streamlit Cloud → 網頁，目前連線正常。")

st.subheader("系統測試")

st.write("Python / Streamlit 基本測試")

name = st.text_input("請輸入你的名字")

if name:
    st.success(f"你好，{name}！JianpuTool 測試成功。")

uploaded_file = st.file_uploader(
    "上傳一個 MP3 測試",
    type=["mp3", "wav"]
)

if uploaded_file:
    st.audio(uploaded_file)
    st.success("✅ 檔案上傳成功！")