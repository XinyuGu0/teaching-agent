"""
LLM service for AI conversation using OpenAI-compatible API
"""
from typing import List, Dict, Optional
from flask import current_app
import time
import random
import os
import httpx

# Global LLM client (lazy loaded)
_llm_client = None

# API配置 - 从环境变量读取，支持 .env 文件
LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'https://api.bltcy.cn/v1')
LLM_API_KEY = os.getenv('LLM_API_KEY', '') or os.getenv('GLM_API_KEY', '')
LLM_MODEL = os.getenv('LLM_MODEL', 'qwen3.5-plus-2026-02-15')


def get_llm_client():
    """Get or initialize OpenAI-compatible client"""
    global _llm_client

    if _llm_client is None:
        try:
            from openai import OpenAI

            # 优先使用 Flask config，其次环境变量/默认值
            api_key = ''
            base_url = LLM_BASE_URL
            try:
                api_key = current_app.config.get('LLM_API_KEY') or current_app.config.get('GLM_API_KEY') or ''
                base_url = current_app.config.get('LLM_BASE_URL') or LLM_BASE_URL
            except RuntimeError:
                # 不在 Flask 上下文中，使用环境变量
                pass

            if not api_key:
                api_key = LLM_API_KEY

            if not api_key:
                raise ValueError("LLM_API_KEY not configured")

            _llm_client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=httpx.Timeout(30.0, read=600.0)
            )
            print(f"LLM client initialized successfully (base_url: {base_url})")

        except Exception as e:
            print(f"Error initializing LLM client: {e}")
            raise

    return _llm_client


def chat(
    messages: List[Dict[str, str]],
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    stream: bool = False,
    tools: List[Dict] = None,
    enable_web_search: bool = False,
    enable_thinking: bool = False,
    retry_count: int = 0,
    retry_delay: float = 1.0,
    timeout_seconds: int = 180
) -> Dict:
    """
    Send chat request to LLM via OpenAI-compatible API

    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Model name (default: qwen3.5-plus-2026-02-15)
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens to generate
        stream: Whether to stream the response
        tools: List of tool definitions
        enable_web_search: Whether to enable web search (ignored for non-GLM)
        enable_thinking: Whether to enable thinking process (ignored)
        retry_count: Number of retries on failure
        retry_delay: Base delay between retries
        timeout_seconds: Request timeout

    Returns:
        Response dictionary
    """
    last_error = None
    max_attempts = max(1, int(retry_count) + 1)
    
    # 使用默认模型
    if model is None:
        model = LLM_MODEL

    for attempt in range(max_attempts):
        try:
            client = get_llm_client()

            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }

            # Add tools if provided
            if tools:
                params["tools"] = tools

            response = client.chat.completions.create(
                **params,
                timeout=timeout_seconds
            )

            if stream:
                return response  # Return generator for streaming

            # Non-streaming response - 添加空列表检查
            if not response.choices or len(response.choices) == 0:
                print("[LLM] 警告: API返回空的choices列表")
                return {
                    'content': '',
                    'role': 'assistant',
                    'finish_reason': 'empty',
                    'tool_calls': None,
                    'usage': {
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'total_tokens': 0
                    }
                }
            
            print(f"[LLM] API响应finish_reason: {response.choices[0].finish_reason}")
            
            # 获取消息内容
            message = response.choices[0].message
            content = message.content or ''
            if not content:
                print("[LLM] 警告: message.content为空")

            return {
                'content': content,
                'role': message.role,
                'finish_reason': response.choices[0].finish_reason,
                'tool_calls': getattr(message, 'tool_calls', None),
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                    'completion_tokens': response.usage.completion_tokens if response.usage else 0,
                    'total_tokens': response.usage.total_tokens if response.usage else 0
                }
            }

        except Exception as e:
            last_error = e
            err_text = str(e)
            print(f"Error calling LLM API (attempt {attempt + 1}/{max_attempts}): {e}")
            if attempt < max_attempts - 1:
                sleep_s = retry_delay * (2 ** attempt)
                if '429' in err_text or 'Too Many Requests' in err_text:
                    sleep_s += random.uniform(0.5, 1.5)
                time.sleep(sleep_s)
                continue
            raise

    if last_error:
        raise last_error


