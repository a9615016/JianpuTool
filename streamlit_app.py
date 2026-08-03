import streamlit as st
import os
import uuid
import traceback
import subprocess
import sys


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


# ==========================
# 套件測試
# ==========================

try:

    from basic_pitch.inference import predict
    import music21

    st.success(
        "BasicPitch + music21 載入成功"
    )


except Exception:

    st.error(
        "套件載入失敗"
    )

    st.code(
        traceback.format_exc()
    )

    st.stop()



# ==========================
# 上傳
# ==========================

uploaded_file = st.file_uploader(
    "上傳 MP3",
    type=["mp3"]
)



if uploaded_file:


    st.success(
        "MP3 上傳完成"
    )


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


    final_musicxml = os.path.join(
        OUTPUT_DIR,
        job_id + "_final.musicxml"
    )


    ly_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".ly"
    )


    pdf_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".pdf"
    )



    with open(
        mp3_file,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )



    if st.button("開始轉換"):



        # ==========================
        # MP3 → MIDI
        # ==========================

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



        # ==========================
        # MIDI → MusicXML
        # ==========================

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

                st.code(
                    r.stderr
                )

                st.stop()



            st.success(
                "MusicXML 產生成功"
            )



        except Exception:

            st.error(
                "MusicXML錯誤"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()




        # ==========================
        # Final Quantize
        # ==========================

        try:

            st.info(
                "Final Quantize..."
            )


            r = subprocess.run(
                [
                    sys.executable,
                    "final_quantize.py",
                    musicxml_file,
                    final_musicxml
                ],
                capture_output=True,
                text=True
            )


            if r.returncode != 0:

                st.error(
                    "final_quantize失敗"
                )

                st.code(
                    r.stderr
                )

                st.stop()



            st.success(
                "節拍量化完成"
            )



        except Exception:


            st.error(
                "Final Quantize錯誤"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()





        # ==========================
        # MusicXML → Jianpu LY
        # ==========================

        try:


            st.info(
                "MusicXML 轉簡譜..."
            )


            r = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "jianpu_ly",
                    final_musicxml
                ],
                capture_output=True,
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



            with open(
                ly_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    r.stdout
                )



            st.success(
                "簡譜產生成功"
            )



        except Exception:


            st.error(
                "jianpu錯誤"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()




        # ==========================
        # LilyPond → PDF
        # ==========================


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
                    "PDF失敗"
                )

                st.code(
                    r.stderr
                )

                st.stop()



            st.success(
                "PDF 完成"
            )



        except Exception:


            st.error(
                "LilyPond錯誤"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()




        # ==========================
        # 下載
        # ==========================


        if os.path.exists(pdf_file):


            with open(
                pdf_file,
                "rb"
            ) as f:


                st.download_button(
                    "下載簡譜 PDF",
                    f,
                    file_name="jianpu.pdf",
                    mime="application/pdf"
                )



        if os.path.exists(midi_file):

            with open(
                midi_file,
                "rb"
            ) as f:


                st.download_button(
                    "下載 MIDI",
                    f,
                    file_name="output.mid",
                    mime="audio/midi"
                )