"""
API 路由模块 - 认证与对话管理
使用 FastAPI APIRouter 组织 RESTful 接口
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel

from app.database import get_db
from app.models.models import User, Conversation, Message
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter()


# ============================================================
#  请求/响应 Schema
# ============================================================
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ProfileUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    school_name: Optional[str] = None
    subject_category: Optional[str] = None
    courses: Optional[list] = None
    teaching_styles: Optional[list] = None


class ConversationCreateRequest(BaseModel):
    title: str = "New Conversation"


class ConversationUpdateRequest(BaseModel):
    title: Optional[str] = None
    state: Optional[str] = None
    requirements: Optional[dict] = None


# ============================================================
#  认证接口
# ============================================================
@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册：创建账户并返回 JWT 令牌"""
    # 检查用户名和邮箱是否已存在
    existing = (await db.execute(
        select(User).where((User.username == body.username) | (User.email == body.email))
    )).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")

    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()

    token = create_access_token({"sub": user.id})
    return {
        "message": "注册成功",
        "access_token": token,
        "user": user.to_dict(),
    }


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录：校验密码并返回 JWT 令牌"""
    user = (await db.execute(
        select(User).where(User.username == body.username)
    )).scalars().first()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token({"sub": user.id})
    return {
        "access_token": token,
        "user": user.to_dict(),
    }


@router.get("/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return {"user": user.to_dict()}


@router.put("/profile")
async def update_profile(
    body: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新用户画像信息"""
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await db.flush()
    return {"message": "画像更新成功", "user": user.to_dict()}


# ============================================================
#  对话管理接口
# ============================================================
@router.get("")
async def list_conversations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的对话列表"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    return {"conversations": [c.to_dict() for c in conversations]}


@router.post("", status_code=201)
async def create_conversation(
    body: ConversationCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新对话，附带欢迎消息"""
    conversation = Conversation(
        user_id=user.id,
        title=body.title,
        state="INITIAL",
    )
    db.add(conversation)
    await db.flush()

    welcome = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="您好！我是AI助手，可以帮您生成专业的PPT和教案。请告诉我您想制作什么主题的PPT？",
        meta_data={"is_welcome": True},
    )
    db.add(welcome)
    return {"conversation": conversation.to_dict()}


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取对话详情（含消息列表）"""
    conv = (await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        )
    )).scalars().first()

    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")

    return {"conversation": conv.to_dict(include_messages=True)}


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除对话及其所有消息"""
    conv = (await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        )
    )).scalars().first()

    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")

    await db.delete(conv)
    return {"message": "对话已删除"}


@router.patch("/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    body: ConversationUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新对话属性（标题、状态、需求）"""
    conv = (await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        )
    )).scalars().first()

    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(conv, field, value)

    return {"conversation": conv.to_dict()}