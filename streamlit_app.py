import streamlit as st
import os
import sys
import tempfile
import zipfile
from pathlib import Path

# ============================================================
# JianpuTool Streamlit Web UI
# MP3/WAV -> Demucs -> BasicPitch -> MIDI -> MusicXML -> Jianpu PDF
# ============================================================

st.set_page_config(
    page_title="JianpuTool - MP3 轉數字簡譜",
    page_icon="🎵",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

# ============================================================
# 頁面標題
# ============================================================

st.title("🎵 JianpuTool")
st.subheader("MP3 / WAV → 主旋律 MIDI → 數字簡譜 PDF")

st.info(
    "完整流程："
    "Demucs 人聲分離 → BasicPitch 主旋律 MIDI → "
    "旋律清理 → MusicXML → 數字簡譜 PDF"
)

# ============================================================
# 上傳音檔
# ============================================================

uploaded_file = st.file_uploader(
    "上傳 MP3 或 WAV 音檔",
    type=["mp3", "wav", "m4a", "flac"],
    help="建議使用人聲清楚、背景伴奏較少的音檔。"
)

st.selectbox(
    "🎙️ 合成音色（用於重新輸出 MP3）",
    options=["piano", "la", "flute", "strings"],
    format_func=lambda v: {
        "piano": "鋼琴",
        "la": "哼唱人聲（La）",
        "flute": "長笛",
        "strings": "弦樂",
    }[v],
    key="voice_choice",
)

# ============================================================
# 初始化 Session State
# ============================================================

if "result" not in st.session_state:
    st.session_state.result = None


# ============================================================
# 建立 ZIP
# ============================================================

def create_zip(workdir):
    """
    將轉換結果打包成 ZIP
    """

    workdir = Path(workdir)

    zip_path = workdir / "jianputool_result.zip"

    files_to_zip = [
        "vocals.wav",
        "raw_melody.mid",
        "clean_melody.mid",
        "final.musicxml",
        "jianpu.pdf",
        "song.mp3",
    ]

    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED
    ) as z:

        for filename in files_to_zip:

            file_path = workdir / filename

            if file_path.exists():
                z.write(
                    file_path,
                    arcname=filename
                )

    return zip_path


# ============================================================
# 顯示下載按鈕
# ============================================================

def show_downloads(result):

    if not result:
        return

    workdir = Path(result["workdir"])

    st.divider()
    st.subheader("📥 下載結果")

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    pdf_path = workdir / "jianpu.pdf"

    if pdf_path.exists():

        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        st.download_button(
            label="📄 下載數字簡譜 PDF",
            data=pdf_data,
            file_name="jianpu.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="download_pdf"
        )

    # --------------------------------------------------------
    # MP3（合成音訊，反向流程新增）
    # --------------------------------------------------------

    mp3_path = result.get("mp3")

    if mp3_path and Path(mp3_path).exists():

        with open(mp3_path, "rb") as f:
            mp3_data = f.read()

        st.audio(mp3_data, format="audio/mp3")

        st.download_button(
            label="🎧 下載合成 MP3（依主旋律 MIDI 重新演奏）",
            data=mp3_data,
            file_name="song.mp3",
            mime="audio/mpeg",
            use_container_width=True,
            key="download_mp3"
        )

    # --------------------------------------------------------
    # Raw MIDI
    # --------------------------------------------------------

    raw_midi = workdir / "raw_melody.mid"

    if raw_midi.exists():

        with open(raw_midi, "rb") as f:
            raw_midi_data = f.read()

        st.download_button(
            label="🎹 下載 raw_melody.mid（主旋律 MIDI）",
            data=raw_midi_data,
            file_name="raw_melody.mid",
            mime="audio/midi",
            use_container_width=True,
            key="download_raw_midi"
        )

    # --------------------------------------------------------
    # Clean MIDI
    # --------------------------------------------------------

    clean_midi = workdir / "clean_melody.mid"

    if clean_midi.exists():

        with open(clean_midi, "rb") as f:
            clean_midi_data = f.read()

        st.download_button(
            label="🎼 下載 clean_melody.mid（整理後 MIDI）",
            data=clean_midi_data,
            file_name="clean_melody.mid",
            mime="audio/midi",
            use_container_width=True,
            key="download_clean_midi"
        )

    # --------------------------------------------------------
    # MusicXML
    # --------------------------------------------------------

    musicxml = workdir / "final.musicxml"

    if musicxml.exists():

        with open(musicxml, "rb") as f:
            musicxml_data = f.read()

        st.download_button(
            label="🎼 下載 final.musicxml",
            data=musicxml_data,
            file_name="final.musicxml",
            mime="application/xml",
            use_container_width=True,
            key="download_musicxml"
        )

    # --------------------------------------------------------
    # ZIP
    # --------------------------------------------------------

    try:

        zip_path = create_zip(workdir)

        with open(zip_path, "rb") as f:
            zip_data = f.read()

        st.success("📦 已建立完整結果 ZIP")

        st.download_button(
            label="📦 下載全部結果 ZIP",
            data=zip_data,
            file_name="jianputool_result.zip",
            mime="application/zip",
            use_container_width=True,
            key="download_zip"
        )

    except Exception as e:

        st.error(f"ZIP 建立失敗：{e}")


