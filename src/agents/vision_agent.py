from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def build_vision_prompt(
    prompt_path: str
) -> str:
    return load_prompt(prompt_path)


def analyze_image(
    prompt_path: str
) -> str:
    return build_vision_prompt(prompt_path)
