import streamlit as st
import os
import uuid
import subprocess
import shutil


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


st.title("🎵 JianpuTool")
st.write("MP3 → MIDI → MusicXML → 簡譜 PDF")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================
# BasicPitch 測試
# ==========================

try:
    from basic_pitch.inference import predict
    BASIC_OK = True
    st.success("BasicPitch 載入成功")
except Exception as e:
    BASIC_OK = False
    st.error("BasicPitch 載入失敗")
    st.exception(e)


# ==========================
# 上傳 MP3
# ==========================

uploaded = st.file_uploader(
    "上傳 MP3",
    type=["mp3"],
    max_upload_size=200
)


if uploaded and BASIC_OK:

    uid = str(uuid.uuid4())

    mp3_path = os.path.join(
        UPLOAD_DIR,
        uid + ".mp3"
    )

    midi_path = os.path.join(
        OUTPUT_DIR,
        uid + ".mid"
    )


    with open(mp3_path,"wb") as f:
        f.write(uploaded.read())


    st.success("MP3 上傳完成")
    st.write("檔案名稱：", uploaded.name)



    # ==========================
    # 1. BasicPitch
    # ==========================

    st.info("BasicPitch 分析音樂...")


    result = subprocess.run(
        [
            "python",
            "basicpitch_convert.py",
            mp3_path,
            midi_path
        ],
        capture_output=True,
        text=True
    )


    if result.returncode != 0:

        st.error("BasicPitch 失敗")
        st.code(result.stderr)
        st.stop()


    st.success("MIDI 產生成功")


    # ==========================
    # 2. MIDI → MusicXML
    # ==========================

    musicxml = os.path.join(
        OUTPUT_DIR,
        uid + ".musicxml"
    )


    st.info("MIDI 轉 MusicXML...")


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


    if result.returncode != 0:

        st.error("MusicXML 失敗")
        st.code(result.stderr)
        st.stop()


    st.success("MusicXML 完成")



    # ==========================
    # 3. Clean MusicXML
    # ==========================

    clean_xml = os.path.join(
        OUTPUT_DIR,
        uid + "_clean.musicxml"
    )


    st.info("清理 MusicXML...")


    result = subprocess.run(
        [
            "python",
            "clean_musicxml.py",
            musicxml,
            clean_xml
        ],
        capture_output=True,
        text=True
    )


    if result.returncode != 0:

        st.error("Clean 失敗")
        st.code(result.stderr)
        st.stop()


    st.success("Clean 完成")



    # ==========================
    # 4. Jianpu 修正
    # ==========================

    final_xml = os.path.join(
        OUTPUT_DIR,
        uid + "_final.musicxml"
    )


    st.info("產生簡譜格式...")


    result = subprocess.run(
        [
            "python",
            "jianpu_fix_musicxml.py",
            clean_xml,
            final_xml
        ],
        capture_output=True,
        text=True
    )


    if result.returncode != 0:

        st.error("簡譜修正失敗")
        st.code(result.stderr)
        st.stop()


    st.success("簡譜 MusicXML 完成")



    # ==========================
    # 5. jianpu-ly
    # ==========================

    st.info("產生 LilyPond...")


    result = subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            final_xml
        ],
        capture_output=True,
        text=True
    )


    if result.returncode != 0:

        st.error("jianpu_ly 失敗")
        st.code(result.stderr)
        st.stop()



    ly_file = final_xml.replace(
        ".musicxml",
        ".ly"
    )


    if not os.path.exists(ly_file):

        st.error("找不到 ly 檔")
        st.stop()


    st.success("LY 完成")



    # ==========================
    # 6. LilyPond PDF
    # ==========================

    st.info("LilyPond 產生 PDF...")


    result = subprocess.run(
        [
            "lilypond",
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

        st.success("🎉 簡譜 PDF 完成")


        with open(pdf_file,"rb") as f:

            st.download_button(
                label="⬇️ 下載簡譜 PDF",
                data=f,
                file_name=os.path.basename(pdf_file),
                mime="application/pdf"
            )


    else:

        st.error("PDF 產生失敗")
        st.code(result.stderr)