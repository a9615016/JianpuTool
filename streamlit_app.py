import streamlit as st
import os
import sys
import subprocess
from pathlib import Path

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
from basic_pitch import note_creation


# ==========================
# JianpuTool V1
# MP3/WAV → MIDI → MusicXML
# ==========================


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


st.title("🎵 JianpuTool V1")
st.write("MP3/WAV → MIDI → MusicXML → 簡譜 PDF")


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================
# Upload
# ==========================

audio_file = st.file_uploader(
    "上傳 MP3/WAV",
    type=["mp3", "wav"],
    key="audio_upload"
)


if audio_file:

    input_path = OUTPUT_DIR / audio_file.name

    with open(input_path, "wb") as f:
        f.write(audio_file.getbuffer())


    st.success("音檔上傳完成")


    if st.button(
        "開始分析",
        key="start"
    ):


        # ======================
        # BasicPitch
        # ======================

        st.write(
            "開始 BasicPitch分析..."
        )


        try:

            model_output = predict(
                str(input_path),
                ICASSP_2022_MODEL_PATH
            )


            midi_path = OUTPUT_DIR / (
                input_path.stem +
                "_basic_pitch.mid"
            )


            note_creation.model_output_to_midi(
                model_output,
                str(midi_path)
            )


            st.success(
                "✅ MIDI產生成功"
            )

            st.write(
                str(midi_path)
            )


        except Exception as e:

            st.error(
                f"BasicPitch錯誤:{e}"
            )

            st.stop()



        # ======================
        # MIDI → MusicXML
        # ======================

        st.write(
            "開始轉 MusicXML..."
        )


        try:

            result = subprocess.run(
                [
                    sys.executable,
                    "midi_to_musicxml_clean.py",
                    str(midi_path)
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(
                    result.stderr
                )

                st.stop()


            musicxml_path = (
                str(midi_path)
                .replace(
                    ".mid",
                    ".musicxml"
                )
            )


            if os.path.exists(
                musicxml_path
            ):

                st.success(
                    "✅ MusicXML完成"
                )

                st.write(
                    musicxml_path
                )


            else:

                st.error(
                    "MusicXML沒有產生"
                )


        except Exception as e:

            st.error(
                f"MusicXML錯誤:{e}"
            )