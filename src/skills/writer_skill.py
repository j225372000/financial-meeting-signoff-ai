from pathlib import Path

from src.skills.base_skill import BaseSkill
from src.agents import writer_agent


class WriterSkill(BaseSkill):
    name = "writer"

    def run(self, inputs: dict, step_config: dict) -> dict:
        prompt_path = step_config["prompt"]

        result = writer_agent.write(
            prompt_path,
            inputs
        )

        return {
            "result": result
        }
