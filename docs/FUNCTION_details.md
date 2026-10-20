# 后端核心函数详细文档

本文档详细介绍了后端核心函数的技术流程和功能概述。

---

## 一、glm_service.py - GLM AI服务

### 1. chat()

**功能概述**：与智谱AI GLM模型进行对话交互的核心函数。

**参数说明**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| messages | List[Dict] | 必填 | 消息列表，每条包含role和content |
| model | str | "glm-4.7" | 模型名称 |
| temperature | float | 0.7 | 采样温度(0-1)，越高越随机 |
| max_tokens | int | 4096 | 最大生成token数 |
| stream | bool | False | 是否流式返回 |
| tools | List[Dict] | None | 工具定义列表 |
| enable_web_search | bool | False | 是否启用联网搜索 |
| enable_thinking | bool | True | 是否启用原生思考模式 |
| retry_count | int | 0 | 重试次数 |
| retry_delay | float | 1.0 | 重试延迟(秒) |

**技术流程**：
```
1. 初始化GLM客户端（单例模式）
2. 构建请求参数（model, messages, temperature等）
3. 如果enable_web_search=True，添加web_search工具
4. 如果enable_thinking=True，通过extra_body启用GLM-4.7原生思考
5. 调用client.chat.completions.create()
6. 如果stream=True，返回生成器；否则返回解析后的字典
7. 失败时按指数退避重试
```

**返回值**：
```python
# 非流式返回
{
    'content': 'AI回复内容',
    'role': 'assistant',
    'finish_reason': 'stop',
    'tool_calls': None,
    'usage': {
        'prompt_tokens': 100,
        'completion_tokens': 200,
        'total_tokens': 300
    }
}

# 流式返回：生成器对象
```

---

### 2. chat_with_context()

**功能概述**：带RAG上下文和可选联网搜索的对话函数。

**参数说明**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| user_message | str | 必填 | 用户消息 |
| conversation_history | List[Dict] | 必填 | 对话历史 |
| context_documents | List[str] | None | RAG检索到的文档 |
| system_prompt | str | None | 系统提示词 |
| enable_web_search | bool | True | 是否启用联网搜索 |
| stream | bool | False | 是否流式返回 |
| enable_thinking | bool | True | 是否启用思考模式 |

**技术流程**：
```
1. 构建消息列表
   ├── 添加系统提示词（默认为PPT/教案助手）
   ├── 添加对话历史
   ├── 如果有context_documents，添加参考资料
   └── 添加当前用户消息

2. 如果enable_web_search=True，构建web_search工具

3. 调用chat()函数，传入所有参数

4. 返回结果（流式或非流式）
```

**使用场景**：
- 用户对话时需要结合上传文档回答
- 需要联网获取最新信息
- 需要保持对话上下文连贯

---

### 3. analyze_image()

**功能概述**：使用GLM-4V视觉模型分析图片。

**参数说明**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| image_url | str | 必填 | 图片URL（支持data URL和HTTP URL） |
| prompt | str | 必填 | 分析提示词/问题 |
| model | str | "glm-4v" | 视觉模型名称 |

**技术流程**：
```
1. 获取GLM客户端
2. 构建多模态消息：
   messages = [{
       "role": "user",
       "content": [
           {"type": "image_url", "image_url": {"url": image_url}},
           {"type": "text", "text": prompt}
       ]
   }]
3. 调用GLM-4V模型
4. 返回分析结果文本
```

**使用场景**：
- 分析PPT页面截图问题
- 识别图片中的文字或图表
- 视觉审查PPT排版

---

## 二、docmee_service.py - 文多多API服务

### 4. generate_content_stream()

**功能概述**：调用文多多API流式生成PPT内容并触发异步PPT生成。

**参数说明**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| outline_markdown | str | 必填 | Markdown格式的大纲 |
| async_gen_pptx | bool | True | 是否启用异步PPT生成 |
| model_id | str | None | PPT生成模型ID |

**技术流程**：
```
1. 构建请求payload：
   {
       'outlineMarkdown': outline_markdown,
       'asyncGenPptx': True,
       'modelId': model_id (可选)
   }

2. 调用_stream_sse()发送POST请求到：
   /docmee/v1/api/ppt/generateContent

3. SSE流处理：
   ├── 逐行读取响应
   ├── 解析data:后的JSON
   ├── 提取文本内容（outlineMarkdown/contentMarkdown等字段）
   ├── 提取pptId（用于后续轮询和下载）
   └── yield {raw, text, ppt_id}

4. 返回生成器，每次yield一个chunk
```

**返回的chunk结构**：
```python
{
    'raw': {...},           # 原始JSON响应对象
    'text': '生成的内容...', # 提取的文本
    'ppt_id': 'xxx'         # PPT ID（用于轮询进度）
}
```

