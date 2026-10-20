"""
AI Agent 服务模块
基于 LangChain + LangGraph 构建 PPT 生成智能体工作流

工作流状态图：
    INITIAL -> COLLECTING -> CHAT -> GENERATING_OUTLINE -> OUTLINE_REVIEWED -> GENERATING_PPT
"""
import json
import logging
from typing import Dict, List, Optional, TypedDict, Annotated
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END

from app.config import settings

logger = logging.getLogger(__name__)


# ============================================================
#  对话状态定义
# ============================================================
class ConversationState(TypedDict, total=False):
    """LangGraph 工作流状态结构"""
    conversation_id: str
    user_id: str
    messages: List[Dict]               # 对话历史
    user_message: str                  # 当前用户消息
    ai_response: str                   # AI 回复内容
    thinking_content: str              # 思考过程（若模型支持）
    state: str                         # 当前状态机节点
    requirements: Dict                 # 已采集的需求
    context_documents: List[str]       # RAG 检索结果
    outline: Optional[Dict]            # 生成的 PPT 大纲
    mindmap: Optional[str]             # 思维导图文本
    user_profile: Optional[Dict]       # 用户画像信息
    should_generate_outline: bool      # 是否触发大纲生成
    should_transition: bool            # 是否应转换状态


# ============================================================
#  LangChain LLM 客户端初始化
# ============================================================
def get_llm_client(
    temperature: float = 0.7,
    max_tokens: int = 4096,
    streaming: bool = False,
) -> ChatOpenAI:
    """
    创建 LangChain ChatOpenAI 客户端实例

    通过 OpenAI 兼容接口对接通义千问 / 智谱GLM 等国产大模型
    """
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        openai_api_key=settings.LLM_API_KEY,
        openai_api_base=settings.LLM_BASE_URL,
        temperature=temperature,
        max_tokens=max_tokens,
        streaming=streaming,
    )


# ============================================================
#  需求提取节点
# ============================================================
REQUIREMENT_KEYS = ["topic", "audience", "purpose", "slide_count", "style"]


def extract_requirements(state: ConversationState) -> ConversationState:
    """
    从用户消息中提取结构化需求

    利用 LLM 解析自然语言，输出 topic/audience/purpose 等字段，
    合并到已有 requirements 中并去重
    """
    existing = state.get("requirements", {})
    user_msg = state.get("user_message", "")

    if not user_msg:
        return state

    llm = get_llm_client(temperature=0.2, max_tokens=800)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你是需求提取助手。从用户消息中提取PPT相关需求，输出JSON。\n"
            "字段：topic（主题）、audience（受众）、purpose（用途）、"
            "slide_count（页数）、style（风格）。\n"
            "只输出JSON，不要解释。"
        )),
        ("human", "已有需求：{existing}\n用户消息：{message}"),
    ])

    try:
        chain = prompt | llm
        result = chain.invoke({
            "existing": json.dumps(existing, ensure_ascii=False),
            "message": user_msg,
        })

        content = result.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()

        extracted = json.loads(content)

        # 合并到已有需求（新值覆盖旧值）
        for key in REQUIREMENT_KEYS:
            if extracted.get(key):
                existing[key] = extracted[key]

        state["requirements"] = existing
    except Exception as e:
        logger.warning(f"需求提取失败，保留已有需求: {e}")

    return state


# ============================================================
#  RAG 检索节点
# ============================================================
def retrieve_context(state: ConversationState) -> ConversationState:
    """
    基于用户消息执行向量检索（RAG）

    从 ChromaDB 中检索与当前问题最相关的文档片段，
    作为上下文注入后续 LLM 调用
    """
    user_msg = state.get("user_message", "")
    if not user_msg:
        state["context_documents"] = []
        return state

    try:
        from app.services.rag_service import search_documents
        from app.utils.embeddings import generate_embedding

        query_embedding = generate_embedding(user_msg)
        results = search_documents(
            query_text=user_msg,
            query_embedding=query_embedding,
            n_results=5,
            filter_metadata={"user_id": state.get("user_id")},
        )
        state["context_documents"] = results.get("documents", [])
    except Exception as e:
        logger.warning(f"RAG 检索失败: {e}")
        state["context_documents"] = []

    return state


