import streamlit as st
import os
import uuid
import traceback
import subprocess

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


st.success("BasicPitch + music21 載入成功")


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


    mp3_file = os.path.join(
        UPLOAD_DIR,
        job_id + ".mp3"
    )

    midi_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".mid"
    )

    xml_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".musicxml"
    )

    pdf_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".pdf"
    )


    with open(mp3_file,"wb") as f:
        f.write(uploaded_file.getbuffer())


    if st.button("開始轉換"):

        try:

            # ==========================
            # MP3 → MIDI
            # ==========================

            st.info(
                "BasicPitch 分析音樂..."
            )


            model_output, midi_data, note_events = predict(
                mp3_file
            )


            midi_data.write(
                midi_file
            )


            st.success(
                "MIDI 產生成功"
            )


            # ==========================
            # MIDI → MusicXML
            # ==========================

            st.info(
                "MIDI 轉 MusicXML..."
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
                "MusicXML 產生成功"
            )


            # ==========================
            # MusicXML → Jianpu PDF
            # ==========================

            st.info(
                "產生簡譜 PDF..."
            )


            subprocess.run(
                [
                    "python",
                    "-m",
                    "jianpu_ly",
                    xml_file
                ],
                stdout=open(
                    "temp.ly",
                    "w",
                    encoding="utf-8"
                ),
                check=True
            )


            subprocess.run(
                [
                    "lilypond",
                    "-o",
                    pdf_file.replace(".pdf",""),
                    "temp.ly"
                ],
                check=True
            )


            st.success(
                "🎉 簡譜 PDF 完成"
            )


            if os.path.exists(pdf_file):

                with open(pdf_file,"rb") as f:

                    st.download_button(
                        "下載簡譜 PDF",
                        f,
                        file_name="jianpu.pdf",
                        mime="application/pdf"
                    )


        except Exception:

            st.error(
                "轉換失敗"
            )

            st.code(
                traceback.format_exc()
            )