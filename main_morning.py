import os
import time
import importlib.util
from pathlib import Path

import google.generativeai as genai
from docx import Document
import pdfplumber


GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

BASE_DIR = "/content/drive/MyDrive/會議紀錄自動化"

MORNING_INPUT_DIR = f"{BASE_DIR}/input/morning/news"
MORNING_KNOWLEDGE_DIR = f"{BASE_DIR}/knowledge/morning"
MORNING_INTERMEDIATE_DIR = f"{BASE_DIR}/intermediate/morning"
MORNING_OUTPUT_DIR = f"{BASE_DIR}/output/morning"

MODEL_MAIN = "models/gemini-2.5-flash-lite"
MODEL_BACKUP = "models/gemini-2.5-flash-lite"


def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save_text(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def read_text_safely(path):
    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp950",
        "big5",
        "latin-1"
    ]

    for enc in encodings:
        try:
            return Path(path).read_text(encoding=enc)
        except UnicodeDecodeError:
            continue

    raise ValueError(f"無法判斷檔案編碼：{path}")


def read_docx(path):
    doc = Document(path)
    texts = []

    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            texts.append(paragraph.text.strip())

    return "\n".join(texts)


def read_pdf(path):
    texts = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                texts.append(page_text)

    return "\n".join(texts)


def read_file(path):
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in [".txt", ".md", ".json"]:
        return read_text_safely(path)

    if suffix == ".docx":
        return read_docx(path)

    if suffix == ".pdf":
        return read_pdf(path)

    raise ValueError(f"不支援格式：{suffix}")


def load_or_generate(path, generator_func):
    if os.path.exists(path):
        print(f"已存在，直接讀取：{path}")
        return read_text(path)

    print(f"不存在，開始產生：{path}")
    result = generator_func()
    save_text(path, result)
    return result


def generate_with_retry(prompt, model_name=MODEL_MAIN, retry=3):
    model = genai.GenerativeModel(model_name)

    for i in range(retry):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"第 {i + 1} 次失敗：{e}")
            time.sleep(30)

    print("改用備援模型")
    model = genai.GenerativeModel(MODEL_BACKUP)
    response = model.generate_content(prompt)
    return response.text


def load_all_news(folder):
    folder_path = Path(folder)

    if not folder_path.exists():
        raise FileNotFoundError(f"找不到新聞資料夾：{folder}")

    news_files = sorted([
        p for p in folder_path.iterdir()
        if p.is_file()
        and not p.name.startswith("~$")
        and p.suffix.lower() in [
            ".txt",
            ".md",
            ".docx",
            ".pdf"
        ]
    ])

    if not news_files:
        raise FileNotFoundError(
            f"新聞資料夾內沒有 .txt、.md、.docx 或 .pdf 檔案：{folder}"
        )

    contents = []

    for file in news_files:
        text = read_file(file)
        contents.append(f"\n\n===== {file.name} =====\n{text}")

    return "\n".join(contents)


def load_knowledge_folder(folder):
    folder_path = Path(folder)

    if not folder_path.exists():
        print(f"未提供知識庫資料夾：{folder}")
        return ""

    files = sorted([
        p for p in folder_path.glob("**/*")
        if p.is_file()
        and not p.name.startswith("~$")
        and p.suffix.lower() in [
            ".txt",
            ".md",
            ".json",
            ".docx",
            ".pdf"
        ]
    ])

    if not files:
        print("知識庫資料夾內沒有可讀取檔案")
        return ""

    contents = []

    for file in files:
        try:
            text = read_file(file)
            contents.append(f"\n\n===== {file.name} =====\n{text}")
        except Exception as e:
            print(f"讀取知識庫檔案失敗：{file}，原因：{e}")

    return "\n".join(contents)


def main():
    genai.configure(api_key=GOOGLE_API_KEY)

    classifier_agent = load_module(
        "classifier_agent",
        "src/agents/classifier_agent.py"
    )

    extractor_agent = load_module(
        "extractor_agent",
        "src/agents/extractor_agent.py"
    )

    knowledge_retriever_agent = load_module(
        "knowledge_retriever_agent",
        "src/agents/knowledge_retriever_agent.py"
    )

    writer_agent = load_module(
        "writer_agent",
        "src/agents/writer_agent.py"
    )

    print("Step 1：讀取晨報新聞與知識庫")

    news_text = load_all_news(MORNING_INPUT_DIR)
    knowledge_text = load_knowledge_folder(MORNING_KNOWLEDGE_DIR)

    print("新聞字數：", len(news_text))
    print("知識庫字數：", len(knowledge_text))

    classify_path = f"{MORNING_INTERMEDIATE_DIR}/classify_result.json"
    extract_path = f"{MORNING_INTERMEDIATE_DIR}/news_extract.json"
    knowledge_match_path = f"{MORNING_INTERMEDIATE_DIR}/knowledge_match.json"

    print("Step 2：執行 News Classifier Agent")

    classify_result = load_or_generate(
        classify_path,
        lambda: generate_with_retry(
            classifier_agent.classify(
                news_text,
                "templates/morning/classifier_prompt.txt"
            )
        )
    )

    print("Step 3：執行 News Extractor Agent")

    news_extract = load_or_generate(
        extract_path,
        lambda: generate_with_retry(
            extractor_agent.extract(
                news_text,
                "templates/morning/extractor_prompt.txt"
            )
        )
    )

    print("Step 4：執行 Knowledge Retriever Agent")

    knowledge_match = load_or_generate(
        knowledge_match_path,
        lambda: generate_with_retry(
            knowledge_retriever_agent.retrieve(
                news_extract,
                knowledge_text,
                "templates/morning/knowledge_retriever_prompt.txt"
            )
        )
    )

    print("Step 5：產生晨報講稿")

    morning_prompt = writer_agent.write(
        "templates/morning/writer_prompt.txt",
        {
            "新聞分類結果": classify_result,
            "新聞萃取結果": news_extract,
            "知識庫補充資料": knowledge_match
        }
    )

    morning_text = generate_with_retry(morning_prompt)

    txt_path = f"{MORNING_OUTPUT_DIR}/morning_brief.txt"

    save_text(txt_path, morning_text)

    print("完成！")
    print(f"中間成果：{MORNING_INTERMEDIATE_DIR}")
    print(f"分類結果：{classify_path}")
    print(f"新聞萃取：{extract_path}")
    print(f"知識庫比對：{knowledge_match_path}")
    print(f"晨報文字檔：{txt_path}")


if __name__ == "__main__":
    main()
