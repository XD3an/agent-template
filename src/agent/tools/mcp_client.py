"""MCP (Model Context Protocol) 客戶端服務"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import nest_asyncio
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from .tool_manager import ToolManager

nest_asyncio.apply()
logger = logging.getLogger(__name__)


class MCPClientService:
    """
    MCP 客戶端服務包裝器，用於管理工具初始化和訪問
    """

    def __init__(self, config: Dict[str, Any], tool_manager: Optional[ToolManager] = None):
        """
        初始化 MCP 客戶端服務並強制初始化工具

        Args:
            config: MCP 客戶端配置
            tool_manager: 工具管理器實例
        """
        self.config = config
        self.client: Optional[MultiServerMCPClient] = None
        self.tools: List[BaseTool] = []
        self.tool_manager = tool_manager
        self._initialized = False

        # 強制同步初始化工具
        self._init_tools()

    def _init_tools(self) -> None:
        """
        強制同步初始化工具
        """
        try:
            logger.info("正在初始化 MCP 客戶端...")
            logger.info(f"配置的伺服器: {list(self.config.keys())}")

            # 逐個檢查伺服器配置
            valid_configs = {}
            for server_name, server_config in self.config.items():
                try:
                    logger.info(f"檢查伺服器 {server_name}: {server_config}")
                    if "command" in server_config and "transport" in server_config:
                        valid_configs[server_name] = server_config
                        logger.info(f"伺服器 {server_name} 配置有效")
                    else:
                        logger.warning(f"伺服器 {server_name} 配置無效，跳過")
                except Exception as e:
                    logger.warning(f"檢查伺服器 {server_name} 時發生錯誤: {e}")

            if not valid_configs:
                logger.warning("沒有有效的 MCP 伺服器配置")
                self._initialized = True
                return

            logger.info(f"嘗試連接 {len(valid_configs)} 個有效伺服器")

            # 使用同步方式初始化工具
            def run_async_init():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        self.client = MultiServerMCPClient(valid_configs)
                        # 嘗試獲取工具，但設置超時
                        self.tools = loop.run_until_complete(
                            asyncio.wait_for(self.client.get_tools(), timeout=30.0)
                        )

                        # 如果有工具管理器，將工具註冊到管理器
                        if self.tool_manager and self.tools:
                            self.tool_manager.register_tools(self.tools, category="mcp")

                        self._initialized = True
                        logger.info(f"成功初始化 {len(self.tools)} 個 MCP 工具")

                    except asyncio.TimeoutError:
                        logger.error("MCP 工具初始化超時")
                        self.tools = []
                        self._initialized = True
                    finally:
                        loop.close()
                except Exception as e:
                    logger.error(f"異步初始化失敗: {e}")
                    self.tools = []
                    self._initialized = False

            # 檢查當前是否在事件循環中
            try:
                current_loop = asyncio.get_running_loop()
                # 在事件循環中，使用線程運行
                import threading
                thread = threading.Thread(target=run_async_init)
                thread.start()
                thread.join()
            except RuntimeError:
                # 不在事件循環中，直接運行
                run_async_init()

        except Exception as e:
            logger.error(f"強制初始化工具時發生錯誤: {e}")
            self.tools = []
            self._initialized = False

    def get_tools(self) -> List[BaseTool]:
        """
        取得已初始化的工具列表

        Returns:
            工具列表，如果未初始化則返回空列表
        """
        if not self._initialized:
            logger.warning("MCP 工具尚未初始化，返回空列表")
            return []
        return self.tools or []

    def get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        """
        根據名稱取得特定工具

        Args:
            name: 工具名稱

        Returns:
            工具實例，如果未找到則返回 None
        """
        if not self.tools:
            return None

        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def is_initialized(self) -> bool:
        """檢查是否已初始化"""
        return self._initialized

    def refresh_tools(self) -> List[BaseTool]:
        """
        重新獲取和初始化工具

        Returns:
            更新後的工具列表
        """
        logger.info("正在重新整理 MCP 工具...")
        self._initialized = False
        self.tools = []
        self._force_init_tools()
        return self.tools

    def get_client_info(self) -> Dict[str, Any]:
        """
        取得客戶端資訊

        Returns:
            包含客戶端狀態和配置的字典
        """
        return {
            "initialized": self._initialized,
            "tool_count": len(self.tools) if self.tools else 0,
            "config_servers": len(self.config) if isinstance(self.config, dict) else 0
        }
