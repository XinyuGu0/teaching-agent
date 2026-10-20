"""
数据模型定义
使用 SQLAlchemy 2.0 声明式映射，定义核心业务表结构
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import String, Text, JSON, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid_str() -> str:
    return str(uuid.uuid4())


# ============================================================
#  用户模型
# ============================================================
class User(Base):
    """用户表：存储账户信息与教师画像"""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # 教师画像字段
    teacher_gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    teacher_age: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    school_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    subject_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    courses: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    teaching_styles: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)

    # 关系
    conversations: Mapped[List["Conversation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def set_password(self, raw: str):
        """对明文密码进行哈希存储"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        """校验密码是否匹配"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, raw)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "teacher_gender": self.teacher_gender,
            "school_name": self.school_name,
            "subject_category": self.subject_category,
            "courses": self.courses or [],
            "teaching_styles": self.teaching_styles or [],
        }


# ============================================================
#  对话模型
# ============================================================
class Conversation(Base):
    """对话表：管理用户与 AI 的会话上下文及需求采集状态"""
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), default="New Conversation")
    status: Mapped[str] = mapped_column(String(20), default="active")
    state: Mapped[str] = mapped_column(String(50), default="INITIAL")  # 状态机当前状态
    requirements: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now, onupdate=_utc_now)

    # 关系
    user: Mapped["User"] = relationship(back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )

    def to_dict(self, include_messages: bool = False) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "status": self.status,
            "state": self.state,
            "requirements": self.requirements,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_messages:
            data["messages"] = [m.to_dict() for m in self.messages]
        return data


# ============================================================
#  消息模型
# ============================================================
class Message(Base):
    """消息表：存储对话中的每条消息，包括元数据"""
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user / assistant / system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)

    # 关系
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    def to_dict(self) -> dict:
        meta = self.meta_data or {}
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "thinkingContent": meta.get("thinking_content", ""),
            "meta_data": meta,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================
#  文档模型
# ============================================================
class Document(Base):
    """文档表：管理用户上传的文件及向量化索引状态"""
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(20), default="uploaded")  # uploaded / indexed / error
    chunk_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "filename": self.filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "status": self.status,
            "chunk_count": self.chunk_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================
#  PPT 模型
# ============================================================
class PPT(Base):
    """PPT 表：记录生成的 PPT 文件及其大纲数据"""
    __tablename__ = "ppts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), default="Untitled")
    theme: Mapped[str] = mapped_column(String(50), default="modern")
    outline: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    slides_data: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    template_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="generating")  # generating / ready / error
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "theme": self.theme,
            "outline": self.outline,
            "status": self.status,
            "file_path": self.file_path,
            "template_id": self.template_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================
#  分享模型
# ============================================================
class ConversationShare(Base):
    """对话分享表：支持生成分享链接和协作访问"""
    __tablename__ = "conversation_shares"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False, index=True
    )
    share_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    share_type: Mapped[str] = mapped_column(String(20), default="view")  # view / collab
    password: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    expire_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now)