**使用场景**：
- 文多多方案生成PPT时
- 需要流式展示生成进度
- 触发异步PPT生成任务

---

## 三、structured_ppt_generator.py - 结构化PPT生成器

### 5. generate_ppt()

**功能概述**：结构化生成PPT的主函数，采用分步骤、模板化的方式。

**参数说明**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| topic | str | 必填 | PPT主题 |
| outline | Dict | 必填 | 大纲结构 |
| requirements | Dict | 必填 | 需求信息 |
| context_documents | List[str] | None | RAG检索的参考文档 |
| conversation_history | List[str] | None | 对话历史中的AI内容 |
| template_id | str | None | 模板ID |

**技术流程**：
```
┌─────────────────────────────────────────────────────────────┐
│                    generate_ppt 主流程                        │
└─────────────────────────────────────────────────────────────┘

1. 初始化 [5%]
   ├── 获取颜色方案
   ├── 提取目录标题
   └── 加载模板（如果有template_id）

2. 生成标题页 [10-12%]
   ├── 有模板：_copy_template_slide(template_path, 0)
   └── 无模板：templates.get_title_slide(topic, subtitle)

3. 生成目录页 [14-15%]
   ├── 有模板：_analyze_slide_layout_with_vision() + _copy_template_slide()
   └── 无模板：templates.get_full_content_slide()

4. 逐页生成内容 [18-90%]
   ┌── for each slide in outline_slides:
   │   ├── _generate_detailed_content() 扩展要点 [每页+2%]
   │   ├── 选择布局（根据页数和位置）
   │   │   ├── 最后一页：双栏布局
   │   │   ├── 每3页：全内容页
   │   │   └── 其他：左文本右图片
   │   └── 有模板：视觉分析+复制模板页
   └──

5. 应用模板占位符 [96%]
   └── _apply_template_placeholders()

6. 质量验证 [98-100%]
   └── validate_ppt_quality()

7. 返回ppt_data
```

**返回值**：
```python
{
    "title": "PPT标题",
    "theme": "商务",
    "slides": [
        {
            "slide_number": 1,
            "background": {"type": "solid", "color": "FFFFFF"},
            "objects": [
                {"type": "text", "text": "...", "x": 1, "y": 1, ...},
                {"type": "image", "path": "...", ...}
            ]
        }
    ]
}
```

---

### 6. _generate_detailed_content()

**功能概述**：为单页幻灯片生成详细内容，将简要大纲扩展为详细要点。

**参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| slide_title | str | 幻灯片标题 |
| outline_points | List[str] | 大纲要点列表 |
| topic | str | PPT主题 |
| context_documents | List[str] | 参考文档 |
| conversation_history | List[str] | 对话历史 |

**技术流程**：
```
1. 构建提示词：
   - 包含PPT主题、幻灯片标题、大纲要点
   - 添加对话历史（最近3条AI回复）
   - 添加参考资料（前2个文档）

2. 调用GLM生成详细内容：
   - temperature=0.4（较稳定）
   - max_tokens=1000
   - 要求返回JSON数组

3. 解析JSON响应：
   - 提取```json代码块
   - 验证每个要点长度>=15字
   - 过短的要点标记"需要扩展"

4. 返回详细要点列表
```

**使用场景**：
- 在generate_ppt()中为每页生成内容
- 将简短大纲扩展为详细内容

---

### 7. _search_quality_image()

**功能概述**：搜索与幻灯片标题相关的高质量图片。

**参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| slide_title | str | 幻灯片标题（作为搜索关键词） |

**技术流程**：
```
1. 调用image_service.search_images(slide_title, num_images=1)
2. 如果找到图片，返回第一个URL
3. 如果没找到，返回占位图
4. 异常时返回None
```

---

### 8. validate_ppt_quality()

**功能概述**：验证生成的PPT质量，检查页数和内容完整性。

**参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| ppt_data | Dict | PPT数据 |
| expected_slide_count | int | 期望的页数 |

**技术流程**：
```
1. 检查页数：
   actual_count = len(ppt_data['slides'])
   if actual_count != expected_slide_count:
       issues.append("页数不符")

2. 检查每页内容：
   for each slide:
   ├── 检查是否有文本对象
   └── 检查元素是否超出边界（x+w>10 或 y+h>7.5）

3. 返回验证结果：
   {
       "valid": True/False,
       "issues": ["问题1", "问题2"],
       "slide_count": actual_count
   }
```

---

### 9. _generate_slide_from_template()

**功能概述**：从模板PPT生成幻灯片，复制布局并替换文字。

**参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| template_path | str | 模板PPT文件路径 |
| slide_index | int | 模板中的幻灯片索引 |
| title | str | 标题文本 |
| content | List[str] | 内容文本列表 |
| is_title | bool | 是否为标题页 |

**技术流程**：
```
1. 加载模板PPT：Presentation(template_path)