# ============================================================
# 主流程
# ============================================================

if uploaded_file:

    st.success(
        f"已選擇：{uploaded_file.name}"
    )

    st.audio(
        uploaded_file.getvalue(),
        format=uploaded_file.type
    )

    if st.button(
        "🚀 開始完整轉換",
        type="primary",
        use_container_width=True
    ):

        # ----------------------------------------------------
        # 建立暫存工作目錄
        # ----------------------------------------------------

        workdir = Path(
            tempfile.mkdtemp(
                prefix="jianputool_"
            )
        )

        input_ext = Path(
            uploaded_file.name
        ).suffix.lower()

        input_audio = workdir / f"input{input_ext}"

        with open(input_audio, "wb") as f:
            f.write(
                uploaded_file.getvalue()
            )

        st.write(
            f"工作目錄：`{workdir}`"
        )

        # ----------------------------------------------------
        # Pipeline
        # ----------------------------------------------------

        try:

            import pipeline

            progress = st.progress(0)

            status = st.empty()

            status.info(
                "🎵 開始轉換..."
            )

            progress.progress(5)

            # ------------------------------------------------
            # 執行完整 Pipeline
            # ------------------------------------------------

            pdf_path = pipeline.convert_pipeline(
                str(input_audio),
                str(workdir)
            )

            progress.progress(85)

            # ------------------------------------------------
            # 反向流程：clean_melody.mid -> 合成 MP3
            # ------------------------------------------------

            mp3_path = None
            clean_midi_path = Path(workdir) / "clean_melody.mid"

            if clean_midi_path.exists():
                try:
                    import midi_to_mp3
                    mp3_path = str(Path(workdir) / "song.mp3")
                    midi_to_mp3.render_mp3(
                        str(clean_midi_path),
                        mp3_path,
                        voice=st.session_state.get("voice_choice", "piano"),
                    )
                except Exception as mp3_err:
                    st.warning(f"⚠ MP3 合成失敗（不影響簡譜 PDF）：{mp3_err}")
                    mp3_path = None

            progress.progress(100)

            status.success(
                "🎉 完整轉換成功！"
            )

            # ------------------------------------------------
            # 儲存結果
            # ------------------------------------------------

            result = {
                "workdir": str(workdir),
                "pdf": str(pdf_path),
                "mp3": mp3_path,
                "input": str(input_audio)
            }

            st.session_state.result = result

            st.success(
                "✅ MP3 → 主旋律 MIDI → 數字簡譜 PDF 完成"
            )

        except Exception as e:

            st.session_state.result = None

            st.error(
                "❌ 轉換失敗"
            )

            st.exception(e)


# ============================================================
# 顯示結果
# ============================================================

if st.session_state.result:

    result = st.session_state.result

    workdir = Path(
        result["workdir"]
    )

    st.divider()

    st.header("🎉 轉換完成")

    # ========================================================
    # 檢查檔案
    # ========================================================

    files = [
        ("vocals.wav", "🎤 人聲 WAV"),
        ("raw_melody.mid", "🎹 主旋律 MIDI"),
        ("clean_melody.mid", "🎼 整理後 MIDI"),
        ("final.musicxml", "🎼 MusicXML"),
        ("jianpu.pdf", "📄 數字簡譜 PDF"),
    ]

    for filename, label in files:

        path = workdir / filename

        if path.exists():

            size = path.stat().st_size

            st.write(
                f"✅ {label}：`{filename}` "
                f"（{size:,} bytes）"
            )

        else:

            st.write(
                f"⚠️ {label}：尚未產生"
            )

    # ========================================================
    # PDF 預覽
    # ========================================================

    pdf_path = workdir / "jianpu.pdf"

    if pdf_path.exists():

        st.divider()

        st.subheader("📄 數字簡譜預覽")

        try:

            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.pdf(
                pdf_bytes
            )

        except Exception as e:

            st.warning(
                f"PDF 預覽失敗，但 PDF 檔案已成功產生：{e}"
            )

    # ========================================================
    # 下載
    # ========================================================

    show_downloads(result)


# ============================================================
# 頁尾
# ============================================================

st.divider()

st.caption(
    "JianpuTool | MP3/WAV → 主旋律 MIDI → 數字簡譜 PDF"
)
