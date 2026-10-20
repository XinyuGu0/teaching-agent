# 后端代码整理文档

## 一、服务层 (Services)

### 1. glm_service.py - GLM AI 服务

**文件作用**: 封装智谱AI GLM模型的调用，提供对话、大纲生成、内容适配等AI能力。

| 函数名 | 作用 | 实现说明 |
|--------|------|----------|
| `get_glm_client()` | 获取/初始化GLM客户端 | 单例模式，使用全局变量缓存客户端实例 |
| `chat()` | 发送对话请求到GLM | 支持流式/非流式、Web搜索、思考模式、重试机制 |
| `chat_with_context()` | 带上下文的对话 | 整合RAG文档、对话历史、系统提示词，返回流式响应 |
| `summarize_outline_intent_from_history()` | 从对话历史提取大纲意图 | 使用LLM分析用户对话，提取主题/受众/用途等结构化信息 |
| `adapt_content_to_template_placeholders()` | 模板占位符内容适配 | 根据模板占位符生成适配的内容，支持封面/目录/内容页等 |
| `generate_text_outline_preview()` | 生成文字版大纲预览 | 生成人类可读的大纲预览文本（非JSON） |
| `generate_ppt_outline()` | 生成PPT大纲和思维导图 | 核心函数：根据主题/需求/上下文生成结构化大纲和思维导图 |
| `refine_outline()` | 优化大纲 | 根据用户反馈修改现有大纲 |
| `analyze_image()` | 图像分析 | 使用GLM-4V视觉模型分析图片 |

---

### 2. docmee_service.py - 文多多API服务

**文件作用**: 封装文多多(Docmee)第三方PPT生成API的调用。

| 函数名 | 作用 | 实现说明 |
|--------|------|----------|
| `__init__()` | 初始化服务 | 从Flask配置读取API密钥、基础URL、超时时间 |
| `_headers()` | 构建请求头 | 包含Content-Type、Accept、Authorization |
| `_extract_text_chunk()` | 提取文本块 | 从SSE响应中提取文本内容，支持多种字段名 |
| `_extract_ppt_id()` | 提取PPT ID | 从响应中递归查找pptId，支持多种嵌套结构 |
| `_stream_sse()` | SSE流式请求处理 | 处理Server-Sent Events流，解析JSON数据块 |
| `generate_outline_stream()` | 流式生成大纲 | 调用`/generateOutline` API，返回SSE流 |
| `generate_content_stream()` | 流式生成内容 | 调用`/generateContent` API，触发异步PPT生成 |
| `async_ppt_info()` | 查询异步PPT状态 | 调用`/asyncPptInfo`查询生成进度 |
| `load_pptx()` | 加载PPTX | 调用`/loadPptx`获取PPT详情 |
| `download_pptx()` | 下载PPTX | 调用`/downloadPptx`获取下载链接 |
| `get_user_ppt_list()` | 获取用户PPT列表 | 调用`/ppt/list`获取用户历史PPT |
| `get_latest_ppt_id()` | 获取最新PPT ID | 从用户列表中获取最近生成的PPT ID（备用方案） |

---

### 3. structured_ppt_generator.py - 结构化PPT生成器

**文件作用**: 采用分步骤、模板化的方式生成高质量PPT。

| 函数名 | 作用 | 实现说明 |
|--------|------|----------|
| `generate_ppt()` | 主生成函数 | 流程：验证大纲→生成标题页→目录页→逐页内容→质量验证 |
| `_generate_detailed_content()` | 生成详细内容 | 使用LLM将大纲要点扩展为详细内容（20-40字/条） |
| `_search_quality_image()` | 搜索配图 | 使用图片服务搜索相关图片 |
| `validate_ppt_quality()` | 质量验证 | 检查页数、内容完整性、边界问题 |
| `_get_template_slide_count()` | 获取模板页数 | 读取模板PPT文件获取页数 |
| `_copy_template_slide()` | 复制模板页 | 完整复制模板页（背景、文本框、图片、形状） |
| `_generate_slide_from_template()` | 从模板生成页 | 复制布局并替换文字内容 |
| `_analyze_slide_layout_with_vision()` | 视觉分析布局 | 使用视觉模型分析应该使用哪个模板页 |
| `_extract_placeholders_by_slide()` | 提取占位符 | 从幻灯片中提取所有`{{xxx}}`占位符 |
| `_apply_template_placeholders()` | 应用占位符替换 | 根据占位符替换模板中的文本和图片 |

