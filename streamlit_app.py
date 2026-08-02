import streamlit as st
import os
import tempfile
import subprocess
import shutil

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


# ==========================
# 設定
# ==========================

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


st.title("🎵 JianpuTool V1")
st.write("MP3/WAV → MIDI → MusicXML → 簡譜 PDF")


# ==========================
# 上傳
# ==========================

uploaded = st.file_uploader(
    "上傳 MP3/WAV",
    type=["mp3", "wav"]
)


if uploaded:

    filename = uploaded.name
    base = os.path.splitext(filename)[0]

    audio_path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    with open(audio_path, "wb") as f:
        f.write(uploaded.getbuffer())


    st.success("音檔上傳完成")


    # ==========================
    # BasicPitch
    # ==========================

    if st.button("開始分析"):

        st.info("開始 BasicPitch 分析...")


        midi_path = os.path.join(
            OUTPUT_DIR,
            base + ".mid"
        )


        try:

            model_output = predict(
                audio_path,
                ICASSP_2022_MODEL_PATH
            )


            # BasicPitch 新版輸出
            model_output[0].write(
                midi_path
            )


            st.success(
                "✅ MIDI 產生成功"
            )


        except Exception as e:

            st.error(
                f"BasicPitch錯誤:{e}"
            )
            st.stop()



        # ==========================
        # MIDI → MusicXML
        # ==========================

        st.info(
            "MIDI → MusicXML"
        )


        musicxml = os.path.join(
            OUTPUT_DIR,
            base + ".musicxml"
        )


        result = subprocess.run(
            [
                "python",
                "midi_to_musicxml_clean.py",
                midi_path,
                musicxml
            ],
            capture_output=True,
            text=True
        )


        if not os.path.exists(musicxml):

            st.error(
                result.stderr
            )
            st.stop()


        st.success(
            "✅ MusicXML完成"
        )



        # ==========================
        # 修正 MusicXML
        # ==========================


        st.info(
            "修正節拍"
        )


        final_xml = os.path.join(
            OUTPUT_DIR,
            base + "_final.musicxml"
        )


        subprocess.run(
            [
                "python",
                "final_quantize.py",
                musicxml,
                final_xml
            ]
        )


        if not os.path.exists(final_xml):

            st.error(
                "final_quantize失敗"
            )
            st.stop()


        st.success(
            "✅ MusicXML修正完成"
        )



        # ==========================
        # Jianpu-ly
        # ==========================


        st.info(
            "產生簡譜"
        )


        ly_file = os.path.join(
            OUTPUT_DIR,
            base + ".ly"
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
                    final_xml
                ],
                stdout=f,
                stderr=subprocess.STDOUT
            )


        st.success(
            "✅ LilyPond檔完成"
        )



        # ==========================
        # LilyPond PDF
        # ==========================


        st.info(
            "輸出PDF"
        )


        subprocess.run(
            [
                "lilypond",
                ly_file
            ]
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
                    file_name=os.path.basename(pdf_file)
                )


        else:

            st.error(
                "PDF生成失敗"
            )