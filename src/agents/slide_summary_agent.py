from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    """
    讀取 Prompt 模板。
    """
    return Path(prompt_path).read_text(encoding="utf-8")


def build_slide_summary_prompt(
    slide_structure: str,
    slide_text: str
) -> str:
    """
    將簡報架構與簡報全文塞入簡報重點整理 Prompt。
    """
    prompt_template = load_prompt(
        "templates/02_extract_slide_summary_prompt.txt"
    )

    return f"""
{prompt_template}

以下為 slide_structure.json：

{slide_structure}

以下為金融機構簡報內容：

{slide_text}
"""


def extract_slide_summary(
    slide_structure: str,
    slide_text: str
) -> str:
    """
    第二階段：依簡報架構整理簡報重點。

    目前先回傳組合後的 Prompt。
    下一步才會接 Gemini 或 OpenAI API。
    """
    return build_slide_summary_prompt(slide_structure, slide_text)