---

### 4. rag_service.py - RAG检索服务

**文件作用**: 使用Chroma向量数据库实现文档索引和检索。

| 函数名 | 作用 | 实现说明 |
|--------|------|----------|
| `get_chroma_client()` | 获取Chroma客户端 | 单例模式，初始化持久化向量数据库 |
| `get_collection()` | 获取/创建集合 | 获取名为"documents"的向量集合 |
| `add_documents()` | 添加文档 | 将文本块、嵌入向量、元数据存入向量库 |
| `search_documents()` | 搜索文档 | 根据查询向量检索相似文档 |
| `delete_documents()` | 删除文档 | 按ID删除文档 |
| `delete_documents_by_metadata()` | 按元数据删除 | 按条件（如document_id）批量删除 |
| `get_collection_stats()` | 获取统计信息 | 返回集合中的文档总数 |

---

## 二、WebSocket层 (websocket/chat.py)

**文件作用**: 处理前端WebSocket连接，实现实时对话、大纲生成、PPT生成等核心功能。

### 事件处理函数

| 事件名 | 函数名 | 作用 |
|--------|--------|------|
| `connect` | `handle_connect()` | 处理客户端连接 |
| `disconnect` | `handle_disconnect()` | 处理客户端断开 |
| `join_conversation` | `handle_join_conversation()` | 加入对话房间，发送历史消息 |
| `send_message` | `handle_send_message()` | **核心**：处理用户消息，AI回复，触发大纲生成 |
| `generate_outline` | `handle_generate_outline()` | **核心**：生成PPT大纲（支持GLM和Docmee两种引擎） |
| `generate_ppt` | `handle_generate_ppt()` | **核心**：使用本地模板生成PPT |
| `generate_api_ppt` | `handle_generate_api_ppt()` | **核心**：使用文多多API生成PPT |
| `update_slide` | `handle_update_slide()` | 更新单页幻灯片 |
| `ai_modify_slide` | `handle_ai_modify_slide()` | AI修改单页幻灯片 |

### handle_send_message() 详细流程

```
1. 验证参数和对话
2. 保存用户消息
3. 初始化状态机，提取需求
4. 检测是否需要生成大纲（关键词触发）
   ├── 如果需要生成大纲：
   │   ├── LLM回顾对话提取主题
   │   ├── 生成文字版大纲预览
   │   ├── RAG检索相关文档
   │   ├── 调用glm_service.generate_ppt_outline()
   │   ├── 保存大纲消息
   │   └── 发送outline_generated事件
   └── 否则：
       ├── RAG检索相关文档
       ├── 注入用户画像
       ├── 调用glm_service.chat_with_context()流式响应
       └── 保存AI消息
```

---

## 三、大纲生成流程（详细版）

### 方案一：GLM引擎（默认）

#### 触发方式
```javascript
// 前端调用
socket.emit('generate_outline', {
  conversation_id: 'xxx',
  user_id: 'xxx',
  topic: '移动应用开发中的数据存储',
  requirements: {
    audience: '大学生',
    purpose: '课程教学',
    slide_count: 12,
    style: '专业',
    outline_engine: 'glm'  // 默认为glm
  }
})
```

#### 详细执行流程

**Step 1: 参数验证** (`handle_generate_outline`)
```python
# 检查必要参数
missing_params = []
if not conversation_id: missing_params.append('conversation_id')
if not user_id: missing_params.append('user_id')
if not topic: missing_params.append('topic')
```

**Step 2: 主题重提取**（可选优化）
```python
# 从对话历史中重新提取主题，避免使用过时的主题
all_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
history_for_extract = [{'role': m.role, 'content': m.content} for m in all_messages if m.content.strip()]

# 调用LLM提取
extracted = glm_service.summarize_outline_intent_from_history(history_for_extract, requirements)
# extracted = {"topic": "...", "audience": "...", "purpose": "...", "slide_count": "...", "style": "..."}

if extracted.get('topic'):
    topic = extracted['topic']  # 使用LLM提取的主题
```

**Step 3: RAG检索相关文档**
```python
# 生成查询向量
query_embedding = embeddings.generate_embedding(topic)

# 搜索向量数据库
search_results = rag_service.search_documents(
    query_text=topic,
    query_embedding=query_embedding,
    n_results=5,
    filter_metadata={'user_id': user_id}  # 只搜索用户自己的文档
)
context_documents = search_results['documents']  # 返回相关文档片段列表
```

