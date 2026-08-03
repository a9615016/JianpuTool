import streamlit as st

st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)

st.title("🎵 JianpuTool")

st.write("MP3 / WAV → MIDI → MusicXML → 簡譜 PDF")

uploaded = st.file_uploader(
    "上傳 MP3 或 WAV",
    type=["mp3", "wav"]
)

if uploaded:
    st.success("檔案收到")