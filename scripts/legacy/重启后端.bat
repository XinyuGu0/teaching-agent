@echo off
echo Historical launcher. Run python backend/run.py from the project root.
exit /b 1
@echo off
chcp 65001 >nul
echo 🔧 清除Python缓存...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
echo ✓ 缓存已清除
echo.
echo 🚀 启动后端服务...
cd backend
python run.py
pause