**Step 4: 调用GLM生成大纲** (`glm_service.generate_ppt_outline`)
```python
# 构建提示词
prompt = f"""请根据以下信息生成一个详细的PPT大纲和思维导图：

主题：{topic}
要求：
- 目标受众：{requirements.get('audience', '通用')}
- 页数：必须严格生成 {slide_count_num} 页（包括标题页）
- 风格：{requirements.get('style', '专业')}
- 用途：{requirements.get('purpose', '教学')}

参考资料：{context_text}
对话上下文：{recent_dialogue}

请以JSON格式返回：
{
  "title": "PPT标题",
  "outline": {
    "slides": [
      {
        "slide_number": 1,
        "title": "幻灯片标题",
        "position": "cover|toc|content|section|ending",
        "target_template_slide_type": "cover|toc|content",
        "target_placeholders": ["{{title}}", "{{text}}"],
        "content_points": ["要点1", "要点2", "要点3"],
        "notes": "演讲备注"
      }
    ]
  },
  "mindmap": "# 主题\n## 第一部分\n### 子主题1"
}
"""

# 调用GLM API
response = chat(messages, temperature=0.45, max_tokens=8000, enable_thinking=False)

# 解析JSON响应
result = json.loads(content)

# 页数矫正（确保页数符合要求）
actual_count = len(result['outline']['slides'])
if actual_count != slide_count_num:
    if actual_count > slide_count_num:
        result['outline']['slides'] = result['outline']['slides'][:slide_count_num]
    else:
        # 补齐缺失的页
        for i in range(actual_count, slide_count_num):
            result['outline']['slides'].append({
                "slide_number": i + 1,
                "title": f"第{i}部分：{topic}",
                "content_points": ["补充要点1", "补充要点2"]
            })
```

**Step 5: 保存消息并发送事件**
```python
# 保存大纲消息
outline_message = Message(
    conversation_id=conversation_id,
    role='assistant',
    content=f"已生成PPT大纲：{result.get('title', topic)}",
    meta_data={
        'outline': outline,
        'mindmap': mindmap,
        'type': 'outline'
    }
)
db.session.add(outline_message)
db.session.commit()

# 发送事件到前端
socketio.emit('outline_generated', {
    'outline': outline,
    'mindmap': mindmap,
    'message': outline_message.to_dict()
}, room=conversation_id)
```

#### 返回数据结构
```json
{
  "outline": {
    "slides": [
      {
        "slide_number": 1,
        "title": "移动应用开发中的数据存储",
        "position": "cover",
        "target_template_slide_type": "cover",
        "target_placeholders": ["{{title}}", "{{subtitle}}"],
        "content_points": ["课程导入", "目标受众"],
        "notes": "标题页"
      },
      {
        "slide_number": 2,
        "title": "目录",
        "position": "toc",
        "target_template_slide_type": "toc",
        "target_placeholders": ["{{toc_title}}", "{{toc_1}}", "{{toc_2}}"],
        "content_points": ["1. 数据存储概述", "2. 本地存储方案"],
        "notes": "目录页"
      },
      {
        "slide_number": 3,
        "title": "数据存储概述",
        "position": "content",
        "target_template_slide_type": "content",
        "target_placeholders": ["{{title}}", "{{text}}"],
        "content_points": [
          "数据存储是指将应用程序产生的数据持久化保存到设备或服务器中的过程",
          "移动应用需要存储用户偏好、缓存内容和业务数据",
          "数据存储直接影响应用的性能、安全性和用户留存"
        ],
        "notes": "内容页"
      }
    ]
  },
  "mindmap": "# 移动应用开发中的数据存储\n## 数据存储概述\n### 定义\n### 重要性\n## 本地存储方案\n### SharedPreferences\n### SQLite\n## 云端存储\n### Firebase\n### AWS"
}
```

---

### 方案二：Docmee引擎（文多多）

#### 触发方式
```javascript
// 前端调用
socket.emit('generate_outline', {
  conversation_id: 'xxx',
  user_id: 'xxx',
  topic: '移动应用开发中的数据存储',
  requirements: {
    outline_engine: 'docmee'  // 指定使用文多多引擎
  }
})
```

