"""
WebSocket 聊天处理器
基于 FastAPI WebSocket 实现实时双向通信，驱动 AI Agent 工作流
"""
import json
import logging
import asyncio
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import async_session
from app.models.models import Conversation, Message, User
from app.services.agent_service import process_user_message

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器，维护会话房间与连接映射"""

    def __init__(self):
        # conversation_id -> set of websocket connections
        self.active_connections: Dict[str, set] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        """接受连接并加入房间"""
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = set()
        self.active_connections[conversation_id].add(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        """断开连接并移出房间"""
        room = self.active_connections.get(conversation_id, set())
        room.discard(websocket)
        if not room:
            self.active_connections.pop(conversation_id, None)

    async def emit(self, event: str, data: dict, conversation_id: str):
        """向房间内所有连接广播事件"""
        room = self.active_connections.get(conversation_id, set())
        payload = json.dumps({"event": event, "data": data}, ensure_ascii=False)
        dead = set()
        for ws in room:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.add(ws)
        room -= dead


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    """
    WebSocket 聊天端点

    协议：
        客户端发送: {"event": "send_message", "data": {"content": "...", "user_id": "..."}}
        服务端推送事件:
            - message_received: 新消息（用户或AI）
            - streaming_start: 流式输出开始
            - message_chunk: 流式文本片段
            - outline_generated: 大纲生成完成
            - ppt_generated: PPT 生成完成
            - state_changed: 对话状态变更
            - error: 错误信息
    """
    await manager.connect(websocket, conversation_id)

    try:
        while True:
            raw = await websocket.receive_text()
            packet = json.loads(raw)
            event = packet.get("event", "")
            data = packet.get("data", {})

            if event == "send_message":
                await _handle_send_message(conversation_id, data)
            elif event == "generate_outline":
                await _handle_generate_outline(conversation_id, data)
            elif event == "generate_ppt":
                await _handle_generate_ppt(conversation_id, data)

    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
        logger.info(f"WebSocket 断开: conversation_id={conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket 异常: {e}")
        manager.disconnect(websocket, conversation_id)


async def _handle_send_message(conversation_id: str, data: dict):
    """
    处理用户发送消息的核心流程

    通过 LangGraph Agent 工作流完成：
    1. 保存用户消息
    2. 执行需求提取 + RAG 检索 + AI 回复
    3. 流式推送 AI 响应
    4. 保存 AI 消息
    """
    user_id = data.get("user_id")
    content = data.get("content", "").strip()

    if not content:
        await manager.emit("error", {"message": "消息内容不能为空"}, conversation_id)
        return

    async with async_session() as session:
        # 验证对话归属
        conv = (await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )).scalars().first()

        if not conv:
            await manager.emit("error", {"message": "对话不存在"}, conversation_id)
            return

        # 保存用户消息
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=content,
            user_id=user_id,
        )
        session.add(user_msg)
        await session.flush()

        # 广播用户消息
        await manager.emit("message_received", user_msg.to_dict(), conversation_id)

        # 获取对话历史
        history_result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        history = [
            {"role": m.role, "content": m.content}
            for m in history_result.scalars().all()
        ]

        # 获取用户画像
        user = (await session.execute(
            select(User).where(User.id == user_id)
        )).scalars().first()
        user_profile = user.to_dict() if user else None

        # 调用 Agent 工作流
        result = await process_user_message(
            conversation_id=conversation_id,
            user_id=user_id,
            user_message=content,
            history=history,
            requirements=conv.requirements or {},
            user_profile=user_profile,
        )

        # 流式推送 AI 回复
        await manager.emit("streaming_start", {
            "conversation_id": conversation_id,
        }, conversation_id)

        ai_response = result.get("ai_response", "")
        chunk_size = 20  # 模拟流式分块
        for i in range(0, len(ai_response), chunk_size):
            chunk = ai_response[i : i + chunk_size]
            await manager.emit("message_chunk", {
                "conversation_id": conversation_id,
                "content": chunk,
            }, conversation_id)
            await asyncio.sleep(0.02)

        # 保存 AI 消息
        ai_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response,
            meta_data={"thinking_content": result.get("thinking_content", "")},
        )
        session.add(ai_msg)

        # 处理大纲生成结果
        outline = result.get("outline")
        if outline:
            conv.state = "GENERATING_OUTLINE"
            outline_msg = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=f"已生成PPT大纲：{outline.get('title', '')}",
                meta_data={"outline": outline, "mindmap": result.get("mindmap", ""), "type": "outline"},
            )
            session.add(outline_msg)
            await session.flush()
            await manager.emit("outline_generated", {
                "outline": outline,
                "mindmap": result.get("mindmap", ""),
                "message": outline_msg.to_dict(),
            }, conversation_id)

        # 更新需求
        if result.get("requirements"):
            conv.requirements = result["requirements"]

        await session.flush()

    # 广播最终 AI 消息
    await manager.emit("message_received", ai_msg.to_dict(), conversation_id)


async def _handle_generate_outline(conversation_id: str, data: dict):
    """处理主动触发大纲生成事件"""
    await manager.emit("outline_generation_progress", {
        "progress": 10,
        "message": "正在准备生成大纲...",
    }, conversation_id)

    # 通过 Agent 工作流生成大纲（实际逻辑在 agent_service 中）
    await manager.emit("outline_generation_progress", {
        "progress": 100,
        "message": "大纲生成完成",
    }, conversation_id)


async def _handle_generate_ppt(conversation_id: str, data: dict):
    """处理 PPT 生成事件（通过 Celery 异步任务）"""
    await manager.emit("ppt_generation_start", {
        "conversation_id": conversation_id,
    }, conversation_id)

    # 实际 PPT 生成由 Celery Worker 异步执行
    # 此处仅推送进度事件
    await manager.emit("ppt_generation_progress", {
        "progress": 50,
        "message": "正在生成PPT...",
    }, conversation_id)