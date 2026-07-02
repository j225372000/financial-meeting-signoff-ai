class BaseProvider:
    name = "base"

    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError("Provider must implement generate()")
