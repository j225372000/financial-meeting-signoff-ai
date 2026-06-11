import os
import time
import importlib.util
from pathlib import Path

import google.generativeai as genai


# =========================
# 基本設定
# =========================

GOOGLE_API_KEY =os.environ["GOOGLE_API_KEY"]

BASE_DIR = "/content/drive/MyDrive/會議紀錄自動化"

SLIDE_FILE = f"{BASE_DIR}/input/slides/金融機構簡報.pdf"
TRANSCRIPT_FILE = f"{BASE_DIR}/input/transcript/元大(Iphone)逐字稿-整理後.docx"
SIGNOFF_SAMPLE_DIR = f"{BASE_DIR}/input/signoff_samples"

INTERMEDIATE_DIR = f"{BASE_DIR}/intermediate"
OUTPUT_DIR = f"{BASE_DIR}/output"

MODEL_MAIN = "models/gemini-2.5-flash"
MODEL_BACKUP = "models/gemini-2.5-flash-lite"


# =========================
# 工具函式
# =========================

def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save_text(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def generate_with_retry(prompt, model_name=MODEL_MAIN, retry=3):
    model = genai.GenerativeModel(model_name)

    for i in range(retry):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"第 {i+1} 次失敗：{e}")
            time.sleep(30)

    print("改用備援模型 flash-lite")
    model = genai.GenerativeModel(MODEL_BACKUP)
    response = model.generate_content(prompt)
    return response.text


def load_signoff_samples(file_loader):
    texts = []

    for file_name in os.listdir(SIGNOFF_SAMPLE_DIR):
        if file_name.endswith(".docx"):
            file_path = os.path.join(SIGNOFF_SAMPLE_DIR, file_name)
            text = file_loader.load_file(file_path)
            texts.append(f"\n\n===== {file_name} =====\n{text}")

    return "\n".join(texts)


# =========================
# 主流程
# =========================

def main():
    genai.configure(api_key=GOOGLE_API_KEY)

    file_loader = load_module("file_loader", "src/utils/file_loader.py")
    text_cleaner = load_module("text_cleaner", "src/utils/text_cleaner.py")

    structure_agent = load_module("structure_agent", "src/agents/structure_agent.py")
    slide_summary_agent = load_module("slide_summary_agent", "src/agents/slide_summary_agent.py")
    transcript_agent = load_module("transcript_agent", "src/transcript_agent.py")
    qa_agent = load_module("qa_agent", "src/qa_agent.py")
    signoff_agent = load_module("signoff_agent", "src/signoff_agent.py")

    print("Step 1：讀取原始資料")
    slide_text = file_loader.load_file(SLIDE_FILE)
    transcript_text = file_loader.load_file(TRANSCRIPT_FILE)
    signoff_style = load_signoff_samples(file_loader)

    cleaned_slide = text_cleaner.clean_slide_text(slide_text)

    print("簡報字數：", len(cleaned_slide))
    print("逐字稿字數：", len(transcript_text))
    print("歷史簽文字數：", len(signoff_style))

    print("Step 2：產生 slide_structure.json")
    structure_prompt = structure_agent.extract_slide_structure(cleaned_slide)
    slide_structure_json = generate_with_retry(structure_prompt)
    save_text(f"{INTERMEDIATE_DIR}/slide_structure.json", slide_structure_json)

    print("Step 3：產生 slide_summary.json")
    slide_summary_prompt = slide_summary_agent.extract_slide_summary(
        slide_structure_json,
        cleaned_slide
    )
    slide_summary_json = generate_with_retry(slide_summary_prompt)
    save_text(f"{INTERMEDIATE_DIR}/slide_summary.json", slide_summary_json)

    print("Step 4：產生 enhanced_summary.json")
    transcript_prompt = transcript_agent.enhance_with_transcript(
        slide_structure_json,
        slide_summary_json,
        transcript_text
    )
    enhanced_summary_json = generate_with_retry(transcript_prompt)
    save_text(f"{INTERMEDIATE_DIR}/enhanced_summary.json", enhanced_summary_json)

    print("Step 5：產生 qa_summary.json")
    qa_prompt = qa_agent.extract_qa(transcript_text)
    qa_summary_json = generate_with_retry(qa_prompt)
    save_text(f"{INTERMEDIATE_DIR}/qa_summary.json", qa_summary_json)

    print("Step 6：產生 final_signoff.txt")
    signoff_prompt = signoff_agent.generate_signoff(
        slide_structure_json,
        slide_summary_json,
        enhanced_summary_json,
        qa_summary_json,
        signoff_style
    )
    final_signoff_text = generate_with_retry(signoff_prompt)
    save_text(f"{OUTPUT_DIR}/final_signoff.txt", final_signoff_text)

    print("完成！")
    print(f"中間成果：{INTERMEDIATE_DIR}")
    print(f"最終簽文：{OUTPUT_DIR}/final_signoff.txt")


if __name__ == "__main__":
    main()
