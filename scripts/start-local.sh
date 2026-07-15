#!/bin/bash
# 本地开发环境启动脚本（Linux/macOS）

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}AI Teaching Assistant 本地启动脚本${NC}"
echo -e "${GREEN}======================================${NC}"
echo

# 检查端口占用并释放
check_and_kill_port() {
    local port=$1
    local pid=$(lsof -ti :$port 2>/dev/null || netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | head -1)
    
    if [ -n "$pid" ]; then
        echo -e "${YELLOW}警告: 端口 $port 已被占用 (PID: $pid)，正在终止...${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

echo -e "${GREEN}[1/4]${NC} 检查端口 9000..."
check_and_kill_port 9000

echo -e "${GREEN}[2/4]${NC} 检查端口 3000..."
check_and_kill_port 3000

# 检查后端虚拟环境
echo
echo -e "${GREEN}[3/4]${NC} 检查后端环境..."
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${YELLOW}创建 Python 虚拟环境...${NC}"
    cd "$BACKEND_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source "$BACKEND_DIR/venv/bin/activate"
fi

# 启动后端
echo -e "${GREEN}启动后端服务 (端口 9000)...${NC}"
cd "$BACKEND_DIR"
python -m uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 检查后端是否成功启动
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}错误: 后端启动失败${NC}"
    exit 1
fi

echo -e "${GREEN}后端服务已启动 (PID: $BACKEND_PID)${NC}"

# 启动前端
echo
echo -e "${GREEN}[4/4]${NC} 启动前端服务..."
cd "$FRONTEND_DIR"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}安装前端依赖...${NC}"
    npm install
fi

echo -e "${GREEN}启动前端服务 (端口 3000)...${NC}"
npm run dev &
FRONTEND_PID=$!

# 等待前端启动
sleep 5

# 检查前端是否成功启动
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}错误: 前端启动失败${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}前端服务已启动 (PID: $FRONTEND_PID)${NC}"

echo
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}所有服务已启动！${NC}"
echo -e "后端 API: ${YELLOW}http://localhost:9000${NC}"
echo -e "前端应用: ${YELLOW}http://localhost:3000${NC}"
echo -e "API 文档: ${YELLOW}http://localhost:9000/docs${NC}"
echo -e "${GREEN}======================================${NC}"
echo

# 捕获 Ctrl+C 信号
cleanup() {
    echo
    echo -e "${YELLOW}正在停止服务...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}服务已停止${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 保持脚本运行
echo "按 Ctrl+C 停止所有服务..."
wait
