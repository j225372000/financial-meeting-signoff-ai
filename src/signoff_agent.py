from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    """
    讀取 Prompt 模板。
    """
    return Path(prompt_path).read_text(encoding="utf-8")


def build_signoff_prompt(
    draft_signoff_outline: str,
    signoff_style: str
) -> str:
    """
    將簽文條列草稿與歷史簽文風格塞入最終潤稿 Prompt。
    """
    prompt_template = load_prompt(
        "templates/05_generate_signoff_prompt.txt"
    )

    return f"""
{prompt_template}

以下為 draft_signoff_outline.txt：

{draft_signoff_outline}

以下為歷史簽文樣本風格：

{signoff_style}
"""


def generate_signoff(
    draft_signoff_outline: str,
    signoff_style: str
) -> str:
    """
    第五階段：依簽文條列草稿進行正式簽文潤稿。

    目前先回傳組合後的 Prompt。
    實際 Gemini 呼叫由 main.py 負責。
    """
    return build_signoff_prompt(
        draft_signoff_outline,
        signoff_style
    )
