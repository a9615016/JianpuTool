import streamlit as st
import os
import uuid
import traceback
import subprocess
import sys

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


# =========================
# 套件測試
# =========================

try:
    import music21
    st.success("BasicPitch + music21 載入成功")

except Exception:
    st.error("套件載入失敗")
    st.code(traceback.format_exc())
    st.stop()



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


    musicxml_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".musicxml"
    )


    clean_xml = os.path.join(
        OUTPUT_DIR,
        job_id + "_clean.musicxml"
    )


    quant_xml = os.path.join(
        OUTPUT_DIR,
        job_id + "_final2.musicxml"
    )


    ly_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".ly"
    )


    pdf_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".pdf"
    )



    with open(mp3_file,"wb") as f:
        f.write(
            uploaded_file.getbuffer()
        )



    if st.button("開始轉換"):



        # =========================
        # MP3 → MIDI
        # =========================

        try:

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


        except Exception:

            st.error(
                "BasicPitch 失敗"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # =========================
        # MIDI → MusicXML
        # =========================

        try:

            st.info(
                "MIDI 轉 MusicXML..."
            )


            r = subprocess.run(
                [
                    sys.executable,
                    "midi_to_musicxml_clean.py",
                    midi_file,
                    musicxml_file
                ],
                capture_output=True,
                text=True
            )


            if r.returncode != 0:

                st.error(
                    "MusicXML失敗"
                )

                st.code(r.stderr)

                st.stop()


            st.success(
                "MusicXML 產生成功"
            )


        except Exception:

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # =========================
        # clean musicxml
        # =========================

        try:

            st.info(
                "修正 MusicXML..."
            )


            r = subprocess.run(
                [
                    sys.executable,
                    "clean_musicxml.py",
                    musicxml_file,
                    clean_xml
                ],
                capture_output=True,
                text=True
            )


            if r.returncode != 0:

                st.error(
                    "clean失敗"
                )

                st.code(r.stderr)

                st.stop()


            st.success(
                "MusicXML 修正完成"
            )


        except Exception:

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # =========================
        # final_quantize
        # =========================

        try:

            st.info(
                "Final Quantize..."
            )


            r = subprocess.run(
                [
                    sys.executable,
                    "final_quantize.py",
                    clean_xml,
                    quant_xml
                ],
                capture_output=True,
                text=True
            )


            if r.returncode != 0:

                st.error(
                    "final_quantize失敗"
                )

                st.code(r.stderr)

                st.stop()



            st.success(
                "節拍量化完成"
            )


        except Exception:

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # =========================
        # jianpu_ly
        # =========================

        try:

            st.info(
                "MusicXML 轉簡譜..."
            )


            with open(
                ly_file,
                "w",
                encoding="utf-8"
            ) as f:


                r = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "jianpu_ly",
                        quant_xml
                    ],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )



            if r.returncode != 0:

                st.error(
                    "jianpu_ly失敗"
                )

                st.code(
                    r.stderr
                )

                st.stop()



            st.success(
                "簡譜產生成功"
            )



        except Exception:

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # =========================
        # LilyPond PDF
        # =========================

        try:

            st.info(
                "產生 PDF..."
            )


            r = subprocess.run(
                [
                    "lilypond",
                    "-o",
                    pdf_file.replace(".pdf",""),
                    ly_file
                ],
                capture_output=True,
                text=True
            )


            if r.returncode != 0:

                st.error(
                    "PDF產生失敗"
                )

                st.code(
                    r.stderr
                )

                st.stop()



            st.success(
                "PDF完成 🎉"
            )


        except Exception:

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # =========================
        # 下載
        # =========================


        if os.path.exists(pdf_file):

            with open(pdf_file,"rb") as f:

                st.download_button(
                    "下載簡譜 PDF",
                    f,
                    file_name="jianpu.pdf",
                    mime="application/pdf"
                )


        if os.path.exists(midi_file):

            with open(midi_file,"rb") as f:

                st.download_button(
                    "下載 MIDI",
                    f,
                    file_name="output.mid",
                    mime="audio/midi"
                )


        if os.path.exists(quant_xml):

            with open(quant_xml,"rb") as f:

                st.download_button(
                    "下載 MusicXML",
                    f,
                    file_name="output.musicxml",
                    mime="application/xml"
                )