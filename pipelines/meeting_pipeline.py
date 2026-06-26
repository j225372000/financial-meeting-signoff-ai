import os
import time
import importlib.util
from pathlib import Path

import google.generativeai as genai


GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = "/content/drive/MyDrive/會議紀錄自動化"

SLIDE_DIR = f"{BASE_DIR}/input/slides"
TRANSCRIPT_DIR = f"{BASE_DIR}/input/transcript"
SIGNOFF_SAMPLE_DIR = f"{BASE_DIR}/input/signoff_samples"

INTERMEDIATE_DIR = f"{BASE_DIR}/intermediate/meeting"
OUTPUT_DIR = f"{BASE_DIR}/output/meeting"

MEETING_TEMPLATE_DIR = PROJECT_ROOT / "templates" / "meeting"

MODEL_MAIN = "models/gemini-2.5-flash-lite"
MODEL_BACKUP = "models/gemini-2.5-flash-lite"


def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(
        module_name,
        file_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save_text(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def generate_with_retry(prompt, model_name=MODEL_MAIN, retry=2):
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


def load_or_generate(path, generator_func):
    if os.path.exists(path):
        print(f"已存在，直接讀取：{path}")
        return read_text(path)

    print(f"不存在，開始產生：{path}")
    result = generator_func()
    save_text(path, result)
    return result


def find_single_file(folder, extensions):
    files = []

    for file_name in os.listdir(folder):
        if file_name.startswith("~$"):
            continue

        if any(file_name.lower().endswith(ext) for ext in extensions):
            files.append(os.path.join(folder, file_name))

    if len(files) == 0:
        raise FileNotFoundError(f"找不到檔案：{folder}")

    if len(files) > 1:
        raise ValueError(f"{folder} 裡有超過一個檔案：\n{files}")

    return files[0]


def load_signoff_samples(file_loader):
    texts = []

    for file_name in os.listdir(SIGNOFF_SAMPLE_DIR):
        if file_name.startswith("~$"):
            continue

        if file_name.endswith(".docx"):
            file_path = os.path.join(SIGNOFF_SAMPLE_DIR, file_name)
            text = file_loader.load_file(file_path)
            texts.append(f"\n\n===== {file_name} =====\n{text}")

    return "\n".join(texts)


def run_meeting_pipeline():
    genai.configure(api_key=GOOGLE_API_KEY)

    file_loader = load_module(
        "file_loader",
        str(PROJECT_ROOT / "src" / "utils" / "file_loader.py")
    )

    text_cleaner = load_module(
        "text_cleaner",
        str(PROJECT_ROOT / "src" / "utils" / "text_cleaner.py")
    )

    docx_writer = load_module(
        "docx_writer",
        str(PROJECT_ROOT / "src" / "utils" / "docx_writer.py")
    )

    extractor_agent = load_module(
        "extractor_agent",
        str(PROJECT_ROOT / "src" / "agents" / "extractor_agent.py")
    )

    writer_agent = load_module(
        "writer_agent",
        str(PROJECT_ROOT / "src" / "agents" / "writer_agent.py")
    )

    print("Step 1：讀取會議紀錄原始資料")

    slide_file = find_single_file(SLIDE_DIR, [".pdf"])
    transcript_file = find_single_file(TRANSCRIPT_DIR, [".docx", ".txt"])

    print("使用簡報：", slide_file)
    print("使用逐字稿：", transcript_file)

    slide_text = file_loader.load_file(slide_file)
    transcript_text = file_loader.load_file(transcript_file)
    signoff_style = load_signoff_samples(file_loader)

    cleaned_slide = text_cleaner.clean_slide_text(slide_text)

    print("簡報字數：", len(cleaned_slide))
    print("逐字稿字數：", len(transcript_text))
    print("歷史簽文字數：", len(signoff_style))

    raw_text = f"""
===== 簡報內容 =====

{cleaned_slide}

===== 逐字稿內容 =====

{transcript_text}
"""

    extract_result_path = f"{INTERMEDIATE_DIR}/extract_result.json"

    print("Step 2：執行 Meeting Extractor Agent")

    extract_result = load_or_generate(
        extract_result_path,
        lambda: generate_with_retry(
            extractor_agent.extract(
                raw_text,
                str(MEETING_TEMPLATE_DIR / "extractor_prompt.txt")
            )
        )
    )

    print("Step 3：執行 Meeting Writer Agent")

    signoff_prompt = writer_agent.write(
        str(MEETING_TEMPLATE_DIR / "writer_prompt.txt"),
        {
            "extract_result.json": extract_result,
            "歷史簽文樣本風格": signoff_style
        }
    )

    final_signoff_text = generate_with_retry(signoff_prompt)

    txt_path = f"{OUTPUT_DIR}/final_signoff.txt"
    docx_path = f"{OUTPUT_DIR}/final_signoff.docx"

    save_text(txt_path, final_signoff_text)

    docx_writer.write_signoff_docx(
        final_signoff_text,
        docx_path
    )

    print("完成！")
    print(f"中間成果：{INTERMEDIATE_DIR}")
    print(f"萃取結果：{extract_result_path}")
    print(f"文字檔：{txt_path}")
    print(f"Word檔：{docx_path}")

    return {
        "extract_result_path": extract_result_path,
        "txt_path": txt_path,
        "docx_path": docx_path,
        "final_text": final_signoff_text
    }
