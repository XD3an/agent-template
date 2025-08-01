import asyncio

from agent import AgentFactory, LLM_Provider


async def multi_agent_example():
    llm = LLM_Provider(model="qwen3:0.6b", provider="ollama")
    factory = AgentFactory()

    # 創建研究員
    researcher = factory.create_agent(
        name="研究員",
        description="專業研究和資訊分析專家",
        system_prompt="""你是一位專業研究員，專注於：
- 系統性資訊搜集
- 批判性分析
- 可靠資料驗證
- 結構化報告撰寫

請保持學術嚴謹性。""",
        model=llm.model,
        tools=["web_search", "pdf_reader"],
        max_iterations=15
    )

    # 創建寫作助手
    writer = factory.create_agent(
        name="寫作助手",
        description="專業內容創作和編輯專家",
        system_prompt="""你是一位專業寫作助手，專注於：
- 內容結構規劃
- 語言表達優化
- 讀者體驗考量
- 品質控制檢查

請創作引人入勝的內容。""",
        model=llm.model,
        tools=["grammar_checker", "style_analyzer"],
        max_iterations=10
    )

    # 初始化代理
    await researcher.initialize()
    await writer.initialize()

    # 協作生成報告
    research_topic = "人工智慧在教育領域的應用"

    # 第一階段：研究
    research_data = await researcher.process_message(
        f"請深入研究 {research_topic}，提供詳細的分析報告"
    )

    # 第二階段：寫作
    final_report = await writer.process_message(
        f"基於以下研究資料，撰寫一份易讀的報告：\n\n{research_data}"
    )

    return final_report

async def main():
    report = await multi_agent_example()
    print(report)

if __name__ == "__main__":
    asyncio.run(main())
