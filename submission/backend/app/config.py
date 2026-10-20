"""
应用配置模块
使用 pydantic-settings 管理配置，支持环境变量和 .env 文件
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """全局配置项"""

    # 应用基础配置
    APP_NAME: str = "AI-PPT-Platform"
    DEBUG: bool = False
    SECRET_KEY: str = "change-in-production"
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/guowaibao"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # JWT 认证配置
    JWT_SECRET_KEY: str = "jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440      # 24小时
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery 配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # LLM API 配置（OpenAI 兼容接口）
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.bltcy.cn/v1"
    LLM_MODEL: str = "qwen3.5-plus-2026-02-15"

    # 豆包图片生成 API
    DOUBAO_BASE_URL: str = "https://api.gpt-best.com/v1"
    DOUBAO_API_KEY: str = ""
    DOUBAO_IMAGE_MODEL: str = "doubao-seedance-1-5-pro-251215"

    # 文档处理服务 API
    DOCMEE_BASE_URL: str = "https://api.bltcy.cn"
    DOCMEE_API_KEY: str = ""

    # OnlyOffice 配置
    ONLYOFFICE_URL: str = "http://localhost:80"
    ONLYOFFICE_JWT_SECRET: str = ""

    # 文件上传配置
    UPLOAD_MAX_SIZE: int = 104857600  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [
        "pdf", "doc", "docx", "ppt", "pptx",
        "xls", "xlsx", "txt", "md",
        "jpg", "jpeg", "png", "gif",
        "mp4", "avi", "mov",
    ]

    # 数据目录配置
    DATA_DIR: str = ""
    USER_UPLOADS_DIR: str = ""
    VECTOR_DB_DIR: str = ""
    GENERATED_PPTS_DIR: str = ""
    TEMPLATES_DIR: str = ""

    # CORS 配置
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    def model_post_init(self, __context):
        """初始化派生目录路径"""
        base = self.BASE_DIR
        data_dir = os.path.join(base, "data")
        if not self.DATA_DIR:
            self.DATA_DIR = data_dir
        if not self.USER_UPLOADS_DIR:
            self.USER_UPLOADS_DIR = os.path.join(data_dir, "user_uploads")
        if not self.VECTOR_DB_DIR:
            self.VECTOR_DB_DIR = os.path.join(data_dir, "vector_db")
        if not self.GENERATED_PPTS_DIR:
            self.GENERATED_PPTS_DIR = os.path.join(data_dir, "generated_ppts")
        if not self.TEMPLATES_DIR:
            self.TEMPLATES_DIR = os.path.join(data_dir, "templates")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# 全局配置单例
settings = Settings()