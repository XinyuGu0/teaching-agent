# 开发与运行

主项目为 Flask + Vue。submission/ 和已有文档按要求保留，submission 是另一套未完成的 FastAPI 草案，不能作为主项目的已验证部署入口。

## 环境

建议 Python 3.12、Node.js 22 LTS 或兼容版本、npm。前端依赖只在 frontend 安装。Python 的 Windows COM 依赖仅在 Windows 安装。主应用直接依赖列在 requirements.txt；原先声明但主应用未导入的实验集成保留在 requirements-optional.txt，按需安装。ChromaDB 升级前须备份已有向量库，本次不打开或升级现有向量库。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements-dev.txt
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
cd frontend
npm ci
npm run build
```

配置本地 .env 后，从项目根目录分别运行 scripts/dev-backend.sh 和 scripts/dev-frontend.sh。也可直接运行 .venv/bin/python backend/run.py，以及在 frontend/ 执行 npm run dev。Windows 使用 .venv\Scripts\python.exe。后端默认只监听 127.0.0.1:5000，调试默认关闭；这些是开发启动方式。

.env、真实数据库、上传资料、生成物、node_modules、缓存均仅供本地使用，不进入 Git。backend/data、backend/instance、backend/ppt 现有资料保留；不随源码发布。首次启动按当前模型创建空表，已有数据库不会被删除。

## 数据库迁移限制

历史 migrations 存在多个起点和分支，缺少完整的建表基线。这次仅修复语法错误，不修改历史 revision，也不自动升级现有数据。空库由应用的 db.create_all() 初始化；这不等于已验证 Alembic 从空库升级。已有数据库变更须先备份、检查 schema 后另行处理，不能直接执行 flask db upgrade 或 stamp 来掩盖不一致。

## 测试

```bash
.venv/bin/python -m pytest
```

默认只执行 backend/tests/unit 和 integration。使用临时数据库、临时数据目录，不调用外部 AI。

backend/tests/manual 保存历史手动测试，部分依赖旧接口、Windows 路径、OfficeCLI、现有账号或付费服务，未宣称全部可运行。它们不参与默认测试，导入时也不执行。逐个审阅后，才可设置 RUN_MANUAL_TESTS=1 并直接执行指定脚本。模板接口脚本还需 TEST_PASSWORD。不可批量运行整个目录。

backend/scripts/legacy 是历史数据维护脚本，可能写库、移动文件、调用模型，仍保留旧环境路径；默认阻止运行。审阅并备份后才可设置 ALLOW_LEGACY_MAINTENANCE=1。scripts/legacy 的旧重启脚本已停用，防止误杀其他进程。

## 外部工具

OfficeCLI-main 的源码、资源和原有第三方声明保留；OfficeCLI 可执行程序、FFmpeg/OCR、OnlyOffice/Collabora 等按启用的功能单独安装。配置样例中的模型名称和网关沿用项目实现，不代表密钥有效或服务已验证。对话与生成测试需另行验证。

## 文件归类

根目录历史说明转入 docs/archive；docme 和已有 docs 不删。临时文件移入 .local-artifacts 并被忽略。项目根 README 和迁移模板 README 从工作目录移出，完整备份保留。submission/ 内文件包括其 README 按“原样保留”的要求未改动；第三方自身说明、许可文件也不删除。
