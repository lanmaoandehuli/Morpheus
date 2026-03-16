@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   🔍 Morpheus 环境检查工具
echo ========================================
echo.

cd /d "%~dp0"

echo 📦 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未安装或未添加到 PATH
    echo    请安装 Python 3.11+: https://www.python.org/
) else (
    python --version
    echo ✅ Python 检查通过
)
echo.

echo 📦 检查 Node.js 环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js 未安装或未添加到 PATH
    echo    请安装 Node.js 18+: https://nodejs.org/
) else (
    node --version
    echo ✅ Node.js 检查通过
)
echo.

echo 📦 检查后端配置...
if exist "backend\.env" (
    echo ✅ backend\.env 存在
    echo.
    echo 配置摘要:
    findstr /C:"LLM_PROVIDER=" backend\.env
    findstr /C:"DEEPSEEK_MODEL=" backend\.env
    findstr /C:"EMBEDDING_MODEL=" backend\.env
) else (
    echo ❌ backend\.env 不存在
    echo    请运行：copy backend\.env.example backend\.env
)
echo.

echo 📦 检查依赖安装...
if exist "backend\__pycache__" (
    echo ✅ 后端依赖已安装
) else (
    echo ⚠️  后端依赖可能未安装
    echo    请运行：cd backend ^&^& pip install -r requirements.txt
)
echo.

if exist "frontend\node_modules" (
    echo ✅ 前端依赖已安装
) else (
    echo ⚠️  前端依赖可能未安装
    echo    请运行：cd frontend ^&^& npm install
)
echo.

echo 📦 检查端口占用...
netstat -ano ^| findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  端口 8000 已被占用
    echo    如已运行 Morpheus，请先关闭或忽略此警告
) else (
    echo ✅ 端口 8000 可用
)

netstat -ano ^| findstr ":3000" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  端口 3000 已被占用
    echo    如已运行 Morpheus，请先关闭或忽略此警告
) else (
    echo ✅ 端口 3000 可用
)
echo.

echo ========================================
echo   检查完成！
echo ========================================
echo.
echo 下一步:
echo 1. 配置 DeepSeek API Key (backend\.env)
echo 2. 安装依赖 (如未安装)
echo 3. 运行 start.bat 启动服务
echo.
pause
