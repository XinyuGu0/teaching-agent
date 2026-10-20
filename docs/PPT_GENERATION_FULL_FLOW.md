# PPT 生成全流程说明（前后端完整链路）

> 适用仓库：`guowaibao1.1`  
> 核心目标：说明“从聊天内容到可下载/可在线编辑 PPT”的完整实现流程、关键事件、数据结构与异常处理。  
> 更新时间：自动生成（基于当前代码）

---

## 1. 总览：两条生成链路并存

当前项目里，PPT 生成实际是**混合架构**：

1. **大纲生成链路 A（WebSocket）**
   - 入口：`socket.emit('generate_outline')`
   - 后端：`backend/app/websocket/chat.py -> handle_generate_outline`
   - 调用：`glm_service.generate_ppt_outline(...)`
   - 输出：`outline_generated` 事件 + 落库消息（`Message.meta_data.outline/mindmap`）

2. **大纲生成链路 B（SSE）**
   - 入口：`POST /api/conversations/<id>/generate-outline`
   - 后端：`backend/app/api/conversation.py -> generate_outline_from_dialogue`
   - 调用：`glm_service.chat(..., stream=True)` 自行拼 JSON
   - 输出：SSE 分阶段事件（`preparing -> ... -> done/error`）

3. **PPT生成链路（WebSocket）**
   - 入口：`socket.emit('generate_ppt')`
   - 后端：`backend/app/websocket/chat.py -> handle_generate_ppt`
   - 调用：`officecli_mcp_service.generate_ppt_from_outline(...)`
   - 输出：`ppt_generation_progress` + `ppt_generated`，并写 `PPT` 表

> 现状：前端 `ChatView.vue` 的“模板生成PPT”流程默认走 **SSE 先产大纲**，再走 **WebSocket 产PPT**。

---

## 2. 前端入口与状态流

### 2.1 关键文件

- 视图：`frontend/src/views/ChatView.vue`
- WebSocket 封装：`frontend/src/services/websocket.js`
- 状态管理：`frontend/src/store/modules/conversation.js`

### 2.2 主要用户动作

1. 用户在聊天页点击“生成PPT”
2. `handleGeneratePPTFromOutline(outline)` 打开模板选择框
3. 用户确认模板后，`confirmGenerateWithTemplate()` 执行：
   - 用 SSE 调 `/api/conversations/{id}/generate-outline` 生成大纲（带实时进度）
   - 完成后调用 `generatePPTWithTemplate(outline, templateId)`
   - 后者通过 `websocketService.generatePPT(...)` 触发后端 WebSocket 生成

### 2.3 前端状态机（Pinia）

`conversation.js` 中维护：

- 大纲状态：
  - `startOutlineGeneration()`
  - `updateOutlineProgress(progress, message)`
  - `finishOutlineGeneration()`
  - `failOutlineGeneration(message)`

- PPT 状态：
  - `startPPTGeneration()`
  - `updatePPTProgress(progress, message, slideNumber, slideData)`
  - `finishPPTGeneration()`
  - `failPPTGeneration(message)`

并记录：

- `pptProgressLogs`（进度日志）
- `generatingSlides`（实时页数据）

### 2.4 WebSocket 事件订阅

`websocket.js` 统一监听：

- 大纲：`outline_generation_start` / `outline_generation_progress` / `outline_generated`
- PPT：`ppt_generation_start` / `ppt_generation_progress` / `ppt_generated` / `ppt_generation_failed`
- 聊天流式：`streaming_start` / `message_chunk` / `thinking_chunk` / `message_received`

---

## 3. 后端 WebSocket：聊天与大纲生成

核心文件：`backend/app/websocket/chat.py`

### 3.1 `send_message` 的自动触发逻辑

用户发消息后，后端会根据关键词/确认语义判断是否应自动生成大纲。若满足条件：

1. emit `outline_generation_start`
2. 分阶段推送 `outline_generation_progress`（如 30/45/75/100）
3. 调用 `glm_service.generate_ppt_outline(...)`
4. 结果写入 `Message.meta_data`：
   - `meta_data.outline`
   - `meta_data.mindmap`
   - `meta_data.type = 'outline'`
5. 广播 `outline_generated`

### 3.2 `@socketio.on('generate_outline')`

手动大纲生成接口，流程和上面类似：

- 校验 `conversation_id/user_id/topic`
- 推送进度
- 读取会话历史
- 调 `glm_service.generate_ppt_outline(...)`
- 落库消息 + 推送 `outline_generated`

> 说明：这里与 SSE 大纲接口存在功能重叠（双实现）。

---

## 4. 后端 SSE：按模板先流式生成大纲

核心文件：`backend/app/api/conversation.py`

接口：`POST /api/conversations/<conversation_id>/generate-outline`

### 4.1 请求参数

- `dialogue`: 对话全文（前端拼接）
- `template_id`: 模板ID（必填）

### 4.2 执行阶段（SSE）

按 `data: {...}` 连续返回：

1. `preparing`（准备）
2. `building_prompt`（构造提示词）
3. `calling_llm`（调用模型）
4. `receiving`（流式接收模型输出）
5. `parsing`（解析JSON）
6. `done`（返回 `outline`）或 `error`

### 4.3 模板约束注入

若 `template_id` 是内置模板（`builtin_` 前缀），会读取模板信息（如页数、布局模式）并注入提示词，约束大纲结构。

---

## 5. 大纲生成服务（GLM）

核心文件：`backend/app/services/glm_service.py`

