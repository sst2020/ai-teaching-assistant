# AI 服务配置与使用说明

## 📊 当前配置状态总结

### ✅ 当前使用的 AI Provider
**DeepSeek** (已启用并配置)

### 🔑 配置详情
```env
USE_DEEPSEEK=true
DEEPSEEK_API_KEY=sk-abf377836ab548169bf609f6ba675e2b
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TEMPERATURE=0.7
DEEPSEEK_MAX_TOKENS=2000
DEEPSEEK_TIMEOUT=60
DEEPSEEK_MAX_RETRIES=3
DEEPSEEK_RETRY_DELAY=1.0
```

---

## 🏗️ AI Provider 架构

### 支持的 AI 提供商

#### 1. **DeepSeek** (当前使用)
- **优先级**: 最高 (USE_DEEPSEEK=true)
- **API 兼容性**: OpenAI-compatible API
- **模型**: deepseek-chat, deepseek-reasoner
- **特点**: 
  - 中文优化
  - 流式响应支持
  - 重试机制
  - 详细日志记录
- **使用场景**: 
  - 代码反馈生成 (中文)
  - 学生问答 (中文)
  - 问题分类
  - 报告分析

#### 2. **FastChat** (本地部署)
- **优先级**: 第二 (USE_FASTCHAT=true)
- **API 兼容性**: OpenAI-compatible API
- **模型**: qwen2.5-7b (可配置)
- **特点**:
  - 本地部署，数据隐私
  - 无 API 费用
  - 中文优化
- **使用场景**: 
  - 离线环境
  - 数据敏感场景
  - 成本控制

#### 3. **OpenAI** (备用)
- **优先级**: 第三 (默认)
- **API**: 官方 OpenAI API
- **模型**: gpt-4, gpt-3.5-turbo
- **特点**:
  - 高质量响应
  - 英文优化
- **使用场景**:
  - 英文教学
  - 高级代码分析

#### 4. **Local LLM** (占位符)
- **优先级**: 最低
- **实现**: 规则基础 + 关键词匹配
- **特点**:
  - 无需 API
  - 功能有限
- **使用场景**:
  - 开发测试
  - 演示环境

---

## 🔄 Provider 选择逻辑

### 优先级顺序 (backend/services/ai_service.py:566-584)
```python
if settings.USE_DEEPSEEK:
    # 使用 DeepSeek
    provider = DeepSeekProvider(config)
elif settings.USE_FASTCHAT:
    # 使用 FastChat
    provider = FastChatProvider(config)
elif config.provider == AIProvider.OPENAI:
    # 使用 OpenAI
    provider = OpenAIProvider(config)
else:
    # 使用 Local LLM (fallback)
    provider = LocalLLMProvider(config)
```

### 切换 Provider 方法

#### 切换到 OpenAI
```env
USE_DEEPSEEK=false
USE_FASTCHAT=false
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE=https://api.openai.com/v1
AI_MODEL=gpt-4
```

#### 切换到 FastChat
```env
USE_DEEPSEEK=false
USE_FASTCHAT=true
FASTCHAT_API_BASE=http://localhost:8000/v1
FASTCHAT_MODEL_NAME=qwen2.5-7b
```

#### 切换到 Local LLM
```env
USE_DEEPSEEK=false
USE_FASTCHAT=false
USE_LOCAL_LLM=true
```

---

## 🎯 功能集成点

### 1. 代码反馈生成
**调用位置**: `backend/api/ai.py:52-68`
```python
ai_result = await ai_service.generate_code_feedback(
    code=request.code,
    analysis_results={
        "overall_score": feedback.overall_score,
        "grade": feedback.overall_grade,
        "issues": [...]
    }
)
```

**使用场景**:
- 学生提交代码后自动生成反馈
- 提供代码改进建议
- 指出代码风格和复杂度问题

