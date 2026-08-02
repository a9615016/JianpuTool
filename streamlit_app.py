import streamlit as st
import os
import subprocess
from pathlib import Path

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


st.set_page_config(
    page_title="JianpuTool V1",
    layout="centered"
)

st.title("🎵 JianpuTool V1")
st.write("MP3/WAV → MIDI → MusicXML → 簡譜 PDF")


OUTPUT = "outputs"
os.makedirs(OUTPUT, exist_ok=True)


uploaded = st.file_uploader(
    "上傳 MP3/WAV",
    type=["mp3", "wav"],
    key="audio_upload"
)


if uploaded:

    input_file = os.path.join(
        OUTPUT,
        uploaded.name
    )

    with open(input_file, "wb") as f:
        f.write(uploaded.getbuffer())


    st.success("音檔上傳完成")


    if st.button("開始轉換"):

        try:

            ################################
            # BasicPitch
            ################################

            st.info("開始 BasicPitch分析...")


            model_path = ICASSP_2022_MODEL_PATH


            model_output, midi_data, note_events = predict(
                input_file,
                model_or_model_path=model_path
            )


            midi_file = os.path.join(
                OUTPUT,
                Path(uploaded.name).stem
                + "_basic_pitch.mid"
            )


            midi_data.write(
                midi_file
            )


            st.success("✅ MIDI產生成功")

            st.write(midi_file)



            ################################
            # MIDI → MusicXML
            ################################

            st.info("開始轉 MusicXML...")


            xml_file = midi_file.replace(
                ".mid",
                ".musicxml"
            )


            subprocess.run(
                [
                    "python",
                    "midi_to_musicxml_clean.py",
                    midi_file,
                    xml_file
                ],
                check=True
            )


            st.success(
                "✅ MusicXML完成"
            )

            st.write(xml_file)



            ################################
            # MusicXML → Jianpu
            ################################

            st.info("開始產生簡譜 PDF...")


            subprocess.run(
                [
                    "python",
                    "-m",
                    "jianpu_ly",
                    xml_file
                ],
                check=True
            )


            st.success(
                "🎉 完成"
            )


        except Exception as e:

            st.error(
                f"錯誤:{e}"
            )