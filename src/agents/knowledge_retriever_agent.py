from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def load_knowledge_folder(folder_path: str) -> str:
    folder = Path(folder_path)

    if not folder.exists():
        return ""

    texts = []

    for file in folder.glob("**/*"):
        if file.is_file() and file.suffix.lower() in [".txt", ".md", ".json"]:
            try:
                content = file.read_text(encoding="utf-8")
                texts.append(f"\n\n===== {file.name} =====\n{content}")
            except Exception:
                continue

    return "\n".join(texts)


def retrieve(
    news_extract: str,
    knowledge_text: str,
    prompt_path: str
) -> str:
    prompt_template = load_prompt(prompt_path)

    return f"""
{prompt_template}

以下為新聞萃取結果：

{news_extract}

以下為知識庫資料：

{knowledge_text}
"""
