import streamlit as st
import os
import uuid
import subprocess
import traceback


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
st.write("MP3 → MIDI → MusicXML → 簡譜 PDF")


mp3 = st.file_uploader(
    "上傳 MP3",
    type=["mp3"]
)


if mp3:

    job = str(uuid.uuid4())

    mp3_path = os.path.join(
        UPLOAD_DIR,
        job + ".mp3"
    )


    with open(mp3_path, "wb") as f:
        f.write(mp3.getbuffer())


    st.success("MP3 上傳完成")


    if st.button("開始轉換"):

        try:

            midi_path = os.path.join(
                OUTPUT_DIR,
                job + ".mid"
            )


            st.info("BasicPitch 分析音樂...")


            result = subprocess.run(
                [
                    "python",
                    "basicpitch_convert.py",
                    mp3_path,
                    midi_path
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error("BasicPitch 失敗")

                st.code(
                    result.stderr
                )

                st.stop()


            st.success(
                "MIDI 完成"
            )


            musicxml_path = os.path.join(
                OUTPUT_DIR,
                job + ".musicxml"
            )


            st.info(
                "MIDI 轉 MusicXML..."
            )


            result = subprocess.run(
                [
                    "python",
                    "midi_to_musicxml_clean.py",
                    midi_path,
                    musicxml_path
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.code(
                    result.stderr
                )

                st.stop()


            st.success(
                "MusicXML 完成"
            )


            st.info(
                "產生簡譜 PDF..."
            )


            subprocess.run(
                [
                    "python",
                    "-m",
                    "jianpu_ly",
                    musicxml_path
                ],
                check=True
            )


            ly_file = musicxml_path.replace(
                ".musicxml",
                ".ly"
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
                    "🎉 完成"
                )


                with open(pdf_file,"rb") as f:

                    st.download_button(
                        "下載簡譜 PDF",
                        f,
                        file_name="jianpu.pdf"
                    )


        except Exception:

            st.error(
                "發生錯誤"
            )

            st.code(
                traceback.format_exc()
            )