import streamlit as st
import os
import uuid
import subprocess
import traceback

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)



st.title("🎵 JianpuTool")
st.write("MP3 → MIDI → MusicXML → 數字簡譜 PDF")



audio = st.file_uploader(
    "上傳 MP3",
    type=["mp3"]
)


if audio:

    job = str(uuid.uuid4())

    mp3_file = os.path.join(
        UPLOAD_DIR,
        job + ".mp3"
    )


    with open(mp3_file,"wb") as f:
        f.write(audio.getbuffer())


    st.success("MP3 上傳完成")


    if st.button("開始轉換"):

        try:

            # =====================
            # 1. BasicPitch
            # =====================

            st.info("1. BasicPitch 分析音樂")


            midi_file = os.path.join(
                OUTPUT_DIR,
                job + ".mid"
            )


            model_output, midi_data, note_events = predict(
                mp3_file,
                ICASSP_2022_MODEL_PATH
            )


            midi_data.write(
                midi_file
            )


            st.success(
                "MIDI 完成"
            )


            # =====================
            # 2. MIDI -> MusicXML
            # =====================

            st.info(
                "2. MIDI 轉 MusicXML"
            )


            musicxml = os.path.join(
                OUTPUT_DIR,
                job + ".musicxml"
            )


            result = subprocess.run(
                [
                    "python",
                    "midi_to_musicxml_clean.py",
                    midi_file,
                    musicxml
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.code(result.stderr)

                raise Exception(
                    "MusicXML 轉換失敗"
                )



            # =====================
            # 3. jianpu-ly
            # =====================

            st.info(
                "3. 產生簡譜"
            )


            subprocess.run(
                [
                    "python",
                    "-m",
                    "jianpu_ly",
                    musicxml
                ],
                cwd=OUTPUT_DIR,
                check=True
            )


            ly_file = musicxml.replace(
                ".musicxml",
                ".ly"
            )



            # =====================
            # 4. LilyPond
            # =====================

            st.info(
                "4. 產生 PDF"
            )


            subprocess.run(
                [
                    "lilypond",
                    ly_file
                ],
                check=True
            )


            pdf_file = ly_file.replace(
                ".ly",
                ".pdf"
            )


            if os.path.exists(pdf_file):

                st.success(
                    "🎉 簡譜完成"
                )


                with open(pdf_file,"rb") as f:

                    st.download_button(
                        "下載簡譜 PDF",
                        f,
                        file_name="jianpu.pdf"
                    )


            else:

                st.error(
                    "PDF 不存在"
                )



        except Exception:

            st.error(
                "轉換失敗"
            )

            st.code(
                traceback.format_exc()
            )