#!/bin/bash

# AI Teaching Assistant - Unix/Linux/macOS 一键启动脚本
# 自动检查环境并启动开发服务器

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示标题
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                AI Teaching Assistant                         ║"
echo "║               Unix/Linux 开发环境启动工具                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查 Node.js
log_info "检查 Node.js 环境..."
if ! command -v node &> /dev/null; then
    log_error "Node.js 未安装或不在 PATH 中"
    log_info "请访问 https://nodejs.org 下载并安装 Node.js"
    exit 1
fi

NODE_VERSION=$(node --version)
log_success "Node.js 版本: $NODE_VERSION"

# 检查 npm
if ! command -v npm &> /dev/null; then
    log_error "npm 未安装或不在 PATH 中"
    exit 1
fi

# 检查 Python
log_info "检查 Python 环境..."
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    log_error "Python 未安装或不在 PATH 中"
    log_info "请访问 https://python.org 下载并安装 Python 3.10+"
    exit 1
fi

# 使用 python3 或 python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

PYTHON_VERSION=$($PYTHON_CMD --version)
log_success "Python 版本: $PYTHON_VERSION"

# 检查项目结构
log_info "检查项目结构..."
if [ ! -f "frontend/package.json" ]; then
    log_error "前端项目不存在: frontend/package.json"
    exit 1
fi

if [ ! -f "backend/requirements.txt" ]; then
    log_error "后端项目不存在: backend/requirements.txt"
    exit 1
fi

# 检查前端依赖
log_info "检查前端依赖..."
if [ ! -d "frontend/node_modules" ]; then
    log_warning "前端依赖未安装，正在安装..."
    cd frontend
    npm install
    if [ $? -ne 0 ]; then
        log_error "前端依赖安装失败"
        exit 1
    fi
    cd ..
    log_success "前端依赖安装完成"
fi

# 检查后端虚拟环境
log_info "检查后端虚拟环境..."
if [ ! -d "backend/venv" ] && [ ! -d "backend/.venv" ]; then
    log_warning "后端虚拟环境未创建，正在创建..."
    cd backend
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        log_error "虚拟环境创建失败"
        exit 1
    fi
    
    log_info "激活虚拟环境并安装依赖..."
    source venv/bin/activate
    $PIP_CMD install -r requirements.txt
    if [ $? -ne 0 ]; then
        log_error "后端依赖安装失败"
        exit 1
    fi
    cd ..
    log_success "后端环境设置完成"
fi

# 检查环境变量文件
log_info "检查环境配置..."
if [ ! -f "frontend/.env" ]; then
    log_warning "前端环境配置不存在，正在创建..."
    cp "frontend/.env.example" "frontend/.env"
    log_success "前端环境配置已创建"
fi

if [ ! -f "backend/.env" ]; then
    log_warning "后端环境配置不存在，正在创建..."
    cp "backend/.env.example" "backend/.env"
    log_success "后端环境配置已创建"
fi

# 设置脚本执行权限
chmod +x scripts/check-environment.js
chmod +x scripts/dev-start.js

# 运行环境检查脚本
log_info "运行完整环境检查..."
node scripts/check-environment.js
if [ $? -ne 0 ]; then
    log_error "环境检查失败，请解决上述问题"
    exit 1
fi

echo
log_success "环境检查通过！"
log_info "启动开发服务器..."
echo

# 启动开发服务器
node scripts/dev-start.js

# 如果脚本执行失败，显示错误信息
if [ $? -ne 0 ]; then
    echo
    log_error "启动失败，请检查上述错误信息"
    echo -e "${YELLOW}常见解决方案:${NC}"
    echo "  1. 确保 Node.js 和 Python 已正确安装"
    echo "  2. 检查端口 3000 和 8000 是否被占用"
    echo "  3. 确保网络连接正常（用于下载依赖）"
    echo "  4. 检查防火墙设置"
    echo "  5. 确保有足够的磁盘空间"
    echo
fi