def chat_with_context(
    user_message: str,
    conversation_history: List[Dict[str, str]],
    context_documents: List[str] = None,
    system_prompt: str = None,
    enable_web_search: bool = False,
    stream: bool = False,
    enable_thinking: bool = False,
    retry_count: int = 1,
    timeout_seconds: int = 60
):
    """
    Chat with LLM including RAG context

    Args:
        user_message: User's message
        conversation_history: Previous messages in conversation
        context_documents: Retrieved documents from RAG
        system_prompt: System prompt to set behavior
        enable_web_search: Whether to enable web search
        stream: Whether to stream the response
        enable_thinking: Whether to enable thinking process (ignored)
        retry_count: Number of retries
        timeout_seconds: Request timeout

    Returns:
        Assistant's response (string if not streaming, generator if streaming)
    """
    messages = []

    # Add system prompt
    if system_prompt:
        base_prompt = system_prompt
    else:
        base_prompt = "你是一个专业的AI助手，帮助用户生成PPT和教案。请根据用户需求和提供的参考资料，给出专业、详细的建议。"
    
    messages.append({
        "role": "system",
        "content": base_prompt
    })

    # Add conversation history
    messages.extend(conversation_history)

    # Add RAG context if available
    if context_documents and len(context_documents) > 0:
        context_text = "\n\n".join([f"参考资料 {i+1}:\n{doc}" for i, doc in enumerate(context_documents)])

        messages.append({
            "role": "system",
            "content": f"以下是相关的参考资料，请结合这些资料回答用户问题：\n\n{context_text}"
        })

    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message
    })

    # Call LLM
    response = chat(
        messages,
        stream=stream,
        retry_count=retry_count,
        timeout_seconds=timeout_seconds
    )

    if stream:
        return response
    else:
        return response['content']


def summarize_outline_intent_from_history(
    conversation_history: List[Dict[str, str]],
    current_requirements: Dict = None
) -> Dict:
    """Use LLM to re-read dialogue and extract structured outline intent"""
    import json

    current_requirements = current_requirements or {}
    history_text = "\n".join([
        f"{m.get('role', 'user')}: {m.get('content', '')}"
        for m in conversation_history[-20:]
        if m.get('content')
    ])

    prompt = f"""请你根据以下对话，提取用于生成PPT大纲的关键信息。

强约束：
1) 只基于用户需求提取，不要沿用助手历史输出中的主题。
2) 主题必须优先使用"用户最近一次明确提出的课程/章节/任务"。
3) 如果用户最新需求与之前内容冲突，必须以最新需求为准。
4) 忽略寒暄与无关话题（如"你好""我是谁"）。
5) 输出必须是JSON，不要输出其他内容。

当前已提取信息（可参考但不要盲从）：
{json.dumps(current_requirements, ensure_ascii=False)}

对话历史：
{history_text}

输出JSON格式：
{{
  "topic": "",
  "audience": "",
  "purpose": "",
  "slide_count": "",
  "style": "",
  "confidence": 0.0,
  "reason": "一句话说明为什么是这个主题（引用最近用户需求）"
}}
"""

    messages = [
        {"role": "system", "content": "你是需求提取助手，只输出合法JSON。"},
        {"role": "user", "content": prompt}
    ]

    response = chat(messages, temperature=0.2, max_tokens=1200)
    content = response.get('content', '{}')

    try:
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        return json.loads(content)
    except Exception:
        return {
            "topic": current_requirements.get('topic', ''),
            "audience": current_requirements.get('audience', ''),
            "purpose": current_requirements.get('purpose', ''),
            "slide_count": str(current_requirements.get('slide_count', '12')),
            "style": current_requirements.get('style', ''),
            "confidence": 0.0,
            "reason": "fallback"
        }


