from src.skills.base_skill import BaseSkill
from src.agents import formatter_agent
from src.providers.provider_registry import get_provider


class FormatterSkill(BaseSkill):
    name = "formatter"

    def run(self, inputs: dict, step_config: dict) -> dict:
        prompt_path = step_config["prompt"]

        provider_name = step_config.get("provider", "gemini")
        model = step_config.get("model")
        retry = step_config.get("retry", 3)

        prompt = formatter_agent.format_report(
            prompt_path,
            inputs
        )

        provider = get_provider(provider_name)

        result = provider.generate(
            prompt=prompt,
            model=model,
            retry=retry
        )

        return {
            "result": result
        }
