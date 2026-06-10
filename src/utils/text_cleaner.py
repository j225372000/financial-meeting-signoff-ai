import re


def clean_slide_text(text):

    patterns = [

        r"僅供內部參考.*?請勿外傳。",

        r"不對外作任何獲利及判斷正確的保證。請勿外傳。",

        r"--- 第 \d+ 頁 ---",

        r"\n\d+\n"
    ]

    for pattern in patterns:

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.DOTALL
        )

    return text
