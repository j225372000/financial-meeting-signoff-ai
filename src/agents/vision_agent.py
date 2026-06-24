from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def analyze_image(prompt_path: str) -> str:
    """
    Vision Agent：
    讀取圖片判讀用 Prompt。
    實際圖片與 Gemini Vision 呼叫由 main_fomc.py 負責。
    """
    return load_prompt(prompt_path)
