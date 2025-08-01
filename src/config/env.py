import os
from dotenv import load_dotenv

def load_env(env_file: str = ".env"):
    """
    載入指定的 .env 檔案（預設為 src/.env）。
    """
    src_dir = os.path.dirname(os.path.dirname(__file__))
    env_path = os.path.join(src_dir, env_file)
    load_dotenv(dotenv_path=env_path, override=True)