#### 详细执行流程

**Step 1: 创建DocmeeService实例**
```python
from app.services.docmee_service import DocmeeService
docmee = DocmeeService()

# 初始化时读取配置
self.base_url = 'https://api.bltcy.cn'
self.api_key = 'sk-xxx'
self.timeout = 60
```

**Step 2: 调用文多多大纲生成API**
```python
# 调用 generate_outline_stream
for chunk in docmee.generate_outline_stream(topic):
    # chunk 结构:
    # {
    #   'raw': {...},           # 原始JSON对象
    #   'text': '大纲内容...',   # 提取的文本
    #   'ppt_id': ''            # pptId（大纲生成时不返回）
    # }
    
    text = chunk.get('text') or ''
    if text:
        outline_markdown += text
        
        # 实时推送到前端聊天
        socketio.emit('message_chunk', {
            'conversation_id': conversation_id,
            'content': text
        }, room=conversation_id)
```

**Step 3: SSE流处理细节** (`_stream_sse`)
```python
def _stream_sse(self, path, payload):
    url = f"{self.base_url}{path}"  # https://api.bltcy.cn/docmee/v1/api/ppt/generateOutline
    
    # 发送POST请求，启用流式接收
    resp = requests.post(url, headers=self._headers(), json=payload, timeout=self.timeout, stream=True)
    
    # 逐行处理SSE数据
    for raw_line in resp.iter_lines(decode_unicode=False):
        line = raw_line.decode('utf-8').strip()
        
        if line.startswith('data:'):
            data = line[5:].strip()  # 提取data:后面的内容
            obj = json.loads(data)   # 解析JSON
            
            yield {
                'raw': obj,
                'text': self._extract_text_chunk(obj),  # 提取文本内容
                'ppt_id': self._extract_ppt_id(obj)     # 提取pptId
            }
```

**Step 4: 保存大纲消息**
```python
outline_message = Message(
    conversation_id=conversation_id,
    role='assistant',
    content=outline_markdown or f"已生成PPT大纲：{topic}",
    meta_data={
        'outline_markdown': outline_markdown,  # 存储Markdown格式的大纲
        'outline_engine': 'docmee',
        'type': 'outline'
    }
)
db.session.add(outline_message)
db.session.commit()

# 发送流完成事件
socketio.emit('outline_stream_complete', {
    'meta_data': outline_message.meta_data
}, room=conversation_id)
```

#### 文多多返回的Markdown格式示例
```markdown
# 移动应用开发中的数据存储

## 什么是数据存储
- 数据存储是指将信息以持久化形式保存在介质中的过程
- 在移动应用中，它涉及本地与云端的结合
- 数据持久化确保应用关闭后数据依然可用

## 存储类型概述
- 本地存储：文件、SQLite、键值对
- 云端存储：云数据库、对象存储
- 选择需考虑数据规模、安全性和成本

## Android SharedPreferences
- 轻量级数据存储机制
- 以键值对形式保存配置数据
- 适用于用户偏好设置、应用状态

## SQLite数据库应用
- 轻量级嵌入式数据库
- 支持SQL语句和事务处理
- 适合中等规模结构化数据
```

---

## 四、PPT生成流程（详细版）

### 方案一：本地模板生成（generate_ppt）

#### 触发方式
```javascript
// 前端调用
socket.emit('generate_ppt', {
  conversation_id: 'xxx',
  user_id: 'xxx',
  outline: { slides: [...] },  // 可选，如果没有则自动生成
  requirements: {
    topic: '移动应用开发中的数据存储',
    audience: '大学生',
    style: '专业'
  },
  theme: 'modern',
  template_id: 'xxx'  // 可选，使用模板
})
```

#### 详细执行流程

**Step 1: 参数验证和初始化**
```python
# 验证必要参数
conversation = Conversation.query.filter_by(id=conversation_id, user_id=user_id).first()
if not conversation:
    emit('error', {'message': '对话不存在'})
    return

# 发送进度事件
socketio.emit('ppt_generation_start', {'conversation_id': conversation_id}, room=conversation_id)
socketio.emit('ppt_generation_progress', {'progress': 10, 'message': '正在分析对话内容...'})
```

