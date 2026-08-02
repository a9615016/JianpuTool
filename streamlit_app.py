import streamlit as st
import os
import subprocess
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


st.set_page_config(
    page_title="JianpuTool V1",
    page_icon="🎵"
)

st.title("🎵 JianpuTool V1")
st.write("MP3/WAV → MIDI → MusicXML → 簡譜 PDF")


OUTPUT = "outputs"

os.makedirs(OUTPUT, exist_ok=True)


uploaded = st.file_uploader(
    "上傳 MP3/WAV",
    type=["mp3","wav"],
    key="audio_upload"
)


if uploaded:

    filename = uploaded.name

    input_path = os.path.join(
        OUTPUT,
        filename
    )

    with open(input_path,"wb") as f:
        f.write(uploaded.getbuffer())


    st.success("音檔上傳完成")


    if st.button(
        "開始轉換",
        key="start_button"
    ):

        try:

            st.write("開始 BasicPitch分析...")


            midi_path = os.path.join(
                OUTPUT,
                filename.rsplit(".",1)[0]
                +"_basic_pitch.mid"
            )


            predict_and_save(
                input_path,
                OUTPUT,
                True,
                True,
                True,
                True,
                ICASSP_2022_MODEL_PATH
            )


            st.success(
                "✅ MIDI產生成功"
            )


            st.write(midi_path)


            st.write(
                "開始轉 MusicXML..."
            )


            result = subprocess.run(
                [
                    "python",
                    "midi_to_musicxml_clean.py",
                    midi_path
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(result.stderr)

            else:

                st.success(
                    "✅ MusicXML完成"
                )

                st.text(result.stdout)


        except Exception as e:

            st.error(
                f"錯誤:{e}"
            )