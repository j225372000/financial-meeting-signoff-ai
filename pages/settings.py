import streamlit as st

st.title("Settings")
st.caption("系統設定。V1 先顯示目前設定，不在網頁修改。")

st.subheader("Google Drive")
st.code("/content/drive/MyDrive/會議紀錄自動化")

st.subheader("模型")
st.code("models/gemini-2.5-flash-lite")

st.subheader("輸出資料夾")
st.code("""
output/meeting
output/fomc
output/morning
""")
