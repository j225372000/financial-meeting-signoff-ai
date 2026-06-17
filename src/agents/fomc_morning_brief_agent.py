from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    return Path(prompt_path).read_text(encoding="utf-8")


def build_fomc_morning_brief_prompt(
    fomc_summary: str,
    fomc_compare: str,
    fomc_implication: str,
    dotplot_summary: str
) -> str:
    prompt_template = load_prompt(
        "templates/fomc/04_fomc_morning_brief_prompt.txt"
    )

    return f"""
{prompt_template}

以下為本次FOMC政策重點整理：

{fomc_summary}

以下為本次與前次FOMC聲明稿比較：

{fomc_compare}

以下為本次FOMC政策意涵分析：

{fomc_implication}

以下為利率點陣圖判讀結果，請務必納入「三、SEP及點陣圖訊號」：

{dotplot_summary}
"""


def generate_fomc_morning_brief(
    fomc_summary: str,
    fomc_compare: str,
    fomc_implication: str,
    dotplot_summary: str
) -> str:
    return build_fomc_morning_brief_prompt(
        fomc_summary,
        fomc_compare,
        fomc_implication,
        dotplot_summary
    )
