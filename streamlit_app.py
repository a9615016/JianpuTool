# ==========================================================
# JianpuTool Streamlit Cloud FINAL V2
# MP3/WAV/MIDI -> MIDI -> MusicXML -> Quantize -> Jianpu PDF
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

PYTHON = sys.executable


# ----------------------------------------------------------
# UI
# ----------------------------------------------------------

st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)

st.title("🎵 JianpuTool")

st.write(
    "MP3 / WAV / MIDI → 數字簡譜 PDF"
)

st.write(
    "Python:",
    PYTHON
)


uploaded_file = st.file_uploader(
    "上傳音樂檔",
    type=[
        "mp3",
        "wav",
        "mid"
    ]
)


# ----------------------------------------------------------
# PROCESS
# ----------------------------------------------------------

if uploaded_file:


    ext = uploaded_file.name.split(".")[-1].lower()


    input_file = os.path.join(
        UPLOAD_DIR,
        f"{uuid.uuid4()}.{ext}"
    )


    with open(input_file, "wb") as f:
        f.write(uploaded_file.getbuffer())


    st.success(
        "上傳完成"
    )


    # ------------------------------------------------------
    # Audio -> MIDI
    # ------------------------------------------------------

    if ext in ["mp3", "wav"]:


        st.info(
            "BasicPitch 分析..."
        )


        midi_path = os.path.join(
            OUTPUT_DIR,
            "melody.mid"
        )


        try:

            _, midi_data, _ = predict(
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

            st.exception(e)
            st.stop()


    else:

        midi_path = input_file



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


    r = subprocess.run(
        [
            PYTHON,
            "midi_to_musicxml_clean.py",
            midi_path,
            raw_xml
        ],
        capture_output=True,
        text=True
    )


    if r.returncode != 0:

        st.error(r.stderr)
        st.stop()



    # ------------------------------------------------------
    # Clean
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
    # Quantize
    # ------------------------------------------------------

    st.info(
        "修正節拍..."
    )


    fixed_xml = os.path.join(
        OUTPUT_DIR,
        "fixed.musicxml"
    )


    q = subprocess.run(
        [
            PYTHON,
            "final_quantize.py",
            final_xml,
            fixed_xml
        ],
        capture_output=True,
        text=True
    )


    st.text(q.stdout)
    st.text(q.stderr)


    if q.returncode != 0:

        st.error(
            "final_quantize失敗"
        )

        st.stop()



    # ------------------------------------------------------
    # Check Measure
    # ------------------------------------------------------

    st.info(
        "檢查小節..."
    )


    check = subprocess.run(
        [
            PYTHON,
            "check_measure.py",
            fixed_xml
        ],
        capture_output=True,
        text=True
    )


    st.code(
        check.stdout
    )


    if "ERROR" in check.stdout:

        st.error(
            "小節仍然不正確"
        )

        st.stop()



    # ------------------------------------------------------
    # Clean again
    # ------------------------------------------------------

    quant_clean = os.path.join(
        OUTPUT_DIR,
        "quant_clean.musicxml"
    )


    subprocess.run(
        [
            PYTHON,
            "clean_musicxml.py",
            fixed_xml,
            quant_clean
        ]
    )


    final_xml = quant_clean



    # ------------------------------------------------------
    # Jianpu LY
    # ------------------------------------------------------

    st.info(
        "產生簡譜 LilyPond..."
    )


    ly = subprocess.run(
        [
            PYTHON,
            "-m",
            "jianpu_ly",
            final_xml
        ],
        capture_output=True,
        text=True
    )


    if ly.returncode != 0:

        st.error(
            ly.stderr
        )

        st.stop()



    # ------------------------------------------------------
    # Find LY
    # ------------------------------------------------------

    ly_file = None


    for name in os.listdir(OUTPUT_DIR):

        if name.endswith(".ly"):

            ly_file = os.path.join(
                OUTPUT_DIR,
                name
            )

            break



    if ly_file is None:

        st.error(
            "找不到 .ly"
        )

        st.stop()



    # ------------------------------------------------------
    # LilyPond
    # ------------------------------------------------------

    st.info(
        "產生PDF..."
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
        ]
    )


    pdf = ly_file.replace(
        ".ly",
        ".pdf"
    )


    if os.path.exists(pdf):


        st.success(
            "🎉 完成"
        )


        with open(pdf, "rb") as f:

            st.download_button(
                "下載簡譜 PDF",
                f,
                file_name="jianpu.pdf",
                mime="application/pdf"
            )


    else:

        st.error(
            "PDF失敗"
        )