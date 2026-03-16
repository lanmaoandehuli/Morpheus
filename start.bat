@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   🚀 Morpheus 小说创作系统启动器
echo ========================================
echo.

cd /d "%~dp0"

echo 📦 检查后端配置...
if not exist "backend\.env" (
    echo ❌ 错误：backend\.env 不存在
    echo    请先复制 .env.example 到 .env 并配置 API Key
    pause
    exit /b 1
)

echo ✅ 后端配置检查通过
echo.

echo 📦 启动后端服务...
start "Morpheus Backend" powershell -Command "cd backend; python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --workers 2 --reload"
echo    后端地址：http://127.0.0.1:8000
echo    API 文档：http://127.0.0.1:8000/docs
echo.

echo ⏳ 等待后端启动...
timeout /t 5 /nobreak >nul

echo.
echo 🎨 启动前端服务...
start "Morpheus Frontend" powershell -Command "cd frontend; npm run dev"
echo    前端地址：http://localhost:3000
echo.

echo ========================================
echo   ✅ Morpheus 启动完成！
echo ========================================
echo.
echo 📱 访问地址：http://localhost:3000
echo 🔧 后端健康：http://127.0.0.1:8000/api/health
echo 📚 API 文档：http://127.0.0.1:8000/docs
echo.
echo 按任意键退出此窗口...
pause >nul
