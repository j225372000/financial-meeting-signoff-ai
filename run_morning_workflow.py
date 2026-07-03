import os
from pathlib import Path

from src.core.context import PlatformContext
from src.core.workflow_engine import WorkflowEngine


BASE_DIR = "/content/drive/MyDrive/會議紀錄自動化"
NEWS_INPUT_DIR = f"{BASE_DIR}/input/morning/news"
OUTPUT_DIR = f"{BASE_DIR}/output/morning"


def read_text_safely(path):
    encodings = ["utf-8", "utf-8-sig", "cp950", "big5", "latin-1"]

    for enc in encodings:
        try:
            return Path(path).read_text(encoding=enc)
        except UnicodeDecodeError:
            continue

    raise ValueError(f"無法判斷檔案編碼：{path}")


def load_news_text():
    folder = Path(NEWS_INPUT_DIR)

    if not folder.exists():
        raise FileNotFoundError(f"找不到新聞資料夾：{NEWS_INPUT_DIR}")

    files = sorted([
        p for p in folder.iterdir()
        if p.is_file()
        and not p.name.startswith("~$")
        and p.suffix.lower() in [".txt", ".md"]
    ])

    if not files:
        raise FileNotFoundError(
            f"新聞資料夾內沒有 .txt 或 .md 檔案：{NEWS_INPUT_DIR}"
        )

    contents = []

    for file in files:
        text = read_text_safely(file)
        contents.append(
            f"\n\n===== 新聞檔案：{file.name} =====\n\n{text}"
        )

    return "\n".join(contents)


def save_text(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")


def main():
    if not os.environ.get("GOOGLE_API_KEY"):
        raise RuntimeError("缺少 GOOGLE_API_KEY，請先設定環境變數。")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    context = PlatformContext()

    news_text = load_news_text()

    context.set("input", "news_text", news_text)
    context.set("output", "txt_path", f"{OUTPUT_DIR}/final_morning_brief_yaml.txt")
    context.set("output", "docx_path", f"{OUTPUT_DIR}/final_morning_brief_yaml.docx")

    engine = WorkflowEngine("workflows/morning.yaml")

    result = engine.run(context)

    final_text = result.get("output", "final_text")
    txt_path = result.get("output", "txt_path")

    save_text(txt_path, final_text)

    print("\n完成 Morning YAML Workflow")
    print(result.to_dict())


if __name__ == "__main__":
    main()
