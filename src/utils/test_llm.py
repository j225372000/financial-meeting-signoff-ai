from src.utils.llm_client import GeminiClient


client = GeminiClient()

response = client.generate(
    "請用一句話介紹台灣證券市場。"
)

print(response)
