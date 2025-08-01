"""Agent type definitions."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """工具調用定義"""
    name: str = Field(description="工具名稱")
    args: Dict[str, Any] = Field(default_factory=dict, description="工具參數")
    call_id: Optional[str] = Field(default=None, description="調用ID")


class Message(BaseModel):
    """訊息定義"""
    role: Literal["system", "user", "assistant", "tool"] = Field(description="訊息角色")
    content: str = Field(description="訊息內容")
    timestamp: datetime = Field(default_factory=datetime.now, description="時間戳")
    tool_calls: Optional[List[ToolCall]] = Field(default=None, description="工具調用")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元數據")


class AgentState(BaseModel):
    """Agent 狀態"""
    messages: List[Message] = Field(default_factory=list, description="對話歷史")
    current_step: Optional[str] = Field(default=None, description="當前步驟")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文數據")
    tool_results: Dict[str, Any] = Field(default_factory=dict, description="工具執行結果")

    model_config = {"arbitrary_types_allowed": True}


class AgentConfig(BaseModel):
    """Agent 配置"""
    name: str = Field(description="Agent 名稱")
    description: str = Field(description="Agent 描述")
    system_prompt: str = Field(description="系統提示詞")
    tools: List[str] = Field(default_factory=list, description="可用工具列表")
    llm_config: Dict[str, Any] = Field(default_factory=dict, description="LLM 配置")
    max_iterations: int = Field(default=10, description="最大迭代次數")
    temperature: float = Field(default=0.7, description="生成溫度")

    model_config = {"use_enum_values": True}
