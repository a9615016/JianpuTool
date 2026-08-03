import streamlit as st
import os

# ==========================
# JianpuTool Simple Homepage
# ==========================

st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 JianpuTool")
st.write("MP3 / WAV / MIDI → 簡譜轉換工具")

st.divider()

st.subheader("上傳音樂檔案")

uploaded_file = st.file_uploader(
    "選擇 MP3、WAV 或 MIDI",
    type=["mp3", "wav", "mid", "midi"]
)

if uploaded_file:

    save_dir = "uploads"
    os.makedirs(save_dir, exist_ok=True)

    file_path = os.path.join(
        save_dir,
        uploaded_file.name
    )

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("上傳完成")

    st.write("檔案名稱:")
    st.code(uploaded_file.name)

    st.write("檔案大小:")
    st.write(f"{uploaded_file.size / 1024:.2f} KB")


st.divider()

st.info(
    """
目前版本：
- ✅ Streamlit 首頁
- ✅ MP3 上傳
- ✅ WAV 上傳
- ✅ MIDI 上傳

下一步整合：
MP3/WAV → BasicPitch → MIDI → MusicXML → Jianpu PDF
"""
)