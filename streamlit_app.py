import streamlit as st
import traceback


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)


st.title("🎵 JianpuTool")
st.write("BasicPitch 測試")


try:

    from basic_pitch.inference import predict

    st.success(
        "✅ BasicPitch import 成功"
    )


except Exception:

    st.error(
        "❌ BasicPitch 載入失敗"
    )

    st.code(
        traceback.format_exc()
    )