import streamlit as st
import os
import uuid
import subprocess
import traceback


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


st.title("🎵 JianpuTool")

st.write(
    "MP3 → MIDI → MusicXML → 簡譜 PDF"
)


uploaded_file = st.file_uploader(
    "上傳 MP3",
    type=["mp3"]
)


if uploaded_file:

    job_id = str(uuid.uuid4())

    mp3_file = os.path.join(
        UPLOAD_DIR,
        job_id + ".mp3"
    )


    with open(mp3_file, "wb") as f:
        f.write(uploaded_file.getbuffer())


    st.success("MP3 上傳完成")

    st.write(
        "檔案名稱：",
        uploaded_file.name
    )


    if st.button("開始轉換"):

        try:

            midi_file = os.path.join(
                OUTPUT_DIR,
                job_id + ".mid"
            )


            st.info(
                "BasicPitch 分析音樂..."
            )


            result = subprocess.run(
                [
                    "python",
                    "basicpitch_convert.py",
                    mp3_file,
                    midi_file
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

                st.stop()


            st.success(
                "MIDI 完成"
            )


            musicxml_file = os.path.join(
                OUTPUT_DIR,
                job_id + ".musicxml"
            )


            st.info(
                "MIDI 轉 MusicXML..."
            )


            result = subprocess.run(
                [
                    "python",
                    "midi_to_musicxml_clean.py",
                    midi_file,
                    musicxml_file
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(
                    "MusicXML 失敗"
                )

                st.code(
                    result.stderr
                )

                st.stop()


            st.success(
                "MusicXML 完成"
            )


            st.info(
                "產生簡譜 PDF..."
            )


            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "jianpu_ly",
                    musicxml_file
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(
                    "jianpu_ly 失敗"
                )

                st.code(
                    result.stderr
                )

                st.stop()


            st.success(
                "簡譜產生完成"
            )


        except Exception:

            st.error(
                "錯誤"
            )

            st.code(
                traceback.format_exc()
            )