def generate_text_outline_preview(topic: str, requirements: Dict) -> str:
    """Generate human-readable text outline before structured outline generation"""
    prompt = f"""请基于以下信息，先生成"文字版大纲预览"（不是JSON）：

主题：{topic}
受众：{requirements.get('audience', '通用')}
用途：{requirements.get('purpose', '教学')}
页数：{requirements.get('slide_count', '12')}
风格：{requirements.get('style', '专业')}

要求：
1) 输出格式：标题 + 6-10个一级要点（编号列表）
2) 每个要点一句话，简洁明确
3) 体现教学结构（导入-核心知识-案例/互动-总结）
4) 仅输出文字版大纲，不要JSON，不要代码块
"""
    messages = [
        {"role": "system", "content": "你是教学PPT策划助手，擅长输出清晰的文字大纲。"},
        {"role": "user", "content": prompt}
    ]
    resp = chat(messages, temperature=0.4, max_tokens=1200)
    return (resp.get('content') or '').strip()


def generate_ppt_outline(
    topic: str,
    requirements: Dict,
    context_documents: List[str] = None,
    explicit_outline_text: str = None,
    conversation_history: List[Dict[str, str]] = None
) -> Dict:
    """Generate PPT outline and mindmap with speed-first settings."""
    import json

    try:
        slide_count_num = int(str(requirements.get('slide_count', '12')).strip())
    except Exception:
        slide_count_num = 12

    slide_count_num = max(6, min(slide_count_num, 20))

    template_info = requirements.get('template_info') or {}
    template_slides = template_info.get('slides') if isinstance(template_info, dict) else []

    compact_context = ''
    if context_documents:
        compact_context = "\n\n".join([
            f"参考{i+1}:{(doc or '')[:380]}"
            for i, doc in enumerate(context_documents[:3])
        ])

    compact_dialogue = ''
    if conversation_history:
        compact_dialogue = "\n".join([
            f"{m.get('role', 'user')}: {(m.get('content') or '').strip()[:140]}"
            for m in conversation_history[-8:]
            if (m.get('content') or '').strip()
        ])

    prompt = f"""请生成PPT大纲与思维导图（速度优先）。

主题：{topic}
受众：{requirements.get('audience', '通用')}
用途：{requirements.get('purpose', '教学')}
风格：{requirements.get('style', '专业')}
页数：{slide_count_num}

模板信息（可选）：{json.dumps(template_slides, ensure_ascii=False)[:1200]}

用户指定大纲（若有，最高优先级）：
{(explicit_outline_text or '').strip()[:1200]}

最近对话（摘要）：
{compact_dialogue}

参考资料（摘要）：
{compact_context}

只返回JSON，不要代码块，不要解释。格式严格如下：
{{
  "title": "...",
  "outline": {{
    "slides": [
      {{
        "slide_number": 1,
        "title": "...",
        "position": "cover|toc|content|section|ending|custom",
        "target_template_slide_type": "cover|toc|content|section|ending|custom",
        "target_placeholders": ["{{title}}", "{{text}}"],
        "content_points": ["...", "...", "..."]
      }}
    ]
  }},
  "mindmap": "# 标题\\n## 分支\\n### 子分支"
}}

硬性约束：
1) slides长度必须等于{slide_count_num}
2) 每页content_points为3条，短句
3) 不输出detailed_content/visual_design/speaker_notes等长字段
4) 若有用户指定大纲，主题与结构必须优先对齐
"""

    messages = [
        {"role": "system", "content": "你是教学PPT大纲生成器。输出必须是可解析JSON，简洁、准确、快速。"},
        {"role": "user", "content": prompt}
    ]

    print(f"[OUTLINE_PROMPT] 准备调用LLM: slide_count={slide_count_num}, history_chars={len(compact_dialogue)}, context_chars={len(compact_context)}")

    response = chat(
        messages,
        temperature=0.35,
        max_tokens=2800,
        retry_count=0,
        retry_delay=1.0,
        timeout_seconds=40
    )

    # Parse JSON response
    import json
    import re

    def _build_fallback_outline():
        slides = []
        for i in range(slide_count_num):
            if i == 0:
                slides.append({
                    "slide_number": 1,
                    "title": topic,
                    "position": "cover",
                    "target_template_slide_type": "cover",
                    "target_placeholders": ["{{title}}", "{{description}}"],
                    "content_points": [
                        requirements.get('purpose', '课程导入'),
                        requirements.get('audience', '目标受众')
                    ],
                    "notes": "标题页"
                })
            else:
                slides.append({
                    "slide_number": i + 1,
                    "title": f"第{i}部分：{topic}",
                    "position": "content",
                    "target_template_slide_type": "content",
                    "target_placeholders": ["{{title}}", "{{text}}", "{{description}}"],
                    "content_points": [
                        "核心概念与定义",
                        "关键知识点讲解",
                        "案例与练习"
                    ],
                    "notes": "自动回退生成"
                })

        return {
            "title": topic,
            "outline": {"slides": slides},
            "mindmap": f"# {topic}\n## 核心知识\n### 概念\n### 方法\n## 实践应用\n### 案例\n### 练习"
        }

    try:
        content = (response.get('content') or '').strip()
        # 尝试提取JSON（可能包含在markdown代码块中）
        if '```json' in content:
            content = content.split('```json', 1)[1].split('```', 1)[0].strip()
        elif '```' in content:
            content = content.split('```', 1)[1].split('```', 1)[0].strip()

        # 若仍不是纯JSON，提取首个{...}对象
        if content and not content.startswith('{'):
            match = re.search(r"\{[\s\S]*\}", content)
            if match:
                content = match.group(0)

        result = json.loads(content)

        # 兼容模型直接返回 slides 数组的情况
        if isinstance(result, dict) and 'outline' not in result and 'slides' in result:
            result = {
                'title': result.get('title', topic),
                'outline': {'slides': result.get('slides') or []},
                'mindmap': result.get('mindmap', '')
            }

        # 兜底补全字段
        if 'outline' not in result or not isinstance(result.get('outline'), dict):
            result['outline'] = {'slides': []}
        if 'slides' not in result['outline'] or not isinstance(result['outline'].get('slides'), list):
            result['outline']['slides'] = []
        if 'title' not in result or not result.get('title'):
            result['title'] = topic
        if 'mindmap' not in result:
            result['mindmap'] = ''

        # 页数矫正
        actual_count = len(result['outline']['slides'])
        if actual_count != slide_count_num:
            print(f"警告：生成的页数({actual_count})与要求({slide_count_num})不符，执行页数矫正")
            if actual_count == 0:
                return _build_fallback_outline()
            if actual_count > slide_count_num:
                result['outline']['slides'] = result['outline']['slides'][:slide_count_num]
            else:
                for i in range(actual_count, slide_count_num):
                    result['outline']['slides'].append({
                        "slide_number": i + 1,
                        "title": f"第{i}部分：{topic}",
                        "content_points": ["补充要点1", "补充要点2", "补充要点3"],
                        "notes": "自动补齐页"
                    })

        return result
    except Exception as e:
        print(f"JSON解析失败: {e}")
        return _build_fallback_outline()


