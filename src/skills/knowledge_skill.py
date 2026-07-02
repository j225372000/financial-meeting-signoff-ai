from src.skills.base_skill import BaseSkill
from src.agents import knowledge_retriever_agent


class KnowledgeSkill(BaseSkill):
    name = "knowledge"

    def run(self, context: dict, step_config: dict) -> dict:
        extract_key = step_config["extract_input"]
        knowledge_key = step_config["knowledge_input"]
        output_key = step_config["output"]
        prompt_path = step_config["prompt"]

        result = knowledge_retriever_agent.retrieve(
            context[extract_key],
            context[knowledge_key],
            prompt_path
        )

        context[output_key] = result
        return context