2. 获取模板幻灯片：prs.slides[slide_index]

3. 分析模板幻灯片：
   ├── 提取所有文本框的位置、字体、颜色
   └── 提取背景信息

4. 替换文本内容：
   ├── 标题页：第一个文本框放标题，第二个放副标题
   └── 内容页：第一个放标题，其余放内容

5. 返回幻灯片数据字典
```

---

### 10. _analyze_slide_layout_with_vision()

**功能概述**：使用视觉模型分析模板，决定当前内容应该使用哪个模板页面。

**参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| template_path | str | 模板PPT文件路径 |
| slide_title | str | 幻灯片标题 |
| content | List[str] | 内容文本列表 |
| is_title | bool | 是否为标题页 |

**技术流程**：
```
1. 如果是标题页，直接返回使用第1页

2. 调用视觉服务分析模板：
   vision_result = vision_service.analyze_ppt_layout(template_path, max_pages=3)

3. 分析当前幻灯片的内容特征：
   content_features = {
       'text_count': len(content),
       'has_title': bool(slide_title),
       'is_short': len(content) <= 2,
       'is_long': len(content) > 4
   }

4. 匹配模板页面：
   for each page in vision_result['pages']:
   ├── content_with_image：适合内容较少的页面
   ├── two_column：适合内容较多的页面
   └── single_column：通用布局

5. 计算置信度，选择最佳匹配

6. 返回布局信息：
   {
       'template_slide_index': 1,
       'layout_type': 'content',
       'confidence': 0.8
   }
```

---

### 11. _extract_placeholders_by_slide()

**功能概述**：从幻灯片列表中提取所有占位符。

**参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| slides | List[Dict] | 幻灯片列表 |

**技术流程**：
```
1. 遍历所有幻灯片
2. 对每个幻灯片，遍历所有objects
3. 如果是文本类型，用正则提取 {{xxx}} 格式的占位符
4. 返回结果：
   [
       {'slide_index': 0, 'placeholders': ['{{title}}', '{{subtitle}}']},
       {'slide_index': 1, 'placeholders': ['{{toc_1}}', '{{toc_2}}']}
   ]
```

---

### 12. _apply_template_placeholders()

**功能概述**：根据占位符替换模板中的文本和图片。

**参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| slides | List[Dict] | 幻灯片列表 |
| slide_contents | List[Dict] | 幻灯片内容 |
| topic | str | PPT主题 |
| outline | Dict | 大纲结构 |
| requirements | Dict | 需求信息 |
| conversation_history | List[str] | 对话历史 |

**技术流程**：
```
1. 提取所有占位符：_extract_placeholders_by_slide(slides)

2. 调用LLM适配内容：
   adapted = glm_service.adapt_content_to_template_placeholders(
       topic, outline, requirements, conversation_history, placeholders_by_slide
   )

3. 遍历每个幻灯片的文本对象：
   for each text object:
   ├── 查找 {{xxx}} 占位符
   ├── 优先使用LLM生成的值
   ├── 否则使用默认规则：
   │   ├── {{title}} → 标题（限28字）
   │   ├── {{subtitle}} → 副标题（限36字）
   │   ├── {{text}} → 内容（限180字）
   │   ├── {{date}} → 当前日期
   │   ├── {{page_number}} → 页码
   │   └── {{toc_N}} → 目录项
   └── 替换文本

4. 处理图片占位符：
   if image.name == '{{image}}':
       image_url = _search_quality_image(title)
       更新图片路径
```

---

## 四、websocket/chat.py - WebSocket事件处理

### 13. handle_update_slide()

**功能概述**：更新单页幻灯片内容。

**参数说明**（前端发送的data）：
| 参数 | 类型 | 说明 |
|------|------|------|
| ppt_id | str | PPT ID |
| slide_number | int | 幻灯片编号（0-indexed） |
| updates | Dict | 更新内容 |

**技术流程**：
```
1. 参数验证：检查ppt_id、slide_number、updates是否齐全

2. 查询PPT记录：
   ppt = PPT.query.get(ppt_id)
   if not ppt: return error

3. 更新幻灯片：
   slides = ppt.slides_data
   slides[slide_number].update(updates)
   ppt.slides_data = slides
   db.session.commit()

4. 发送更新事件：
   emit('slide_updated', {
       'ppt_id': ppt_id,
       'slide_number': slide_number,
       'slide': slides[slide_number]
   })
