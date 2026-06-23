from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def extract(raw_text: str) -> str:
    prompt_template = load_prompt(
        "templates/extractor_prompt.txt"
    )

    return f"""
{prompt_template}

以下為原始資料：

{raw_text}
"""
