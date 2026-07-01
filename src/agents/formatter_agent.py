from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def format_report(prompt_path: str, data: dict) -> str:
    prompt_template = load_prompt(prompt_path)

    content = "\n\n".join(
        f"【{key}】\n{value}"
        for key, value in data.items()
    )

    return f"""
{prompt_template}

以下為待格式化內容：

{content}
"""
