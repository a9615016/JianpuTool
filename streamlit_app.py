import streamlit as st
from pathlib import Path
import subprocess
import os

from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


BASE = Path(".")
OUTPUT = BASE / "outputs"

OUTPUT.mkdir(
    exist_ok=True
)


st.title("🎵 JianpuTool V1")
st.write(
    "MP3/WAV → MIDI → MusicXML → 簡譜 PDF"
)


audio = st.file_uploader(
    "上傳 MP3/WAV",
    type=["mp3", "wav"],
    key="main_audio_upload"
)



if audio:


    input_file = OUTPUT / audio.name


    with open(input_file, "wb") as f:

        f.write(
            audio.getbuffer()
        )


    st.success(
        "音檔上傳完成"
    )


    if st.button(
        "開始轉換",
        key="convert_button"
    ):


        try:


            # =========================
            # 1. BasicPitch
            # =========================

            st.info(
                "開始 BasicPitch分析..."
            )


            predict_and_save(

                audio_path_list=[
                    str(input_file)
                ],

                output_directory=str(OUTPUT),

                save_midi=True,

                sonify_midi=False,

                save_model_outputs=False,

                save_notes=False,

                model_or_model_path=
                    ICASSP_2022_MODEL_PATH
            )



            midi_file = OUTPUT / (
                input_file.stem +
                "_basic_pitch.mid"
            )



            if not midi_file.exists():

                st.error(
                    "MIDI產生失敗"
                )

                st.stop()



            st.success(
                "✅ MIDI產生成功"
            )

            st.write(
                midi_file
            )



            # =========================
            # 2. MIDI → MusicXML
            # =========================

            st.info(
                "開始轉 MusicXML..."
            )


            musicxml_file = OUTPUT / (
                input_file.stem +
                "_basic_pitch.musicxml"
            )



            result = subprocess.run(

                [
                    "python",
                    "midi_to_musicxml_clean.py",
                    str(midi_file),
                    str(musicxml_file)
                ],

                capture_output=True,

                text=True
            )



            if not musicxml_file.exists():

                st.error(
                    result.stderr
                )

                st.stop()



            st.success(
                "✅ MusicXML完成"
            )

            st.write(
                musicxml_file
            )



            # =========================
            # 3. MusicXML → jianpu
            # =========================

            st.info(
                "產生簡譜..."
            )



            ly_file = OUTPUT / (
                input_file.stem +
                "_jianpu.ly"
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
                        str(musicxml_file)
                    ],

                    stdout=f,

                    stderr=subprocess.PIPE,

                    text=True
                )



            st.success(
                "✅ jianpu.ly完成"
            )



            # =========================
            # 4. LilyPond PDF
            # =========================


            st.info(
                "產生PDF..."
            )



            subprocess.run(

                [
                    "lilypond",
                    str(ly_file)
                ],

                capture_output=True,

                text=True
            )



            pdf_file = ly_file.with_suffix(
                ".pdf"
            )



            if pdf_file.exists():


                st.success(
                    "🎉 簡譜PDF完成"
                )


                with open(
                    pdf_file,
                    "rb"
                ) as f:


                    st.download_button(

                        label="下載簡譜PDF",

                        data=f,

                        file_name=pdf_file.name,

                        mime="application/pdf"
                    )


            else:


                st.warning(
                    "PDF未產生，請查看LilyPond錯誤"
                )



        except Exception as e:


            st.error(
                f"錯誤:{e}"
            )