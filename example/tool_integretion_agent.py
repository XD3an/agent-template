import asyncio
import json

from agent import AgentFactory, LLM_Provider, MCPClientService, ToolManager


async def tool_integration_example():
    # 載入 MCP 配置
    with open("mcp_config.json", 'r') as f:
        mcp_config = json.load(f)

    # 初始化工具管理器
    tool_manager = ToolManager()

    # 初始化 MCP 客戶端
    mcp_client = MCPClientService(
        mcp_config["mcpServers"],
        tool_manager
    )

    # 初始化 LLM
    llm = LLM_Provider(model="qwen3:0.6b", provider="ollama")

    # 創建具備工具能力的 Agent
    factory = AgentFactory(tool_manager=tool_manager)

    agent = factory.create_agent(
        name="工具專家",
        description="能夠使用各種工具的專業助理",
        system_prompt="你可以使用各種工具來完成任務。根據需要選擇合適的工具。",
        model=llm.model,
        tools=tool_manager.get_tool_names(),  # 使用所有可用工具
        max_iterations=10
    )

    await agent.initialize()
    return agent

async def main():
    agent = await tool_integration_example()
    result = await agent.process_message("請用合適的工具查詢天氣")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
