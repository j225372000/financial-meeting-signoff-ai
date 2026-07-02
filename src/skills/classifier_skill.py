from src.skills.base_skill import BaseSkill
from src.agents import classifier_agent


class ClassifierSkill(BaseSkill):
    name = "classifier"

    def run(self, context: dict, step_config: dict) -> dict:
        input_key = step_config["input"]
        output_key = step_config["output"]
        prompt_path = step_config["prompt"]

        result = classifier_agent.classify(
            context[input_key],
            prompt_path
        )

        context[output_key] = result
        return context
