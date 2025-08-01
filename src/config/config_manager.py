"""配置管理系統"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """模型配置"""
    provider: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None


@dataclass
class MCPConfig:
    """MCP 配置"""
    servers: Dict[str, Any]


@dataclass
class LoggingConfig:
    """日誌配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None


@dataclass
class AppConfig:
    """應用程式總配置"""
    model: ModelConfig
    mcp: Optional[MCPConfig] = None
    logging: LoggingConfig = None
    debug: bool = False
    max_execution_time: int = 300

    def __post_init__(self):
        if self.logging is None:
            self.logging = LoggingConfig()


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._config: Optional[AppConfig] = None

    def load_config(self, config_path: Optional[str] = None) -> AppConfig:
        """
        載入配置

        Args:
            config_path: 配置文件路徑，如果為 None 則使用預設路徑

        Returns:
            AppConfig: 應用配置物件
        """
        if config_path is None:
            # 嘗試多個可能的配置文件
            possible_paths = [
                self.config_dir / "config.yaml",
                self.config_dir / "config.yml",
                self.config_dir / "config.json",
                Path("config.yaml"),
                Path("config.yml"),
                Path("config.json")
            ]

            config_file = None
            for path in possible_paths:
                if path.exists():
                    config_file = path
                    break

            if config_file is None:
                logger.warning("未找到配置文件，使用預設配置")
                return self._create_default_config()
        else:
            config_file = Path(config_path)

        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")

        try:
            # 載入配置文件
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() in ['.yaml', '.yml']:
                    raw_config = yaml.safe_load(f)
                else:
                    raw_config = json.load(f)

            # 轉換為配置物件
            self._config = self._parse_config(raw_config)
            logger.info(f"成功載入配置文件: {config_file}")
            return self._config

        except Exception as e:
            logger.error(f"載入配置文件失敗: {e}")
            raise

    def _parse_config(self, raw_config: Dict[str, Any]) -> AppConfig:
        """解析原始配置字典為配置物件"""

        # 解析模型配置
        model_config = raw_config.get("model", {})
        model = ModelConfig(
            provider=model_config.get("provider", "ollama"),
            model=model_config.get("model", "llama3:latest"),
            api_key=model_config.get("api_key"),
            base_url=model_config.get("base_url"),
            temperature=model_config.get("temperature", 0.7),
            max_tokens=model_config.get("max_tokens")
        )

        # 解析 MCP 配置
        mcp_config = None
        if "mcp" in raw_config:
            mcp_config = MCPConfig(servers=raw_config["mcp"])

        # 解析日誌配置
        logging_config = LoggingConfig()
        if "logging" in raw_config:
            log_config = raw_config["logging"]
            logging_config = LoggingConfig(
                level=log_config.get("level", "INFO"),
                format=log_config.get("format", logging_config.format),
                file_path=log_config.get("file_path")
            )

        return AppConfig(
            model=model,
            mcp=mcp_config,
            logging=logging_config,
            debug=raw_config.get("debug", False),
            max_execution_time=raw_config.get("max_execution_time", 300)
        )

    def _create_default_config(self) -> AppConfig:
        """創建預設配置"""
        return AppConfig(
            model=ModelConfig(
                provider="ollama",
                model="qwen3:0.6b"
            ),
            debug=False
        )

    def save_config(self, config: AppConfig, config_path: str) -> None:
        """
        保存配置到文件

        Args:
            config: 配置物件
            config_path: 保存路徑
        """
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # 轉換為字典
        config_dict = asdict(config)

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                if config_file.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"配置已保存到: {config_file}")

        except Exception as e:
            logger.error(f"保存配置失敗: {e}")
            raise

    def get_config(self) -> Optional[AppConfig]:
        """取得當前配置"""
        return self._config

    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        更新配置

        Args:
            updates: 要更新的配置項
        """
        if self._config is None:
            self._config = self._create_default_config()

        # 這裡可以實現更複雜的配置更新邏輯
        # 目前簡單處理
        for key, value in updates.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    def setup_logging(self) -> None:
        """根據配置設置日誌"""
        if self._config is None:
            return

        logging_config = self._config.logging

        # 設置日誌級別
        log_level = getattr(logging, logging_config.level.upper(), logging.INFO)

        # 配置根日誌記錄器
        handlers = []

        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(logging_config.format)
        console_handler.setFormatter(console_formatter)
        handlers.append(console_handler)

        # 文件處理器（如果配置了）
        if logging_config.file_path:
            file_handler = logging.FileHandler(logging_config.file_path, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(logging_config.format)
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)

        # 配置根記錄器
        logging.basicConfig(
            level=log_level,
            format=logging_config.format,
            handlers=handlers
        )

        logger.info(f"日誌系統已配置，級別: {logging_config.level}")
