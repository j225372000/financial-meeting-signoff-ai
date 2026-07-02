from importlib import import_module


SKILL_REGISTRY = {
    "classifier": {
        "module": "src.skills.classifier_skill",
        "class": "ClassifierSkill",
        "description": "新聞或資料分類",
    },
    "extractor": {
        "module": "src.skills.extractor_skill",
        "class": "ExtractorSkill",
        "description": "從原始資料萃取重點",
    },
    "knowledge": {
        "module": "src.skills.knowledge_skill",
        "class": "KnowledgeSkill",
        "description": "根據萃取結果補充知識庫資料",
    },
    "writer": {
        "module": "src.skills.writer_skill",
        "class": "WriterSkill",
        "description": "依 Prompt 產生草稿或報告",
    },
    "formatter": {
        "module": "src.skills.formatter_skill",
        "class": "FormatterSkill",
        "description": "將文字整理成指定格式",
    },
    "docx": {
        "module": "src.skills.docx_skill",
        "class": "DocxSkill",
        "description": "輸出 Word 檔案",
    },
}


def get_skill(skill_name: str):
    if skill_name not in SKILL_REGISTRY:
        raise ValueError(f"未知 Skill：{skill_name}")

    skill_info = SKILL_REGISTRY[skill_name]

    module = import_module(skill_info["module"])
    skill_class = getattr(module, skill_info["class"])

    return skill_class()


def list_skills():
    return {
        name: {
            "description": info.get("description", "")
        }
        for name, info in SKILL_REGISTRY.items()
    }
