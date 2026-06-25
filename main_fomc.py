import os
import time
import importlib.util
from pathlib import Path

import pdfplumber
import google.generativeai as genai


GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

BASE_DIR = "/content/drive/MyDrive/會議紀錄自動化"

PROJECT_ROOT = Path(__file__).resolve().parent
FOMC_TEMPLATE_DIR = PROJECT_ROOT / "templates" / "fomc"

FOMC_INPUT_DIR = f"{BASE_DIR}/input/fomc"
FOMC_INTERMEDIATE_DIR = f"{BASE_DIR}/intermediate/fomc"
FOMC_OUTPUT_DIR = f"{BASE_DIR}/output/fomc"

MODEL_MAIN = "models/gemini-2.5-flash-lite"
MODEL_BACKUP = "models/gemini-2.5-flash-lite"


def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_pdf(path):
    texts = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text)

    return "\n".join(texts)


def read_input(path):
    if path.lower().endswith(".txt"):
        return Path(path).read_text(encoding="utf-8")

    if path.lower().endswith(".pdf"):
        return read_pdf(path)

    raise ValueError(f"不支援的格式：{path}")


def save_text(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")


def load_or_generate(path, generator_func):
    if os.path.exists(path):
        print(f"已存在，直接讀取：{path}")
        return Path(path).read_text(encoding="utf-8")

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


def generate_image_with_retry(prompt, image_path, model_name=MODEL_MAIN, retry=3):
    from PIL import Image

    model = genai.GenerativeModel(model_name)
    image = Image.open(image_path)

    for i in range(retry):
        try:
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            print(f"第 {i + 1} 次失敗：{e}")
            time.sleep(30)

    print("改用備援模型")
    model = genai.GenerativeModel(MODEL_BACKUP)
    response = model.generate_content([prompt, image])
    return response.text


def main():
    genai.configure(api_key=GOOGLE_API_KEY)

    docx_writer = load_module(
        "docx_writer",
        str(PROJECT_ROOT / "src" / "utils" / "docx_writer.py")
    )

    extractor_agent = load_module(
        "extractor_agent",
        str(PROJECT_ROOT / "src" / "agents" / "extractor_agent.py")
    )

    compare_agent = load_module(
        "compare_agent",
        str(PROJECT_ROOT / "src" / "agents" / "compare_agent.py")
    )

    analysis_agent = load_module(
        "analysis_agent",
        str(PROJECT_ROOT / "src" / "agents" / "analysis_agent.py")
    )

    writer_agent = load_module(
        "writer_agent",
        str(PROJECT_ROOT / "src" / "agents" / "writer_agent.py")
    )

    vision_agent = load_module(
        "vision_agent",
        str(PROJECT_ROOT / "src" / "agents" / "vision_agent.py")
    )

    print("Step 1：讀取 FOMC 原始資料")

    statement_current = read_input(
        f"{FOMC_INPUT_DIR}/statement_current.pdf"
    )

    statement_previous = read_input(
        f"{FOMC_INPUT_DIR}/statement_previous.pdf"
    )

    sep_text = read_input(
        f"{FOMC_INPUT_DIR}/sep.pdf"
    )

    press_conference_path = f"{FOMC_INPUT_DIR}/press_conference.pdf"

    if os.path.exists(press_conference_path):
        press_conference = read_input(press_conference_path)
    else:
        print("未提供記者會逐字稿")
        press_conference = ""

    dotplot_path = f"{FOMC_INPUT_DIR}/dotplot.png"

    print("本次聲明稿字數：", len(statement_current))
    print("前次聲明稿字數：", len(statement_previous))
    print("SEP資料字數：", len(sep_text))
    print("記者會資料字數：", len(press_conference))
    print("點陣圖檔案：", dotplot_path)

    dotplot_path_out = f"{FOMC_INTERMEDIATE_DIR}/dotplot_summary.json"
    extract_path = f"{FOMC_INTERMEDIATE_DIR}/extract_result.json"
    compare_path = f"{FOMC_INTERMEDIATE_DIR}/compare_result.json"
    analysis_path = f"{FOMC_INTERMEDIATE_DIR}/analysis_result.json"

    print("Step 2：判讀 FOMC Dot Plot")

    dotplot_summary = load_or_generate(
        dotplot_path_out,
        lambda: generate_image_with_retry(
            vision_agent.analyze_image(
                str(FOMC_TEMPLATE_DIR / "dotplot_prompt.txt")
            ),
            dotplot_path
        )
    )

    print("Step 3：執行 FOMC Extractor Agent")

    raw_fomc_text = f"""
===== 本次FOMC聲明稿 =====

{statement_current}

===== SEP資料 =====

{sep_text}

===== Dot Plot判讀 =====

{dotplot_summary}

===== Powell記者會 =====

{press_conference}
"""

    fomc_extract = load_or_generate(
        extract_path,
        lambda: generate_with_retry(
            extractor_agent.extract(
                raw_fomc_text,
                str(FOMC_TEMPLATE_DIR / "extractor_prompt.txt")
            )
        )
    )

    print("Step 4：執行 FOMC Compare Agent")

    fomc_compare = load_or_generate(
        compare_path,
        lambda: generate_with_retry(
            compare_agent.compare(
                str(FOMC_TEMPLATE_DIR / "compare_prompt.txt"),
                {
                    "本次FOMC聲明稿": statement_current,
                    "前次FOMC聲明稿": statement_previous
                }
            )
        )
    )

    print("Step 5：執行 FOMC Analysis Agent")

    fomc_analysis = load_or_generate(
        analysis_path,
        lambda: generate_with_retry(
            analysis_agent.analyze(
                str(FOMC_TEMPLATE_DIR / "analysis_prompt.txt"),
                {
                    "FOMC政策重點": fomc_extract,
                    "聲明稿比較": fomc_compare
                }
            )
        )
    )

    print("Step 6：產生 FOMC 即時晨報")

    morning_brief_prompt = writer_agent.write(
        str(FOMC_TEMPLATE_DIR / "writer_prompt.txt"),
        {
            "FOMC政策重點": fomc_extract,
            "聲明稿比較": fomc_compare,
            "政策意涵分析": fomc_analysis,
            "點陣圖判讀": dotplot_summary
        }
    )

    morning_brief_text = generate_with_retry(
        morning_brief_prompt
    )

    txt_path = f"{FOMC_OUTPUT_DIR}/fomc_morning_brief.txt"
    docx_path = f"{FOMC_OUTPUT_DIR}/fomc_morning_brief.docx"

    save_text(txt_path, morning_brief_text)

    docx_writer.write_signoff_docx(
        morning_brief_text,
        docx_path
    )

    print("完成！")
    print(f"FOMC中間成果：{FOMC_INTERMEDIATE_DIR}")
    print(f"點陣圖判讀：{dotplot_path_out}")
    print(f"政策重點：{extract_path}")
    print(f"聲明稿比較：{compare_path}")
    print(f"政策分析：{analysis_path}")
    print(f"文字檔：{txt_path}")
    print(f"Word檔：{docx_path}")


if __name__ == "__main__":
    main()
