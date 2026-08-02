import streamlit as st

st.title("🎵 JianpuTool")

st.write("MP3 → 簡譜")

uploaded = st.file_uploader(
    "選擇MP3",
    type=["mp3","wav"]
)

if uploaded:
    st.success("收到")