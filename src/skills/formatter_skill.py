from src.skills.base_skill import BaseSkill
from src.agents import formatter_agent


class FormatterSkill(BaseSkill):
    name = "formatter"

    def run(self, context: dict, step_config: dict) -> dict:
        output_key = step_config["output"]
        prompt_path = step_config["prompt"]
        data_keys = step_config["data"]

        data = {
            key: context[key]
            for key in data_keys
        }

        result = formatter_agent.format_report(
            prompt_path,
            data
        )

        context[output_key] = result
        return context
