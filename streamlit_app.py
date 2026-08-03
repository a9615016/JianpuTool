# ==========================================================
# JianpuTool Streamlit App V1.0
# MP3/WAV -> BasicPitch -> MIDI -> MusicXML -> Jianpu PDF
# ==========================================================

import streamlit as st
import os
import uuid
import subprocess
import shutil


from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


# ----------------------------------------------------------
# Path
# ----------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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


# ----------------------------------------------------------
# UI
# ----------------------------------------------------------

st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


st.title("🎵 JianpuTool")
st.write(
    "MP3 / WAV → MIDI → MusicXML → 數字簡譜 PDF"
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
# Convert
# ----------------------------------------------------------

if uploaded_file:


    ext = uploaded_file.name.split(".")[-1].lower()


    input_file = os.path.join(
        UPLOAD_DIR,
        f"{uuid.uuid4()}.{ext}"
    )


    # save upload
    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )


    st.success(
        f"上傳完成: {uploaded_file.name}"
    )


    st.write(
        "檔案位置:"
    )

    st.code(
        input_file
    )


    if not os.path.exists(input_file):

        st.error(
            "音檔保存失敗"
        )

        st.stop()



    # ------------------------------------------------------
    # MIDI
    # ------------------------------------------------------

    if ext in [
        "mp3",
        "wav"
    ]:


        st.info(
            "開始 BasicPitch 音樂辨識..."
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

    musicxml_path = os.path.join(
        OUTPUT_DIR,
        "raw.musicxml"
    )


    st.info(
        "MIDI轉MusicXML..."
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
            "python",
            "clean_musicxml.py",
            musicxml_path,
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
            "python",
            "jianpu_fix_musicxml.py",
            clean_xml,
            final_xml
        ]
    )


    # ------------------------------------------------------
    # jianpu-ly
    # ------------------------------------------------------

    st.info(
        "產生簡譜..."
    )


    subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            final_xml
        ]
    )


    ly_file = os.path.join(
        OUTPUT_DIR,
        "final.ly"
    )


    # ------------------------------------------------------
    # LilyPond
    # ------------------------------------------------------

    st.info(
        "LilyPond輸出PDF..."
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


    pdf_file = ly_file.replace(
        ".ly",
        ".pdf"
    )


    if os.path.exists(pdf_file):

        st.success(
            "完成！"
        )


        with open(
            pdf_file,
            "rb"
        ) as f:

            st.download_button(
                label="下載簡譜 PDF",
                data=f,
                file_name="jianpu.pdf",
                mime="application/pdf"
            )


    else:

        st.error(
            "PDF產生失敗"
        )