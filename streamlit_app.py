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


    with open(input_path, "wb") as f:
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

                audio_path_list=[
                    input_path
                ],

                output_directory=OUTPUT_DIR,

                save_midi=True,

                sonify_midi=False,

                save_model_outputs=False,

                save_notes=True,

                model_or_model_path=ICASSP_2022_MODEL_PATH

            )


            st.success(
                "✅ BasicPitch 完成"
            )


            midi_files = []

            for file in os.listdir(OUTPUT_DIR):

                if file.endswith(".mid"):

                    midi_files.append(file)


            if len(midi_files) > 0:

                midi_path = os.path.join(
                    OUTPUT_DIR,
                    midi_files[-1]
                )


                st.success(
                    "✅ MIDI 產生成功"
                )


                st.write(
                    midi_path
                )


                with open(
                    midi_path,
                    "rb"
                ) as f:


                    st.download_button(
                        label="下載 MIDI",
                        data=f,
                        file_name=os.path.basename(midi_path),
                        mime="audio/midi"
                    )


            else:

                st.warning(
                    "找不到 MIDI 檔案"
                )


        except Exception as e:

            st.error(
                f"BasicPitch錯誤: {e}"
            )