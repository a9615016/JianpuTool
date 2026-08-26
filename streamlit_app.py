import streamlit as st
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime


# ============================================================
# JianpuTool Professional MVP 3.0
#
# MP3 / WAV / M4A / FLAC
#       ↓
# Demucs 人聲分離
#       ↓
# BasicPitch 主旋律 MIDI
#       ↓
# Melody Clean
#       ↓
# MIDI -> MusicXML
#       ↓
# MusicXML Duration Fix
#       ↓
# jianpu-ly
#       ↓
# LilyPond
#       ↓
# 數字簡譜 PDF
# ============================================================


# ============================================================
# Streamlit 設定
# ============================================================

st.set_page_config(
    page_title="JianpuTool Professional",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Session State
# ============================================================

if "result" not in st.session_state:
    st.session_state.result = None

if "running" not in st.session_state:
    st.session_state.running = False

if "last_error" not in st.session_state:
    st.session_state.last_error = None

if "voice_choice" not in st.session_state:
    st.session_state.voice_choice = "piano"


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        color: #777;
        margin-bottom: 20px;
    }

    .success-title {
        font-size: 30px;
        font-weight: 800;
    }

    .file-card {
        padding: 12px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 工具：檔案大小
# ============================================================

def human_size(path):

    path = Path(path)

    if not path.exists():
        return "-"

    size = path.stat().st_size

    if size < 1024:
        return f"{size:,} B"

    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"

    return f"{size / 1024 / 1024:.2f} MB"


# ============================================================
# 工具：讀檔
# ============================================================

def read_binary(path):

    path = Path(path)

    if not path.exists():
        return None

    with open(path, "rb") as f:
        return f.read()


# ============================================================
# 建立 ZIP
# ============================================================

def create_zip(workdir):

    workdir = Path(workdir)

    zip_path = workdir / "jianputool_result.zip"

    files_to_zip = [

        "vocals.wav",

        "raw_melody.mid",

        "clean_melody.mid",

        "final.musicxml",

        "final_fixed.musicxml",

        "score.ly",

        "jianpu.pdf",

        "song.mp3",

    ]

    added = 0

    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as z:

        for filename in files_to_zip:

            path = workdir / filename

            if path.is_file():

                z.write(
                    path,
                    arcname=filename,
                )

                added += 1

    if added == 0:

        raise RuntimeError(
            "沒有結果檔案可以加入 ZIP"
        )

    return zip_path


# ============================================================
# 結果檔案狀態
# ============================================================

def show_file_status(
    workdir,
    filename,
    label,
):

    path = Path(workdir) / filename

    if path.exists():

        st.success(
            f"✅ {label}："
            f"`{filename}`"
            f"  ({human_size(path)})"
        )

        return True

    st.warning(
        f"⚠️ {label}：尚未產生"
    )

    return False


# ============================================================
# 下載區
# ============================================================

def show_downloads(result):

    if not result:
        return

    workdir = Path(
        result["workdir"]
    )

    st.divider()

    st.header(
        "📥 下載結果"
    )

    # ========================================================
    # PDF
    # ========================================================

    pdf_path = (
        workdir / "jianpu.pdf"
    )

    if pdf_path.exists():

        st.download_button(

            label="📄 下載數字簡譜 PDF",

            data=read_binary(
                pdf_path
            ),

            file_name="jianpu.pdf",

            mime="application/pdf",

            use_container_width=True,

            type="primary",

            key="download_pdf_mvp30",
        )

    # ========================================================
    # MP3
    # ========================================================

    mp3_path = result.get(
        "mp3"
    )

    if (
        mp3_path
        and Path(mp3_path).exists()
    ):

        mp3_data = read_binary(
            mp3_path
        )

        st.audio(
            mp3_data,
            format="audio/mpeg",
        )

        st.download_button(

            label="🎧 下載合成 MP3",

            data=mp3_data,

            file_name="song.mp3",

            mime="audio/mpeg",

            use_container_width=True,

            key="download_mp3_mvp30",
        )

    # ========================================================
    # MIDI
    # ========================================================

    col1, col2 = st.columns(2)

    raw_midi = (
        workdir / "raw_melody.mid"
    )

    clean_midi = (
        workdir / "clean_melody.mid"
    )

    with col1:

        if raw_midi.exists():

            st.download_button(

                label="🎹 下載 raw_melody.mid",

                data=read_binary(
                    raw_midi
                ),

                file_name="raw_melody.mid",

                mime="audio/midi",

                use_container_width=True,

                key="download_raw_midi_mvp30",
            )

    with col2:

        if clean_midi.exists():

            st.download_button(

                label="🎼 下載 clean_melody.mid",

                data=read_binary(
                    clean_midi
                ),

                file_name="clean_melody.mid",

                mime="audio/midi",

                use_container_width=True,

                key="download_clean_midi_mvp30",
            )

    # ========================================================
    # MusicXML
    # ========================================================

    col1, col2 = st.columns(2)

    final_xml = (
        workdir / "final.musicxml"
    )

    fixed_xml = (
        workdir / "final_fixed.musicxml"
    )

    with col1:

        if final_xml.exists():

            st.download_button(

                label="🎼 下載 final.musicxml",

                data=read_binary(
                    final_xml
                ),

                file_name="final.musicxml",

                mime="application/xml",

                use_container_width=True,

                key="download_final_xml_mvp30",
            )

    with col2:

        if fixed_xml.exists():

            st.download_button(

                label="🛠️ 下載 final_fixed.musicxml",

                data=read_binary(
                    fixed_xml
                ),

                file_name="final_fixed.musicxml",

                mime="application/xml",

                use_container_width=True,

                key="download_fixed_xml_mvp30",
            )

    # ========================================================
    # ZIP
    # ========================================================

    try:

        zip_path = create_zip(
            workdir
        )

        st.download_button(

            label="📦 下載全部結果 ZIP",

            data=read_binary(
                zip_path
            ),

            file_name="jianputool_result.zip",

            mime="application/zip",

            use_container_width=True,

            key="download_zip_mvp30",
        )

        st.caption(
            "ZIP 會自動包含目前實際產生的 "
            "MIDI、MusicXML、PDF、MP3、LilyPond 等檔案。"
        )

    except Exception as e:

        st.warning(
            f"ZIP 建立失敗：{e}"
        )


# ============================================================
# Header
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🎵 JianpuTool Professional'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'MP3 / WAV → 主旋律 MIDI → 數字簡譜 PDF'
    '</div>',
    unsafe_allow_html=True,
)

