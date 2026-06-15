import re


def clean_text(text: str) -> str:
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.replace("**", "")
    text = text.replace("*", "")
    text = text.strip()
    return text


def split_sections(text: str):
    """
    依 enhanced_summary.json 目前格式切出各 section。
    """
    text = clean_text(text)

    pattern = r'\{\s*"section_title"\s*:\s*"([^"]+)"\s*,\s*"transcript_enhancement"\s*:\s*\['
    matches = list(re.finditer(pattern, text))

    sections = []

    for i, match in enumerate(matches):
        title = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]
        sections.append((title, block))

    return sections


def extract_topics(section_block: str):
    """
    從每個 section 中抓 topic/content。
    """
    pattern = r'"topic"\s*:\s*"([^"]+)"\s*,\s*"content"\s*:\s*"([^"]+)"'
    items = re.findall(pattern, section_block, flags=re.S)

    cleaned = []

    for topic, content in items:
        topic = clean_text(topic)
        content = clean_text(content)
        content = re.sub(r"\s+", " ", content)
        cleaned.append((topic, content))

    return cleaned


def split_qa_items(qa_summary: str):
    """
    先做簡單版：從 qa_summary 中抓可能的 Q&A 條目。
    若抓不到，就整段保留。
    """
    text = clean_text(qa_summary)

    # 常見格式：topic/content
    pattern = r'"topic"\s*:\s*"([^"]+)"\s*,\s*"content"\s*:\s*"([^"]+)"'
    items = re.findall(pattern, text, flags=re.S)

    if items:
        return [(clean_text(q), clean_text(a)) for q, a in items]

    # 常見格式：question/answer
    pattern = r'"question"\s*:\s*"([^"]+)"\s*,\s*"answer"\s*:\s*"([^"]+)"'
    items = re.findall(pattern, text, flags=re.S)

    if items:
        return [(clean_text(q), clean_text(a)) for q, a in items]

    return [("Q&A重點", text)]


def build_signoff_outline(
    slide_structure: str,
    slide_summary: str,
    enhanced_summary: str,
    qa_summary: str
) -> str:
    """
    將 Agent 產出的素材，先轉成接近正式簽文的條列草稿。
    這一步不呼叫 Gemini。
    """

    outline = []

    outline.append("主旨：謹陳報本次金融機構來行簡報重點如說明，擬陳閱後存查，敬請核示。")
    outline.append("")
    outline.append("說明：")

    sections = split_sections(enhanced_summary)

    chinese_numbers = [
        "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"
    ]

    # 正文最多先取前四章，避免 Q&A 被推到第五章
    for idx, (section_title, section_block) in enumerate(sections[:4]):
        section_no = chinese_numbers[idx]

        outline.append("")
        outline.append(f"{section_no}、{section_title}")

        topics = extract_topics(section_block)

        if not topics:
            continue

        # 每章用一個 subsection，維持正式簽文條列風格
        outline.append("(1) 重點內容")

        for item_idx, (topic, content) in enumerate(topics, start=1):
            outline.append(f"{item_idx}. {content}")

    # Q&A 固定為第四點或最後一點
    outline.append("")
    outline.append("四、Q&A重點")

    qa_items = split_qa_items(qa_summary)

    for idx, (question, answer) in enumerate(qa_items, start=1):
        outline.append(f"({idx}) {question}")
        outline.append(answer)

    outline.append("")
    outline.append("調撥科　謹簽")

    return "\n".join(outline)
