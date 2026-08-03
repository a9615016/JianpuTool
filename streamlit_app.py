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


UPLOAD_DIR="uploads"
OUTPUT_DIR="outputs"

os.makedirs(UPLOAD_DIR,exist_ok=True)
os.makedirs(OUTPUT_DIR,exist_ok=True)



try:
    import music21
    st.success("BasicPitch + music21 載入成功")

except Exception:
    st.error("套件錯誤")
    st.code(traceback.format_exc())
    st.stop()



uploaded_file=st.file_uploader(
    "上傳 MP3",
    type=["mp3"]
)



if uploaded_file:


    st.success("MP3 上傳完成")

    job=str(uuid.uuid4())


    mp3=os.path.join(
        UPLOAD_DIR,
        job+".mp3"
    )


    mid=os.path.join(
        OUTPUT_DIR,
        job+".mid"
    )


    xml=os.path.join(
        OUTPUT_DIR,
        job+".musicxml"
    )


    fixed_xml=os.path.join(
        OUTPUT_DIR,
        job+"_fix.musicxml"
    )


    ly=os.path.join(
        OUTPUT_DIR,
        job+".ly"
    )


    pdf=os.path.join(
        OUTPUT_DIR,
        job+".pdf"
    )


    with open(mp3,"wb") as f:
        f.write(uploaded_file.getbuffer())



    if st.button("開始轉換"):


        # =====================
        # MP3 → MIDI
        # =====================

        try:

            st.info("BasicPitch 分析音樂...")


            model_output,midi_data,note_events=predict(mp3)


            midi_data.write(mid)


            st.success(
                "MIDI 產生成功"
            )


        except Exception:

            st.error("BasicPitch失敗")
            st.code(traceback.format_exc())
            st.stop()



        # =====================
        # MIDI → MusicXML
        # =====================

        try:

            st.info("MIDI 轉 MusicXML...")


            r=subprocess.run(
                [
                    sys.executable,
                    "midi_to_musicxml_clean.py",
                    mid,
                    xml
                ],
                capture_output=True,
                text=True
            )


            if r.returncode!=0:
                st.error("MusicXML失敗")
                st.code(r.stderr)
                st.stop()


            st.success(
                "MusicXML 產生成功"
            )


        except Exception:

            st.code(traceback.format_exc())
            st.stop()



        # =====================
        # MusicXML 修正
        # =====================

        try:

            st.info(
                "修正小節..."
            )


            r=subprocess.run(
                [
                    sys.executable,
                    "clean_musicxml.py",
                    xml,
                    fixed_xml
                ],
                capture_output=True,
                text=True
            )


            if r.returncode!=0:

                st.error(
                    "MusicXML修正失敗"
                )

                st.code(r.stderr)
                st.stop()



            st.success(
                "MusicXML 修正完成"
            )


        except Exception:

            st.code(traceback.format_exc())
            st.stop()



        # =====================
        # MusicXML → jianpu ly
        # =====================


        try:


            st.info(
                "MusicXML 轉簡譜..."
            )


            with open(ly,"w",encoding="utf8") as f:

                r=subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "jianpu_ly",
                        fixed_xml
                    ],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )


            if r.returncode!=0:

                st.error(
                    "jianpu_ly失敗"
                )

                st.code(r.stderr)
                st.stop()


            st.success(
                "簡譜產生成功"
            )


        except Exception:

            st.code(traceback.format_exc())
            st.stop()



        # =====================
        # LilyPond PDF
        # =====================


        try:


            st.info(
                "產生PDF..."
            )


            r=subprocess.run(
                [
                    "lilypond",
                    "-o",
                    pdf.replace(".pdf",""),
                    ly
                ],
                capture_output=True,
                text=True
            )


            if r.returncode!=0:

                st.error(
                    "PDF失敗"
                )

                st.code(r.stderr)

                st.stop()



            st.success(
                "PDF完成 🎉"
            )


        except Exception:

            st.code(traceback.format_exc())



        #下載


        with open(pdf,"rb") as f:

            st.download_button(
                "下載簡譜 PDF",
                f,
                file_name="jianpu.pdf",
                mime="application/pdf"
            )