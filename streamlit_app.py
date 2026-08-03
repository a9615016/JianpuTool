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


    midi_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".mid"
    )


    with open(input_file,"wb") as f:
        f.write(uploaded_file.getbuffer())


    if st.button("開始轉簡譜 PDF"):

        try:

            # =====================
            # MP3 → MIDI
            # =====================

            st.info(
                "BasicPitch 分析音樂..."
            )


            model_output, midi_data, note_events = predict(
                input_file
            )


            midi_data.write(
                midi_file
            )


            st.success(
                "MIDI 產生成功"
            )


            # =====================
            # MIDI → MusicXML
            # =====================

            musicxml = os.path.join(
                OUTPUT_DIR,
                job_id + ".musicxml"
            )


            st.info(
                "MIDI 轉 MusicXML..."
            )


            r = subprocess.run(
                [
                    "python",
                    "midi_to_musicxml_clean.py",
                    midi_file,
                    musicxml
                ],
                capture_output=True,
                text=True
            )


            if r.returncode != 0:
                st.error("MusicXML失敗")
                st.code(r.stderr)
                st.stop()


            st.success(
                "MusicXML完成"
            )


            # =====================
            # jianpu-ly
            # =====================

            st.info(
                "產生簡譜..."
            )


            ly_file = os.path.join(
                OUTPUT_DIR,
                job_id + ".ly"
            )


            with open(ly_file,"w",encoding="utf-8") as f:

                r = subprocess.run(
                    [
                        "python",
                        "-m",
                        "jianpu_ly",
                        musicxml
                    ],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )


            if not os.path.exists(ly_file):
                st.error("LY產生失敗")
                st.code(r.stderr)
                st.stop()


            st.success(
                "LY完成"
            )


            # =====================
            # LilyPond PDF
            # =====================

            st.info(
                "產生 PDF..."
            )


            subprocess.run(
                [
                    "lilypond",
                    ly_file
                ]
            )


            pdf_file = ly_file.replace(
                ".ly",
                ".pdf"
            )


            if os.path.exists(pdf_file):

                st.success(
                    "🎉 簡譜 PDF 完成"
                )


                with open(pdf_file,"rb") as f:

                    st.download_button(
                        "下載簡譜 PDF",
                        f,
                        file_name="jianpu.pdf",
                        mime="application/pdf"
                    )


            else:
                st.error("PDF不存在")


        except Exception:

            st.error(
                "轉換失敗"
            )

            st.code(
                traceback.format_exc()
            )