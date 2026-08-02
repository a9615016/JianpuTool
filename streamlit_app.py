import streamlit as st
import os
import subprocess
from pathlib import Path

from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


OUTPUT = Path("outputs")
OUTPUT.mkdir(exist_ok=True)


st.title("🎵 JianpuTool V1")
st.write("MP3/WAV → MIDI → MusicXML → 簡譜 PDF")


audio = st.file_uploader(
    "上傳 MP3/WAV",
    type=["mp3","wav"],
    key="audio_upload"
)


if audio:

    input_file = OUTPUT / audio.name

    with open(input_file,"wb") as f:
        f.write(audio.getbuffer())


    st.success("音檔上傳完成")


    if st.button("開始轉換"):


        try:

            # ======================
            # 1. BasicPitch
            # ======================

            st.info("開始 BasicPitch 分析...")


            midi_file = OUTPUT / (
                input_file.stem +
                "_basic_pitch.mid"
            )


            predict_and_save(
                [str(input_file)],
                str(OUTPUT),
                True,
                False,
                False,
                ICASSP_2022_MODEL_PATH
            )


            # BasicPitch 名稱修正
            generated = OUTPUT / (
                input_file.stem +
                "_basic_pitch.mid"
            )


            if generated.exists():

                st.success("✅ MIDI產生成功")
                st.write(generated)


            else:
                st.error("MIDI不存在")
                st.stop()



            # ======================
            # 2. MIDI → MusicXML
            # ======================

            st.info("開始轉 MusicXML...")


            musicxml = OUTPUT / (
                input_file.stem +
                "_basic_pitch.musicxml"
            )


            cmd = [
                "python",
                "midi_to_musicxml_clean.py",
                str(generated),
                str(musicxml)
            ]


            result=subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )


            if musicxml.exists():

                st.success("✅ MusicXML完成")
                st.write(musicxml)

            else:

                st.error(result.stderr)
                st.stop()



            # ======================
            # 3. MusicXML → Jianpu
            # ======================

            st.info("開始產生簡譜...")


            ly_file = OUTPUT / (
                input_file.stem +
                "_jianpu.ly"
            )


            with open(ly_file,"w",encoding="utf-8") as f:

                subprocess.run(
                    [
                        "python",
                        "-m",
                        "jianpu_ly",
                        str(musicxml)
                    ],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )



            # ======================
            # 4. LilyPond PDF
            # ======================

            st.info("開始 LilyPond PDF...")


            subprocess.run(
                [
                    r"C:\lilypond-2.26.0\bin\lilypond.exe",
                    str(ly_file)
                ],
                capture_output=True,
                text=True
            )


            pdf = ly_file.with_suffix(".pdf")


            if pdf.exists():

                st.success("🎉 完成 PDF")

                st.download_button(
                    "下載簡譜PDF",
                    open(pdf,"rb"),
                    file_name=pdf.name
                )

            else:

                st.warning(
                    "LY成功，但PDF失敗，查看LilyPond錯誤"
                )



        except Exception as e:

            st.error(
                f"錯誤:{e}"
            )