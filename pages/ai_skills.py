import streamlit as st

st.title("ai_skills")
st.caption("管理 AI 能力。V1 先作為 Skill 清單，暫不開放編輯。")

skills = [
    "金融專業潤飾",
    "公文助手",
    "市場分析",
    "簡報文字",
    "摘要整理",
    "英文翻譯",
    "會議紀錄簽文",
    "FOMC 即時晨報",
    "每日金融晨報"
]

for skill in skills:
    with st.container(border=True):
        st.subheader(skill)
        st.write("狀態：啟用")
        st.write("版本：v1.0")
