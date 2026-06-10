from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    """
    讀取 Prompt 模板。
    """
    return Path(prompt_path).read_text(encoding="utf-8")


def build_signoff_prompt(
    slide_structure: str,
    slide_summary: str,
    transcript_enhancement: str,
    qa_summary: str,
    signoff_style: str
) -> str:
    """
    將所有中間成果與簽文風格塞入最終簽文生成 Prompt。
    """
    prompt_template = load_prompt(
        "templates/05_generate_signoff_prompt.txt"
    )

    return f"""
{prompt_template}

以下為 slide_structure.json：

{slide_structure}

以下為 slide_summary.json：

{slide_summary}

以下為 transcript_enhancement.json：

{transcript_enhancement}

以下為 qa_summary.json：

{qa_summary}

以下為歷史簽文樣本風格：

{signoff_style}
"""


def generate_signoff(
    slide_structure: str,
    slide_summary: str,
    transcript_enhancement: str,
    qa_summary: str,
    signoff_style: str
) -> str:
    """
    第五階段：產出正式簽文草稿。

    目前先回傳組合後的 Prompt。
    下一步才會接 Gemini 或 OpenAI API。
    """
    return build_signoff_prompt(
        slide_structure,
        slide_summary,
        transcript_enhancement,
        qa_summary,
        signoff_style
    )
