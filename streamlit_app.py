import streamlit as st
import requests
import uuid


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


st.title("🎵 JianpuTool")

st.write(
    "MP3 → MIDI → MusicXML → 簡譜 PDF"
)


# 改成你的 Cloudflare Tunnel 網址
API_URL = "https://你的網址.trycloudflare.com/convert"


uploaded_file = st.file_uploader(
    "上傳 MP3",
    type=["mp3"]
)


if uploaded_file:

    st.success("MP3 上傳完成")

    st.write(
        "檔案名稱：",
        uploaded_file.name
    )


    if st.button("開始轉換"):

        with st.spinner("正在分析音樂..."):

            try:

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "audio/mpeg"
                    )
                }


                response = requests.post(
                    API_URL,
                    files=files,
                    timeout=600
                )


                if response.status_code == 200:

                    st.success(
                        "簡譜 PDF 產生完成"
                    )


                    st.download_button(
                        label="下載簡譜 PDF",
                        data=response.content,
                        file_name="jianpu.pdf",
                        mime="application/pdf"
                    )


                else:

                    st.error(
                        "轉換失敗"
                    )

                    st.code(
                        response.text
                    )


            except Exception as e:

                st.error(
                    "連線錯誤"
                )

                st.code(
                    str(e)
                )