**Step 2: 大纲准备**（如果没有提供大纲）
```python
if not outline:
    # 使用GLM生成大纲
    topic = conversation.requirements.get('topic', '主题演示')
    
    # RAG检索
    query_embedding = embeddings.generate_embedding(topic)
    search_results = rag_service.search_documents(query_text=topic, query_embedding=query_embedding)
    
    # 生成大纲
    outline_result = glm_service.generate_ppt_outline(topic=topic, requirements=requirements)
    outline = outline_result['outline']
```

**Step 3: 创建结构化生成器**
```python
from app.services.structured_ppt_generator import StructuredPPTGenerator

structured_generator = StructuredPPTGenerator()

# 设置进度回调
def progress_callback(progress_info):
    socketio.emit('ppt_generation_progress', {
        'progress': progress_info['progress'],
        'message': progress_info['message'],
        'slide_number': progress_info.get('slide_number'),
        'slide_data': progress_info.get('slide_data')
    }, room=conversation_id)

structured_generator.set_progress_callback(progress_callback)
```

**Step 4: 生成PPT内容** (`StructuredPPTGenerator.generate_ppt`)
```python
def generate_ppt(self, topic, outline, requirements, context_documents, conversation_history, template_id):
    slides = []
    outline_slides = outline.get('slides', [])
    
    # 1. 生成标题页
    title_slide = self.templates.get_title_slide(topic, subtitle)
    slides.append(title_slide)
    
    # 2. 生成目录页
    toc_slide = self.templates.get_full_content_slide(title="目录", content_points=toc_points)
    slides.append(toc_slide)
    
    # 3. 逐页生成内容
    for i, slide_outline in enumerate(outline_slides, start=3):
        # 使用LLM扩展内容要点
        detailed_points = self._generate_detailed_content(
            slide_title=slide_outline.get('title'),
            outline_points=slide_outline.get('content_points', []),
            topic=topic
        )
        
        # 根据位置选择布局
        if slide_outline.get('position') == 'ending':
            slide = self.templates.get_two_column_slide(...)  # 结尾页用双栏
        else:
            slide = self.templates.get_content_slide(...)  # 内容页
        
        slides.append(slide)
    
    # 4. 质量验证
    validation_result = self.validate_ppt_quality(ppt_data, expected_slide_count)
    
    return {"title": topic, "slides": slides}
```

**Step 5: 生成PPTX文件**（使用python-pptx库）
```python
from pptx import Presentation
from pptx.util import Inches

# 如果有模板
if template and template.file_path:
    prs = Presentation(template.file_path)  # 加载模板
    
    # 提取模板占位符
    placeholders_by_slide = []
    for slide in prs.slides:
        phs = re.findall(r'\{\{[^}]+\}\}', slide.text)
        placeholders_by_slide.append({'slide_index': ..., 'placeholders': phs})
    
    # LLM适配内容
    adapted = glm_service.adapt_content_to_template_placeholders(
        topic=topic, outline=outline, placeholders_by_slide=placeholders_by_slide
    )
    
    # 替换占位符
    for slide_index, slide in enumerate(prs.slides):
        for shape in slide.shapes:
            if shape.has_text_frame:
                # 替换 {{title}}, {{text}} 等占位符
                text = re.sub(r'\{\{title\}\}', topic, shape.text)
                shape.text_frame.paragraphs[0].runs[0].text = text
else:
    # 无模板，使用默认布局
    prs = Presentation()
    blank_layout = prs.slide_layouts[6]
    for slide_data in ppt_data['slides']:
        slide = prs.slides.add_slide(blank_layout)
        # 添加文本框等元素
        textbox = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        textbox.text_frame.text = slide_data['text']

# 保存文件
prs.save(file_path)
```

**Step 6: 视觉审查**（可选）
```python
from app.services.collabora_converter import convert_pptx_to_pngs
from app.services.vision_service import vision_service

# 将PPTX转换为PNG图片
png_paths = convert_pptx_to_pngs(file_path, rendered_dir)

# 分析每页的问题
for idx, png_path in enumerate(png_paths):
    issues = vision_service.analyze_page_issues(png_path, idx)
    if issues.get('has_issues'):
        # 调整字体大小、行间距等
        scale = issues.get('text_scale', 1.0)
        for run in slide.shapes[idx].text_frame.paragraphs[0].runs:
            run.font.size = Pt(int(run.font.size.pt * scale))

# 重新保存
prs.save(file_path)
```

