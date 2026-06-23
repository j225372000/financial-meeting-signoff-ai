from pathlib import Path
import json
import re


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def clean_json_text(text: str) -> str:
    text = text.strip()
    text = text.replace("```json", "")
    text = text.replace("```", "")
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return text


def run_extractor(model, source_type: str, raw_text: str) -> dict:
    """
    真正的 Extractor Agent：
    1. 讀取 extractor prompt
    2. 放入原始資料
    3. 呼叫模型
    4. 回傳 JSON dict
    """

    prompt_template = load_prompt("templates/extractor_prompt.txt")

    full_prompt = f"""
{prompt_template}

資料類型：
{source_type}

以下為原始資料：

{raw_text}
"""

    response = model.generate_content(full_prompt)
    json_text = clean_json_text(response.text)

    return json.loads(json_text)
