from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def build_prompt(
    prompt_path: str,
    sections: dict
) -> str:
    prompt_template = load_prompt(prompt_path)

    content_blocks = []

    for title, content in sections.items():
        content_blocks.append(f"\n以下為{title}：\n\n{content}")

    return prompt_template + "\n".join(content_blocks)
