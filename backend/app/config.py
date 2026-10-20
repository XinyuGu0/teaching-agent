import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///guowaibao.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # File Upload Configuration
    UPLOAD_MAX_SIZE = int(os.getenv('UPLOAD_MAX_SIZE', 104857600))  # 100MB
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'pdf,doc,docx,ppt,pptx,xls,xlsx,txt,md,jpg,jpeg,png,gif,mp4,avi,mov,mp3,wav,m4a,ogg,flac,aac').split(',')

    # Data Directories
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    KNOWLEDGE_BASE_DIR = os.path.join(DATA_DIR, 'knowledge_base')
    USER_UPLOADS_DIR = os.path.join(DATA_DIR, 'user_uploads')
    VECTOR_DB_DIR = os.path.join(DATA_DIR, 'vector_db')
    GENERATED_PPTS_DIR = os.path.join(DATA_DIR, 'generated_ppts')
    GENERATED_LESSONS_DIR = os.path.join(DATA_DIR, 'generated_lessons')
    TEMPLATES_DIR = os.path.join(DATA_DIR, 'templates')
    
    # Upload folder (general purpose)
    UPLOAD_FOLDER = DATA_DIR

    # GLM API Configuration (legacy, kept for backward compatibility)
    GLM_API_KEY = os.getenv('GLM_API_KEY', '')

    # LLM API Configuration (OpenAI-compatible, used by Qwen model)
    LLM_API_KEY = os.getenv('LLM_API_KEY', '')
    LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'https://api.bltcy.cn/v1')
    LLM_MODEL = os.getenv('LLM_MODEL', 'qwen3.5-plus-2026-02-15')

    # Doubao async image generation (via OpenAI-compatible gateway)
    DOUBAO_BASE_URL = os.getenv('DOUBAO_BASE_URL', 'https://api.gpt-best.com/v1')
    DOUBAO_API_KEY = os.getenv('DOUBAO_API_KEY', '')
    DOUBAO_IMAGE_MODEL = os.getenv('DOUBAO_IMAGE_MODEL', 'doubao-seedance-1-5-pro-251215')
    DOUBAO_ASYNC_TIMEOUT_SECONDS = int(os.getenv('DOUBAO_ASYNC_TIMEOUT_SECONDS', '75'))
    DOUBAO_ASYNC_POLL_INTERVAL_SECONDS = float(os.getenv('DOUBAO_ASYNC_POLL_INTERVAL_SECONDS', '2.5'))

    # Docmee (文多多) PPT API
    DOCMEE_BASE_URL = os.getenv('DOCMEE_BASE_URL', 'https://api.bltcy.cn')
    DOCMEE_API_KEY = os.getenv('DOCMEE_API_KEY', '')
    DOCMEE_TIMEOUT_SECONDS = int(os.getenv('DOCMEE_TIMEOUT_SECONDS', '60'))
    DOCMEE_POLL_INTERVAL_SECONDS = float(os.getenv('DOCMEE_POLL_INTERVAL_SECONDS', '5'))
    DOCMEE_PPT_MODEL_ID = os.getenv('DOCMEE_PPT_MODEL_ID', 'docmee-ppt-generate')

    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')

    # WOPI / Collabora Configuration
    WOPI_BASE_URL = os.getenv('WOPI_BASE_URL', 'http://127.0.0.1:9980')
    WOPI_HOST = os.getenv('WOPI_HOST', 'http://127.0.0.1:5000')  # Collabora 可访问的后端地址
    WOPI_SECRET_KEY = os.getenv('WOPI_SECRET_KEY', SECRET_KEY)
    WOPI_TOKEN_TTL = int(os.getenv('WOPI_TOKEN_TTL', 3600))
    
    # OnlyOffice Configuration
    ONLYOFFICE_URL = os.getenv('ONLYOFFICE_URL', 'http://localhost:80')
    ONLYOFFICE_JWT_SECRET = os.getenv('ONLYOFFICE_JWT_SECRET', '')
    PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', '')

    # Celery Configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
