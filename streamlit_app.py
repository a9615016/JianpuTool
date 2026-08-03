import streamlit as st
import os
import uuid
import subprocess


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


mp3 = st.file_uploader(
    "上傳 MP3",
    type=["mp3"]
)


if mp3:

    job = str(uuid.uuid4())

    mp3_path = os.path.join(
        UPLOAD_DIR,
        job + ".mp3"
    )


    with open(mp3_path, "wb") as f:
        f.write(mp3.getbuffer())


    st.success("MP3 上傳完成")

    st.write(
        "檔案名稱：",
        mp3.name
    )


    if st.button("開始轉換"):

        midi_path = os.path.join(
            OUTPUT_DIR,
            job + ".mid"
        )

        st.info(
            "BasicPitch 分析音樂..."
        )


        result = subprocess.run(
            [
                "python",
                "basicpitch_convert.py",
                mp3_path,
                midi_path
            ],
            capture_output=True,
            text=True
        )


        if result.returncode != 0:

            st.error(
                "BasicPitch 失敗"
            )

            st.code(
                result.stderr
            )

        else:

            st.success(
                "MIDI 產生成功"
            )