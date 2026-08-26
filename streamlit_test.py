import streamlit as st

st.set_page_config(
    page_title="JianpuTool 測試",
    page_icon="🎵"
)

st.title("🎵 JianpuTool 測試網站")

st.success("✅ Streamlit 成功啟動！")

st.write("GitHub → Streamlit Cloud 測試成功。")

name = st.text_input("請輸入你的名字")

if name:
    st.info(f"你好，{name}！")

st.divider()

st.write("如果你能看到這個頁面，代表免費 Streamlit Cloud 基本部署正常。")
