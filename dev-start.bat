@echo off
REM AI Teaching Assistant - Windows 一键启动脚本
REM 自动检查环境并启动开发服务器

setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                AI Teaching Assistant                         ║
echo ║                Windows 开发环境启动工具                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM 检查 Node.js
echo [INFO] 检查 Node.js 环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js 未安装或不在 PATH 中
    echo [INFO] 请从 https://nodejs.org 下载并安装 Node.js
    pause
    exit /b 1
)

REM 检查 Python
echo [INFO] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装或不在 PATH 中
    echo [INFO] 请从 https://python.org 下载并安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查项目结构
echo [INFO] 检查项目结构...
if not exist "frontend\package.json" (
    echo [ERROR] 前端项目不存在: frontend\package.json
    pause
    exit /b 1
)

if not exist "backend\requirements.txt" (
    echo [ERROR] 后端项目不存在: backend\requirements.txt
    pause
    exit /b 1
)

REM 检查前端依赖
echo [INFO] 检查前端依赖...
if not exist "frontend\node_modules" (
    echo [WARNING] 前端依赖未安装，正在安装...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo [ERROR] 前端依赖安装失败
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo [SUCCESS] 前端依赖安装完成
)

REM 检查后端虚拟环境
echo [INFO] 检查后端虚拟环境...
if not exist "backend\venv" (
    if not exist "backend\.venv" (
        echo [WARNING] 后端虚拟环境未创建，正在创建...
        cd backend
        python -m venv venv
        if errorlevel 1 (
            echo [ERROR] 虚拟环境创建失败
            cd ..
            pause
            exit /b 1
        )
        
        echo [INFO] 激活虚拟环境并安装依赖...
        call venv\Scripts\activate.bat
        pip install -r requirements.txt
        if errorlevel 1 (
            echo [ERROR] 后端依赖安装失败
            cd ..
            pause
            exit /b 1
        )
        cd ..
        echo [SUCCESS] 后端环境设置完成
    )
)

REM 检查环境变量文件
echo [INFO] 检查环境配置...
if not exist "frontend\.env" (
    echo [WARNING] 前端环境配置不存在，正在创建...
    copy "frontend\.env.example" "frontend\.env" >nul
    echo [SUCCESS] 前端环境配置已创建
)

if not exist "backend\.env" (
    echo [WARNING] 后端环境配置不存在，正在创建...
    copy "backend\.env.example" "backend\.env" >nul
    echo [SUCCESS] 后端环境配置已创建
)

REM 运行环境检查脚本
echo [INFO] 运行完整环境检查...
node scripts\check-environment.js
if errorlevel 1 (
    echo [ERROR] 环境检查失败，请解决上述问题
    pause
    exit /b 1
)

echo.
echo [SUCCESS] 环境检查通过！
echo [INFO] 启动开发服务器...
echo.

REM 启动开发服务器
node scripts\dev-start.js

REM 如果脚本执行失败，显示错误信息
if errorlevel 1 (
    echo.
    echo [ERROR] 启动失败，请检查上述错误信息
    echo [INFO] 常见解决方案:
    echo   1. 确保 Node.js 和 Python 已正确安装
    echo   2. 检查端口 3000 和 8000 是否被占用
    echo   3. 确保网络连接正常（用于下载依赖）
    echo   4. 检查防火墙设置
    echo.
    pause
)

endlocal
