import streamlit as st
import os


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵",
    layout="centered"
)


# =========================
# 首頁
# =========================

st.title("🎵 JianpuTool")

st.write(
    """
    ## MP3 → MIDI → MusicXML → 簡譜 PDF
    
    AI 音樂轉簡譜工具
    """
)


st.success("JianpuTool 啟動成功")


# =========================
# 上傳區
# =========================

st.subheader("🎧 上傳 MP3")


uploaded_file = st.file_uploader(
    "選擇 MP3 檔案",
    type=["mp3"]
)


if uploaded_file:

    st.success("MP3 上傳完成")

    st.write(
        "檔案名稱：",
        uploaded_file.name
    )

    st.write(
        "檔案大小：",
        round(uploaded_file.size / 1024 / 1024, 2),
        "MB"
    )


    # 暫存
    os.makedirs(
        "uploads",
        exist_ok=True
    )


    save_path = os.path.join(
        "uploads",
        uploaded_file.name
    )


    with open(save_path, "wb") as f:
        f.write(
            uploaded_file.getbuffer()
        )


    st.info(
        "等待轉換流程..."
    )


# =========================
# 狀態
# =========================

st.divider()

st.write(
    """
    目前流程：

    ✅ MP3 上傳
    
    ⏳ BasicPitch → MIDI
    
    ⏳ MIDI → MusicXML
    
    ⏳ MusicXML → Jianpu
    
    ⏳ LilyPond → PDF
    """
)