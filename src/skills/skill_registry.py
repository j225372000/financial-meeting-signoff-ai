from src.skills.classifier_skill import ClassifierSkill
from src.skills.extractor_skill import ExtractorSkill
from src.skills.knowledge_skill import KnowledgeSkill
from src.skills.writer_skill import WriterSkill
from src.skills.formatter_skill import FormatterSkill
from src.skills.docx_skill import DocxSkill


SKILL_REGISTRY = {
    "classifier": ClassifierSkill(),
    "extractor": ExtractorSkill(),
    "knowledge": KnowledgeSkill(),
    "writer": WriterSkill(),
    "formatter": FormatterSkill(),
    "docx": DocxSkill(),
}


def get_skill(skill_name: str):
    if skill_name not in SKILL_REGISTRY:
        raise ValueError(f"未知 Skill：{skill_name}")

    return SKILL_REGISTRY[skill_name]
