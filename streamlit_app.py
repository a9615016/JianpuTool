# ==========================================================
# JianpuTool Streamlit Cloud FINAL
# MP3/WAV -> MIDI -> MusicXML -> Quantize -> Jianpu PDF
# ==========================================================

import streamlit as st
import os
import uuid
import subprocess
import shutil
import sys


from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH



# ----------------------------------------------------------
# PATH
# ----------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploads"
)


OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)


os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


PYTHON = sys.executable



# ----------------------------------------------------------
# UI
# ----------------------------------------------------------

st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool"
)


st.write(
    "MP3 / WAV / MIDI → 數字簡譜 PDF"
)


st.write(
    "Python:",
    PYTHON
)



uploaded_file = st.file_uploader(
    "上傳音樂檔案",
    type=[
        "mp3",
        "wav",
        "mid"
    ]
)



# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------

if uploaded_file:


    ext = uploaded_file.name.split(".")[-1].lower()


    input_file = os.path.join(
        UPLOAD_DIR,
        f"{uuid.uuid4()}.{ext}"
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )


    st.success(
        "上傳完成"
    )


    # ------------------------------------------------------
    # Audio -> MIDI
    # ------------------------------------------------------

    if ext in [
        "mp3",
        "wav"
    ]:


        st.info(
            "BasicPitch 音樂辨識..."
        )


        midi_path = os.path.join(
            OUTPUT_DIR,
            "melody.mid"
        )


        try:

            model_output, midi_data, note_events = predict(
                input_file,
                ICASSP_2022_MODEL_PATH
            )


            with open(
                midi_path,
                "wb"
            ) as f:

                f.write(
                    midi_data
                )


        except Exception as e:

            st.error(
                "BasicPitch錯誤"
            )

            st.exception(e)

            st.stop()


    else:

        midi_path = input_file



    st.success(
        "MIDI完成"
    )



    # ------------------------------------------------------
    # MIDI -> MusicXML
    # ------------------------------------------------------

    raw_xml = os.path.join(
        OUTPUT_DIR,
        "raw.musicxml"
    )


    st.info(
        "MIDI轉MusicXML..."
    )


    result = subprocess.run(
        [
            PYTHON,
            "midi_to_musicxml_clean.py",
            midi_path,
            raw_xml
        ],
        capture_output=True,
        text=True
    )


    if result.returncode != 0:

        st.error(
            result.stderr
        )

        st.stop()



    # ------------------------------------------------------
    # Clean MusicXML
    # ------------------------------------------------------

    clean_xml = os.path.join(
        OUTPUT_DIR,
        "clean.musicxml"
    )


    subprocess.run(
        [
            PYTHON,
            "clean_musicxml.py",
            raw_xml,
            clean_xml
        ]
    )



    # ------------------------------------------------------
    # Jianpu Fix
    # ------------------------------------------------------

    final_xml = os.path.join(
        OUTPUT_DIR,
        "final.musicxml"
    )


    subprocess.run(
        [
            PYTHON,
            "jianpu_fix_musicxml.py",
            clean_xml,
            final_xml
        ]
    )



    # ------------------------------------------------------
    # Final Quantize
    # ------------------------------------------------------

    st.info(
        "修正小節節拍..."
    )


    fixed_xml = os.path.join(
        OUTPUT_DIR,
        "fixed.musicxml"
    )


    result = subprocess.run(
        [
            PYTHON,
            "final_quantize.py",
            final_xml,
            fixed_xml
        ],
        capture_output=True,
        text=True
    )


    if result.returncode != 0:

        st.error(
            result.stderr
        )

        st.stop()


    final_xml = fixed_xml



    # ------------------------------------------------------
    # jianpu-ly
    # ------------------------------------------------------

    st.info(
        "產生簡譜 LilyPond..."
    )


    result = subprocess.run(
        [
            PYTHON,
            "-m",
            "jianpu_ly",
            final_xml
        ],
        capture_output=True,
        text=True
    )


    if result.returncode != 0:

        st.error(
            result.stderr
        )

        st.stop()



    ly_file = os.path.join(
        OUTPUT_DIR,
        "fixed.ly"
    )


    if not os.path.exists(ly_file):

        # jianpu-ly 預設名稱保險處理

        possible = [
            "fixed.musicxml.ly",
            "fixed.ly",
            "jianpu.ly"
        ]

        for f in possible:

            p = os.path.join(
                OUTPUT_DIR,
                f
            )

            if os.path.exists(p):

                ly_file = p
                break



    # ------------------------------------------------------
    # LilyPond
    # ------------------------------------------------------

    st.info(
        "LilyPond產生PDF..."
    )


    lilypond = shutil.which(
        "lilypond"
    )


    if lilypond is None:

        st.error(
            "找不到 LilyPond"
        )

        st.stop()



    subprocess.run(
        [
            lilypond,
            ly_file
        ],
        capture_output=True,
        text=True
    )



    pdf_file = ly_file.replace(
        ".ly",
        ".pdf"
    )



    if os.path.exists(pdf_file):

        st.success(
            "🎉 簡譜PDF完成"
        )


        with open(
            pdf_file,
            "rb"
        ) as f:


            st.download_button(
                "下載簡譜PDF",
                f,
                file_name="jianpu.pdf",
                mime="application/pdf"
            )


    else:

        st.error(
            "PDF產生失敗"
        )