from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def build_style_learning_prompt(signoff_samples_text: str) -> str:
    prompt_template = load_prompt(
        "templates/06_style_learning_prompt.txt"
    )

    return f"""
{prompt_template}

以下為歷史簽文樣本：

{signoff_samples_text}
"""


def learn_signoff_style(signoff_samples_text: str) -> str:
    """
    第六階段：分析歷史簽文樣本，產出簽文風格規則庫。
    目前先回傳 Prompt，之後接 Gemini。
    """
    return build_style_learning_prompt(signoff_samples_text)
