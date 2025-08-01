# 🚀 Agent Template 使用指南

## 📋 目錄

1. [快速開始](#快速開始)
2. [基礎概念](#基礎概念)
3. [進階使用](#進階使用)
4. [故障排除](#故障排除)
5. [最佳實踐](#最佳實踐)

---

## 🚀 快速開始

### 1. 環境準備

```bash
# 1. 克隆項目
git clone <your-repo-url>
cd agent-template

# 2. 進入源碼目錄
cd src

# 3. 安裝依賴
uv sync  # 推薦
# 或者
pip install -r requirements.txt

# 4. 配置環境
cp .env.example .env
# 編輯 .env 文件，添加您的 API 金鑰
```

### 2. 第一次運行

```bash
# 確保在 src 目錄下
cd src

# 運行測試範例
python test.py
```

### 3. 基本使用模式

以下是三種主要的使用模式：

#### 模式 1: 簡單 Agent

```python
import asyncio
from agent import AgentFactory, LLM_Provider

async def simple_agent():
    # 初始化 LLM
    llm = LLM_Provider(model="qwen3:0.6b", provider="ollama")

    # 創建工廠
    factory = AgentFactory()

    # 創建 Agent
    agent = factory.create_agent(
        name="助理",
        description="通用助理",
        system_prompt="你是一個有用的AI助理",
        model=llm.model,
        tools=[],
        max_iterations=5
    )

    # 使用
    await agent.initialize()
    response = await agent.process_message("你好")
    print(response)

asyncio.run(simple_agent())
```

#### 模式 2: 具備工具的 Agent

```python
from agent.tools import ToolManager, MCPClientService
import json

async def tool_enabled_agent():
    # 載入工具配置
    with open("mcp_config.json", 'r') as f:
        mcp_config = json.load(f)

    # 初始化工具
    tool_manager = ToolManager()
    mcp_client = MCPClientService(mcp_config["mcpServers"], tool_manager)

    # 創建具備工具的 Agent
    factory = AgentFactory(tool_manager=tool_manager)
    agent = factory.create_agent(
        name="工具專家",
        description="能使用工具的助理",
        system_prompt="你可以使用工具來協助用戶",
        model=llm.model,
        tools=tool_manager.get_tool_names(),  # 使用所有工具
        max_iterations=10
    )

    await agent.initialize()
    response = await agent.process_message("幫我搜索最新的AI新聞")
    print(response)
```

#### 模式 3: 多 Agent 協作

```python
async def multi_agent_collaboration():
    factory = AgentFactory()

    # 創建專業團隊
    team_config = {
        "researcher": {
            "name": "研究員",
            "description": "專業研究人員",
            "system_prompt": "你是專業研究員，負責資料蒐集和分析",
            "tools": ["web_search"],
            "max_iterations": 15
        },
        "writer": {
            "name": "寫手",
            "description": "內容創作專家",
            "system_prompt": "你是專業寫手，負責內容創作和編輯",
            "tools": ["grammar_checker"],
            "max_iterations": 10
        }
    }

    team = factory.create_multi_agent_team(team_config, llm.model)

    # 協作任務
    topic = "AI在教育中的應用"

    # 第一階段：研究
    research_result = await team["researcher"].process_message(f"研究{topic}")

    # 第二階段：寫作
    final_article = await team["writer"].process_message(
        f"基於以下研究寫一篇文章：{research_result}"
    )

    return final_article
```

---

## 🧠 基礎概念

### Agent 架構

本框架基於 **ReAct** (Reasoning + Acting) 架構：

```
思考 (Think) → 行動 (Act) → 觀察 (Observe) → 反思 (Reflect)
```

### 核心組件

1. **LLM_Provider**: 統一的語言模型接口
2. **AgentFactory**: Agent 創建和管理
3. **ToolManager**: 工具統一管理
4. **MCPClientService**: MCP 協議工具整合

### 數據流

```
用戶輸入 → Agent → LLM → 工具調用 → 結果整合 → 回應用戶
```

---

## 🔧 進階使用

### 自定義工具

```python
from langchain_core.tools import BaseTool

class CustomTool(BaseTool):
    name: str = "custom_calculator"
    description: str = "執行數學計算"

    def _run(self, expression: str) -> str:
        try:
            result = eval(expression)  # 注意：生產環境需要安全處理
            return f"計算結果: {result}"
        except Exception as e:
            return f"計算錯誤: {e}"

# 註冊工具
tool_manager = ToolManager()
tool_manager.register_tool(CustomTool(), category="math")
```

### 配置管理

```python
from agent.config import ConfigManager

# 載入配置
config_manager = ConfigManager()
config = config_manager.load_config("config.json")

# 使用配置創建組件
llm = LLM_Provider(
    model=config.model.model,
    provider=config.model.provider,
    api_key=config.model.api_key
)
```

---

## 🐛 故障排除

### 常見問題

#### 1. 模組導入錯誤

```bash
# 確保在 src 目錄下執行
cd src
python test.py
```

#### 2. API 金鑰配置錯誤

```python
# 檢查環境變數
import os
print("OpenAI:", "✓" if os.getenv("OPENAI_API_KEY") else "✗")
print("Anthropic:", "✓" if os.getenv("ANTHROPIC_API_KEY") else "✗")
```

#### 3. Ollama 連接失敗

```bash
# 檢查 Ollama 是否運行
curl http://localhost:11434/api/tags

# 拉取模型
ollama pull qwen3:0.6b
```

#### 4. MCP 工具初始化失敗

```python
# 檢查 MCP 配置
import json
with open("mcp_config.json", 'r') as f:
    config = json.load(f)
    print("配置的服務器:", list(config["mcpServers"].keys()))
```

### 除錯技巧

```python
import logging

# 啟用詳細日誌
logging.basicConfig(level=logging.DEBUG)

# 檢查 Agent 狀態
print(f"Agent 名稱: {agent.name}")
print(f"工具數量: {len(agent.get_available_tools())}")
print(f"對話歷史: {len(agent.get_conversation_history())}")
```

---

## 🏆 最佳實踐

### 1. Agent 設計原則

- **職責單一**: 每個 Agent 專注於特定領域
- **提示明確**: 撰寫清晰具體的系統提示
- **工具適配**: 選擇與任務相關的工具

### 2. 效能優化

```python
# 生產環境配置
agent = factory.create_agent(
    name="生產助理",
    description="生產環境優化的助理",
    system_prompt="簡潔專業的系統提示",
    model=llm.model,
    tools=["essential_tool"],  # 只使用必要工具
    max_iterations=5,  # 限制迭代次數
    temperature=0.3  # 降低隨機性
)
```

### 3. 錯誤處理

```python
async def robust_agent_interaction(agent, message):
    try:
        response = await agent.process_message(message)
        return response
    except Exception as e:
        logging.error(f"Agent 處理失敗: {e}")
        # 實施重試邏輯
        return await agent.process_message("抱歉，請重新表達您的問題")
```

### 4. 資源管理

```python
# 適當的資源清理
async def cleanup_agent(agent):
    # 清理狀態
    agent.reset_state()

    # 關閉工具連接
    if hasattr(agent.tool_manager, 'close'):
        await agent.tool_manager.close()
```

### 5. 安全考量

- **輸入驗證**: 驗證用戶輸入的安全性
- **工具限制**: 限制工具的執行權限
- **日誌記錄**: 記錄重要操作用於審計

```python
# 安全的工具配置
safe_tools = ["web_search", "calculator"]  # 避免文件系統操作工具
```

---

## 🎯 實際應用場景

以下是一些具體的應用場景，展示如何在實際專案中使用 Agent Template。

### 場景 1: 研究報告生成

適用於需要收集資訊、分析數據並撰寫報告的場景。

```python
import asyncio
from agent import AgentFactory, LLM_Provider

async def research_process():
    """執行完整的研究和報告生成流程"""
    llm = LLM_Provider(model="gpt-4", provider="openai")
    factory = AgentFactory()

    # 創建研究員 Agent
    researcher = factory.create_agent(
        name="研究員",
        description="專業研究員，擅長資料收集和分析",
        system_prompt="""你是一位專業研究員，具備以下能力：
- 系統性資訊搜集與整理
- 批判性思維和分析能力
- 可靠資料來源驗證
- 結構化報告撰寫

工作流程：
1. 理解研究主題和需求
2. 制定研究策略和方法
3. 收集相關資料和數據
4. 分析整理並得出結論
5. 撰寫詳細的研究報告

請保持學術嚴謹性和客觀性。""",
        model=llm.model,
        tools=["web_search", "pdf_reader", "data_analyzer"],
        max_iterations=15,
        temperature=0.3
    )

    # 創建寫作助手 Agent
    writer = factory.create_agent(
        name="寫作助手",
        description="專業內容創作和編輯專家",
        system_prompt="""你是一位專業寫作助手，專精於：
- 內容結構規劃和優化
- 語言表達和文風調整
- 讀者體驗和可讀性提升
- 品質控制和校對

寫作原則：
- 邏輯清晰，結構合理
- 語言流暢，表達準確
- 重點突出，層次分明
- 符合目標讀者需求

請創作引人入勝且專業的內容。""",
        model=llm.model,
        tools=["grammar_checker", "style_analyzer", "readability_checker"],
        max_iterations=10,
        temperature=0.5
    )

    # 初始化 Agents
    await researcher.initialize()
    await writer.initialize()

    # 執行研究和寫作流程
    research_topic = "2024年人工智慧在醫療領域的最新發展"

    print("🔍 開始研究階段...")
    research_data = await researcher.process_message(
        f"請深入研究「{research_topic}」，包括：\n"
        "1. 最新技術發展趨勢\n"
        "2. 實際應用案例分析\n"
        "3. 面臨的挑戰和限制\n"
        "4. 未來發展預測\n\n"
        "請提供詳細的研究報告，包含數據支撐和可靠來源。"
    )

    print("✍️ 開始寫作階段...")
    final_report = await writer.process_message(
        f"基於以下研究資料，撰寫一份專業且易讀的報告：\n\n{research_data}\n\n"
        "要求：\n"
        "- 結構清晰，包含摘要、正文、結論\n"
        "- 語言專業但易懂\n"
        "- 重點突出，邏輯順暢\n"
        "- 適合非專業讀者閱讀"
    )

    return final_report

# 使用範例
async def main():
    report = await research_process()
    print("📄 研究報告生成完成：")
    print(report)

if __name__ == "__main__":
    asyncio.run(main())
```

### 場景 2: 程式開發輔助

適用於代碼開發、審查和優化的場景。

```python
import asyncio
from agent import AgentFactory, LLM_Provider

async def coding_process():
    """執行程式開發和代碼審查流程"""
    llm = LLM_Provider(model="gpt-4", provider="openai")
    factory = AgentFactory()

    # 創建程式設計師 Agent
    coder = factory.create_agent(
        name="程式設計師",
        description="資深軟體工程師，專注於高品質代碼開發",
        system_prompt="""你是一位資深軟體工程師，具備以下技能：
- 多語言程式設計經驗
- 軟體架構設計能力
- 最佳實踐和設計模式應用
- 性能優化和安全考量

開發原則：
- 代碼可讀性和可維護性
- 遵循編程規範和最佳實踐
- 考慮性能和安全性
- 撰寫清晰的註釋和文檔

請確保代碼品質和專業性。""",
        model=llm.model,
        tools=["code_executor", "linter", "formatter"],
        max_iterations=12,
        temperature=0.2
    )

    # 創建代碼審查員 Agent
    reviewer = factory.create_agent(
        name="審查員",
        description="代碼品質專家，專注於代碼審查和優化建議",
        system_prompt="""你是一位代碼審查專家，專注於：
- 代碼品質評估和改進建議
- 安全漏洞識別和修復
- 性能瓶頸分析和優化
- 最佳實踐合規性檢查

審查重點：
- 代碼邏輯正確性
- 安全性和穩定性
- 性能和效率
- 可讀性和可維護性
- 測試覆蓋率

請提供具體且可操作的改進建議。""",
        model=llm.model,
        tools=["security_scanner", "performance_analyzer", "test_generator"],
        max_iterations=8,
        temperature=0.1
    )

    # 初始化 Agents
    await coder.initialize()
    await reviewer.initialize()

    # 開發和審查流程
    requirement = """
    需求：實現一個高效的分散式快取系統

    功能要求：
    1. 支援多種數據類型存儲
    2. 具備自動過期機制
    3. 支援集群部署
    4. 提供監控和統計功能
    5. 確保數據一致性

    技術要求：
    - 使用 Python 實現
    - 支援 Redis 作為後端
    - 包含完整的錯誤處理
    - 提供單元測試
    """

    print("👨‍💻 開始開發階段...")
    code_result = await coder.process_message(
        f"請根據以下需求開發代碼：\n{requirement}\n\n"
        "請提供：\n"
        "1. 完整的類設計和實現\n"
        "2. 詳細的註釋說明\n"
        "3. 使用範例\n"
        "4. 基本的單元測試"
    )

    print("🔍 開始審查階段...")
    review_result = await reviewer.process_message(
        f"請審查以下代碼，並提供改進建議：\n\n{code_result}\n\n"
        "審查重點：\n"
        "- 代碼架構和設計模式\n"
        "- 性能和安全性\n"
        "- 錯誤處理和邊界情況\n"
        "- 測試完整性\n"
        "- 文檔和註釋品質"
    )

    return {
        "original_code": code_result,
        "review_feedback": review_result
    }

# 使用範例
async def main():
    result = await coding_process()
    print("💻 開發結果：")
    print(result["original_code"])
    print("\n🔍 審查意見：")
    print(result["review_feedback"])

if __name__ == "__main__":
    asyncio.run(main())
```

### 場景 3: 商業諮詢流程

適用於商業分析、策略制定和問題解決的場景。

```python
import asyncio
from agent import AgentFactory, LLM_Provider

async def business_consulting():
    """執行商業諮詢和策略分析"""
    llm = LLM_Provider(model="gpt-4", provider="openai")
    factory = AgentFactory()

    # 創建商業顧問 Agent
    consultant = factory.create_agent(
        name="商業顧問",
        description="資深商業策略顧問，專精企業諮詢和戰略規劃",
        system_prompt="""你是一位資深商業顧問，具備以下專業能力：
- 商業策略制定和執行
- 市場分析和競爭情報
- 組織診斷和優化
- 風險評估和管理
- 財務分析和預測

諮詢方法：
- 結構化問題分析
- 數據驅動的決策支持
- 實用且可執行的建議
- 風險和機會並重
- 短期和長期平衡考量

請提供專業、實用且具有操作性的商業建議。""",
        model=llm.model,
        tools=["market_analyzer", "financial_calculator", "risk_assessor"],
        max_iterations=15,
        temperature=0.3
    )

    # 創建數據分析師 Agent
    analyst = factory.create_agent(
        name="數據分析師",
        description="資深數據分析師，專精商業數據分析和洞察發現",
        system_prompt="""你是一位資深數據分析師，專精於：
- 商業數據收集和清理
- 統計分析和趨勢識別
- 數據視覺化和報告
- 預測模型建立
- 業務指標監控

分析原則：
- 數據準確性和可靠性
- 統計方法的正確應用
- 清晰的視覺化呈現
- 實用的商業洞察
- 可操作的建議

請提供基於數據的客觀分析和洞察。""",
        model=llm.model,
        tools=["data_processor", "chart_generator", "trend_analyzer"],
        max_iterations=12,
        temperature=0.2
    )

    # 初始化 Agents
    await consultant.initialize()
    await analyst.initialize()

    # 商業諮詢案例
    business_challenge = """
    公司背景：一家中型電商平台

    面臨問題：
    - 客戶留存率持續下降（從 65% 降至 45%）
    - 獲客成本不斷上升（增長 40%）
    - 競爭對手推出更優惠的服務
    - 客戶滿意度評分下滑

    現有數據：
    - 月活躍用戶：100萬
    - 平均訂單金額：$85
    - 客服回應時間：24小時
    - 退貨率：12%
    """

    print("📊 開始數據分析...")
    data_analysis = await analyst.process_message(
        f"請分析以下商業問題的數據面向：\n{business_challenge}\n\n"
        "請提供：\n"
        "1. 問題的數據分析框架\n"
        "2. 關鍵指標的趨勢分析\n"
        "3. 可能的根本原因識別\n"
        "4. 建議收集的額外數據\n"
        "5. 量化評估方法"
    )

    print("💼 開始策略諮詢...")
    strategic_advice = await consultant.process_message(
        f"基於以下商業挑戰和數據分析，請提供策略建議：\n\n"
        f"商業挑戰：\n{business_challenge}\n\n"
        f"數據分析：\n{data_analysis}\n\n"
        "請提供：\n"
        "1. 問題診斷和根本原因\n"
        "2. 短期和長期解決方案\n"
        "3. 實施優先順序和時間規劃\n"
        "4. 預期效果和風險評估\n"
        "5. 成功指標和監控方式"
    )

    return {
        "data_analysis": data_analysis,
        "strategic_advice": strategic_advice
    }

# 使用範例
async def main():
    result = await business_consulting()
    print("📊 數據分析報告：")
    print(result["data_analysis"])
    print("\n💼 策略諮詢建議：")
    print(result["strategic_advice"])

if __name__ == "__main__":
    asyncio.run(main())
```

### 場景 4: 內容創作管線

適用於多媒體內容創作和編輯的場景。

```python
import asyncio
from agent import AgentFactory, LLM_Provider

async def content_creation_pipeline():
    """執行完整的內容創作流程"""
    llm = LLM_Provider(model="gpt-4", provider="openai")
    factory = AgentFactory()

    # 創建內容策劃師
    planner = factory.create_agent(
        name="內容策劃師",
        description="內容策略專家，負責內容規劃和主題設計",
        system_prompt="""你是內容策略專家，專精於：
- 目標受眾分析和內容定位
- 內容主題規劃和創意發想
- 多平台內容策略制定
- 內容行銷效果評估

策劃原則：
- 深度理解目標受眾需求
- 創新且有吸引力的內容主題
- 跨平台內容適配策略
- 可衡量的內容效果目標

請提供具有創意且實用的內容策略。""",
        model=llm.model,
        tools=["audience_analyzer", "trend_monitor"],
        max_iterations=10,
        temperature=0.7
    )

    # 創建內容撰寫者
    writer = factory.create_agent(
        name="內容撰寫者",
        description="專業內容創作者，擅長多種形式的內容創作",
        system_prompt="""你是專業內容創作者，具備：
- 多種文體和格式的寫作能力
- 不同平台內容特性理解
- SEO 和關鍵字優化技巧
- 讀者參與度提升策略

創作原則：
- 內容原創性和品質
- 適合目標平台的風格
- 讀者友善和易讀性
- 有效的 CTA 和互動設計

請創作引人入勝且有價值的內容。""",
        model=llm.model,
        tools=["seo_optimizer", "readability_checker"],
        max_iterations=12,
        temperature=0.6
    )

    # 初始化 Agents
    await planner.initialize()
    await writer.initialize()

    # 內容創作需求
    content_brief = """
    內容目標：推廣一款新的健身 App
    目標受眾：25-40 歲注重健康的上班族
    平台：部落格、社群媒體、電子報

    App 特色：
    - AI 個人化訓練計畫
    - 居家健身課程
    - 營養建議和追蹤
    - 社群挑戰功能

    內容需求：
    - 3 篇部落格文章
    - 10 則社群媒體貼文
    - 1 份電子報內容
    """

    print("📋 開始內容策劃...")
    content_strategy = await planner.process_message(
        f"請為以下內容需求制定策略：\n{content_brief}\n\n"
        "請提供：\n"
        "1. 目標受眾詳細分析\n"
        "2. 內容主題和角度建議\n"
        "3. 各平台內容策略\n"
        "4. 內容日程安排\n"
        "5. 成效評估指標"
    )

    print("✍️ 開始內容創作...")
    content_creation = await writer.process_message(
        f"基於以下策略，創作具體內容：\n\n{content_strategy}\n\n"
        "請提供：\n"
        "1. 3 篇部落格文章標題和大綱\n"
        "2. 10 則社群媒體貼文內容\n"
        "3. 1 份電子報完整內容\n"
        "4. SEO 關鍵字建議\n"
        "5. 視覺內容建議"
    )

    return {
        "strategy": content_strategy,
        "content": content_creation
    }

# 使用範例
async def main():
    result = await content_creation_pipeline()
    print("📋 內容策略：")
    print(result["strategy"])
    print("\n✍️ 創作內容：")
    print(result["content"])

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔗 相關資源

- [LangChain 文檔](https://python.langchain.com/)
- [LangGraph 指南](https://langchain-ai.github.io/langgraph/)
- [MCP 協議規範](https://modelcontextprotocol.io/)
- [Ollama 使用指南](https://ollama.com/)
