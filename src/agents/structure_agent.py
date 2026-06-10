from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    """
    讀取 Prompt 模板。
    """
    return Path(prompt_path).read_text(encoding="utf-8")


def build_structure_prompt(slide_text: str) -> str:
    """
    將簡報文字塞入簡報架構提取 Prompt。
    """
    prompt_template = load_prompt(
        "templates/01_extract_slide_structure_prompt.txt"
    )

    return f"""
{prompt_template}

以下為金融機構簡報內容：

{slide_text}
"""


def extract_slide_structure(slide_text: str) -> str:
    """
    第一階段：提取簡報架構。

    目前先回傳組合後的 Prompt。
    下一步才會接 Gemini 或 OpenAI API。
    """
    return build_structure_prompt(slide_text)
