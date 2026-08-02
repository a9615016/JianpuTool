import streamlit as st
import sys

st.write("Python version:")
st.write(sys.version)
import os
import tempfile

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


st.title("🎵 JianpuTool")
st.write("MP3 → MIDI → 簡譜")


uploaded = st.file_uploader(
    "上傳 MP3/WAV",
    type=["mp3", "wav"]
)


if uploaded:

    input_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    input_file.write(uploaded.read())
    input_file.close()


    st.info("開始 BasicPitch 分析...")


    try:
        model_output, midi_data, note_events = predict(
            input_file.name,
            ICASSP_2022_MODEL_PATH
        )


        midi_path = "output.mid"

        midi_data.write(midi_path)


        st.success("✅ MIDI 產生成功")

        st.download_button(
            "下載 MIDI",
            open(midi_path,"rb"),
            file_name="output.mid"
        )


    except Exception as e:
        st.error(e)