import streamlit as st
import os
import uuid
import traceback

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


# BasicPitch 測試
st.success("BasicPitch 載入成功")


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


    output_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".mid"
    )


    with open(input_file, "wb") as f:
        f.write(
            uploaded_file.getbuffer()
        )


    if st.button("開始轉 MIDI"):

        try:

            st.info(
                "BasicPitch 分析音樂..."
            )


            model_output, midi_data, note_events = predict(
                input_file
            )


            midi_data.write(
                output_file
            )


            st.success(
                "MIDI 產生成功"
            )


            with open(
                output_file,
                "rb"
            ) as f:

                st.download_button(
                    "下載 MIDI",
                    f,
                    file_name="output.mid",
                    mime="audio/midi"
                )


        except Exception:

            st.error(
                "BasicPitch 失敗"
            )

            st.code(
                traceback.format_exc()
            )