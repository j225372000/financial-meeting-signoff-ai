from src.core.workflow_engine import WorkflowEngine


context = {
    "news_text": """
美國聯準會官員表示，通膨仍高於目標，市場預期降息時點可能延後。
美元指數上升，美債殖利率走高，投資人持續關注後續就業與通膨數據。
"""
}

engine = WorkflowEngine("workflows/morning_test.yaml")

result = engine.run(context)

print("\n===== 執行結果 =====")
print(result)
