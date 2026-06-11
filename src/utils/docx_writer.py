from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn


def write_signoff_docx(text: str, output_path: str):
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "標楷體"
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "標楷體")
    style.font.size = Pt(14)

    for line in text.splitlines():
        line = line.strip()

        if not line:
            doc.add_paragraph("")
            continue

        p = doc.add_paragraph()
        run = p.add_run(line)
        run.font.name = "標楷體"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "標楷體")
        run.font.size = Pt(14)

    doc.save(output_path)