st.info(
    "🎯 Professional MVP 3.0："
    "自動人聲分離、主旋律擷取、"
    "MIDI 清理、MusicXML 修正、"
    "數字簡譜 PDF，以及完整結果下載。"
)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.header(
        "⚙️ 轉換設定"
    )

    voice_choice = st.selectbox(

        "🎙️ 合成音色",

        options=[
            "piano",
            "la",
            "flute",
            "strings",
        ],

        format_func=lambda v: {

            "piano": "🎹 鋼琴",

            "la": "🎤 哼唱人聲（La）",

            "flute": "🪈 長笛",

            "strings": "🎻 弦樂",

        }[v],

        key="voice_choice",
    )

    st.divider()

    st.markdown(
        "### 🔄 轉換流程"
    )

    st.markdown(
        """
        1. 🎤 人聲分離
        2. 🎹 主旋律 MIDI
        3. 🧹 旋律清理
        4. 🎼 MusicXML
        5. 🛠️ Duration 修正
        6. 🔢 數字簡譜
        7. 📄 PDF
        """
    )

    st.divider()

    st.caption(
        "JianpuTool Professional MVP 3.0"
    )


# ============================================================
# Upload
# ============================================================

uploaded_file = st.file_uploader(

    "🎵 上傳音檔",

    type=[
        "mp3",
        "wav",
        "m4a",
        "flac",
    ],

    help=(
        "建議使用人聲清楚、"
        "背景伴奏較少的音檔。"
    ),
)


