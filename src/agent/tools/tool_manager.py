"""工具管理器"""

import logging
from typing import Any, Dict, List, Optional

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class ToolManager:
    """統一的工具管理器"""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tool_categories: Dict[str, List[str]] = {}

    def register_tool(self, tool: BaseTool, category: str = "general") -> None:
        """註冊工具"""
        tool_name = tool.name
        self._tools[tool_name] = tool

        if category not in self._tool_categories:
            self._tool_categories[category] = []
        self._tool_categories[category].append(tool_name)

        logger.info(f"已註冊工具: {tool_name} (類別: {category})")

    def register_tools(self, tools: List[BaseTool], category: str = "general") -> None:
        """批量註冊工具"""
        for tool in tools:
            self.register_tool(tool, category)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """取得指定工具"""
        return self._tools.get(name)

    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """取得指定類別的工具"""
        tool_names = self._tool_categories.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]

    def get_all_tools(self) -> List[BaseTool]:
        """取得所有工具"""
        return list(self._tools.values())

    def get_tool_names(self) -> List[str]:
        """取得所有工具名稱"""
        return list(self._tools.keys())

    def get_categories(self) -> List[str]:
        """取得所有類別"""
        return list(self._tool_categories.keys())

    def remove_tool(self, name: str) -> bool:
        """移除工具"""
        if name in self._tools:
            del self._tools[name]

            # 從類別中移除
            for category, tool_names in self._tool_categories.items():
                if name in tool_names:
                    tool_names.remove(name)

            logger.info(f"已移除工具: {name}")
            return True
        return False

    def clear_tools(self) -> None:
        """清空所有工具"""
        self._tools.clear()
        self._tool_categories.clear()
        logger.info("已清空所有工具")

    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """取得工具資訊"""
        tool = self.get_tool(name)
        if not tool:
            return None

        return {
            "name": tool.name,
            "description": tool.description,
            "args": getattr(tool, "args", {}),
            "return_direct": getattr(tool, "return_direct", False)
        }

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """列出所有工具資訊"""
        return {
            name: self.get_tool_info(name)
            for name in self._tools.keys()
        }
