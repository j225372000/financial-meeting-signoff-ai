import streamlit as st

st.set_page_config(
    page_title="Financial AI Toolbox",
    layout="wide"
)

st.title("Financial AI Toolbox")
st.caption("把重複性的金融工作，做成可一鍵執行的 AI 工具。")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("✍️ Writing Toolbox")
    st.write("金融專業潤飾、公文、摘要、市場分析、翻譯。")
    st.page_link(
        "pages/1_✍️_Writing_Toolbox.py",
        label="進入 Writing Toolbox",
        icon="✍️"
    )

with col2:
    st.subheader("⚙️ Automation")
    st.write("會議紀錄、FOMC、每日晨報等固定流程。")
    st.page_link(
        "pages/2_⚙️_Automation.py",
        label="進入 Automation",
        icon="⚙️"
    )

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("🧠 AI Skills")
    st.write("管理 AI 能力、Prompt、模型與版本。")
    st.page_link(
        "pages/3_🧠_AI_Skills.py",
        label="進入 AI Skills",
        icon="🧠"
    )

with col4:
    st.subheader("⚙️ Settings")
    st.write("API、Google Drive、模型與系統設定。")
    st.page_link(
        "pages/4_⚙️_Settings.py",
        label="進入 Settings",
        icon="⚙️"
    )
