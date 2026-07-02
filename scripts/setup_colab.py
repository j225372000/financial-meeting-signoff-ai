import os
import subprocess
from pathlib import Path

from google.colab import userdata


PROJECT_ROOT = Path("/content/financial-meeting-signoff-ai")


def run(cmd):
    print(f"\n>>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def setup_google_api():

    print("Step 3：設定 GOOGLE_API_KEY")

    api_key = userdata.get("GOOGLE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "找不到 GOOGLE_API_KEY，請先到 Colab Secrets 建立。"
        )

    os.environ["GOOGLE_API_KEY"] = api_key

    print("✓ GOOGLE_API_KEY 已載入")


def main():

    print("Step 1：安裝套件")
    run(f"pip install -r {PROJECT_ROOT / 'requirements.txt'}")

    print("Step 2：確認 cloudflared")
    cloudflared_path = PROJECT_ROOT / "cloudflared"

    if not cloudflared_path.exists():
        run(
            f"wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 "
            f"-O {cloudflared_path}"
        )
        run(f"chmod +x {cloudflared_path}")

    setup_google_api()

    print("\n✓ Colab 環境初始化完成")


if __name__ == "__main__":
    main()