**Step 7: 保存到数据库并发送事件**
```python
# 保存PPT记录
ppt = PPT(
    conversation_id=conversation_id,
    user_id=user_id,
    title=ppt_data.get('title'),
    outline=outline,
    slides_data=ppt_data.get('slides'),
    file_path=file_path,
    status='ready'
)
db.session.add(ppt)
db.session.commit()

# 发送完成事件
socketio.emit('ppt_generated', {'ppt': ppt.to_dict()}, room=conversation_id)
socketio.emit('ppt_generation_progress', {'progress': 100, 'message': 'PPT生成完成！'})
```

---

### 方案二：文多多API生成（generate_api_ppt）

#### 触发方式
```javascript
// 前端调用（需要先通过文多多生成大纲）
socket.emit('generate_api_ppt', {
  conversation_id: 'xxx',
  user_id: 'xxx',
  outline_markdown: '# 主题\n## 第一章\n- 要点1\n- 要点2',  // 文多多大纲格式
  requirements: {
    topic: '移动应用开发中的数据存储'
  }
})
```

#### 详细执行流程

**Step 1: 创建PPT记录**
```python
# 先创建PPT记录（状态为generating）
ppt = PPT(
    conversation_id=conversation_id,
    user_id=user_id,
    title=requirements.get('topic', 'PPT'),
    status='generating'  # 标记为生成中
)
db.session.add(ppt)
db.session.commit()

# 准备文件路径
filename = f"{safe_title}_{ppt.id}.pptx"
file_path = os.path.join(generated_dir, filename)
```

**Step 2: 启动后台线程**
```python
# 在后台线程中执行（不阻塞WebSocket连接）
def generate_api_ppt_task():
    with app_obj.app_context():
        # ... 生成逻辑 ...

thread = threading.Thread(target=generate_api_ppt_task)
thread.daemon = True
thread.start()
```

**Step 3: 调用文多多内容生成API**
```python
from app.services.docmee_service import DocmeeService
docmee = DocmeeService()

# 流式生成内容
ppt_id_holder = {'id': None}
for chunk in docmee.generate_content_stream(
    outline_markdown=outline_markdown,
    async_gen_pptx=True,  # 启用异步PPT生成
    model_id='direct-generate-pptx'
):
    ppt_id = chunk.get('ppt_id')
    if ppt_id:
        ppt_id_holder['id'] = ppt_id  # 捕获pptId
        break

# 如果没有捕获到pptId，尝试备用方案
if not ppt_id_holder['id']:
    fallback_ppt_id = docmee.get_latest_ppt_id()  # 从用户列表获取
    ppt_id_holder['id'] = fallback_ppt_id
```

**Step 4: 轮询生成进度**
```python
import time

ppt_id = ppt_id_holder['id']
while True:
    # 查询异步PPT状态
    info = docmee.async_ppt_info(ppt_id)
    
    # info 结构示例:
    # {"total": 12, "current": 5, "status": "generating"}
    
    total = info.get('total')
    current = info.get('current')
    
    if total and current:
        progress = int((current / total) * 100)
        socketio.emit('ppt_generation_progress', {
            'progress': progress,
            'message': f'API生成：{current}/{total} 页已生成'
        })
        
        if current >= total:
            break  # 生成完成
    
    time.sleep(5)  # 每5秒轮询一次
```

**Step 5: 下载PPTX文件**
```python
# 获取下载链接
download_resp = docmee.download_pptx(ppt_id)
# download_resp 结构示例:
# {"fileUrl": "https://api.bltcy.cn/download/xxx.pptx"}

download_url = download_resp.get('fileUrl')

# 下载文件
import requests
headers = {'Authorization': f'Bearer {docmee.api_key}'}
r = requests.get(download_url, headers=headers)
r.raise_for_status()

# 保存文件
with open(file_path, 'wb') as f:
    f.write(r.content)
```

**Step 6: 更新数据库并发送事件**
```python
# 更新PPT记录
ppt.file_path = file_path
ppt.status = 'ready'  # 标记为完成
db.session.commit()

# 发送完成事件
socketio.emit('ppt_generated', {'ppt': ppt.to_dict()}, room=conversation_id)
socketio.emit('ppt_generation_progress', {'progress': 100, 'message': 'API生成：PPT生成完成'})
```

