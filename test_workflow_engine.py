import os

from src.core.context import PlatformContext
from src.core.workflow_engine import WorkflowEngine


if not os.environ.get("GOOGLE_API_KEY"):
    raise RuntimeError(
        "缺少 GOOGLE_API_KEY。請先在 Colab cell 執行：\n"
        "from google.colab import userdata\n"
        "import os\n"
        "os.environ['GOOGLE_API_KEY'] = userdata.get('GOOGLE_API_KEY')"
    )


context = PlatformContext()

context.set(
    "memory",
    "classify_result",
    "分類：重大新聞／美國貨幣政策"
)

context.set(
    "memory",
    "extract_result",
    "聯準會官員表示通膨仍高於目標，市場預期降息時點可能延後。"
)

engine = WorkflowEngine("workflows/morning_test.yaml")

result = engine.run(context)

print("\n===== 執行結果 =====")
print(result.to_dict())