if uploaded_file:

    st.success(
        f"已選擇：{uploaded_file.name}"
    )

    with st.expander(
        "🎧 預覽原始音檔",
        expanded=True,
    ):

        st.audio(
            uploaded_file.getvalue(),
            format=uploaded_file.type,
        )

    st.divider()

    start_button = st.button(

        "🚀 開始完整轉換",

        type="primary",

        use_container_width=True,

        disabled=st.session_state.running,
    )

    if start_button:

        st.session_state.running = True

        st.session_state.last_error = None

        st.session_state.result = None

        # ====================================================
        # 工作目錄
        # ====================================================

        workdir = Path(
            tempfile.mkdtemp(
                prefix="jianputool_"
            )
        )

        input_ext = Path(
            uploaded_file.name
        ).suffix.lower()

        input_audio = (
            workdir /
            f"input{input_ext}"
        )

        with open(
            input_audio,
            "wb"
        ) as f:

            f.write(
                uploaded_file.getvalue()
            )

        # ====================================================
        # Progress
        # ====================================================

        st.subheader(
            "🔄 轉換進度"
        )

        progress = st.progress(
            0
        )

        status = st.empty()

        detail = st.empty()

        try:

            import pipeline

            status.info(
                "🎵 初始化 Pipeline..."
            )

            detail.write(
                f"工作目錄：`{workdir}`"
            )

            progress.progress(
                5
            )

            # =================================================
            # Pipeline
            # =================================================

            status.info(
                "⚙️ 正在執行完整 Pipeline..."
            )

            detail.write(
                "Demucs → BasicPitch → "
                "Melody Clean → MusicXML → "
                "Duration Fix → jianpu-ly → LilyPond"
            )

            progress.progress(
                10
            )

            pdf_path = (
                pipeline.convert_pipeline(
                    str(input_audio),
                    str(workdir),
                )
            )

            progress.progress(
                85
            )

            # =================================================
            # MIDI -> MP3
            # =================================================

            mp3_path = None

            clean_midi_path = (
                workdir /
                "clean_melody.mid"
            )

            if clean_midi_path.exists():

                status.info(
                    "🎧 正在合成主旋律 MP3..."
                )

                try:

                    import midi_to_mp3

                    mp3_path = (
                        workdir /
                        "song.mp3"
                    )

                    midi_to_mp3.render_mp3(

                        str(
                            clean_midi_path
                        ),

                        str(
                            mp3_path
                        ),

                        voice=voice_choice,
                    )

                    if not mp3_path.exists():

                        mp3_path = None

                except Exception as mp3_error:

                    st.warning(
                        "⚠️ MP3 合成失敗，"
                        "但不影響簡譜 PDF："
                        f"{mp3_error}"
                    )

                    mp3_path = None

            # =================================================
            # 最終檢查
            # =================================================

            progress.progress(
                95
            )

            status.info(
                "🔍 正在檢查輸出..."
            )

            required_files = [

                "clean_melody.mid",

                "jianpu.pdf",

            ]

            missing = [

                filename

                for filename in required_files

                if not (
                    workdir /
                    filename
                ).exists()

            ]

            if missing:

                raise RuntimeError(

                    "Pipeline 執行完成，"
                    "但缺少必要輸出："
                    + ", ".join(missing)

                )

            progress.progress(
                100
            )

            status.success(
                "🎉 完整轉換成功！"
            )

            detail.success(
                "MP3 → 主旋律 MIDI → "
                "MusicXML → 數字簡譜 PDF 完成"
            )

            # =================================================
            # 儲存結果
            # =================================================

            st.session_state.result = {

                "workdir": str(
                    workdir
                ),

                "pdf": str(
                    pdf_path
                ),

                "mp3": (
                    str(mp3_path)
                    if mp3_path
                    else None
                ),

                "input": str(
                    input_audio
                ),

                "original_name":
                    uploaded_file.name,

                "created_at":
                    datetime.now().isoformat(),

            }

            st.session_state.running = False

            st.balloons()

        except Exception as e:

            st.session_state.running = False

            st.session_state.result = None

            st.session_state.last_error = str(
                e
            )

            progress.progress(
                100
            )

            status.error(
                "❌ 轉換失敗"
            )

            with st.expander(
                "🔎 查看完整錯誤資訊",
                expanded=True,
            ):

                st.exception(
                    e
                )


