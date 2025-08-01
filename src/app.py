import asyncio
import json
import os


class AgentApp:
    def __init__(self):
        self.agent = None
        self.factory = None
        self.tool_manager = None
        self.llm = None

    async def setup(self):
        print("🤖 Agent Template 快速測試")
        print("=" * 40)

        # 1. 初始化 LLM
        print("\n📚 1. 初始化 LLM 提供商...")
        from agent.core.llm_factory import LLM_Provider

        self.llm = LLM_Provider(
            model="qwen3:0.6b",
            provider="ollama",
            base_url="http://localhost:11434"
        )
        print("✅ LLM 初始化完成")

        # 2. 初始化工具管理器和 MCP 客戶端
        print("\n🔧 2. 載入工具和 MCP 配置...")
        from agent.tools.mcp_client import MCPClientService
        from agent.tools.tool_manager import ToolManager

        self.tool_manager = ToolManager()

        config_path = os.path.join(os.path.dirname(__file__), "mcp_config.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                mcp_config = json.load(f)
                servers = list(mcp_config['mcpServers'].keys())
                print(f"✅ 已載入 MCP 配置: {servers}")
        except Exception as e:
            print(f"⚠️  無法載入 MCP 配置: {e}")
            print("ℹ️  將使用空配置繼續")
            mcp_config = {"mcpServers": {}}

        # 初始化 MCP 工具
        self.mcp_client = MCPClientService(mcp_config["mcpServers"], self.tool_manager)
        available_tools = self.tool_manager.get_tool_names()
        print(f"🛠️  可用工具數量: {len(available_tools)}")

        # 3. 創建代理工廠和 Agent
        print("\n🏭 3. 創建 Agent...")
        from agent import AgentFactory
        self.factory = AgentFactory(tool_manager=self.tool_manager)

        # 直接創建代理，使用可用的工具
        self.agent = self.factory.create_agent(
            name="我的智能助理",
            description="一個通用的AI助理，可以使用各種工具協助用戶",
            system_prompt="""你是一位智能助理，具備以下能力：

**核心功能：**
- 回答各種問題並提供準確資訊
- 協助完成各種任務
- 使用可用工具增強服務品質

**工作原則：**
- 使用繁體中文與用戶溝通
- 按照 思考→行動→觀察→反思 的循環處理任務
- 主動使用可用工具來增強回答品質
- 提供準確、有用且完整的回答
- 承認不確定性並尋求澄清

請友善且專業地協助用戶！""",
            model=self.llm.model,
            tools=available_tools,
            max_iterations=10,
            temperature=0.7
        )

        print(f"✅ Agent '{self.agent.name}' 創建完成")

        # 4. 初始化 Agent
        print("\n🔄 4. 初始化 Agent...")
        try:
            await self.agent.initialize()
            print("✅ Agent 初始化成功")
        except Exception as e:
            print(f"❌ Agent 初始化失敗: {e}")
            print("ℹ️  嘗試使用簡化配置...")
            # 重新創建簡化版本
            self.agent = self.factory.create_agent(
                name="簡化助理",
                description="簡化版AI助理",
                system_prompt="你是一個有用的AI助理，請用繁體中文回答問題。",
                model=self.llm.model,
                tools=[],
                max_iterations=5,
                temperature=0.7
            )
            await self.agent.initialize()
            print("✅ 簡化版 Agent 初始化成功")

    async def test_conversation(self):
        print("\n🎯 5. 測試基本對話...")
        try:
            test_response = await self.agent.process_message("你好！請簡單介紹一下你的功能。")
            print(f"📝 測試回應: {test_response[:100]}...")
            print("✅ 基本對話測試成功")
        except Exception as e:
            print(f"❌ 基本對話測試失敗: {e}")
            return False
        return True

    async def interact(self):
        print("\n" + "="*50)
        print("🚀 準備就緒！開始互動模式")
        print("💡 輸入 'exit' 或 'quit' 結束對話")
        print("💡 輸入 'help' 查看可用功能")
        print("="*50)

        while True:
            try:
                user_input = input("\n🙋 您: ")

                if user_input.strip().lower() in ("exit", "quit", "結束", "退出"):
                    print("\n👋 再見！感謝使用 Agent Template！")
                    break

                if user_input.strip().lower() == "help":
                    print(f"""
📖 可用功能：
• Agent 名稱: {self.agent.name}
• 描述: {self.agent.config.description}
• 可用工具: {len(self.agent.get_available_tools())} 個
• 最大迭代: {self.agent.config.max_iterations}
• 對話歷史: {len(self.agent.get_conversation_history())} 條

💬 試試問我：
- "你好，你能做什麼？"
- "幫我分析一下 Python 的優勢"
- "什麼是人工智慧？"
""")
                    continue

                if not user_input.strip():
                    print("ℹ️  請輸入您的問題...")
                    continue

                print("\n🤔 思考中...")
                response = await self.agent.process_message(user_input)
                print(f"\n🤖 {self.agent.name}:")
                print(response)

            except KeyboardInterrupt:
                print("\n\n👋 偵測到 Ctrl+C，結束對話")
                break
            except Exception as e:
                print(f"\n❌ 處理過程中發生錯誤: {e}")
                print("ℹ️  請重試或輸入 'exit' 結束")

    def run(self):
        try:
            asyncio.run(self._run())
        except KeyboardInterrupt:
            print("\n👋 程式已終止")
        except Exception as e:
            print(f"\n💥 程式執行錯誤: {e}")
            print("ℹ️  請檢查配置並重試")

    async def _run(self):
        await self.setup()
        ok = await self.test_conversation()
        if ok:
            await self.interact()

# 讓其他模組可以 import
app = AgentApp()

if __name__ == "__main__":
    app.run()
