import os
import time
import importlib.util
from pathlib import Path

import pdfplumber
import google.generativeai as genai


GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

BASE_DIR = "/content/drive/MyDrive/會議紀錄自動化"

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
        return Path(path).read_text(
            encoding="utf-8"
        )

    if path.lower().endswith(".pdf"):
        return read_pdf(path)

    raise ValueError(
        f"不支援的格式：{path}"
    )


def save_text(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")


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
    model = genai.GenerativeModel(model_name)

    image_file = genai.upload_file(image_path)

    for i in range(retry):
        try:
            response = model.generate_content(
                [
                    prompt,
                    image_file
                ]
            )
            return response.text

        except Exception as e:
            print(f"第 {i + 1} 次失敗：{e}")
            time.sleep(30)

    print("改用備援模型")
    model = genai.GenerativeModel(MODEL_BACKUP)
    response = model.generate_content(
        [
            prompt,
            image_file
        ]
    )
    return response.text


def load_or_generate(path, generator_func):
    if os.path.exists(path):
        print(f"已存在，直接讀取：{path}")
        return Path(path).read_text(encoding="utf-8")

    print(f"不存在，開始產生：{path}")
    result = generator_func()
    save_text(path, result)
    return result


def main():
    genai.configure(api_key=GOOGLE_API_KEY)

    docx_writer = load_module(
        "docx_writer",
        "src/utils/docx_writer.py"
    )

    fomc_summary_agent = load_module(
        "fomc_summary_agent",
        "src/agents/fomc_summary_agent.py"
    )

    fomc_compare_agent = load_module(
        "fomc_compare_agent",
        "src/agents/fomc_compare_agent.py"
    )

    fomc_implication_agent = load_module(
        "fomc_implication_agent",
        "src/agents/fomc_implication_agent.py"
    )

    fomc_morning_brief_agent = load_module(
        "fomc_morning_brief_agent",
        "src/agents/fomc_morning_brief_agent.py"
    )

    fomc_dotplot_agent = load_module(
        "fomc_dotplot_agent",
        "src/agents/fomc_dotplot_agent.py"
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

    press_conference = read_input(
        f"{FOMC_INPUT_DIR}/press_conference.pdf"
    )

    dotplot_path = f"{FOMC_INPUT_DIR}/dotplot.png"

    print("本次聲明稿字數：", len(statement_current))
    print("前次聲明稿字數：", len(statement_previous))
    print("SEP資料字數：", len(sep_text))
    print("記者會資料字數：", len(press_conference))
    print("點陣圖檔案：", dotplot_path)

    dotplot_path_out = f"{FOMC_INTERMEDIATE_DIR}/dotplot_summary.json"
    summary_path = f"{FOMC_INTERMEDIATE_DIR}/fomc_summary.json"
    compare_path = f"{FOMC_INTERMEDIATE_DIR}/fomc_compare.json"
    implication_path = f"{FOMC_INTERMEDIATE_DIR}/fomc_implication.json"

    print("Step 2：判讀 FOMC Dot Plot")

    dotplot_summary = load_or_generate(
        dotplot_path_out,
        lambda: generate_image_with_retry(
            fomc_dotplot_agent.build_dotplot_prompt(),
            dotplot_path
        )
    )

    print("Step 3：產生 FOMC Summary")

    fomc_summary = load_or_generate(
        summary_path,
        lambda: generate_with_retry(
            fomc_summary_agent.extract_fomc_summary(
                statement_current,
                sep_text + "\n\n以下為點陣圖判讀結果：\n" + dotplot_summary,
                press_conference
            )
        )
    )

    print("Step 4：產生 FOMC Statement Compare")

    fomc_compare = load_or_generate(
        compare_path,
        lambda: generate_with_retry(
            fomc_compare_agent.compare_fomc_statement(
                statement_current,
                statement_previous
            )
        )
    )

    print("Step 5：產生 FOMC Implication")

    fomc_implication = load_or_generate(
        implication_path,
        lambda: generate_with_retry(
            fomc_implication_agent.analyze_fomc_implication(
                fomc_summary,
                fomc_compare
            )
        )
    )

    print("Step 6：產生 FOMC 即時晨報")

    morning_brief_prompt = (
        fomc_morning_brief_agent.generate_fomc_morning_brief(
            fomc_summary + "\n\n以下為點陣圖判讀結果：\n" + dotplot_summary,
            fomc_compare,
            fomc_implication
        )
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
    print(f"文字檔：{txt_path}")
    print(f"Word檔：{docx_path}")


if __name__ == "__main__":
    main()
