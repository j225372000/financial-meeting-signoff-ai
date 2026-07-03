from src.skills.base_skill import BaseSkill
from src.agents import extractor_agent
from src.providers.provider_registry import get_provider


class ExtractorSkill(BaseSkill):
    name = "extractor"

    def run(self, inputs: dict, step_config: dict) -> dict:
        prompt_path = step_config["prompt"]

        provider_name = step_config.get("provider", "gemini")
        model = step_config.get("model")
        retry = step_config.get("retry", 3)

        text = inputs["text"]

        prompt = extractor_agent.extract(
            text,
            prompt_path
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
