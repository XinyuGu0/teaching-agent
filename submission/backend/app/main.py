"""
FastAPI 应用入口模块
负责初始化应用、注册路由、配置中间件和生命周期事件
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base, init_db
from app.api import auth, conversation, document, ppt, share
from app.websocket.chat import router as ws_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """应用生命周期管理：启动时初始化数据库，关闭时清理资源"""
    logger.info("应用启动中，正在初始化数据库...")
    await init_db()

    # 确保数据目录存在
    for directory in [
        settings.USER_UPLOADS_DIR,
        settings.VECTOR_DB_DIR,
        settings.GENERATED_PPTS_DIR,
        settings.TEMPLATES_DIR,
    ]:
        os.makedirs(directory, exist_ok=True)

    logger.info("应用启动完成")
    yield
    logger.info("应用正在关闭...")


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例"""
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI驱动的PPT生成与教案辅助平台",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS 中间件配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册 API 路由
    app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
    app.include_router(conversation.router, prefix="/api/conversations", tags=["对话"])
    app.include_router(document.router, prefix="/api/documents", tags=["文档"])
    app.include_router(ppt.router, prefix="/api/ppts", tags=["PPT"])
    app.include_router(share.router, prefix="/api/shares", tags=["分享"])

    # 注册 WebSocket 路由
    app.include_router(ws_router)

    # 静态文件服务：提供上传文件访问
    os.makedirs(settings.USER_UPLOADS_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.USER_UPLOADS_DIR), name="uploads")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.DEBUG,
        log_level="info",
    )