def refine_outline(
    current_outline: Dict,
    user_feedback: str,
    context_documents: List[str] = None
) -> Dict:
    """
    Refine PPT outline based on user feedback
    """
    import json

    prompt = f"""当前PPT大纲：
{json.dumps(current_outline, ensure_ascii=False, indent=2)}

用户反馈：
{user_feedback}

请根据用户反馈修改大纲，并以相同的JSON格式返回修改后的大纲。
"""

    if context_documents:
        context_text = "\n\n".join([f"参考资料 {i+1}:\n{doc}" for i, doc in enumerate(context_documents)])
        prompt += f"\n\n参考资料：\n{context_text}"

    messages = [
        {"role": "system", "content": "你是一个专业的PPT设计师，根据用户反馈优化PPT大纲。"},
        {"role": "user", "content": prompt}
    ]

    response = chat(messages, temperature=0.7)

    try:
        refined_outline = json.loads(response['content'])
        return refined_outline
    except json.JSONDecodeError:
        return current_outline


def generate_all_slides_commands(
    topic: str,
    total_slides: int,
    requirements: Dict = None,
    style_theme: str = None,
    full_dialogue: str = '',
    full_context: str = '',
    ai_outline_content: str = ''
) -> Dict:
    """
    一次性生成所有幻灯片的OfficeCLI命令
    """
    import json
    
    requirements = requirements or {}
    
    # 加载OfficeCLI技能知识
    from app.services.officecli_skill_loader import get_skill_knowledge
    skill_knowledge = get_skill_knowledge()
    skill_content = skill_knowledge.raw_content[:8000] if skill_knowledge.loaded else ""
    
    prompt = f'''# OfficeCLI 完整PPT生成任务

你是资深PPT设计师，使用OfficeCLI命令行工具创建完整的PPT。

## ⚠️ 核心要求（必须严格遵守）

1. **按顺序生成**：必须按照第1页、第2页、第3页...的顺序依次生成，不能跳页或乱序
2. **内容严格对应**：每页的内容必须严格对应AI大纲中对应页面的内容，不能混淆
3. **页数完整**：必须生成完整的 {total_slides} 页，不能遗漏
4. **风格统一**：所有页面使用完全相同的配色方案和字体风格

## OfficeCLI命令规范

{skill_content}

## 设计任务

### PPT主题
{topic}

### 页数要求
共 {total_slides} 页（必须全部生成）

### AI生成的文字大纲（⚠️ 每页内容必须严格对应以下大纲！）
{ai_outline_content}

### 完整对话历史（补充上下文）
{full_dialogue}

### 参考资料
{full_context}

### 需求配置
{json.dumps(requirements, ensure_ascii=False, indent=2)}

## 设计要求

### 1. 整体设计原则
- **风格统一**：所有页面使用一致的配色方案、字体风格、布局风格
- **专业美观**：每页都要精心设计，不能有简陋的页面
- **内容完整**：严格按照AI大纲的内容设计，不要遗漏要点

### 2. 配色方案（选择一套并全程保持）
推荐专业配色：
- 商务蓝：主色 #1E3A5F，辅色 #4A90D9，强调色 #F39C12
- 科技感：主色 #0D47A1，辅色 #2196F3，强调色 #00BCD4
- 教育绿：主色 #2E7D32，辅色 #4CAF50，强调色 #FF9800
- 简约灰：主色 #37474F，辅色 #78909C，强调色 #FF5722

### 3. 页面类型设计
- **封面页（第1页）**：大标题、副标题、装饰元素、纯色背景
- **目录页（可选）**：清晰的章节导航
- **内容页**：根据内容选择图示类型
- **结尾页（最后一页）**：总结、致谢、联系方式

### 4. 形状类型（重要！）
**支持的形状类型**：rect, roundRect, ellipse, triangle, diamond, pentagon, hexagon, star, arrow, chevron
**注意**：不支持 `circle`，请使用 `ellipse` 代替！

### 5. 坐标和尺寸约束（重要！）
- 所有坐标(x, y)必须 >= 0，不能使用负值
- 所有尺寸(width, height)必须 > 0，不能使用负值
- 推荐范围：x: 0-25cm, y: 0-19cm, width: 1-25cm, height: 0.5-18cm

### 6. 命令数量要求
- 封面页：至少15条命令
- 内容页：每页至少20条命令
- 结尾页：至少12条命令

## 输出格式

请按以下格式输出每一页的设计：

```
=== 第1页 [封面] ===
设计说明：[简述设计思路]

命令：
officecli add deck.pptx / --type slide --prop background="#1E3A5F"
officecli add deck.pptx /slide[1] --type shape --prop text="{topic}" --prop x="2cm" --prop y="3cm" ...
... 更多命令

=== 第2页 [内容] ===
...
```

现在请开始设计完整的PPT：
'''

    messages = [
        {
            "role": "system", 
            "content": """你是资深PPT设计师，擅长设计专业、美观、风格统一的演示文稿。

设计原则：
1. 整体风格统一：配色、字体、布局保持一致
2. 每页精心设计：不能有简陋的页面
3. 内容准确：严格按照大纲内容设计
4. 视觉丰富：使用图示、表格、装饰元素

输出格式：按页面分块输出命令，不需要JSON格式，使用清晰的文本格式。"""
        },
        {"role": "user", "content": prompt}
    ]

    try:
        print(f"[LLM] 开始一次性生成所有页面，共{total_slides}页")
        response = chat(
            messages,
            temperature=0.3,
            max_tokens=32768,
            retry_count=3,
            retry_delay=3.0,
            timeout_seconds=600
        )
        
        content = response.get('content', '')
        finish_reason = response.get('finish_reason', '')
        
        print(f"[LLM] LLM返回内容长度: {len(content)}, finish_reason: {finish_reason}")
        
        if not content or not content.strip():
            print(f"[LLM] LLM返回空内容")
            return {
                "success": False,
                "error": "LLM返回空内容",
                "slides": []
            }
        
        # 解析命令输出
        slides_commands = parse_slides_from_text(content, total_slides)
        
        print(f"[LLM] 解析完成，共{len(slides_commands)}页命令")
        
        return {
            "success": True,
            "raw_content": content,
            "slides": slides_commands,
            "total_slides": len(slides_commands)
        }
        
    except Exception as e:
        print(f"[LLM] 生成所有页面命令失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "slides": []
        }