函数：`generate_ppt_outline(topic, requirements, context_documents, explicit_outline_text, conversation_history)`

### 5.1 输入压缩与提示词构造

- `slide_count` 会被限制在 `[6, 20]`
- 上下文文档压缩（最多取前几条，每条截断）
- 对话历史压缩（保留近几轮）
- 将模板信息、用户显式大纲、上下文摘要拼入 prompt

### 5.2 输出协议（强约束 JSON）

要求模型只输出：

- `title`
- `outline.slides[]`
  - `slide_number`
  - `title`
  - `position`
  - `target_template_slide_type`
  - `target_placeholders`
  - `content_points`
- `mindmap`

### 5.3 解析与兜底

- 兼容 markdown code block 包裹 JSON
- 兼容返回 `slides` 顶层数组的异常格式
- 自动补字段
- 页数不一致时裁剪/补齐
- 彻底失败时回退到 `_build_fallback_outline()`

---

## 6. PPT 生成服务（OfficeCLI MCP）

核心文件：`backend/app/services/officecli_mcp_service.py`

统一入口：`generate_ppt_from_outline(...)`

### 6.1 三种生成模式

1. **内置模板** `template_type='builtin'`
   - 调 `build_sh_generator.generate_with_llm(...)`
   - 适合平台预置模板脚本化生成

2. **用户上传模板** `template_type='uploaded'`
   - 走 `_generate_ppt_from_template(...)`
   - 先提取模板占位符，再填充内容

3. **空白生成** `template_type='blank'`
   - 走 `_generate_ppt_with_llm(...)`
   - 从零构建幻灯片

### 6.2 上传模板生成子流程

`_generate_ppt_from_template(...)` 典型步骤：

1. 发送进度（分析模板）
2. 提取模板占位符
3. 比较模板页数与大纲页数，必要时克隆页面
4. 调用 GLM 的模板适配内容能力（按占位符产出）
5. merge/写入
6. 验证并修复

### 6.3 进度回调机制

`generate_ppt_from_outline` 接收 `progress_callback`，由 WebSocket 层转发为 `ppt_generation_progress`，实现前端实时进度条与日志。

---

## 7. WebSocket `generate_ppt` 端到端流程

位置：`backend/app/websocket/chat.py -> handle_generate_ppt`

1. 参数校验：`conversation_id/user_id` 必填
2. emit `ppt_generation_start`
3. 若未带 outline：后端可先自动生成 outline
4. 取 topic、检索上下文、收集对话历史
5. 解析模板来源：
   - `builtin_` 前缀 => 内置模板
   - 其他ID => 查询 `Template` 表，校验文件存在
6. 调用 `officecli_service.generate_ppt_from_outline(...)`
7. 生成成功后：
   - 写入 `PPT` 记录（含 `file_path`, `outline`, `template_id`, `status=ready`）
   - emit `ppt_generated`
8. 失败：emit `ppt_generation_failed` 或 error

---

## 8. PPT 文件访问与在线编辑链路

核心文件：`backend/app/api/ppt.py`

### 8.1 下载

- `GET /api/ppts/<ppt_id>/download`
- 若无文件，`_ensure_ppt_file(ppt)` 会尝试由 `slides_data` 回填生成 `.pptx`

### 8.2 OnlyOffice / WOPI

- `GET /api/ppts/<ppt_id>/wopi`
  - 生成 file_url / callback_url / doc_key / token
  - 返回给前端编辑器配置
- 还包含 file、callback 等配套接口（同文件内）

---

## 9. 关键数据对象

### 9.1 Message.meta_data（大纲消息）

```json
{
  "type": "outline",
  "outline": { "title": "...", "slides": [...] },
  "mindmap": "# ..."
}
```

### 9.2 WebSocket PPT 进度事件

```json
{
  "progress": 65,
  "message": "正在填充第3页...",
  "slide_number": 3,
  "slide_data": {"objects": [...]}
}
```

### 9.3 PPT 记录（数据库）

典型字段：

- `id`
- `conversation_id`
- `user_id`
- `title`
- `outline`
- `slides_data`
- `template_id`
- `file_path`
- `status`

---

## 10. 当前实现的注意事项（重要）

1. **大纲双通道并存（WS + SSE）**
   - 维护成本高，行为可能不一致。

2. **前端存在 window 全局临时变量**
   - `window.currentDialogue/window.currentOutline` 可被覆盖，不利于并发会话安全。

3. **PPT 生成链路较长**
   - 涉及模板、RAG、LLM、OfficeCLI，建议统一 request_id 贯穿日志。

4. **失败回退策略已具备但分散**
   - GLM 大纲回退、文件回填生成等能力已存在，建议文档化状态码与错误码。

---

## 11. 推荐后续优化（可选）

1. 统一大纲生成入口（建议仅保留一种：WS 或 SSE）。
2. 把 ChatView 中“模板选择 / SSE 大纲 / WS 生成”拆分为 composable/service，降低组件复杂度。
3. 用 store 替代 `window.*` 临时变量。
4. 抽象统一进度协议，约定所有阶段字段（stage/progress/message/detail/request_id）。

---

## 12. 代码定位索引

- 前端
  - `frontend/src/views/ChatView.vue`
  - `frontend/src/services/websocket.js`
  - `frontend/src/store/modules/conversation.js`

- 后端
  - `backend/app/websocket/chat.py`
  - `backend/app/api/conversation.py`
  - `backend/app/api/ppt.py`
  - `backend/app/services/glm_service.py`
  - `backend/app/services/officecli_mcp_service.py`
