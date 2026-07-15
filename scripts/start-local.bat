@echo off
chcp 65001 >nul
:: 本地开发环境启动脚本（Windows）

echo ======================================
echo AI Teaching Assistant 本地启动脚本
echo ======================================
echo.

:: 检查端口占用
echo [1/4] 检查端口 9000...
netstat -ano | findstr :9000 >nul
if %errorlevel% == 0 (
    echo 警告: 端口 9000 已被占用，尝试终止进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :9000') do (
        taskkill /F /PID %%a 2>nul
    )
)

echo [2/4] 检查端口 3000...
netstat -ano | findstr :3000 >nul
if %errorlevel% == 0 (
    echo 警告: 端口 3000 已被占用，尝试终止进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
        taskkill /F /PID %%a 2>nul
    )
)

echo.
echo [3/4] 配置环境变量并启动后端服务...
:: 设置后端环境变量（使用本地 MySQL）
set APP_NAME=AI Teaching Assistant API
set APP_VERSION=1.0.0
set DEBUG=true
set LOG_LEVEL=INFO
set HOST=127.0.0.1
set PORT=9000
set DATABASE_URL=mysql+aiomysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant
set DATABASE_ECHO=false
set RABBITMQ_URL=
set SECRET_KEY=local-dev-secret-key
set CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
set RATE_LIMIT_ENABLED=false

start "Backend (Port 9000)" cmd /k "cd /d E:\Code\repo\ai-teaching-assistant-frontend\backend && .\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload"

:: 等待后端启动
timeout /t 3 /nobreak >nul

echo.
echo [4/4] 启动前端服务...
start "Frontend (Port 3000)" cmd /k "cd /d E:\Code\repo\ai-teaching-assistant-frontend\frontend && npm run dev"

echo.
echo ======================================
echo 服务启动中...
echo 后端: http://localhost:9000
echo 前端: http://localhost:3000
echo API文档: http://localhost:9000/docs
echo ======================================
echo.
echo 注意: 请确保 MySQL 服务已启动，并创建了数据库和用户
echo 数据库: ai_teaching_assistant
echo 用户: ai_teaching@localhost / 密码: ai_teaching_dev
echo.

:: 自动打开浏览器
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo 按任意键停止所有服务...
pause >nul

:: 终止进程
taskkill /FI "WINDOWTITLE eq Backend (Port 9000)*" /F 2>nul
taskkill /FI "WINDOWTITLE eq Frontend (Port 3000)*" /F 2>nul

echo 服务已停止。
pause