def parse_slides_from_text(text: str, expected_slides: int) -> list:
    """从文本中解析每一页的命令"""
    import re
    
    slides = []
    
    slide_pattern = r'===\s*第(\d+)页.*?==='
    parts = re.split(slide_pattern, text, flags=re.IGNORECASE)
    
    if len(parts) < 3:
        slide_pattern2 = r'(?:^|\n)\s*(?:第\s*(\d+)\s*页|Slide\s*(\d+))'
        parts = re.split(slide_pattern2, text, flags=re.IGNORECASE)
    
    current_slide = 1
    for i in range(1, len(parts), 2):
        if i + 1 >= len(parts):
            break
            
        slide_num_str = parts[i]
        slide_content = parts[i + 1] if i + 1 < len(parts) else ''
        
        try:
            slide_num = int(slide_num_str)
        except:
            slide_num = current_slide
        
        commands = extract_commands_from_text(slide_content)
        
        if commands:
            slides.append({
                "slide_index": slide_num,
                "commands": commands,
                "raw_content": slide_content[:500]
            })
        
        current_slide += 1
    
    if not slides:
        commands = extract_commands_from_text(text)
        if commands:
            slide_cmds = {}
            for cmd in commands:
                slide_idx = extract_slide_index(cmd)
                if slide_idx not in slide_cmds:
                    slide_cmds[slide_idx] = []
                slide_cmds[slide_idx].append(cmd)
            
            for slide_idx in sorted(slide_cmds.keys()):
                slides.append({
                    "slide_index": slide_idx,
                    "commands": slide_cmds[slide_idx],
                    "raw_content": ""
                })
    
    if len(slides) < expected_slides:
        print(f"[PARSE] 警告：解析到{len(slides)}页，预期{expected_slides}页")
    
    return slides


