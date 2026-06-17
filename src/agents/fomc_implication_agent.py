from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def build_fomc_implication_prompt(
    fomc_summary: str,
    fomc_compare: str
) -> str:
    prompt_template = load_prompt(
        "templates/fomc/03_fomc_implication_prompt.txt"
    )

    return f"""
{prompt_template}

以下為本次FOMC政策重點整理：

{fomc_summary}

以下為本次與前次FOMC聲明稿比較：

{fomc_compare}
"""


def analyze_fomc_implication(
    fomc_summary: str,
    fomc_compare: str
) -> str:
    return build_fomc_implication_prompt(
        fomc_summary,
        fomc_compare
    )
