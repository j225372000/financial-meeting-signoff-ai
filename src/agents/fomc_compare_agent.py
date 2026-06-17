from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def build_fomc_compare_prompt(
    statement_current: str,
    statement_previous: str
) -> str:
    prompt_template = load_prompt(
        "templates/fomc/02_fomc_compare_prompt.txt"
    )

    return f"""
{prompt_template}

以下為本次FOMC聲明稿：

{statement_current}

以下為前次FOMC聲明稿：

{statement_previous}
"""


def compare_fomc_statement(
    statement_current: str,
    statement_previous: str
) -> str:
    return build_fomc_compare_prompt(
        statement_current,
        statement_previous
    )
