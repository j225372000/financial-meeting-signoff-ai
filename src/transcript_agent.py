from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    """
    讀取 Prompt 模板。
    """
    return Path(prompt_path).read_text(encoding="utf-8")


def build_transcript_enhancement_prompt(
    slide_structure: str,
    slide_summary: str,
    transcript_text: str
) -> str:
    """
    將簡報架構、簡報重點與逐字稿塞入逐字稿補強 Prompt。
    """
    prompt_template = load_prompt(
        "templates/03_enhance_with_transcript_prompt.txt"
    )

    return f"""
{prompt_template}

以下為 slide_structure.json：

{slide_structure}

以下為 slide_summary.json：

{slide_summary}

以下為會議逐字稿：

{transcript_text}
"""


def enhance_with_transcript(
    slide_structure: str,
    slide_summary: str,
    transcript_text: str
) -> str:
    """
    第三階段：用逐字稿補強簡報重點。

    目前先回傳組合後的 Prompt。
    下一步才會接 Gemini 或 OpenAI API。
    """
    return build_transcript_enhancement_prompt(
        slide_structure,
        slide_summary,
        transcript_text
    )