# ============================================================
#  AI 对话生成节点
# ============================================================
def generate_chat_response(state: ConversationState) -> ConversationState:
    """
    调用 LLM 生成对话回复（流式）

    组装系统提示词（含用户画像 + RAG 上下文 + 状态引导），
    与对话历史一起发送给 LLM
    """
    llm = get_llm_client(temperature=0.7, streaming=True)

    # 构建系统提示词
    system_content = _build_system_prompt(state)

    # 组装 LangChain 消息列表
    lc_messages = [SystemMessage(content=system_content)]
    for msg in state.get("messages", []):
        if msg.get("role") == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        elif msg.get("role") == "assistant":
            lc_messages.append(AIMessage(content=msg["content"]))

    lc_messages.append(HumanMessage(content=state.get("user_message", "")))

    # 流式生成
    full_response = ""
    for chunk in llm.stream(lc_messages):
        if hasattr(chunk, "content") and chunk.content:
            full_response += chunk.content

    state["ai_response"] = full_response
    return state


def _build_system_prompt(state: ConversationState) -> str:
    """根据当前状态和上下文构建系统提示词"""
    prompt = (
        "你是AI教学助手，帮助用户制作专业的PPT和教案。\n"
        "你能够根据用户需求生成结构清晰的PPT大纲，支持多种文档格式。\n"
    )

    # 注入用户画像
    profile = state.get("user_profile")
    if profile:
        parts = []
        if profile.get("nickname"):
            parts.append(f"昵称：{profile['nickname']}")
        if profile.get("school_name"):
            parts.append(f"学校：{profile['school_name']}")
        if profile.get("courses"):
            parts.append(f"课程：{', '.join(profile['courses'])}")
        if parts:
            prompt += "\n[用户画像]\n" + "\n".join(parts) + "\n请结合画像给出个性化建议。\n"

    # 注入 RAG 上下文
    docs = state.get("context_documents", [])
    if docs:
        context_text = "\n\n".join([f"参考资料 {i+1}:\n{doc}" for i, doc in enumerate(docs[:3])])
        prompt += f"\n[检索到的参考资料]\n{context_text}\n请基于上述资料回答。\n"

    return prompt


# ============================================================
#  大纲生成节点
# ============================================================
def generate_outline_node(state: ConversationState) -> ConversationState:
    """
    调用 LLM 生成 PPT 结构化大纲和思维导图

    输出格式：
    {
        "title": "...",
        "outline": {"slides": [...]},
        "mindmap": "# 标题\\n## 分支\\n### 子分支"
    }
    """
    requirements = state.get("requirements", {})
    topic = requirements.get("topic", "主题演示")

    try:
        slide_count = int(str(requirements.get("slide_count", "12")).strip())
    except ValueError:
        slide_count = 12
    slide_count = max(6, min(slide_count, 20))

    llm = get_llm_client(temperature=0.35, max_tokens=2800)

    prompt = f"""请生成PPT大纲与思维导图。

主题：{topic}
受众：{requirements.get('audience', '通用')}
用途：{requirements.get('purpose', '教学')}
风格：{requirements.get('style', '专业')}
页数：{slide_count}

只返回JSON，不要代码块，不要解释。格式如下：
{{
  "title": "...",
  "outline": {{
    "slides": [
      {{
        "slide_number": 1,
        "title": "...",
        "position": "cover|toc|content|section|ending",
        "content_points": ["...", "...", "..."]
      }}
    ]
  }},
  "mindmap": "# 标题\\n## 分支\\n### 子分支"
}}

约束：
1) slides长度必须等于{slide_count}
2) 每页content_points为3条短句
"""

    messages = [
        SystemMessage(content="你是教学PPT大纲生成器。输出必须是可解析JSON。"),
        HumanMessage(content=prompt),
    ]

    try:
        result = llm.invoke(messages)
        content = result.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        outline_data = json.loads(content)
        state["outline"] = outline_data.get("outline", outline_data)
        state["mindmap"] = outline_data.get("mindmap", "")
    except Exception as e:
        logger.error(f"大纲生成失败: {e}")
        # 兜底：生成基础大纲
        state["outline"] = _build_fallback_outline(topic, slide_count)
        state["mindmap"] = f"# {topic}\n## 核心知识\n### 概念\n### 方法\n## 实践应用"

    return state


