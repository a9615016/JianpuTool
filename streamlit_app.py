import streamlit as st
import os
import uuid
import traceback
import subprocess
import sys
import shutil


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



# ======================
# 套件測試
# ======================

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


    quantize_file = os.path.join(
        OUTPUT_DIR,
        job_id + "_quantize.musicxml"
    )


    bar_file = os.path.join(
        OUTPUT_DIR,
        job_id + "_bar.musicxml"
    )


    split_file = os.path.join(
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


        # ======================
        # MP3 → MIDI
        # ======================

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
                "BasicPitch失敗"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # ======================
        # MIDI → MusicXML
        # ======================

        try:

            st.info(
                "MIDI 轉 MusicXML..."
            )


            result = subprocess.run(
                [
                    sys.executable,
                    "midi_to_musicxml_clean.py",
                    midi_file,
                    musicxml_file
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(
                    "MusicXML失敗"
                )

                st.code(
                    result.stderr
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



        # ======================
        # Final Quantize
        # ======================

        try:

            st.info(
                "Final Quantize..."
            )


            result = subprocess.run(
                [
                    sys.executable,
                    "final_quantize.py",
                    musicxml_file,
                    quantize_file
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(
                    "final_quantize失敗"
                )

                st.code(
                    result.stderr
                )

                st.stop()


            st.success(
                "節拍量化完成"
            )


        except Exception:

            st.error(
                "Quantize錯誤"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # ======================
        # bar split fix
        # ======================

        try:

            st.info(
                "修正小節線..."
            )


            result = subprocess.run(
                [
                    sys.executable,
                    "bar_split_fix.py",
                    quantize_file,
                    bar_file
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(
                    "小節修正失敗"
                )

                st.code(
                    result.stderr
                )

                st.stop()


            st.success(
                "小節修正完成"
            )


        except Exception:

            st.error(
                "bar修正錯誤"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # ======================
        # split cross bar
        # ======================

        try:

            st.info(
                "切割跨小節音符..."
            )


            
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(
                    "跨小節修正失敗"
                )

                st.code(
                    result.stderr
                )

                st.stop()


            st.success(
                "跨小節修正完成"
            )


        except Exception:

            st.error(
                "split錯誤"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # ======================
        # MusicXML → jianpu ly
        # ======================

        try:

            st.info(
                "MusicXML 轉簡譜..."
            )


            with open(
                ly_file,
                "w",
                encoding="utf-8"
            ) as f:


                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "jianpu_ly",
                        split_file
                    ],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )


            if result.returncode != 0:

                st.error(
                    "jianpu_ly失敗"
                )

                st.code(
                    result.stderr
                )

                st.stop()


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



        # ======================
        # LilyPond PDF
        # ======================

        try:

            st.info(
                "LilyPond 產生 PDF..."
            )


            lilypond = shutil.which(
                "lilypond"
            )


            if lilypond is None:

                st.error(
                    "找不到 LilyPond"
                )

                st.stop()



            result = subprocess.run(
                [
                    lilypond,
                    "-o",
                    pdf_file.replace(".pdf",""),
                    ly_file
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(
                    "PDF失敗"
                )

                st.code(
                    result.stderr
                )

                st.stop()


            st.success(
                "🎉 簡譜 PDF 完成"
            )


        except Exception:

            st.error(
                "PDF錯誤"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # ======================
        # Downloads
        # ======================


        for file, name, mime in [

            (midi_file,"output.mid","audio/midi"),

            (musicxml_file,
             "output.musicxml",
             "application/xml"),

            (pdf_file,
             "jianpu.pdf",
             "application/pdf")

        ]:


            if os.path.exists(file):

                with open(file,"rb") as f:

                    st.download_button(
                        name,
                        f,
                        file_name=name,
                        mime=mime
                    )