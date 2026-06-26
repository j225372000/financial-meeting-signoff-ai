import streamlit as st

st.title("writing_toolbox.py")
st.caption("即時處理一段文字，不是完整工作流。")

skill = st.selectbox(
    "選擇寫作工具",
    [
        "金融專業潤飾",
        "公文助手",
        "市場分析",
        "簡報文字",
        "摘要整理",
        "英文翻譯",
        "一句話精簡",
        "內容擴充",
        "條列整理"
    ]
)

input_text = st.text_area(
    "請貼上要處理的文字",
    height=220
)

st.button("開始處理", type="primary")

st.info("下一階段會接上 Gemini，依不同 Skill 套用不同 Prompt。")
