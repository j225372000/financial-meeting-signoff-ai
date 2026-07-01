import os
import re
import time
import importlib.util
from pathlib import Path

import google.generativeai as genai
from docx import Document
import pdfplumber


GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

BASE_DIR = "/content/drive/MyDrive/會議紀錄自動化"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MORNING_TEMPLATE_DIR = PROJECT_ROOT / "templates" / "morning"

MORNING_INPUT_DIR = f"{BASE_DIR}/input/morning/news"
MORNING_KNOWLEDGE_DIR = f"{BASE_DIR}/knowledge/morning"
MORNING_INTERMEDIATE_DIR = f"{BASE_DIR}/intermediate/morning"
MORNING_ITEMS_DIR = f"{MORNING_INTERMEDIATE_DIR}/items"
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
    encodings = ["utf-8", "utf-8-sig", "cp950", "big5", "latin-1"]

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


def list_news_files(folder):
    folder_path = Path(folder)

    if not folder_path.exists():
        raise FileNotFoundError(f"找不到新聞資料夾：{folder}")

    news_files = sorted([
        p for p in folder_path.iterdir()
        if p.is_file()
        and not p.name.startswith("~$")
        and p.suffix.lower() in [".txt", ".md", ".docx", ".pdf"]
    ])

    if not news_files:
        raise FileNotFoundError(
            f"新聞資料夾內沒有 .txt、.md、.docx 或 .pdf 檔案：{folder}"
        )

    return news_files


