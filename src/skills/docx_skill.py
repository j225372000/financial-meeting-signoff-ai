from src.skills.base_skill import BaseSkill
from src.utils import docx_writer


class DocxSkill(BaseSkill):
    name = "docx"

    def run(self, context: dict, step_config: dict) -> dict:
        input_key = step_config["input"]
        output_path_key = step_config["output_path_key"]
        mode = step_config.get("mode", "morning")

        output_path = context[output_path_key]

        if mode == "morning":
            docx_writer.write_morning_docx(
                context[input_key],
                output_path
            )

        elif mode == "signoff":
            docx_writer.write_signoff_docx(
                context[input_key],
                output_path
            )

        else:
            raise ValueError(f"不支援的 docx mode：{mode}")

        context["docx_output_path"] = output_path
        return context
