from pathlib import Path
import yaml

from src.skills.skill_registry import get_skill


class WorkflowEngine:

    def __init__(self, workflow_path):

        self.workflow_path = Path(workflow_path)

        if not self.workflow_path.exists():
            raise FileNotFoundError(workflow_path)

        with open(self.workflow_path, "r", encoding="utf-8") as f:
            self.workflow = yaml.safe_load(f)

    def run(self, context=None):

        if context is None:
            context = {}

        print(f"\nWorkflow：{self.workflow['name']}")

        for step in self.workflow["steps"]:

            skill_name = step["skill"]

            print(f"\n==========")
            print(f"Step：{step['id']}")
            print(f"Skill：{skill_name}")

            skill = get_skill(skill_name)

            context = skill.run(
                context=context,
                step_config=step
            )

        return context