```

**前端调用示例**：
```javascript
socket.emit('update_slide', {
  ppt_id: 'xxx',
  slide_number: 2,
  updates: {
    title: '新标题',
    content_points: ['新要点1', '新要点2']
  }
})
```

---

### 14. handle_ai_modify_slide()

**功能概述**：使用AI根据用户指令修改单页幻灯片。

**参数说明**（前端发送的data）：
| 参数 | 类型 | 说明 |
|------|------|------|
| ppt_id | str | PPT ID |
| slide_number | int | 幻灯片编号（0-indexed） |
| instruction | str | 用户修改指令 |

**技术流程**：
```
1. 参数验证：检查ppt_id、slide_number、instruction是否齐全

2. 查询PPT记录：
   ppt = PPT.query.get(ppt_id)
   if not ppt: return error

3. 获取当前幻灯片数据：
   slides = ppt.slides_data
   current_slide = slides[slide_number]

4. 调用AI修改：
   modified_slide = ppt_generator.modify_slide_with_ai(
       slide_data=current_slide,
       instruction=instruction,
       context=f"PPT主题：{ppt.title}"
   )

5. 更新数据库：
   slides[slide_number] = modified_slide
   ppt.slides_data = slides
   db.session.commit()

6. 发送更新事件：
   emit('slide_updated', {
       'ppt_id': ppt_id,
       'slide_number': slide_number,
       'slide': modified_slide
   })
```

**前端调用示例**：
```javascript
socket.emit('ai_modify_slide', {
  ppt_id: 'xxx',
  slide_number: 3,
  instruction: '把这一页的标题改得更吸引人，内容增加一个案例'
})
```

**AI修改流程**：
```
ppt_generator.modify_slide_with_ai() 内部：
1. 构建提示词，包含当前幻灯片数据和用户指令
2. 调用GLM生成修改后的内容
3. 解析返回的JSON
4. 返回修改后的幻灯片数据
```

---

## 五、函数调用关系图

```
┌─────────────────────────────────────────────────────────────────┐
│                      前端 WebSocket 调用                         │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ update_slide  │     │ ai_modify_slide │     │  generate_ppt   │
│   (直接更新)   │     │   (AI修改)      │     │  (完整生成)     │
└───────────────┘     └────────┬────────┘     └────────┬────────┘
                               │                       │
                               ▼                       ▼
                      ┌─────────────────┐     ┌─────────────────┐
                      │ ppt_generator.  │     │ StructuredPPT   │
                      │ modify_slide_   │     │ Generator.      │
                      │ with_ai()       │     │ generate_ppt()  │
                      └────────┬────────┘     └────────┬────────┘
                               │                       │
                               ▼                       ├──────────────┐
                      ┌─────────────────┐             │              │
                      │ glm_service.    │             ▼              ▼
                      │ chat()          │     ┌─────────────┐ ┌─────────────┐
                      └─────────────────┘     │ _generate_  │ │ _apply_     │
                                              │ detailed_   │ │ template_   │
                                              │ content()   │ │ placeholders│
                                              └─────────────┘ └─────────────┘
                                                      │              │
                                                      ▼              ▼
                                              ┌─────────────────────────┐
                                              │    glm_service.chat()   │
                                              │    (GLM API调用)        │
                                              └─────────────────────────┘
```

---

## 六、总结

| 函数名 | 所在文件 | 核心功能 | 关键技术 |
|--------|----------|----------|----------|
| chat | glm_service.py | GLM对话 | 流式响应、重试机制、思考模式 |
| chat_with_context | glm_service.py | 带上下文对话 | RAG检索、联网搜索 |
| analyze_image | glm_service.py | 图像分析 | GLM-4V多模态 |
| generate_content_stream | docmee_service.py | 文多多内容生成 | SSE流式处理 |
| generate_ppt | structured_ppt_generator.py | 结构化PPT生成 | 模板化、分步骤 |
| _generate_detailed_content | structured_ppt_generator.py | 扩展内容要点 | LLM内容扩展 |
| _search_quality_image | structured_ppt_generator.py | 搜索配图 | 图片服务API |
| validate_ppt_quality | structured_ppt_generator.py | 质量验证 | 页数/边界检查 |
| _generate_slide_from_template | structured_ppt_generator.py | 模板生成幻灯片 | python-pptx |
| _analyze_slide_layout_with_vision | structured_ppt_generator.py | 视觉分析布局 | 视觉模型 |
| _extract_placeholders_by_slide | structured_ppt_generator.py | 提取占位符 | 正则匹配 |
| _apply_template_placeholders | structured_ppt_generator.py | 应用占位符 | LLM适配+替换 |
| update_slide | chat.py | 更新幻灯片 | WebSocket事件 |
| ai_modify_slide | chat.py | AI修改幻灯片 | LLM修改+WebSocket |