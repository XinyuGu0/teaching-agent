"""
认证服务模块
提供密码哈希、JWT 令牌生成与校验、用户身份提取
"""
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.models.models import User


def hash_password(raw: str) -> str:
    """对明文密码进行 bcrypt 哈希"""
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_ctx.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    """校验密码与哈希是否匹配"""
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_ctx.verify(raw, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    生成 JWT 访问令牌

    Args:
        data: 载荷数据，通常包含 {"sub": user_id}
        expires_delta: 自定义过期时间间隔

    Returns:
        编码后的 JWT 字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    ))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """解码并验证 JWT 令牌，失败时抛出异常"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效令牌")


async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI 依赖注入：从请求头提取并验证当前用户

    用法：
        @router.get("/me")
        async def me(user: User = Depends(get_current_user)):
            return {"user": user.to_dict()}
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="认证格式错误")

    token = authorization[7:]
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="令牌缺少用户标识")

    user = (await db.execute(
        select(User).where(User.id == user_id)
    )).scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return user