#### 文多多API调用流程图
```
┌─────────────────────────────────────────────────────────────────┐
│                    文多多API生成流程                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. generate_content_stream()                                     │
│    - 发送大纲Markdown                                             │
│    - 启用 asyncGenPptx=true                                      │
│    - SSE流式返回内容                                              │
│    - 捕获 pptId                                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. async_ppt_info(pptId) [轮询]                                  │
│    - 每5秒查询一次                                                │
│    - 返回 {total, current, status}                               │
│    - 发送进度到前端                                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ (current >= total)
┌─────────────────────────────────────────────────────────────────┐
│ 3. download_pptx(pptId)                                          │
│    - 获取下载链接 fileUrl                                         │
│    - 下载PPTX二进制文件                                           │
│    - 保存到本地                                                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. 完成                                                           │
│    - 更新PPT状态为ready                                           │
│    - 发送ppt_generated事件                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

### 两种方案对比

| 特性 | 本地模板生成 | 文多多API生成 |
|------|-------------|--------------|
| **生成引擎** | 本地python-pptx | 文多多云端API |
| **模板支持** | 支持自定义模板 | 使用文多多模板 |
| **生成速度** | 较快（本地处理） | 较慢（API调用+轮询） |
| **可控性** | 高（完全本地） | 低（依赖API） |
| **样式质量** | 取决于模板 | 文多多专业样式 |
| **依赖** | 无外部依赖 | 需要文多多API密钥 |
| **适用场景** | 需要自定义模板 | 快速生成专业PPT |

---

## 五、关键调用关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端 (Vue.js)                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ WebSocket
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   websocket/chat.py                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │ send_message   │  │generate_outline│  │  generate_ppt  │    │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘    │
└──────────┼───────────────────┼───────────────────┼─────────────┘
           │                   │                   │
           ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Services 层                               │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  glm_service    │  │docmee_service   │  │structured_ppt   │ │
│  │                 │  │                 │  │  _generator     │ │
│  │ • chat()        │  │ • generate_     │  │                 │ │
│  │ • generate_     │  │   outline_      │  │ • generate_ppt()│ │
│  │   ppt_outline() │  │   stream()      │  │ • validate_     │ │
│  │ • adapt_        │  │ • generate_     │  │   ppt_quality() │ │
│  │   content_to_   │  │   content_      │  │ • _apply_       │ │
│  │   template()    │  │   stream()      │  │   placeholders()│ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │           │
│           ▼                    │                    ▼           │
│  ┌─────────────────┐           │           ┌─────────────────┐ │
│  │  rag_service    │           │           │  image_service  │ │
│  │                 │           │           │                 │ │
│  │ • search_       │           │           │ • search_images │ │
│  │   documents()   │           │           │                 │ │
│  │ • add_          │           │           └─────────────────┘ │
│  │   documents()   │           │                               │
│  └────────┬────────┘           │                               │
└───────────┼────────────────────┼───────────────────────────────┘
            │                    │
            ▼                    ▼
┌───────────────────┐  ┌───────────────────┐
│  Chroma 向量库    │  │  文多多 API       │
│  (本地存储)       │  │  (api.bltcy.cn)   │
└───────────────────┘  └───────────────────┘
```

---

## 六、数据模型

### 核心模型

| 模型 | 文件 | 作用 |
|------|------|------|
| `User` | models/user.py | 用户信息（昵称、学校、课程、授课风格等） |
| `Conversation` | models/conversation.py | 对话（标题、状态、需求、上下文） |
| `Message` | models/conversation.py | 消息（角色、内容、元数据） |
| `Document` | models/document.py | 上传的文档（文件路径、向量ID） |
| `PPT` | models/ppt.py | 生成的PPT（大纲、幻灯片数据、文件路径） |
| `Template` | models/template.py | PPT模板（文件路径、模板信息） |

---

## 七、配置项 (.env)

| 配置项 | 作用 |
|--------|------|
| `GLM_API_KEY` | 智谱AI API密钥 |
| `DOCMEE_BASE_URL` | 文多多API基础URL |
| `DOCMEE_API_KEY` | 文多多API密钥 |
| `DOCMEE_PPT_MODEL_ID` | PPT生成模型ID |
| `DOCMEE_TIMEOUT_SECONDS` | API超时时间 |
| `DOCMEE_POLL_INTERVAL_SECONDS` | 轮询间隔 |
| `VECTOR_DB_DIR` | 向量数据库目录 |
| `GENERATED_PPTS_DIR` | 生成的PPT存储目录 |