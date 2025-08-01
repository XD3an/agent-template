# agent-template

基於 LangChain 的 AI Agent 簡易開發模板

## 🌟 核心特性

**簡潔設計**：採用直接參數化創建模式，無需複雜的模板配置

- ✅ **開箱即用**：直接使用參數創建 Agent，無需預先配置模板
- ✅ **靈活配置**：支援完全自定義的 Agent 配置
- ✅ **類型安全**：基於 Pydantic 的強類型驗證
- ✅ **標準協議**：支援 MCP (Model Context Protocol) 工具整合

**架構特點**：

```python
agent = factory.create_agent(
    name="研究助理",
    description="專業研究和分析專家",
    system_prompt="你是一位專業研究員...",
    model=llm.model,
    tools=["web_search", "pdf_reader"],
    max_iterations=10,
    temperature=0.7
)
```

## 🌟 架構是啥?

### 🧠 ReAct 框架

- **推理循環** - 思考 → 行動 → 觀察 → 反思的智能決策流程
- **工具整合** - 無縫接入各種外部工具和 API
- **上下文記憶** - 維護對話狀態和執行歷史
- **錯誤恢復** - 自動錯誤處理和重試機制

### 🔧 標準化工具生態

- **MCP 協議支援** - Model Context Protocol 標準化工具接口
- **統一工具管理** - 工具註冊、發現、調用的完整生命週期
- **模塊化設計** - 輕鬆擴展新工具和功能
- **安全執行** - 隔離環境確保系統安全

### 👥 多 Agent 協作

- **團隊編排** - 支援多個專業 Agent 協同工作
- **狀態同步** - Agent 間資訊共享和協調
- **工作流管理** - 基於 LangGraph 的複雜流程編排
- **彈性組建** - 根據任務需求動態組建團隊

---

## 🚀 快速開始

### 🛠️ 環境設置

**1. 克隆專案**

```bash
git clone https://github.com/your-username/agent-template.git
cd agent-template
```

**2. 安裝依賴**

```bash
# 使用 uv（推薦）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

**3. 環境配置**

在 `src/` 目錄下創建 `.env` 文件，參考 [.env.example](src/.env.example)：

```env
# 選擇其中一個 LLM 提供商配置

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Google Gemini
GOOGLE_API_KEY=your-google-api-key

# 本地 Ollama (預設)
OLLAMA_BASE_URL=http://localhost:11434

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_ENDPOINT=your-azure-endpoint
```

### ⚡ 基礎使用

**立即開始**

```bash
cd src
uv run test.py
```

## 🔧 核心組件

### LLM 提供商

支援多種語言模型：

```python
# OpenAI GPT 模型
llm = LLM_Provider(model="gpt-4", provider="openai")

# Anthropic Claude 模型
llm = LLM_Provider(model="claude-3-haiku-20240307", provider="anthropic")

# Google Gemini 模型
llm = LLM_Provider(model="gemini-pro", provider="google")

# 本地 Ollama 模型
llm = LLM_Provider(model="qwen3:0.6b", provider="ollama")

# DeepSeek 模型
llm = LLM_Provider(model="deepseek-r1", provider="deepseek")
```

### Agent 工廠

```python
from agent import AgentFactory, LLM_Provider, ToolManager

# 初始化 LLM 提供者 (LLM_Provider)
llm = LLM_Provider(model="qwen3:0.6b", provider="ollama")

# 創建具備工具管理的工廠 (AgentFactory)
tool_manager = ToolManager()
factory = AgentFactory(tool_manager=tool_manager)

agent = factory.create_agent(
    name="專家助理",
    description="領域專家",
    system_prompt="詳細的系統提示...",
    model=llm.model,
    tools=["calculator", "web_search"],
    max_iterations=10,
    temperature=0.7
)

# 使用自定義創建 (使用 AgentConfig 先定義 config，再使用 AgentFactory 創建)
from agent.types import AgentConfig

config = AgentConfig(
    name="自定義助理",
    description="完全自定義的助理",
    system_prompt="你是一個自定義助理...",
    tools=["custom_tool"],
    max_iterations=15,
    temperature=0.5
)

custom_agent = factory.create_custom_agent(config, llm.model)

# 創建團隊
team_config = {
    "researcher": {
        "name": "研究專家",
        "description": "專業研究員",
        "system_prompt": "研究專用提示...",
        "tools": ["web_search"],
        "max_iterations": 15
    },
    "analyst": {
        "name": "數據分析師",
        "description": "數據分析專家",
        "system_prompt": "分析專用提示...",
        "tools": ["calculator", "data_processor"],
        "max_iterations": 12
    }
}

team = factory.create_multi_agent_team(team_config, llm.model)
```

### MCP 工具整合

```python
# MCP 配置文件 (mcp_config.json)
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "transport": "stdio"
    },
    "everything": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-everything"],
      "transport": "stdio"
    }
  }
}


# 程式中使用
import json
import os

from agent import MCPClientService, ToolManager

# 初始化工具管理器
tool_manager = ToolManager()

# 初始化 MCP 客戶端服務
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

mcp_client = MCPClientService(mcp_config["mcpServers"], tool_manager)
available_tools = mcp_client.get_tools()
print(f"可用工具: {[tool.name for tool in available_tools]}")
```

### 🎯 核心用法

---

#### 1. 創建單一 Agent

```python
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
```

#### 2. 多 Agent 協作

```python
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
```

#### 3. 使用工具管理器和 MCP

```python
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
    result = await agent.process_message("請用合適的工具查詢 HackerNews (https://news.ycombinator.com/) 的最新內容")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

> 💡 **想了解更多使用方式？**
> 查看 **[詳細使用指南](USAGE_GUIDE.md)** 獲取：

---

## 📁 專案架構

```
src/
├── agent/                      # 核心代理模組
│   ├── __init__.py            # 模組初始化
│   ├── core/                  # 核心功能
│   │   ├── agent_factory.py   # 代理工廠
│   │   ├── base_agent.py      # 基礎代理類別
│   │   └── llm_factory.py     # LLM 提供商工廠
│   ├── tools/                 # 工具管理
│   │   ├── mcp_client.py      # MCP 客戶端服務
│   │   └── tool_manager.py    # 統一工具管理器
│   ├── types/                 # 類型定義
│   │   ├── __init__.py
│   │   └── agent_types.py     # 代理相關類型
│   └── utils/                 # 工具函數
│       └── config_loader.py   # 配置載入器
├── config/                    # 配置管理
│   ├── config_manager.py      # 配置管理器
│   └── env.py                 # 環境變數載入
├── test.py                    # 快速測試範例
├── pyproject.toml            # 專案依賴配置
└── mcp_config.json           # MCP 工具配置
```

### 架構層次

- **核心層 (Core Layer)**: AgentFactory、BaseAgent/ReactAgent、LLM_Provider
- **工具層 (Tool Layer)**: ToolManager、MCPClientService
- **類型層 (Type Layer)**: AgentTypes

## 📦 依賴項目

主要依賴：

- `langgraph` - 工作流編排框架
- `langchain` - LLM 抽象層
- `pydantic` - 資料驗證
- `mcp` - Model Context Protocol 支援

詳見 `pyproject.toml` 文件。

---

## 📄 授權一下?

[LICENSE](LICENSE)
