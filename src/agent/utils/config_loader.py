import json
from pathlib import Path


def load_config(config_path: str) -> dict:
    """
    Load a JSON config file and return its contents as a dictionary.
    Raises FileNotFoundError or json.JSONDecodeError on error.
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)
