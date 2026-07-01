from docx import Document

TEMPLATE = "templates/morning/morning_report_template.docx"

doc = Document(TEMPLATE)

print("=" * 60)
print("Styles")
print("=" * 60)

for style in doc.styles:
    try:
        print(f"{style.type}  |  {style.name}")
    except:
        pass

print()
print("=" * 60)
print("Paragraphs")
print("=" * 60)

for i, p in enumerate(doc.paragraphs, 1):

    text = p.text.strip()

    if text:
        print(
            f"{i:02d}. "
            f"[{p.style.name}] "
            f"{text}"
        )
