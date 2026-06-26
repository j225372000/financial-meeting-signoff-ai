import subprocess
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent

st.title("Automation")
st.caption("固定流程自動化：Input → AI → Output。")

job = st.radio(
    "選擇自動化工作",
    [
        "會議紀錄簽文",
        "FOMC 即時晨報",
        "每日金融晨報"
    ]
)

if job == "會議紀錄簽文":
    command = ["python", "src/main.py"]
    output_file = "/content/drive/MyDrive/會議紀錄自動化/output/meeting/final_signoff.docx"

elif job == "FOMC 即時晨報":
    mode = st.selectbox(
        "FOMC 執行模式",
        ["full", "extract_only", "writer_only", "skip_analysis"]
    )
    command = ["python", "main_fomc.py", "--mode", mode]
    output_file = "/content/drive/MyDrive/會議紀錄自動化/output/fomc/fomc_morning_brief.docx"

else:
    command = ["python", "main_morning.py"]
    output_file = "/content/drive/MyDrive/會議紀錄自動化/output/morning/morning_brief.txt"

st.code(" ".join(command))

if st.button("開始執行", type="primary"):
    with st.spinner("執行中，請稍候..."):
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )

    st.subheader("執行結果")
    st.text(result.stdout)

    if result.stderr:
        st.subheader("系統訊息")
        st.warning(result.stderr)

    if Path(output_file).exists():
        st.success("已產生輸出檔案")

        with open(output_file, "rb") as f:
            st.download_button(
                label="下載結果",
                data=f,
                file_name=Path(output_file).name
            )
    else:
        st.warning("尚未找到輸出檔案")
