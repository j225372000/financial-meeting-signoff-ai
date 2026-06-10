from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    """
    讀取 Prompt 模板。
    """
    return Path(prompt_path).read_text(encoding="utf-8")


def build_qa_prompt(transcript_text: str) -> str:
    """
    將逐字稿塞入 Q&A 抽取 Prompt。
    """
    prompt_template = load_prompt(
        "templates/04_extract_qa_prompt.txt"
    )

    return f"""
{prompt_template}

以下為會議逐字稿：

{transcript_text}
"""


def extract_qa(transcript_text: str) -> str:
    """
    第四階段：抽取 Q&A 重點。

    目前先回傳組合後的 Prompt。
    下一步才會接 Gemini 或 OpenAI API。
    """
    return build_qa_prompt(transcript_text)
