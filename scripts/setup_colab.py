import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path("/content/financial-meeting-signoff-ai")


def run(cmd):
    print(f"\n>>> {cmd}")
    subprocess.run(cmd, shell=True, check=True)


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

    print("完成：Colab 環境已設定")


if __name__ == "__main__":
    main()
