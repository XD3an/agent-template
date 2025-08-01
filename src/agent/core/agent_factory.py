"""Agent 工廠 - 簡化版本，直接使用參數創建 Agent"""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel

from ..core.base_agent import BaseAgent, ReactAgent
from ..tools.tool_manager import ToolManager
from ..types.agent_types import AgentConfig

logger = logging.getLogger(__name__)


# ============================================================================
# Agent 工廠
# ============================================================================

class AgentFactory:
    """
    簡化的 Agent 工廠 - 直接使用參數創建 Agent

    功能：
    1. 直接創建 Agent，無需模板
    2. 支援自定義配置
    3. 多 Agent 協作
    """

    def __init__(self, tool_manager: Optional[ToolManager] = None):
        self.tool_manager = tool_manager
        logger.info("初始化簡化版 Agent 工廠")

    def create_agent(
        self,
        name: str,
        description: str,
        system_prompt: str,
        model: BaseChatModel,
        tools: Optional[List[str]] = None,
        max_iterations: int = 10,
        temperature: float = 0.7
    ) -> ReactAgent:
        """創建 Agent"""
        # 創建配置
        config = AgentConfig(
            name=name,
            description=description,
            system_prompt=system_prompt,
            tools=tools or [],
            max_iterations=max_iterations,
            temperature=temperature
        )

        # 創建 Agent
        agent = ReactAgent(
            config=config,
            model=model,
            tool_manager=self.tool_manager
        )

        logger.info(f"成功創建 Agent: {config.name}")
        return agent

    def create_custom_agent(
        self,
        config: AgentConfig,
        model: BaseChatModel
    ) -> ReactAgent:
        """創建完全自定義的 Agent"""
        agent = ReactAgent(
            config=config,
            model=model,
            tool_manager=self.tool_manager
        )
        logger.info(f"成功創建自定義 Agent: {config.name}")
        return agent

    def create_multi_agent_team(
        self,
        team_config: Dict[str, Dict[str, Any]],
        model: BaseChatModel
    ) -> Dict[str, ReactAgent]:
        """創建多 Agent 協作團隊"""
        team = {}

        for agent_id, config in team_config.items():
            # 提取配置參數
            name = config.get("name", agent_id)
            description = config.get("description", f"Agent {agent_id}")
            system_prompt = config.get("system_prompt", "你是一個有用的AI助理。")
            tools = config.get("tools", [])
            max_iterations = config.get("max_iterations", 10)
            temperature = config.get("temperature", 0.7)

            agent = self.create_agent(
                name=name,
                description=description,
                system_prompt=system_prompt,
                model=model,
                tools=tools,
                max_iterations=max_iterations,
                temperature=temperature
            )
            team[agent_id] = agent

        logger.info(f"成功創建多 Agent 團隊，包含 {len(team)} 個 Agent")
        return team

    def get_factory_status(self) -> Dict[str, Any]:
        """獲取工廠狀態"""
        return {
            "tool_manager": self.tool_manager is not None,
            "capabilities": [
                "直接參數創建 Agent",
                "自定義配置支援",
                "多Agent協作",
                "工具管理整合"
            ]
        }
