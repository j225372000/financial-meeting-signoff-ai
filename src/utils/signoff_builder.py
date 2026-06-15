def build_signoff_outline(
    slide_structure: str,
    slide_summary: str,
    enhanced_summary: str,
    qa_summary: str
) -> str:
    """
    將前面 Agent 產出的素材，先組成簽文條列草稿。
    這一步不呼叫 Gemini，只負責固定格式與素材順序。
    """

    outline = []

    outline.append("主旨：謹陳報本次金融機構來行簡報重點如說明，擬陳閱後存查，敬請核示。")
    outline.append("")
    outline.append("說明：")
    outline.append("")

    outline.append("一、簡報章節架構")
    outline.append("")
    outline.append(slide_structure)
    outline.append("")

    outline.append("二、簡報重點素材")
    outline.append("")
    outline.append(slide_summary)
    outline.append("")

    outline.append("三、逐字稿補充重點")
    outline.append("")
    outline.append(enhanced_summary)
    outline.append("")

    outline.append("四、Q&A重點")
    outline.append("")
    outline.append(qa_summary)
    outline.append("")

    outline.append("調撥科　謹簽")

    return "\n".join(outline)
