import streamlit as st
import os
import subprocess
import uuid
import shutil


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


uploaded = st.file_uploader(
    "上傳 MP3",
    type=["mp3"]
)


if uploaded:

    job = str(uuid.uuid4())

    mp3_path = os.path.join(
        UPLOAD_DIR,
        job + ".mp3"
    )

    with open(mp3_path, "wb") as f:
        f.write(uploaded.getbuffer())


    st.success("MP3 上傳完成")


    if st.button("開始轉換"):


        try:

            # ==========================
            # 1. BasicPitch MP3 -> MIDI
            # ==========================

            st.info("1. BasicPitch 分析音樂...")


            midi_path = os.path.join(
                OUTPUT_DIR,
                job + ".mid"
            )


            cmd = [
                "python",
                "basicpitch_convert.py",
                mp3_path,
                midi_path
            ]


            subprocess.run(
                cmd,
                check=True
            )


            # ==========================
            # 2. MIDI -> MusicXML
            # ==========================

            st.info("2. MIDI 轉 MusicXML")


            musicxml = os.path.join(
                OUTPUT_DIR,
                job + ".musicxml"
            )


            subprocess.run(
                [
                    "python",
                    "midi_to_musicxml_clean.py",
                    midi_path,
                    musicxml
                ],
                check=True
            )


            # ==========================
            # 3. jianpu-ly
            # ==========================

            st.info("3. 產生簡譜")


            ly_file = os.path.join(
                OUTPUT_DIR,
                job + ".ly"
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


            generated_ly = os.path.join(
                OUTPUT_DIR,
                os.path.basename(musicxml).replace(
                    ".musicxml",
                    ".ly"
                )
            )


            shutil.move(
                generated_ly,
                ly_file
            )


            # ==========================
            # 4. LilyPond PDF
            # ==========================

            st.info("4. LilyPond 產生 PDF")


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

                st.success("完成！")

                with open(pdf_file,"rb") as f:

                    st.download_button(
                        "下載簡譜 PDF",
                        f,
                        file_name="jianpu.pdf",
                        mime="application/pdf"
                    )


            else:

                st.error("PDF 產生失敗")


        except Exception as e:

            st.error(
                f"錯誤：{e}"
            )