def extract_commands_from_text(text: str) -> list:
    """从文本中提取OfficeCLI命令"""
    import re
    
    commands = []
    
    cmd_pattern = r'officecli\s+(\w+)\s+(\S+)\s+(\S+)(?:\s+--type\s+(\S+))?((?:\s+--prop\s+[^-\s][^\s]*)*)'
    
    for match in re.finditer(cmd_pattern, text, re.IGNORECASE):
        try:
            command = match.group(1)
            file_path = match.group(2)
            path = match.group(3)
            element_type = match.group(4) or ''
            props_str = match.group(5) or ''
            
            props = {}
            prop_pattern = r'--prop\s+([^=]+)=(?:"([^"]*)"|\'([^\']*)\'|(\S+))'
            for prop_match in re.finditer(prop_pattern, props_str):
                key = prop_match.group(1).strip()
                value = prop_match.group(2) or prop_match.group(3) or prop_match.group(4) or ''
                value = value.strip().strip('"\'')
                props[key] = value
            
            cmd_dict = {
                "command": command,
                "path": path,
                "type": element_type,
                "props": props
            }
            
            if command in ['add', 'set', 'remove', 'move']:
                commands.append(cmd_dict)
                
        except Exception as e:
            print(f"[PARSE] 解析命令失败: {e}")
            continue
    
    # 兼容JSON格式
    json_pattern = r'\{\s*"command"\s*:\s*"([^"]+)"\s*,\s*"path"\s*:\s*"([^"]+)"\s*,\s*"type"\s*:\s*"([^"]*)"\s*,\s*"props"\s*:\s*(\{[^}]*\})\s*\}'
    for match in re.finditer(json_pattern, text):
        try:
            import json
            cmd_dict = {
                "command": match.group(1),
                "path": match.group(2),
                "type": match.group(3),
                "props": json.loads(match.group(4))
            }
            if cmd_dict not in commands:
                commands.append(cmd_dict)
        except:
            pass
    
    return commands


