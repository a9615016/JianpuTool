import streamlit as st
import os
import tempfile
import shutil

from basic_pitch.inference import predict_and_save


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


    if st.button("開始 BasicPitch 分析"):


        try:

            st.info(
                "開始 BasicPitch 分析..."
            )


            predict_and_save(
                input_path,
                OUTPUT_DIR,
                base,
                True,     # save MIDI
                True      # sonify
            )


            st.success(
                "✅ BasicPitch完成"
            )


            # 搜尋 MIDI

            midi_file = None

            for f in os.listdir(OUTPUT_DIR):

                if f.endswith(".mid"):

                    midi_file = os.path.join(
                        OUTPUT_DIR,
                        f
                    )

                    break


            if midi_file:


                st.success(
                    "✅ MIDI 產生成功"
                )


                st.audio(
                    midi_file
                )


                with open(
                    midi_file,
                    "rb"
                ) as f:

                    st.download_button(
                        "下載 MIDI",
                        f,
                        file_name=os.path.basename(midi_file)
                    )


            else:

                st.error(
                    "沒有找到 MIDI"
                )


        except Exception as e:

            st.error(
                f"BasicPitch錯誤: {e}"
            )