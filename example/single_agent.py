import asyncio

from agent import AgentFactory, LLM_Provider


async def main():
    # 初始化 LLM 提供商
    llm = LLM_Provider(
        model="qwen3:0.6b",  # 或 "gpt-4", "claude-3-haiku-20240307"
        provider="ollama"    # 或 "openai", "anthropic", "google"
    )

    # 創建代理工廠
    factory = AgentFactory()

    # 創建通用助理
    agent = factory.create_agent(
        name="我的助理",
        description="一個有用的AI助理",
        system_prompt="""你是一位智能助理，具備以下能力：

**工作原則：**
- 按照 思考→行動→觀察→反思 的循環處理任務
- 使用繁體中文與用戶溝通
- 主動使用可用工具增強回答品質
- 承認不確定性並尋求澄清

請提供準確、有用且完整的回答。""",
        model=llm.model,
        tools=[],  # 可添加工具名稱列表
        max_iterations=10,
        temperature=0.7
    )

    # 初始化並使用
    await agent.initialize()
    response = await agent.process_message("你好！請介紹一下你的功能。")
    print(f"助理回應: {response}")

if __name__ == "__main__":
    asyncio.run(main())