def load_knowledge_folder(folder):
    folder_path = Path(folder)

    if not folder_path.exists():
        print(f"未提供知識庫資料夾：{folder}")
        return ""

    files = sorted([
        p for p in folder_path.glob("**/*")
        if p.is_file()
        and not p.name.startswith("~$")
        and p.suffix.lower() in [".txt", ".md", ".json", ".docx", ".pdf"]
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


def safe_name(file_path):
    stem = Path(file_path).stem
    stem = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", stem)
    stem = stem.strip("_")
    return stem or "news"


def build_news_block(file_name, text):
    return f"""
===== 新聞檔案：{file_name} =====

{text}
"""


def run():
    genai.configure(api_key=GOOGLE_API_KEY)

    classifier_agent = load_module(
        "classifier_agent",
        str(PROJECT_ROOT / "src" / "agents" / "classifier_agent.py")
    )

    extractor_agent = load_module(
        "extractor_agent",
        str(PROJECT_ROOT / "src" / "agents" / "extractor_agent.py")
    )

    knowledge_retriever_agent = load_module(
        "knowledge_retriever_agent",
        str(PROJECT_ROOT / "src" / "agents" / "knowledge_retriever_agent.py")
    )

    writer_agent = load_module(
        "writer_agent",
        str(PROJECT_ROOT / "src" / "agents" / "writer_agent.py")
    )

    formatter_agent = load_module(
        "formatter_agent",
        str(PROJECT_ROOT / "src" / "agents" / "formatter_agent.py")
    )

    docx_writer = load_module(
        "docx_writer",
        str(PROJECT_ROOT / "src" / "utils" / "docx_writer.py")
    )

    print("Step 1：讀取晨報新聞與知識庫")

    news_files = list_news_files(MORNING_INPUT_DIR)
    knowledge_text = load_knowledge_folder(MORNING_KNOWLEDGE_DIR)

    print("新聞檔案數：", len(news_files))
    print("知識庫字數：", len(knowledge_text))

    all_news_items = []

    print("Step 2：逐則新聞執行 Classifier / Extractor / Knowledge Retriever")

    for idx, news_file in enumerate(news_files, start=1):
        item_name = safe_name(news_file)
        prefix = f"{idx:02d}_{item_name}"

        print(f"\n處理第 {idx} 則新聞：{news_file.name}")

        news_text = read_file(news_file)
        news_block = build_news_block(news_file.name, news_text)

        print("新聞字數：", len(news_text))

        classify_path = f"{MORNING_ITEMS_DIR}/{prefix}_classify.json"
        extract_path = f"{MORNING_ITEMS_DIR}/{prefix}_extract.json"
        knowledge_match_path = f"{MORNING_ITEMS_DIR}/{prefix}_knowledge.json"
        item_bundle_path = f"{MORNING_ITEMS_DIR}/{prefix}_item.json"

        classify_result = load_or_generate(
            classify_path,
            lambda: generate_with_retry(
                classifier_agent.classify(
                    news_block,
                    str(MORNING_TEMPLATE_DIR / "classifier_prompt.txt")
                )
            )
        )

        news_extract = load_or_generate(
            extract_path,
            lambda: generate_with_retry(
                extractor_agent.extract(
                    news_block,
                    str(MORNING_TEMPLATE_DIR / "extractor_prompt.txt")
                )
            )
        )

        knowledge_match = load_or_generate(
            knowledge_match_path,
            lambda: generate_with_retry(
                knowledge_retriever_agent.retrieve(
                    news_extract,
                    knowledge_text,
                    str(MORNING_TEMPLATE_DIR / "knowledge_retriever_prompt.txt")
                )
            )
        )

        item_bundle = f"""
{{
  "news_file": "{news_file.name}",
  "classify_result": {repr(classify_result)},
  "news_extract": {repr(news_extract)},
  "knowledge_match": {repr(knowledge_match)}
}}
"""

        save_text(item_bundle_path, item_bundle)

        all_news_items.append(
            f"""
==============================
新聞序號：{idx}
新聞檔名：{news_file.name}
==============================

【分類結果】
{classify_result}

【新聞萃取結果】
{news_extract}

【知識庫補充資料】
{knowledge_match}
"""
        )

    combined_items_text = "\n\n".join(all_news_items)

    combined_items_path = f"{MORNING_INTERMEDIATE_DIR}/all_news_items.json"
    save_text(combined_items_path, combined_items_text)

    print("\nStep 3：Writer 整合所有新聞，產生晨報草稿")

    morning_prompt = writer_agent.write(
        str(MORNING_TEMPLATE_DIR / "writer_prompt.txt"),
        {
            "各則新聞整理結果": combined_items_text,
            "寫作要求": (
                "請依各則新聞分段整理，避免混淆不同新聞。"
                "每則新聞應保留清楚邏輯，並使用金融專業、主管早報口吻。"
                "此階段負責內容品質、語氣與邏輯，不負責最終版型。"
            )
        }
    )

    morning_draft_text = generate_with_retry(morning_prompt)

    raw_txt_path = f"{MORNING_OUTPUT_DIR}/morning_brief_raw.txt"
    save_text(raw_txt_path, morning_draft_text)

    print("\nStep 4：Formatter 依早報格式產生正式晨報")

    formatter_prompt = formatter_agent.format_report(
        str(MORNING_TEMPLATE_DIR / "formatter_prompt.txt"),
        {
            "逐則新聞分類與整理結果": combined_items_text,
            "Writer晨報草稿": morning_draft_text,
            "格式規則": (
                "分類屬於股市、債市、匯市者，放入「二、市場摘要」。"
                "其餘分類放入「一、重大新聞」。"
                "請依使用者提供的早報格式整理，不新增事實。"
            )
        }
    )

    final_morning_text = generate_with_retry(formatter_prompt)

    final_txt_path = f"{MORNING_OUTPUT_DIR}/final_morning_brief.txt"
    save_text(final_txt_path, final_morning_text)

    print("\nStep 5：產生晨報 Word 檔")

    final_docx_path = f"{MORNING_OUTPUT_DIR}/final_morning_brief.docx"

    docx_writer.write_morning_docx(
        final_morning_text,
        final_docx_path
    )

    print("完成！")
    print(f"中間成果資料夾：{MORNING_INTERMEDIATE_DIR}")
    print(f"逐則新聞中間檔：{MORNING_ITEMS_DIR}")
    print(f"整合新聞資料：{combined_items_path}")
    print(f"Writer草稿：{raw_txt_path}")
    print(f"正式晨報文字檔：{final_txt_path}")
    print(f"正式晨報Word檔：{final_docx_path}")

    return {
        "intermediate_dir": MORNING_INTERMEDIATE_DIR,
        "items_dir": MORNING_ITEMS_DIR,
        "combined_items_path": combined_items_path,
        "raw_txt_path": raw_txt_path,
        "final_txt_path": final_txt_path,
        "final_docx_path": final_docx_path,
    }