def extract_slide_index(cmd: dict) -> int:
    """从命令中提取slide索引"""
    import re
    path = cmd.get('path', '/')
    match = re.search(r'/slide\[(\d+)\]', path)
    if match:
        return int(match.group(1))
    return 1


def generate_single_slide_commands(
    topic: str,
    slide_index: int,
    total_slides: int,
    requirements: Dict = None,
    style_theme: str = None,
    compact_dialogue: str = '',
    compact_context: str = '',
    slide_title: str = None,
    slide_content: List[str] = None,
    ai_outline_content: str = ''
) -> Dict:
    """
    生成单个幻灯片的OfficeCLI命令（JSON格式）
    
    逐页生成模式：每次只生成一页的命令，支持传入该页的具体标题和内容
    
    Args:
        topic: PPT主题
        slide_index: 当前页码（1-based）
        total_slides: 总页数
        requirements: 需求配置
        style_theme: 风格主题
        compact_dialogue: 压缩的对话历史
        compact_context: 压缩的参考资料
        slide_title: 该页的标题（来自大纲）
        slide_content: 该页的内容要点列表（来自大纲）
        ai_outline_content: 完整的AI大纲内容（用于保持整体一致性）
    
    Returns:
        包含commands列表的字典
    """
    import json
    
    requirements = requirements or {}
    
    is_cover = slide_index == 1
    is_ending = slide_index == total_slides
    
    # 使用传入的标题，或使用默认标题
    if slide_title:
        default_title = slide_title
    elif is_cover:
        default_title = topic
    elif is_ending:
        default_title = "总结与致谢"
    else:
        default_title = f"第{slide_index}页"
    
    # 格式化该页的内容要点
    slide_content_text = ""
    if slide_content:
        slide_content_text = "\n".join([f"  - {point}" for point in slide_content])

    prompt = f'''# OfficeCLI 单页PPT生成任务（逐页生成）

你是资深PPT设计师，使用OfficeCLI命令行工具创建单页PPT。

## 当前任务

### PPT主题
{topic}

### 当前页信息
- 页码：{slide_index} / {total_slides}
- 页面类型：{"**封面页**" if is_cover else ("**结尾页**" if is_ending else "**内容页**")}

### 上下文信息
1. **对话摘要**：
{compact_dialogue}

2. **参考资料**：
{compact_context}

3. **需求配置**：
{json.dumps(requirements, ensure_ascii=False, indent=2)}

## 输出格式（必须是合法JSON）

```json
{{
  "slide_index": {slide_index},
  "slide_type": "{"cover" if is_cover else ("ending" if is_ending else "content")}",
  "design_note": "设计说明",
  "slide_title": "该页标题",
  "commands": [
    {{
      "command": "add",
      "path": "/",
      "type": "slide",
      "props": {{
        "background": "F5F5F5"
      }}
    }},
    {{
      "command": "add",
      "path": "/slide[{slide_index}]",
      "type": "shape",
      "props": {{
        "text": "标题文本",
        "x": "2cm",
        "y": "1cm",
        "width": "20cm",
        "height": "2cm"
      }}
    }}
  ]
}}
```

**严格遵循**：
1. 输出必须是合法的JSON格式
2. 所有属性放在props对象中
3. 路径使用1-based索引：/slide[{slide_index}]
4. 不要输出代码块标记，直接输出JSON
'''

    messages = [
        {
            "role": "system", 
            "content": """你是资深PPT设计师。
**输出格式**：必须是合法的JSON，不要代码块标记，不要其他文字。"""
        },
        {"role": "user", "content": prompt}
    ]

    try:
        response = chat(
            messages,
            temperature=0.4,
            max_tokens=8192,
            retry_count=1,
            retry_delay=1.0
        )
        
        content = response.get('content', '')
        finish_reason = response.get('finish_reason', '')
        
        print(f"[LLM] LLM返回内容长度: {len(content)}, finish_reason: {finish_reason}")
        
        if not content or not content.strip():
            print(f"[LLM] LLM返回空内容")
            return {
                "slide_index": slide_index,
                "slide_type": "cover" if is_cover else ("ending" if is_ending else "content"),
                "design_note": "LLM返回空内容",
                "commands": []
            }
        
        try:
            cleaned_content = content
            if '```json' in cleaned_content:
                cleaned_content = cleaned_content.split('```json')[1].split('```')[0].strip()
            elif '```' in cleaned_content:
                parts = cleaned_content.split('```')
                if len(parts) >= 2:
                    cleaned_content = parts[1].strip()
                    if cleaned_content.startswith('json'):
                        cleaned_content = cleaned_content[4:].strip()
            
            result = json.loads(cleaned_content)
            
            if 'commands' not in result:
                result['commands'] = []
            if 'slide_index' not in result:
                result['slide_index'] = slide_index
            if 'slide_type' not in result:
                result['slide_type'] = "cover" if is_cover else ("ending" if is_ending else "content")
            
            print(f"[LLM] JSON解析成功，命令数: {len(result.get('commands', []))}")
            return result
            
        except json.JSONDecodeError as e:
            print(f"[LLM] JSON解析失败: {e}")
            
            # 尝试从内容中提取JSON对象
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    result = json.loads(json_match.group(0))
                    if 'commands' not in result:
                        result['commands'] = []
                    return result
                except:
                    pass
            
            return {
                "slide_index": slide_index,
                "slide_type": "cover" if is_cover else ("ending" if is_ending else "content"),
                "design_note": f"JSON解析失败: {str(e)}",
                "commands": []
            }
        
    except Exception as e:
        print(f"[LLM] 生成单页命令失败: {e}")
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"AI生成单页命令失败: {e}")


