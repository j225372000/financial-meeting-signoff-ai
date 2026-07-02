class BaseSkill:
    name = "base"

    def run(self, context: dict, step_config: dict) -> dict:
        raise NotImplementedError("Skill must implement run()")
