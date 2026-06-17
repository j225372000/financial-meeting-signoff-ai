from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(
        encoding="utf-8"
    )


def build_dotplot_prompt():

    return load_prompt(
        "templates/fomc/00_fomc_dotplot_prompt.txt"
    )
