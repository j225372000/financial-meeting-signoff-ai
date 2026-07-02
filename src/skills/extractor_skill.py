from src.skills.base_skill import BaseSkill
from src.agents import extractor_agent


class ExtractorSkill(BaseSkill):
    name = "extractor"

    def run(self, context: dict, step_config: dict) -> dict:
        input_key = step_config["input"]
        output_key = step_config["output"]
        prompt_path = step_config["prompt"]

        result = extractor_agent.extract(
            context[input_key],
            prompt_path
        )

        context[output_key] = result
        return context
