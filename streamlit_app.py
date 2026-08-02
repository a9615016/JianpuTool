import streamlit as st
import os
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH
from music21 import converter


OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


st.title("🎵 JianpuTool V40")
st.write("MP3/WAV → BasicPitch MIDI → MusicXML")


# =========================
# 唯一上傳元件
# =========================

uploaded = st.file_uploader(
    "上傳 MP3/WAV",
    type=["mp3", "wav"],
    key="audio_upload"
)


if uploaded:


    input_path = os.path.join(
        OUTPUT_DIR,
        uploaded.name
    )


    with open(input_path, "wb") as f:
        f.write(uploaded.read())


    st.success("音檔上傳完成")


    if st.button("開始轉換"):


        # =========================
        # BasicPitch
        # =========================

        st.info("開始 BasicPitch 分析...")


        try:

            predict_and_save(
                [input_path],
                OUTPUT_DIR,
                True,
                True,
                True,
                ICASSP_2022_MODEL_PATH
            )


            st.success(
                "✅ BasicPitch 完成"
            )


        except Exception as e:

            st.error(
                f"BasicPitch錯誤:{e}"
            )


        # 找 MIDI

        midi_files = [
            f for f in os.listdir(OUTPUT_DIR)
            if f.endswith(".mid")
        ]


        if midi_files:


            midi_path = os.path.join(
                OUTPUT_DIR,
                midi_files[-1]
            )


            st.success(
                f"✅ MIDI產生成功\n\n{midi_path}"
            )


            # =========================
            # MIDI → MusicXML
            # =========================

            st.info(
                "開始轉 MusicXML..."
            )


            try:


                score = converter.parse(
                    midi_path
                )


                xml_path = midi_path.replace(
                    ".mid",
                    ".musicxml"
                )


                score.write(
                    "musicxml",
                    xml_path
                )


                st.success(
                    f"✅ MusicXML完成\n\n{xml_path}"
                )


                with open(
                    xml_path,
                    "rb"
                ) as f:

                    st.download_button(
                        "下載 MusicXML",
                        f,
                        file_name=os.path.basename(xml_path)
                    )


            except Exception as e:

                st.error(
                    f"MusicXML錯誤:{e}"
                )


        else:

            st.warning(
                "沒有找到 MIDI"
            )