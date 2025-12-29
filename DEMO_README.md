# FastChat + ChatGLM4-6B Demo

本地大模型部署Demo，用于AI教学助手系统。

## 📁 目录结构

```
G:\ai-chatglm-demo\
├── venv\                      # Python虚拟环境
├── models\chatglm4-6b\       # ChatGLM4-6B模型
├── scripts\                   # 启动脚本
├── logs\                      # 日志文件
├── test\                      # 测试脚本
└── README.md                  # 本文件
```

## 🚀 快速启动

### 方式1: 一键启动 (推荐)
```batch
cd G:\ai-chatglm-demo
scripts\start_all.bat
```

### 方式2: 分步启动
```batch
# 1. 启动Controller
scripts\start_controller.bat

# 2. 启动Worker (等待5秒)
scripts\start_worker.bat

# 3. 启动API Server (等待30秒)
scripts\start_api.bat
```

## 🧪 测试

### API测试
```batch
cd G:\ai-chatglm-demo
venv\Scripts\activate
python test\test_api.py
```

### 集成测试
```batch
cd E:\Code\repo\ai-teaching-assistant-frontend\backend
python test_local_llm.py
```

## 📊 API文档

- **API地址**: http://localhost:8000/v1
- **文档地址**: http://localhost:8000/docs
- **模型名称**: `chatglm4-6b` 或 `gpt-3.5-turbo` (别名)

## 🔧 配置

### 显存优化
如果遇到显存不足，可以调整 `scripts/start_worker.bat`:
- 减少 `--max-gpu-memory` (如改为 6GiB)
- 使用 `--load-8bit` 或 `--load-4bit` 量化

### 性能优化
- 增加 `--max-gpu-memory` 提升性能
- 移除 `--load-8bit` 使用FP16精度

## 📝 日志

日志文件位于 `logs\` 目录:
- `controller.log` - Controller日志
- `worker.log` - Worker日志
- `api.log` - API Server日志

## ⚠️ 故障排查

### 问题1: 显存不足
**解决**: 使用 `--load-8bit` 或 `--load-4bit` 量化

### 问题2: 模型加载慢
**原因**: 首次加载需要30-60秒
**解决**: 耐心等待

### 问题3: API连接失败
**检查**: 
1. Controller是否启动 (http://localhost:21001)
2. Worker是否注册成功
3. 查看日志文件

## 📞 支持

如有问题，请查看日志文件或联系开发团队。

