# AI-PPT-Platform 部署技术栈文档

## 一、技术栈总览

### 前端 (Frontend)
| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue 3** | 3.x | 前端框架（Composition API） |
| **Vite** | 5.x | 构建工具 |
| **Pinia** | 2.x | 状态管理 |
| **Vue Router** | 4.x | 路由管理 |
| **Tailwind CSS** | 3.x | UI 样式框架 |
| **Axios** | 1.x | HTTP 请求 |
| **WebSocket** | 原生 | 实时通信 |
| **Nginx** | latest | 反向代理 + 静态资源托管 |

### 后端 (Backend)
| 技术 | 版本 | 用途 |
|------|------|------|
| **FastAPI** | 0.115 | Web 框架 |
| **Uvicorn** | 0.30 | ASGI 服务器 |
| **SQLAlchemy** | 2.0 | ORM（async 模式） |
| **Pydantic** | 2.x | 数据校验 + 配置管理 |
| **JWT (PyJWT)** | 2.x | 用户认证 |
| **WebSocket** | FastAPI 内置 | 实时双向通信 |

### AI / 智能体 (AI Agent)
| 技术 | 版本 | 用途 |
|------|------|------|
| **LangChain** | 0.3 | LLM 编排框架 |
| **LangGraph** | 0.2 | 多步工作流状态机 |
| **ChatOpenAI** | LangChain 内置 | OpenAI 兼容接口客户端 |
| **通义千问 (Qwen)** | qwen3.5-plus | 主对话 LLM |
| **ChromaDB** | 0.5 | 向量数据库（RAG） |

### 数据层 (Data)
| 技术 | 版本 | 用途 |
|------|------|------|
| **PostgreSQL** | 16 | 关系型主数据库 |
| **Redis** | 7 | 缓存 + Celery Broker |
| **ChromaDB** | 0.5 | 向量数据库（嵌入存储） |

### 异步任务 (Task Queue)
| 技术 | 版本 | 用途 |
|------|------|------|
| **Celery** | 5.4 | 异步任务队列 |
| **Redis** | 7 | Broker + Result Backend |

### 文档服务 (Document)
| 技术 | 版本 | 用途 |
|------|------|------|
| **OnlyOffice** | 8.2 | 在线文档编辑器 |
| **python-pptx** | 1.0 | PPT 文件生成 |
| **python-docx** | 1.1 | Word 文件解析 |

### 部署 (Deployment)
| 技术 | 用途 |
|------|------|
| **Docker** | 容器化 |
| **Docker Compose** | 多容器编排 |
| **Nginx** | 反向代理 + 负载均衡 |

### 外部 API 服务
| 服务 | 用途 |
|------|------|
| **通义千问 API** | 主 LLM 对话 + 大纲生成 |
| **豆包 API** | AI 图片/视频生成 |
| **Docmee API** | 文档解析服务 |

---

## 二、部署架构图（文字版）

```
                        ┌──────────────────────┐
                        │      用户浏览器       │
                        │   (Vue3 + WebSocket)  │
                        └──────────┬───────────┘
                                   │ HTTP / WS
                                   ▼
                        ┌──────────────────────┐
                        │       Nginx          │ :80
                        │  反向代理 + 静态资源   │
                        │  /api/* → backend    │
                        │  /ws/*  → backend    │
                        └──────────┬───────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              ▼              ▼
           ┌──────────────┐ ┌──────────┐ ┌──────────────┐
           │   Frontend   │ │ Backend  │ │  OnlyOffice  │
           │   (静态文件)  │ │ (FastAPI)│ │  Doc Server  │
           │   Nginx 托管  │ │  :5000   │ │    :8080     │
           └──────────────┘ └────┬─────┘ └──────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
            ┌────────────┐ ┌─────────┐ ┌────────────┐
            │ PostgreSQL │ │  Redis  │ │  ChromaDB  │
            │   :5432    │ │  :6379  │ │ (内嵌)     │
            │  关系数据   │ │ 缓存+MQ │ │ 向量检索   │
            └────────────┘ └────┬────┘ └────────────┘
                                │
                                ▼
                        ┌──────────────┐
                        │ Celery Worker│
                        │  异步任务     │
                        │ (PPT生成等)   │
                        └──────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
            ┌────────────┐ ┌─────────┐ ┌──────────┐
            │ 通义千问API │ │ 豆包API  │ │Docmee API│
            │  LLM 对话   │ │ 图片生成  │ │ 文档解析  │
            └────────────┘ └─────────┘ └──────────┘
```

---

## 三、容器清单

| 容器名 | 镜像 | 端口 | 说明 |
|--------|------|------|------|
| `ai-ppt-frontend` | 自建 (node+nginx) | 80:80 | 前端静态文件 + 反代 |
| `ai-ppt-backend` | 自建 (python) | 5000:5000 | FastAPI 后端 |
| `ai-ppt-celery` | 自建 (python) | 无 | Celery Worker |
| `ai-ppt-postgres` | postgres:16-alpine | 5432:5432 | PostgreSQL |
| `ai-ppt-redis` | redis:7-alpine | 6379:6379 | Redis |
| `ai-ppt-onlyoffice` | onlyoffice:8.2 | 8080:80 | OnlyOffice |

---

## 四、快速部署

```bash
# 1. 克隆项目
cd submission

# 2. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 .env 填入 API Key

# 3. 一键启动
docker-compose up -d

# 4. 访问
# 前端：http://localhost
# 后端 API：http://localhost:5000/docs
# OnlyOffice：http://localhost:8080
```

---

## 五、核心数据流

1. **用户对话**：浏览器 → WebSocket → FastAPI → LangGraph Agent → 通义千问 → 流式返回
2. **PPT 生成**：用户触发 → WebSocket → Celery Worker → python-pptx → 文件下载
3. **RAG 检索**：上传文档 → 解析分块 → Embedding → ChromaDB → 对话时检索增强
4. **文档协作**：OnlyOffice → 回调 API → 保存修改