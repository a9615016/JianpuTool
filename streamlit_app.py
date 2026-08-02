import streamlit as st
import os

from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


OUTPUT_DIR = "outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


st.title("🎵 JianpuTool")

st.write(
    "MP3/WAV → BasicPitch MIDI"
)


uploaded_file = st.file_uploader(
    "上傳 MP3/WAV",
    type=["mp3", "wav"]
)


if uploaded_file:

    filename = uploaded_file.name

    base = os.path.splitext(filename)[0]


    input_path = os.path.join(
        OUTPUT_DIR,
        filename
    )


    with open(
        input_path,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )


    st.success(
        "音檔上傳完成"
    )


    if st.button(
        "開始 BasicPitch 分析"
    ):

        try:

            st.info(
                "開始 BasicPitch 分析..."
            )


            predict_and_save(

                input_path,

                OUTPUT_DIR,

                True,    # save_midi

                True,    # sonify_midi

                False,   # save_model_outputs

                True,    # save_notes

                ICASSP_2022_MODEL_PATH

            )


            st.success(
                "✅ MIDI 產生成功"
            )


            midi_files = []

            for f in os.listdir(OUTPUT_DIR):

                if f.endswith(".mid"):

                    midi_files.append(f)


            if midi_files:

                midi_path = os.path.join(
                    OUTPUT_DIR,
                    midi_files[0]
                )


                st.write(
                    "輸出:",
                    midi_path
                )


                with open(
                    midi_path,
                    "rb"
                ) as midi_file:


                    st.download_button(
                        label="下載 MIDI",
                        data=midi_file,
                        file_name=os.path.basename(midi_path),
                        mime="audio/midi"
                    )


            else:

                st.warning(
                    "沒有找到 MIDI 檔"
                )


        except Exception as e:

            st.error(
                f"BasicPitch錯誤: {e}"
            )