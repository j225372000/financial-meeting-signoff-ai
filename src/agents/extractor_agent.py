from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def extract(raw_text: str, prompt_path: str) -> str:
    prompt_template = load_prompt(prompt_path)

    return f"""
{prompt_template}

以下為原始資料：

{raw_text}
"""
