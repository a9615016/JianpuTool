import streamlit as st
import os
import uuid
import traceback
import subprocess
import sys

from basic_pitch.inference import predict


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


# 測試套件
try:
    import music21
    st.success("BasicPitch + music21 載入成功")
except Exception:
    st.error("套件載入失敗")
    st.code(traceback.format_exc())
    st.stop()



uploaded_file = st.file_uploader(
    "上傳 MP3",
    type=["mp3"]
)



if uploaded_file:

    st.success("MP3 上傳完成")

    st.write(
        "檔案名稱：",
        uploaded_file.name
    )


    job_id = str(uuid.uuid4())


    input_file = os.path.join(
        UPLOAD_DIR,
        job_id + ".mp3"
    )


    midi_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".mid"
    )


    musicxml_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".musicxml"
    )


    with open(input_file, "wb") as f:
        f.write(
            uploaded_file.getbuffer()
        )


    if st.button("開始轉換"):

        # ======================
        # MP3 → MIDI
        # ======================

        try:

            st.info(
                "BasicPitch 分析音樂..."
            )


            model_output, midi_data, note_events = predict(
                input_file
            )


            midi_data.write(
                midi_file
            )


            st.success(
                "MIDI 產生成功"
            )


        except Exception:

            st.error(
                "BasicPitch 失敗"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # ======================
        # MIDI → MusicXML
        # ======================

        try:

            st.info(
                "MIDI 轉 MusicXML..."
            )


            result = subprocess.run(
                [
                    sys.executable,
                    "midi_to_musicxml_clean.py",
                    midi_file,
                    musicxml_file
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(
                    "MusicXML失敗"
                )

                st.code(
                    result.stderr
                )

                st.stop()


            st.success(
                "MusicXML 產生成功"
            )


        except Exception:

            st.error(
                "MusicXML錯誤"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # ======================
        # Download
        # ======================


        with open(
            midi_file,
            "rb"
        ) as f:

            st.download_button(
                "下載 MIDI",
                f,
                file_name="output.mid",
                mime="audio/midi"
            )


        with open(
            musicxml_file,
            "rb"
        ) as f:

            st.download_button(
                "下載 MusicXML",
                f,
                file_name="output.musicxml",
                mime="application/xml"
            )