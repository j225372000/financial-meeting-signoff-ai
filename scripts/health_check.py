import os
from pathlib import Path
import requests


PROJECT_ROOT = Path("/content/financial-meeting-signoff-ai")
DRIVE_DIR = Path("/content/drive/MyDrive/會議紀錄自動化")


def check(name, condition):
    mark = "✅" if condition else "❌"
    print(f"{mark} {name}")


def main():
    print("Health Check")

    check("專案資料夾", PROJECT_ROOT.exists())
    check("app.py", (PROJECT_ROOT / "app.py").exists())
    check("pages", (PROJECT_ROOT / "pages").exists())
    check("requirements.txt", (PROJECT_ROOT / "requirements.txt").exists())

    check("Google Drive 資料夾", DRIVE_DIR.exists())

    check("templates/meeting", (PROJECT_ROOT / "templates" / "meeting").exists())
    check("templates/fomc", (PROJECT_ROOT / "templates" / "fomc").exists())
    check("templates/morning", (PROJECT_ROOT / "templates" / "morning").exists())

    check("GOOGLE_API_KEY", bool(os.environ.get("GOOGLE_API_KEY")))

    try:
        response = requests.get("http://localhost:8501", timeout=3)
        check("Streamlit localhost:8501", response.status_code == 200)
    except Exception:
        check("Streamlit localhost:8501", False)


if __name__ == "__main__":
    main()