def review_and_fix_slide_commands(
    topic: str,
    slide_data: Dict,
    slide_index: int,
    original_commands: str,
    ppt_path: str = "deck.pptx"
) -> str:
    """检查并修复单页幻灯片的命令"""
    import json
    
    slide_title = slide_data.get('title', f'第{slide_index}页')
    content_points = slide_data.get('content_points', [])
    
    prompt = f'''# OfficeCLI 命令检查与修复任务

你是OfficeCLI命令专家。请检查以下命令是否符合规范，如有问题请修复。

## 原始命令

{original_commands}

## 幻灯片信息
- 标题：{slide_title}
- 内容：{json.dumps(content_points[:3], ensure_ascii=False)}

## 任务

1. 检查每条命令是否符合规范
2. 修复所有格式错误
3. 确保路径索引正确（当前是第{slide_index}页）
4. 输出修复后的命令

直接输出修复后的bash命令，每行一条。
'''

    messages = [
        {
            "role": "system", 
            "content": "你是OfficeCLI命令检查专家。检查命令格式，修复错误，直接输出修复后的命令。"
        },
        {"role": "user", "content": prompt}
    ]

    try:
        response = chat(
            messages,
            temperature=0.2,
            max_tokens=2000,
            retry_count=1,
            retry_delay=1.0
        )
        
        content = response.get('content', '')
        
        if not content or not content.strip():
            print(f"检查修复返回空内容，使用原始命令")
            return original_commands
        
        return content
        
    except Exception as e:
        print(f"检查修复命令失败: {e}")
        return original_commands


# 兼容性别名
get_glm_client = get_llm_client