@echo off
echo ========================================
echo FastChat + ChatGLM4 Demo 启动脚本
echo ========================================

cd /d G:\ai-chatglm-demo

echo [1/3] 启动 Controller...
start "FastChat Controller" cmd /k scripts\start_controller.bat

timeout /t 5 /nobreak

echo [2/3] 启动 Model Worker...
start "FastChat Worker" cmd /k scripts\start_worker.bat

timeout /t 30 /nobreak

echo [3/3] 启动 API Server...
start "FastChat API" cmd /k scripts\start_api.bat

echo.
echo ========================================
echo 所有服务已启动！
echo API地址: http://localhost:8000/v1
echo 文档地址: http://localhost:8000/docs
echo ========================================
pause

