import os
import time
import importlib.util

import google.generativeai as genai


GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

BASE_DIR = "/content/drive/MyDrive/會議紀錄自動化"

SLIDE_DIR = f"{BASE_DIR}/input/slides"
TRANSCRIPT_DIR = f"{BASE_DIR}/input/transcript"
SIGNOFF_SAMPLE_DIR = f"{BASE_DIR}/input/signoff_samples"

INTERMEDIATE_DIR = f"{BASE_DIR}/intermediate"
OUTPUT_DIR = f"{BASE_DIR}/output"

MODEL_MAIN = "models/gemini-2.5-flash-lite"
MODEL_BACKUP = "models/gemini-2.5-flash-lite"


def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
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


def main():
    genai.configure(api_key=GOOGLE_API_KEY)

    file_loader = load_module("file_loader", "src/utils/file_loader.py")
    text_cleaner = load_module("text_cleaner", "src/utils/text_cleaner.py")
    docx_writer = load_module("docx_writer", "src/utils/docx_writer.py")
    signoff_builder = load_module("signoff_builder", "src/utils/signoff_builder.py")

    structure_agent = load_module("structure_agent", "src/agents/structure_agent.py")
    summary_agent = load_module("summary_agent", "src/agents/summary_agent.py")
    transcript_agent = load_module("transcript_agent", "src/transcript_agent.py")
    qa_agent = load_module("qa_agent", "src/qa_agent.py")
    writer_agent = load_module("writer_agent", "src/agents/writer_agent.py")

    print("Step 1：讀取原始資料")

    slide_file = find_single_file(SLIDE_DIR, [".pdf"])
    transcript_file = find_single_file(TRANSCRIPT_DIR, [".docx"])

    print("使用簡報：", slide_file)
    print("使用逐字稿：", transcript_file)

    slide_text = file_loader.load_file(slide_file)
    transcript_text = file_loader.load_file(transcript_file)
    signoff_style = load_signoff_samples(file_loader)

    cleaned_slide = text_cleaner.clean_slide_text(slide_text)

    print("簡報字數：", len(cleaned_slide))
    print("逐字稿字數：", len(transcript_text))
    print("歷史簽文字數：", len(signoff_style))

    slide_structure_path = f"{INTERMEDIATE_DIR}/slide_structure.json"
    slide_summary_path = f"{INTERMEDIATE_DIR}/slide_summary.json"
    enhanced_summary_path = f"{INTERMEDIATE_DIR}/enhanced_summary.json"
    qa_summary_path = f"{INTERMEDIATE_DIR}/qa_summary.json"

    print("Step 2：取得 slide_structure.json")
    slide_structure_json = load_or_generate(
        slide_structure_path,
        lambda: generate_with_retry(
            structure_agent.extract_slide_structure(cleaned_slide)
        )
    )

    print("Step 3：取得 slide_summary.json")
    slide_summary_json = load_or_generate(
        slide_summary_path,
        lambda: generate_with_retry(
            summary_agent.summarize(
                "templates/02_extract_slide_summary_prompt.txt",
                {
                    "slide_structure.json": slide_structure_json,
                    "簡報文字": cleaned_slide
                }
            )
        )
    )

    print("Step 4：取得 enhanced_summary.json")
    enhanced_summary_json = load_or_generate(
        enhanced_summary_path,
        lambda: generate_with_retry(
            transcript_agent.enhance_with_transcript(
                slide_structure_json,
                slide_summary_json,
                transcript_text
            )
        )
    )

    print("Step 5：取得 qa_summary.json")
    qa_summary_json = load_or_generate(
        qa_summary_path,
        lambda: generate_with_retry(
            qa_agent.extract_qa(transcript_text)
        )
    )

    print("Step 6：建立簽文草稿")

    draft_outline = signoff_builder.build_signoff_outline(
        slide_structure_json,
        slide_summary_json,
        enhanced_summary_json,
        qa_summary_json
    )

    draft_outline_path = f"{INTERMEDIATE_DIR}/draft_signoff_outline.txt"
    save_text(draft_outline_path, draft_outline)

    print(f"簽文草稿已建立：{draft_outline_path}")

    print("Step 7：潤稿產生正式簽文")

    signoff_prompt = writer_agent.write(
        "templates/05_generate_signoff_prompt.txt",
        {
            "draft_signoff_outline.txt": draft_outline,
            "歷史簽文樣本風格": signoff_style
        }
    )

    final_signoff_text = generate_with_retry(
        signoff_prompt
    )

    txt_path = f"{OUTPUT_DIR}/final_signoff.txt"
    docx_path = f"{OUTPUT_DIR}/final_signoff.docx"

    save_text(txt_path, final_signoff_text)

    docx_writer.write_signoff_docx(
        final_signoff_text,
        docx_path
    )

    print("完成！")
    print(f"中間成果：{INTERMEDIATE_DIR}")
    print(f"簽文草稿：{draft_outline_path}")
    print(f"文字檔：{txt_path}")
    print(f"Word檔：{docx_path}")


if __name__ == "__main__":
    main()
