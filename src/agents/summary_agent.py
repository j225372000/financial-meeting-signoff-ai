from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def build_summary_prompt(
    prompt_path: str,
    sections: dict
) -> str:
    prompt_template = load_prompt(prompt_path)

    content = [prompt_template]

    for title, value in sections.items():
        content.append(f"\n\n以下為{title}：\n\n{value}")

    return "".join(content)


def summarize(
    prompt_path: str,
    sections: dict
) -> str:
    return build_summary_prompt(
        prompt_path,
        sections
    )
