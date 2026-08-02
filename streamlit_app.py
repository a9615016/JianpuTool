import streamlit as st

st.title("JianpuTool")

st.write("MP3 → MIDI → MusicXML → 簡譜 PDF")

uploaded = st.file_uploader(
    "上傳 MP3",
    type=["mp3","wav"]
)

if uploaded:
    st.success("收到音檔：" + uploaded.name)