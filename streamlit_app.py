import streamlit as st
import os
import subprocess
from pathlib import Path

import streamlit as st


@st.cache_resource
def load_basic_pitch():
    from basic_pitch.inference import predict
    return predict


predict = load_basic_pitch()
from basic_pitch import ICASSP_2022_MODEL_PATH


# =========================
# 設定
# =========================

st.set_page_config(
    page_title="JianpuTool V1",
    layout="centered"
)


st.title("🎵 JianpuTool V1")
st.write("MP3/WAV → MIDI → MusicXML → 簡譜 PDF")


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# =========================
# Upload
# =========================

uploaded = st.file_uploader(
    "上傳 MP3/WAV",
    type=["mp3", "wav"],
    key="jianputool_upload"
)


if uploaded:


    input_file = os.path.join(
        OUTPUT_DIR,
        uploaded.name
    )


    with open(input_file, "wb") as f:
        f.write(
            uploaded.getbuffer()
        )


    st.success(
        "音檔上傳完成"
    )


    if st.button(
        "開始轉換",
        key="start_button"
    ):


        try:

            # =========================
            # BasicPitch
            # =========================

            st.info(
                "開始 BasicPitch分析..."
            )


            model_output, midi_data, note_events = predict(
                input_file,
                model_or_model_path=ICASSP_2022_MODEL_PATH
            )


            midi_file = os.path.join(
                OUTPUT_DIR,
                Path(uploaded.name).stem
                + "_basic_pitch.mid"
            )


            midi_data.write(
                midi_file
            )


            st.success(
                "✅ MIDI產生成功"
            )

            st.write(
                midi_file
            )



            # =========================
            # MIDI → MusicXML
            # =========================


            st.info(
                "開始轉 MusicXML..."
            )


            xml_file = os.path.join(
                OUTPUT_DIR,
                Path(uploaded.name).stem
                + "_basic_pitch.musicxml"
            )


            converter_script = os.path.join(
                BASE_DIR,
                "midi_to_musicxml_clean.py"
            )


            result = subprocess.run(
                [
                    "python",
                    converter_script,
                    midi_file,
                    xml_file
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(
                    "midi_to_musicxml_clean.py錯誤"
                )

                st.code(
                    result.stderr
                )

                st.stop()



            st.success(
                "✅ MusicXML完成"
            )

            st.write(
                xml_file
            )



            # =========================
            # MusicXML → Jianpu
            # =========================


            st.info(
                "開始產生簡譜..."
            )


            result2 = subprocess.run(
                [
                    "python",
                    "-m",
                    "jianpu_ly",
                    xml_file
                ],
                capture_output=True,
                text=True
            )


            if result2.returncode != 0:

                st.error(
                    "jianpu_ly錯誤"
                )

                st.code(
                    result2.stderr
                )

                st.stop()


            st.success(
                "🎉 Jianpu完成"
            )


        except Exception as e:

            st.error(
                f"錯誤:{e}"
            )