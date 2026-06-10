from pathlib import Path
import pdfplumber
from docx import Document


def read_txt(file_path: str) -> str:
    return Path(file_path).read_text(encoding="utf-8")


def read_docx(file_path: str) -> str:
    doc = Document(file_path)
    paragraphs = []

    for p in doc.paragraphs:
        text = p.text.strip()
        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


def read_pdf(file_path: str) -> str:
    pages_text = []

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages_text.append(f"\n--- 第 {i} 頁 ---\n{text}")

    return "\n".join(pages_text)


def load_file(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()

    if suffix == ".txt":
        return read_txt(file_path)

    if suffix == ".docx":
        return read_docx(file_path)

    if suffix == ".pdf":
        return read_pdf(file_path)

    raise ValueError(f"不支援的檔案格式：{suffix}")