def _build_fallback_outline(topic: str, slide_count: int) -> dict:
    """大纲生成失败时的兜底方案"""
    slides = []
    for i in range(slide_count):
        slides.append({
            "slide_number": i + 1,
            "title": topic if i == 0 else f"第{i}部分",
            "position": "cover" if i == 0 else ("ending" if i == slide_count - 1 else "content"),
            "content_points": ["核心概念", "关键知识点", "案例与练习"],
        })
    return {"title": topic, "slides": slides}


# ============================================================
#  LangGraph 工作流构建
# ============================================================
def should_generate_outline(state: ConversationState) -> str:
    """
    条件边：判断是否需要触发大纲生成

    Returns:
        "generate_outline" 或 "chat"
    """
    if state.get("should_generate_outline"):
        return "generate_outline"
    return "chat"


def build_conversation_graph() -> StateGraph:
    """
    构建 LangGraph 对话工作流

    节点流程：
        extract_requirements -> retrieve_context -> route
            -> chat -> END
            -> generate_outline -> END
    """
    graph = StateGraph(ConversationState)

    # 添加节点
    graph.add_node("extract_requirements", extract_requirements)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("chat", generate_chat_response)
    graph.add_node("generate_outline", generate_outline_node)

    # 设置入口
    graph.set_entry_point("extract_requirements")

    # 添加边
    graph.add_edge("extract_requirements", "retrieve_context")
    graph.add_conditional_edges(
        "retrieve_context",
        should_generate_outline,
        {
            "chat": "chat",
            "generate_outline": "generate_outline",
        },
    )
    graph.add_edge("chat", END)
    graph.add_edge("generate_outline", END)

    return graph


# 编译工作流图
conversation_graph = build_conversation_graph().compile()


# ============================================================
#  对外服务接口
# ============================================================
async def process_user_message(
    conversation_id: str,
    user_id: str,
    user_message: str,
    history: List[Dict],
    requirements: Dict,
    user_profile: Optional[Dict] = None,
) -> Dict:
    """
    处理用户消息的统一入口

    通过 LangGraph 工作流自动完成：
    1. 需求提取
    2. RAG 文档检索
    3. 对话回复 / 大纲生成

    Args:
        conversation_id: 对话 ID
        user_id: 用户 ID
        user_message: 用户发送的文本
        history: 历史消息列表
        requirements: 已采集的需求
        user_profile: 用户画像

    Returns:
        包含 AI 回复 / 大纲的结果字典
    """
    # 检测是否触发大纲生成
    generate_keywords = ["生成大纲", "生成ppt", "开始生成", "开始制作"]
    should_generate = any(kw in user_message.lower() for kw in generate_keywords)

    initial_state: ConversationState = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "messages": history,
        "user_message": user_message,
        "ai_response": "",
        "thinking_content": "",
        "state": "CHAT",
        "requirements": requirements or {},
        "context_documents": [],
        "outline": None,
        "mindmap": None,
        "user_profile": user_profile,
        "should_generate_outline": should_generate,
        "should_transition": False,
    }

    # 执行工作流
    result = await conversation_graph.ainvoke(initial_state)

    return {
        "ai_response": result.get("ai_response", ""),
        "requirements": result.get("requirements", {}),
        "outline": result.get("outline"),
        "mindmap": result.get("mindmap"),
        "state": result.get("state", "CHAT"),
    }