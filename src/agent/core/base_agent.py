"""基礎 Agent 類別定義"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent

from ..tools.tool_manager import ToolManager
from ..types.agent_types import AgentConfig, AgentState, Message

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """基礎 Agent 抽象類別"""

    def __init__(self, config: AgentConfig, model: BaseChatModel, tool_manager: Optional[ToolManager] = None):
        self.config = config
        self.model = model
        self.tool_manager = tool_manager
        self.state = AgentState()
        self._agent = None

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def role(self) -> str:
        return self.config.role

    @abstractmethod
    async def initialize(self) -> None:
        """初始化 Agent"""
        pass

    @abstractmethod
    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """處理訊息"""
        pass

    async def stream_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        """流式回應"""
        # 預設實現，子類可覆寫
        response = await self.process_message(message, context)
        yield response

    def get_available_tools(self) -> List[BaseTool]:
        """取得可用工具"""
        if not self.tool_manager:
            return []

        tool_names = self.config.tools
        if not tool_names:
            return self.tool_manager.get_all_tools()

        return [self.tool_manager.get_tool(name) for name in tool_names if self.tool_manager.get_tool(name)]

    def add_message(self, message: Message) -> None:
        """添加訊息到狀態"""
        self.state.messages.append(message)

    def get_conversation_history(self, limit: Optional[int] = None) -> List[Message]:
        """取得對話歷史"""
        if limit:
            return self.state.messages[-limit:]
        return self.state.messages

    def reset_state(self) -> None:
        """重置狀態"""
        self.state = AgentState()


class ReactAgent(BaseAgent):
    """基於 ReAct 的 Agent 實現"""

    async def initialize(self) -> None:
        """初始化 ReAct Agent"""
        try:
            tools = self.get_available_tools()

            # 使用 LangGraph 最新 API，直接傳入 prompt 參數
            self._agent = create_react_agent(
                model=self.model,
                tools=tools,
                prompt=self.config.system_prompt
            )
            logger.info(f"成功初始化 {self.name} Agent，工具數量: {len(tools)}")
        except Exception as e:
            logger.error(f"初始化 {self.name} Agent 失敗: {e}")
            raise

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """處理訊息"""
        if not self._agent:
            await self.initialize()

        try:
            # 創建訊息物件
            user_message = Message(role="user", content=message)
            self.add_message(user_message)

            # 準備輸入
            input_data = {
                "messages": [{"role": msg.role, "content": msg.content} for msg in self.state.messages]
            }

            # 調用 agent
            result = await self._agent.ainvoke(input_data)

            # 處理結果
            if isinstance(result, dict) and "messages" in result:
                last_message = result["messages"][-1]
                response_content = getattr(last_message, "content", str(last_message))
            else:
                response_content = str(result)

            # 添加回應到狀態
            assistant_message = Message(role="assistant", content=response_content)
            self.add_message(assistant_message)

            return response_content

        except Exception as e:
            error_msg = f"處理訊息時發生錯誤: {e}"
            logger.error(error_msg)
            return error_msg

    async def stream_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        """流式回應"""
        if not self._agent:
            await self.initialize()

        try:
            user_message = Message(role="user", content=message)
            self.add_message(user_message)

            input_data = {
                "messages": [{"role": msg.role, "content": msg.content} for msg in self.state.messages]
            }

            # 使用 astream 進行流式處理
            async for chunk in self._agent.astream(input_data):
                if isinstance(chunk, dict) and "messages" in chunk:
                    last_message = chunk["messages"][-1]
                    content = getattr(last_message, "content", "")
                    if content:
                        yield content

        except Exception as e:
            error_msg = f"流式處理時發生錯誤: {e}"
            logger.error(error_msg)
            yield error_msg
