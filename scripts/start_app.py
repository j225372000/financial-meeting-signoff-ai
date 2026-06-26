import re
import time
import subprocess
from pathlib import Path


PROJECT_ROOT = Path("/content/financial-meeting-signoff-ai")
STREAMLIT_LOG = Path("/content/streamlit.log")
CLOUDFLARE_LOG = Path("/content/cloudflare.log")


def run_background(cmd, log_path):
    with open(log_path, "w") as f:
        subprocess.Popen(
            cmd,
            shell=True,
            cwd=PROJECT_ROOT,
            stdout=f,
            stderr=f
        )


def main():
    print("Step 1：啟動 Streamlit")

    run_background(
        "streamlit run app.py --server.port 8501 --server.address 0.0.0.0",
        STREAMLIT_LOG
    )

    time.sleep(5)

    print("Step 2：啟動 Cloudflare Tunnel")

    run_background(
        "./cloudflared tunnel --url http://localhost:8501",
        CLOUDFLARE_LOG
    )

    print("Step 3：等待網址產生")

    url = None

    for _ in range(30):
        time.sleep(2)

        if CLOUDFLARE_LOG.exists():
            text = CLOUDFLARE_LOG.read_text(errors="ignore")
            match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", text)

            if match:
                url = match.group(0)
                break

    if url:
        print("\nFinancial AI Toolbox 已啟動：")
        print(url)
    else:
        print("尚未取得網址，請查看 /content/cloudflare.log")


if __name__ == "__main__":
    main()
