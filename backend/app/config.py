"""
项目配置管理
通过 .env 文件或环境变量加载配置
"""

import os
from pathlib import Path

from pydantic_settings import BaseSettings

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """应用配置"""

    # ---- 基础配置 ----
    APP_NAME: str = "辅导员工作辅助平台"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # ---- 数据库 ----
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'app.db'}"

    # ---- 文件上传 ----
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_FILE_SIZE_MB: int = 10  # 最大上传文件大小 (MB)
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp"}

    # ---- LLM 配置（二选一即可） ----
    LLM_PROVIDER: str = "openai"  # "openai" 或 "gemini"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""  # 可选，用于代理
    OPENAI_MODEL: str = "gpt-4o"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # ---- CORS ----
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:5175", "http://127.0.0.1:5173"]
    # 生产环境通过环境变量追加，如: CORS_EXTRA_ORIGINS=https://yourdomain.com
    CORS_EXTRA_ORIGINS: str = ""

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()

# 确保必要目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(BASE_DIR / "data", exist_ok=True)