### 2. 学生问答
**调用位置**: `backend/services/qa_service.py:62-108`
```python
ai_answer = await self.ai.answer_question(request.question, context)
```

**使用场景**:
- 学生提问时自动回答
- 问题分类和优先级判断
- 决定是否需要教师介入

### 3. 报告分析
**调用位置**: `backend/services/report_analysis_service.py:498-513`
```python
response = await self.ai_service.generate_response(
    prompt=prompt,
    system_prompt="你是一位严谨的学术报告评审专家...",
    max_tokens=2000,
    temperature=0.3
)
```

**使用场景**:
- 分析报告逻辑结构
- 评估创新性
- 语言质量评估

### 4. 代码评分
**调用位置**: `backend/services/grading_service.py:74-80`
```python
ai_feedback = await self.ai.generate_code_feedback(
    code=submission.content,
    analysis_results={...}
)
```

**使用场景**:
- 自动评分
- 生成评分报告
- 提供学习建议

---

## ⚙️ 配置最佳实践

### 开发环境
```env
USE_DEEPSEEK=true
DEEPSEEK_TIMEOUT=60
DEEPSEEK_MAX_RETRIES=3
LOG_LEVEL=DEBUG
```

### 生产环境
```env
USE_DEEPSEEK=true
DEEPSEEK_TIMEOUT=30
DEEPSEEK_MAX_RETRIES=2
LOG_LEVEL=INFO
ENABLE_REQUEST_LOGGING=false
```

### 离线环境
```env
USE_FASTCHAT=true
FASTCHAT_API_BASE=http://localhost:8000/v1
FASTCHAT_TIMEOUT=300
```

---

## 🐛 常见问题与解决方案

### 问题 1: AI 响应超时
**症状**: `DeepSeek服务超时: 请求超过 60 秒未响应`
**解决方案**:
1. 增加 `DEEPSEEK_TIMEOUT` 值
2. 检查网络连接
3. 减少 `DEEPSEEK_MAX_TOKENS`

### 问题 2: API Key 无效
**症状**: `401 Unauthorized` 或 `Invalid API Key`
**解决方案**:
1. 验证 API Key 是否正确
2. 检查 API Key 是否过期
3. 确认 API Base URL 正确

### 问题 3: 中文响应乱码
**症状**: 返回的中文显示为乱码
**解决方案**:
1. 确认使用 DeepSeek 或 FastChat (中文优化)
2. 检查数据库编码设置
3. 验证前端字符编码

### 问题 4: 响应质量差
**症状**: AI 回答不准确或不相关
**解决方案**:
1. 调整 `TEMPERATURE` 参数 (0.3-0.9)
2. 增加 `MAX_TOKENS` 允许更长响应
3. 优化 system_prompt 和 user_prompt
4. 考虑切换到更强大的模型

---

## 📈 性能监控

### 查看 AI 交互统计
```python
from services.ai_service import ai_service

stats = ai_service.get_interaction_stats()
print(stats)
# {
#     "total_interactions": 150,
#     "average_latency_ms": 2500,
#     "by_type": {
#         "generate_code_feedback": 50,
#         "answer_question": 80,
#         "categorize_question": 20
#     }
# }
```

### 日志监控
```bash
# 查看 AI 请求日志
tail -f backend/logs/app.log | grep "DeepSeek API"
```

---

## 🔐 安全建议

1. **不要提交 API Key 到版本控制**
   - 使用 `.env` 文件
   - 添加到 `.gitignore`

2. **使用环境变量**
   - 生产环境使用环境变量而非 `.env` 文件
   - 使用密钥管理服务 (如 AWS Secrets Manager)

3. **限制 API 使用**
   - 设置合理的 `MAX_TOKENS`
   - 实施速率限制
   - 监控 API 使用量

4. **数据隐私**
   - 敏感数据使用本地 LLM (FastChat)
   - 不要将学生个人信息发送到外部 API
   - 遵守数据保护法规


