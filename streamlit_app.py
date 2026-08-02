import streamlit as st
import os

from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


OUTPUT_DIR = "outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


st.title("🎵 JianpuTool")

st.write(
    "MP3/WAV → BasicPitch MIDI"
)


uploaded_file = st.file_uploader(
    "上傳 MP3/WAV",
    type=["mp3", "wav"]
)


if uploaded_file:

    filename = uploaded_file.name

    base = os.path.splitext(filename)[0]


    input_path = os.path.join(
        OUTPUT_DIR,
        filename
    )


    with open(input_path, "wb") as f:
        f.write(
            uploaded_file.getbuffer()
        )


    st.success(
        "音檔上傳完成"
    )


    if st.button(
        "開始 BasicPitch 分析"
    ):

        try:

            st.info(
                "開始 BasicPitch 分析..."
            )


            predict_and_save(

                audio_path_list=[
                    input_path
                ],

                output_directory=OUTPUT_DIR,

                save_midi=True,

                sonify_midi=False,

                save_model_outputs=False,

                save_notes=True,

                model_or_model_path=ICASSP_2022_MODEL_PATH

            )


            st.success(
                "✅ BasicPitch 完成"
            )


            midi_files = []

            for file in os.listdir(OUTPUT_DIR):

                if file.endswith(".mid"):

                    midi_files.append(file)


            if len(midi_files) > 0:

                midi_path = os.path.join(
                    OUTPUT_DIR,
                    midi_files[-1]
                )


                st.success(
                    "✅ MIDI 產生成功"
                )


                st.write(
                    midi_path
                )


                with open(
                    midi_path,
                    "rb"
                ) as f:


                    st.download_button(
                        label="下載 MIDI",
                        data=f,
                        file_name=os.path.basename(midi_path),
                        mime="audio/midi"
                    )


            else:

                st.warning(
                    "找不到 MIDI 檔案"
                )


        except Exception as e:

            st.error(
                f"BasicPitch錯誤: {e}"
            )
import streamlit as st
import os
import subprocess
import tempfile
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


st.title("🎵 JianpuTool V40")

uploaded = st.file_uploader(
    "上傳 MP3/WAV",
    type=["mp3","wav"]
)


if uploaded:

    input_path = os.path.join(
        OUTPUT_DIR,
        uploaded.name
    )

    with open(input_path,"wb") as f:
        f.write(uploaded.read())


    st.success("音檔上傳完成")


    if st.button("開始轉換"):


        # -----------------------
        # BasicPitch
        # -----------------------

        st.write("開始 BasicPitch 分析...")


        midi_path = os.path.join(
            OUTPUT_DIR,
            uploaded.name+"_basic_pitch.mid"
        )


        try:

            predict_and_save(
                [input_path],
                OUTPUT_DIR,
                True,
                True,
                True,
                ICASSP_2022_MODEL_PATH
            )


            st.success("✅ BasicPitch 完成")


        except Exception as e:
            st.error(
                f"BasicPitch錯誤:{e}"
            )


        # 找 MIDI

        midi_files=[
            f for f in os.listdir(OUTPUT_DIR)
            if f.endswith(".mid")
        ]


        if midi_files:

            midi_file=os.path.join(
                OUTPUT_DIR,
                midi_files[-1]
            )

            st.success(
                f"✅ MIDI產生成功\n{midi_file}"
            )


            # -----------------------
            # MIDI -> MusicXML
            # -----------------------

            st.write(
                "開始 MusicXML..."
            )


            xml_file=midi_file.replace(
                ".mid",
                ".musicxml"
            )


            try:

                from music21 import converter


                score=converter.parse(
                    midi_file
                )

                score.write(
                    "musicxml",
                    xml_file
                )


                st.success(
                    "✅ MusicXML完成"
                )


            except Exception as e:

                st.error(
                    f"MusicXML錯誤:{e}"
                )



            # -----------------------
            # MusicXML -> Jianpu
            # -----------------------

            st.write(
                "開始產生簡譜 PDF..."
            )


            try:

                ly_file=xml_file.replace(
                    ".musicxml",
                    ".ly"
                )


                with open(
                    ly_file,
                    "w",
                    encoding="utf-8"
                ) as f:

                    subprocess.run(
                        [
                            "python",
                            "-m",
                            "jianpu_ly",
                            xml_file
                        ],
                        stdout=f
                    )


                pdf=subprocess.run(
                    [
                        "lilypond",
                        ly_file
                    ],
                    capture_output=True
                )


                pdf_file=ly_file.replace(
                    ".ly",
                    ".pdf"
                )


                if os.path.exists(pdf_file):

                    st.success(
                        "🎉 簡譜PDF完成"
                    )


                    st.download_button(
                        "下載簡譜PDF",
                        open(pdf_file,"rb"),
                        file_name=os.path.basename(pdf_file)
                    )


                else:

                    st.error(
                        "PDF產生失敗"
                    )


            except Exception as e:

                st.error(
                    f"簡譜錯誤:{e}"
                )