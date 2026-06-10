from src.pipelines.signoff_pipeline import run_signoff_pipeline


def main():
    slide_text = """
    這裡放金融機構簡報文字測試資料。
    """

    transcript_text = """
    這裡放會議逐字稿測試資料。
    """

    signoff_style = """
    主旨：謹陳報○年○月○日○○公司來行簡報重點如說明，擬陳閱後存查，敬請核示。
    說明：
    一、……
    四、Q&A重點
    """

    result = run_signoff_pipeline(
        slide_text=slide_text,
        transcript_text=transcript_text,
        signoff_style=signoff_style
    )

    print(result["signoff_prompt"])


if __name__ == "__main__":
    main()
