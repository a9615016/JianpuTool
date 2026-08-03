import streamlit as st
import os
import uuid
import traceback
import subprocess
import sys


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


st.title("🎵 JianpuTool")

st.write(
    "MP3 → MIDI → MusicXML → 簡譜 PDF"
)


UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =====================
# 套件測試
# =====================

try:
    from basic_pitch.inference import predict
    import music21

    st.success(
        "BasicPitch + music21 載入成功"
    )

except Exception:

    st.error(
        "套件載入失敗"
    )

    st.code(
        traceback.format_exc()
    )

    st.stop()



uploaded_file = st.file_uploader(
    "上傳 MP3",
    type=["mp3"]
)


if uploaded_file:

    st.success(
        "MP3 上傳完成"
    )

    st.write(
        "檔案名稱：",
        uploaded_file.name
    )


    job_id = str(uuid.uuid4())


    input_file = os.path.join(
        UPLOAD_DIR,
        job_id + ".mp3"
    )


    with open(input_file,"wb") as f:
        f.write(
            uploaded_file.getbuffer()
        )


    if st.button("開始轉換"):

        st.info(
            "測試模式：檔案上傳成功"
        )


        st.success(
            "下一步加入 MIDI → MusicXML → PDF"
        )