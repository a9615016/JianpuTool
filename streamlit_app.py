import streamlit as st
import os
import sys
import subprocess
from pathlib import Path

from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


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


# output資料夾

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================
# 上傳音檔
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
        key="start_button"
    ):


        # ==========================
        # BasicPitch
        # ==========================

        st.write("開始 BasicPitch分析...")


        try:

            predict_and_save(
                [str(input_path)],
                str(OUTPUT_DIR),
                True,
                True,
                False,
                ICASSP_2022_MODEL_PATH
            )


            midi_files = list(
                OUTPUT_DIR.glob("*.mid")
            )


            if midi_files:

                midi_path = midi_files[-1]


                st.success(
                    "✅ MIDI產生成功"
                )

                st.write(
                    str(midi_path)
                )


            else:

                st.error(
                    "找不到MIDI"
                )
                st.stop()



        except Exception as e:

            st.error(
                f"BasicPitch錯誤: {e}"
            )

            st.stop()



        # ==========================
        # MIDI → MusicXML
        # ==========================


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
                f"MusicXML錯誤: {e}"
            )