# ============================================================
# Result
# ============================================================

if st.session_state.result:

    result = (
        st.session_state.result
    )

    workdir = Path(
        result["workdir"]
    )

    st.divider()

    st.markdown(
        '<div class="success-title">'
        '🎉 轉換完成'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        f"原始檔案："
        f"{result.get('original_name', '-')}"
    )

    # ========================================================
    # Output status
    # ========================================================

    st.subheader(
        "📊 輸出結果"
    )

    output_files = [

        (
            "vocals.wav",
            "🎤 人聲 WAV",
        ),

        (
            "raw_melody.mid",
            "🎹 主旋律 MIDI",
        ),

        (
            "clean_melody.mid",
            "🎼 整理後 MIDI",
        ),

        (
            "final.musicxml",
            "🎼 原始 MusicXML",
        ),

        (
            "final_fixed.musicxml",
            "🛠️ 修正後 MusicXML",
        ),

        (
            "score.ly",
            "🎵 LilyPond score",
        ),

        (
            "jianpu.pdf",
            "📄 數字簡譜 PDF",
        ),

        (
            "song.mp3",
            "🎧 合成 MP3",
        ),

    ]

    for filename, label in output_files:

        show_file_status(
            workdir,
            filename,
            label,
        )

    # ========================================================
    # PDF Preview
    # ========================================================

    pdf_path = (
        workdir /
        "jianpu.pdf"
    )

    if pdf_path.exists():

        st.divider()

        st.subheader(
            "📄 數字簡譜預覽"
        )

        try:

            pdf_bytes = read_binary(
                pdf_path
            )

            st.pdf(
                pdf_bytes
            )

        except Exception as e:

            st.warning(
                "PDF 預覽失敗，"
                "但 PDF 已成功產生："
                f"{e}"
            )

    # ========================================================
    # Downloads
    # ========================================================

    show_downloads(
        result
    )

    # ========================================================
    # MuseScore
    # ========================================================

    st.divider()

    st.info(
        "💡 想進一步修改樂譜時，"
        "可以下載 `final_fixed.musicxml`，"
        "再使用 MuseScore 4 開啟與編輯。"
    )


# ============================================================
# 首頁
# ============================================================

if (
    not uploaded_file
    and not st.session_state.result
):

    st.divider()

    st.subheader(
        "✨ JianpuTool 可以做什麼？"
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.markdown(
            """
            ### 🎤 主旋律擷取

            從音檔分離人聲，
            再使用 AI 擷取主旋律。
            """
        )

    with col2:

        st.markdown(
            """
            ### 🎼 MIDI / MusicXML

            自動整理旋律，
            產生可編輯的 MIDI
            與 MusicXML。
            """
        )

    with col3:

        st.markdown(
            """
            ### 🔢 數字簡譜

            自動產生數字簡譜 PDF，
            並提供完整 ZIP 下載。
            """
        )

    st.divider()

    st.info(
        "📌 建議使用人聲清楚、"
        "背景伴奏較少的音檔，"
        "通常比較容易得到乾淨的主旋律。"
    )


# ============================================================
# Footer
# ============================================================

st.divider()

st.caption(
    "JianpuTool Professional MVP 3.0 | "
    "MP3/WAV → 主旋律 MIDI → MusicXML → "
    "數字簡譜 PDF"
)