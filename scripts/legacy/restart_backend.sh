#!/bin/sh
echo "Historical launcher: use scripts/dev-backend.sh instead." >&2
exit 1
#!/bin/bash

echo "🔧 清除Python缓存..."
find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find backend -type f -name "*.pyc" -delete 2>/dev/null
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

echo "✓ 缓存已清除"
echo ""
echo "🚀 启动后端服务..."
cd backend && python run.py