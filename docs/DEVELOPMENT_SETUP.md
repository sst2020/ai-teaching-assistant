# AI Teaching Assistant - 开发环境设置指南

本指南提供了完整的前后端协同调试环境配置方案，包含增强调试功能和一键启动脚本。

## 🚀 快速开始

### 一键启动（推荐）

**Windows 用户：**
```bash
# 双击运行或在命令行执行
dev-start.bat
```

**Linux/macOS 用户：**
```bash
# 在终端执行
./dev-start.sh
```

### 手动启动

如果需要更多控制，可以手动启动各个服务：

```bash
# 1. 环境检查
node scripts/check-environment.js

# 2. 启动后端 (终端1)
cd backend
python -m uvicorn app.main:app --reload --port 8000

# 3. 启动前端 (终端2)
cd frontend
npm start
```

## 📋 系统要求

### 必需软件
- **Node.js** 18.0.0 或更高版本
- **Python** 3.10.0 或更高版本
- **npm** (随 Node.js 安装)
- **pip** (随 Python 安装)

### 推荐软件
- **Git** (版本控制)
- **VS Code** (代码编辑器)
- **Postman** 或 **Insomnia** (API 测试)

## 🔧 环境配置

### 前端环境变量 (`frontend/.env`)

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# App Configuration
REACT_APP_NAME=AI Teaching Assistant
REACT_APP_VERSION=1.0.0

# Debug Configuration
REACT_APP_DEBUG_MODE=true
REACT_APP_LOG_LEVEL=debug
REACT_APP_ENABLE_DEBUG_PANEL=true
REACT_APP_ENABLE_API_LOGGING=true
REACT_APP_ENABLE_PERFORMANCE_MONITORING=true

# Development Tools
REACT_APP_ENABLE_API_TESTER=true
REACT_APP_ENABLE_ERROR_BOUNDARY=true
REACT_APP_AUTO_OPEN_DEVTOOLS=false
```

### 后端环境变量 (`backend/.env`)

```env
# Application Settings
APP_NAME="AI Teaching Assistant API"
APP_VERSION="1.0.0"
DEBUG=true
LOG_LEVEL=DEBUG

# Development & Debugging Settings
ENABLE_REQUEST_LOGGING=true
ENABLE_RESPONSE_LOGGING=true
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_ERROR_TRACKING=true
LOG_SQL_QUERIES=false
PRETTY_PRINT_LOGS=true

# Server Settings
HOST=0.0.0.0
PORT=8000
WORKERS=1
RELOAD=true

# CORS Settings (Enhanced for Development)
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
CORS_ALLOW_HEADERS=["*"]
CORS_EXPOSE_HEADERS=["X-Request-ID", "X-Response-Time"]
```

## 🐛 调试功能

### 1. 调试面板

前端应用包含一个强大的调试面板，提供：

- **性能监控**: 实时API响应时间统计
- **错误日志**: 详细的错误信息和堆栈跟踪
- **请求追踪**: 完整的API调用历史
- **统计信息**: 成功率、平均响应时间等

**使用方法：**
- 调试面板仅在开发环境下显示
- 点击右上角的 "🐛 Debug" 按钮打开/关闭
- 支持最小化和全屏模式

### 2. 增强日志记录

**前端日志：**
- 详细的API请求/响应日志
- 性能计时信息
- 错误分类和上下文
- 请求ID关联追踪

**后端日志：**
- 彩色控制台输出
- 结构化日志格式
- 请求生命周期追踪
- 性能监控和告警

### 3. 请求追踪

每个API请求都有唯一的请求ID，方便前后端日志关联：

```
前端: 🚀 [API Request] POST /api/v1/qa/ask (ID: abc12345)
后端: INFO | 14:30:25 | abc12345 | main:85 | 🚀 POST /api/v1/qa/ask
```

## 🛠️ 开发工具

### 浏览器开发者工具

**推荐设置：**
1. 打开 Chrome DevTools (F12)
2. 进入 Network 面板查看API请求
3. 进入 Console 面板查看详细日志
4. 进入 Application 面板查看存储数据

### API 测试工具

**内置API测试器：**
- 访问 `http://localhost:3000` 后点击调试面板
- 选择 "API测试" 标签页
- 支持所有API端点的在线测试

**外部工具：**
- **Postman**: 导入 `docs/api-collection.json`
- **Insomnia**: 导入 `docs/api-spec.yaml`
- **VS Code REST Client**: 使用 `docs/api-requests.http`

### 性能监控

**前端性能：**
- React DevTools Profiler
- 内置性能监控面板
- 网络请求时间统计

**后端性能：**
- 自动慢查询检测 (>2秒)
- 内存使用监控
- 数据库查询分析

## 📊 服务状态

### 健康检查端点

- **前端**: `http://localhost:3000` (主页)
- **后端**: `http://localhost:8000/health`
- **API文档**: `http://localhost:8000/docs`

### 端口使用

| 服务 | 端口 | 用途 |
|------|------|------|
| 前端开发服务器 | 3000 | React 应用 |
| 后端API服务器 | 8000 | FastAPI 应用 |
| 数据库 | - | SQLite (文件) |

## 🔍 故障排除

### 常见问题

**1. 端口被占用**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:3000 | xargs kill -9
```

**2. 依赖安装失败**
```bash
# 清除缓存重新安装
cd frontend && rm -rf node_modules package-lock.json && npm install
cd backend && rm -rf venv && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

**3. CORS 错误**
- 检查后端 `.env` 中的 `CORS_ORIGINS` 配置
- 确保前端URL在允许列表中

**4. API 连接失败**
- 确认后端服务正在运行
- 检查防火墙设置
- 验证 `REACT_APP_API_URL` 配置

### 调试技巧

**1. 启用详细日志**
```env
# frontend/.env
REACT_APP_LOG_LEVEL=debug

# backend/.env
LOG_LEVEL=DEBUG
```

**2. 查看网络请求**
- 打开浏览器开发者工具
- 进入 Network 面板
- 筛选 XHR/Fetch 请求

**3. 检查控制台错误**
- 前端错误在浏览器 Console 面板
- 后端错误在终端输出

## 📚 更多资源

- [前端开发指南](./frontend/README.md)
- [后端开发指南](./backend/README.md)
- [API 文档](http://localhost:8000/docs)
- [系统测试报告](./SYSTEM_TESTING_REPORT.md)
- [用户界面指南](./USER_INTERFACE_GUIDE.md)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 Pull Request

---

如有问题，请查看 [故障排除](#故障排除) 部分或提交 Issue。
