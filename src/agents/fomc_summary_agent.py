from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def build_fomc_summary_prompt(
    statement_current: str,
    sep_text: str,
    press_conference: str
) -> str:
    prompt_template = load_prompt(
        "templates/fomc/01_fomc_summary_prompt.txt"
    )

    return f"""
{prompt_template}

以下為本次 FOMC 聲明稿：

{statement_current}

以下為本次 SEP / 點陣圖相關資料：

{sep_text}

以下為鮑爾記者會逐字稿或重點：

{press_conference}
"""


def extract_fomc_summary(
    statement_current: str,
    sep_text: str,
    press_conference: str
) -> str:
    return build_fomc_summary_prompt(
        statement_current,
        sep_text,
        press_conference
    )
