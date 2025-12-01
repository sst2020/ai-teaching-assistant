# AI 智能教学助手 - 项目待办事项清单

> **最后更新：** 2024年12月
> **项目状态：** MVP 已完成 ✅
> **复杂度指标：** 🟢 简单 | 🟡 中等 | 🔴 困难 | ⏱️ 耗时较长

本文档概述了 AI 智能教学助手项目的剩余任务、优先级和贡献机会。

## 🎉 MVP 状态

最小可行产品（MVP）已完成，包含以下核心功能：
- ✅ 用户认证（登录、注册、登出）
- ✅ 作业提交（集成 Monaco 代码编辑器）
- ✅ 文件上传（自动语言检测）
- ✅ 成绩查看（支持筛选和排序）
- ✅ 学生仪表板
- ✅ 前后端集成
- ✅ API 文档（Swagger UI）

**相关文档：**
- 📄 [用户界面指南](docs/USER_INTERFACE_GUIDE.md)
- 📄 [系统测试报告](docs/SYSTEM_TESTING_REPORT.md)
- 📄 [调试指南](docs/DEBUGGING_GUIDE.md)

---

## 目录

- [优先级说明](#优先级说明)
- [✅ 已完成功能](#-已完成功能)
- [🔐 安全与认证](#-安全与认证)
- [🖥️ 前端开发](#️-前端开发)
- [⚙️ 后端增强](#️-后端增强)
- [🧪 测试](#-测试)
- [📚 文档](#-文档)
- [🚀 DevOps 与部署](#-devops-与部署)
- [🎯 未来增强功能](#-未来增强功能)

---

## 优先级说明

| 优先级 | 描述 |
|--------|------|
| **P0** | 关键 - 阻塞其他工作 |
| **P1** | 高 - 核心功能 |
| **P2** | 中 - 重要功能 |
| **P3** | 低 - 锦上添花 |

---

## ✅ 已完成功能

> **状态：** 已实现
> **最后更新：** 2024年11月

### 智能反馈生成系统 ✅

> **完成时间：** 2024年11月

#### 交付物 1：反馈生成服务 ✅

- [x] 🟡 **FeedbackGenerationService** - `backend/services/feedback_service.py`
  - 基于代码分析结果的上下文感知反馈生成
  - 多种反馈语气：鼓励型、专业型、详细型、简洁型、友好型、严格型
  - 针对 Python、JavaScript、Java、TypeScript、C、C++ 的语言特定最佳实践
  - 分类反馈：代码质量、逻辑效率、风格可读性、安全性、最佳实践、建议、鼓励
  - 优势/改进点/下一步建议识别

- [x] 🟢 **反馈 Schemas** - `backend/schemas/feedback.py`
  - 所有反馈操作的 Pydantic 模型
  - FeedbackTone、FeedbackCategory、TemplateCategory 枚举
  - 所有端点的请求/响应模型

- [x] 🟢 **FeedbackTemplate 模型** - `backend/models/feedback_template.py`
  - 用于存储反馈模板的 SQLAlchemy 模型
  - 支持分类、严重程度、标签和变量

#### 交付物 2：AI 集成接口 ✅

- [x] 🔴 **AIService** - `backend/services/ai_service.py`
  - OpenAI/Claude 集成，可配置提供商
  - 未配置 API 密钥时回退到本地响应
  - 交互跟踪和统计

- [x] 🟢 **AIInteraction 模型** - `backend/models/ai_interaction.py`
  - 跟踪 AI 交互历史
  - 存储提示词、响应、使用的令牌数和延迟

- [x] 🟡 **AI API 端点** - `backend/api/ai.py`
  - `POST /api/v1/ai/generate-feedback` - 生成综合反馈
  - `POST /api/v1/ai/explain-code` - 向学生解释代码
  - `POST /api/v1/ai/suggest-improvements` - 建议代码改进
  - `POST /api/v1/ai/answer-question` - 回答学生问题
  - `GET /api/v1/ai/config` - 获取 AI 配置
  - `GET /api/v1/ai/stats` - 获取交互统计
  - `GET /api/v1/ai/health` - 检查 AI 服务健康状态

#### 交付物 3：反馈模板库 ✅

- [x] 🟡 **反馈模板 API** - `backend/api/feedback_templates.py`
  - `GET /api/v1/feedback-templates` - 列出模板（支持过滤）
  - `POST /api/v1/feedback-templates` - 创建新模板
  - `GET /api/v1/feedback-templates/{id}` - 按 ID 获取模板
  - `PUT /api/v1/feedback-templates/{id}` - 更新模板
  - `DELETE /api/v1/feedback-templates/{id}` - 删除模板
  - `GET /api/v1/feedback-templates/categories/list` - 列出所有分类
  - `POST /api/v1/feedback-templates/{id}/increment-usage` - 跟踪模板使用

- [x] 🟢 **CRUD 操作** - `backend/utils/crud.py`
  - CRUDFeedbackTemplate：get_by_category、get_by_tags、increment_usage、search
  - CRUDAIInteraction：get_by_user、get_by_type、get_stats、log_interaction

- [x] 🟢 **种子脚本** - `backend/scripts/seed_feedback_templates.py`
  - 7 个分类共 29 个默认模板：
    - 常见问题（5 个模板）
    - 命名（3 个模板）
    - 风格（3 个模板）
    - 复杂度（3 个模板）
    - 安全（4 个模板）
    - 鼓励（6 个模板）
    - 语言特定（5 个模板）

- [x] 🟢 **测试** - `backend/tests/test_feedback_system.py`
  - 反馈生成、AI 服务和模板的综合测试

#### 剩余设置步骤

- [ ] 🟢 **运行数据库迁移** (P0)
  ```bash
  cd backend
  python -m alembic revision --autogenerate -m "Add feedback_templates and ai_interactions tables"
  python -m alembic upgrade head
  ```

- [ ] 🟢 **填充反馈模板** (P0)
  ```bash
  cd backend
  python -m scripts.seed_feedback_templates
  ```

- [ ] 🟢 **配置 OPENAI_API_KEY**（可选）
  - 在 `.env` 文件中设置 `OPENAI_API_KEY` 以启用 AI 功能
  - 没有 API 密钥时，系统使用本地回退响应

- [ ] 🟢 **运行反馈系统测试** (P1)
  ```bash
  cd backend
  python -m pytest tests/test_feedback_system.py -v
  ```

---

## 🔐 安全与认证

> **状态：** MVP 已完成 ✅（开发环境认证）
> **优先级：** P1 - 需要生产环境认证
> **依赖：** 无

### JWT 认证系统 ✅（MVP）

- [x] 🟡 **创建认证中间件** (P0) ✅
  - 创建了 `backend/api/auth.py` 路由
  - 实现了 `/auth/login` 端点（返回 JWT）
  - 实现了 `/auth/logout` 端点
  - 实现了 `/auth/refresh` 端点
  - 实现了 `/auth/register` 端点
  - 实现了 `/auth/me` 端点
  - **注意：** 当前使用内存存储用于开发

- [x] 🟢 **前端认证上下文** (P0) ✅
  - 创建了 `frontend/src/contexts/AuthContext.tsx`
  - JWT 存储在 localStorage
  - API 调用时自动刷新令牌
  - 实现了受保护路由包装器

### 生产环境认证（待完成）

- [ ] 🔴 **实现带数据库存储的生产 JWT** (P0)
  - 从内存存储迁移到数据库存储
  - 使用 bcrypt 添加密码哈希
  - 实现令牌黑名单用于登出
  - **验收标准：**
    - 令牌在可配置时间后过期（默认：30分钟）
    - 支持刷新令牌
    - 安全密码存储

- [ ] 🟡 **为 Student 模型添加密码字段** (P1)
  - 更新 `backend/models/student.py`
  - 创建 Alembic 迁移
  - 更新注册端点以哈希密码
  - **文件：** `backend/models/student.py`, `backend/schemas/student.py`

### 基于角色的访问控制 (RBAC)

- [ ] 🔴 **设计和实现用户角色** (P1)
  - 创建带有角色的 `User` 模型（学生、教师、管理员）
  - 创建 `Role` 和 `Permission` 模型
  - **验收标准：**
    - 学生：提交作业、查看自己的成绩、提问
    - 教师：批改作业、查看所有提交、回答问题
    - 管理员：完全访问权限、用户管理

- [ ] 🟡 **创建 Teacher 模型和端点** (P1)
  - 创建 `backend/models/teacher.py`
  - 创建 `backend/api/teachers.py` 路由
  - 实现教师 CRUD 操作
  - **交付物：** 模型、schemas、路由、测试

- [ ] 🟡 **实现权限装饰器** (P2)
  - 创建 `@require_role("teacher")` 装饰器
  - 创建 `@require_permission("grade_assignments")` 装饰器
  - **文件：** `backend/core/permissions.py`

---

## 🖥️ 前端开发

> **状态：** MVP 已完成 ✅
> **优先级：** P2 - 增强功能
> **当前状态：** 所有核心页面已实现

### 认证界面 ✅

- [x] 🟡 **创建登录页面** (P0) ✅
  - 创建了 `frontend/src/pages/Login.tsx`
  - 包含邮箱和密码的表单
  - 错误处理和验证
  - 成功后重定向到仪表板
  - Toast 通知反馈

- [x] 🟡 **创建注册页面** (P0) ✅
  - 创建了 `frontend/src/pages/Register.tsx`
  - 学生注册表单（带验证）
  - 角色选择（学生/教师）

- [x] 🟢 **实现认证上下文和钩子** (P0) ✅
  - 创建了 `frontend/src/contexts/AuthContext.tsx`
  - JWT 存储在 localStorage
  - API 调用时自动刷新令牌

- [x] 🟢 **添加受保护路由包装器** (P1) ✅
  - 创建了 `frontend/src/components/common/ProtectedRoute.tsx`
  - 将未认证用户重定向到登录页

### 学生管理界面 ✅

- [x] 🟡 **创建学生仪表板页面** (P1) ✅
  - 创建了 `frontend/src/pages/StudentDashboard.tsx`
  - 查看已注册课程
  - 查看作业和截止日期
  - 查看提交历史和成绩
  - 统计摘要

- [x] 🟡 **创建作业提交页面** (P1) ✅
  - 创建了 `frontend/src/pages/SubmitAssignment.tsx`
  - Monaco 代码编辑器集成（语法高亮）
  - 文件上传（拖放支持）
  - 语言自动检测
  - 草稿自动保存到 localStorage
  - 评分标准显示面板
  - 确认对话框

- [x] 🟢 **创建成绩页面** (P2) ✅
  - 创建了 `frontend/src/pages/Grades.tsx`
  - 成绩分布图表
  - 可排序和筛选的表格
  - 详细提交模态框
  - 成绩字母徽章（A、B、C、D、F）
  - URL 深度链接到提交

### 教师/管理员界面

- [ ] 🔴 **创建教师仪表板** (P1)
  - 查看所有学生
  - 查看所有提交
  - 批改队列
  - 分析概览
  - **文件：** `frontend/src/pages/TeacherDashboard.tsx`

- [ ] 🟡 **创建作业管理页面** (P1)
  - 创建/编辑/删除作业
  - 设置截止日期和评分标准
  - 批量操作
  - **文件：** `frontend/src/pages/ManageAssignments.tsx`

- [ ] 🟡 **创建批改界面** (P1)
  - 查看提交内容
  - AI 建议评分（可覆盖）
  - 反馈编辑器
  - 批量批改支持
  - **文件：** `frontend/src/pages/GradingInterface.tsx`

- [ ] 🔴 **创建管理员面板** (P2)
  - 用户管理（CRUD）
  - 系统设置
  - 分析仪表板
  - **文件：** `frontend/src/pages/AdminPanel.tsx`

### UI/UX 改进 ✅

- [x] 🟢 **实现 React Router** (P0) ✅
  - 使用 React Router v7
  - 所有页面正确路由
  - **文件：** `frontend/src/App.tsx`

- [x] 🟢 **添加 Toast 通知** (P2) ✅
  - 创建了 `frontend/src/components/common/Toast.tsx`
  - 创建了 `frontend/src/contexts/ToastContext.tsx`
  - 成功/错误/信息/警告通知

- [x] 🟢 **改进响应式设计** (P2) ✅
  - 移动端友好布局
  - Material Design 3 响应式断点
  - **文件：** 所有 CSS 文件使用 MD3 设计令牌

- [x] 🟢 **添加无障碍功能** (P2) ✅
  - 创建了 `frontend/src/components/common/ConfirmDialog.tsx`
  - 焦点陷阱和键盘导航
  - 屏幕阅读器的 ARIA 属性
  - 可见的焦点指示器

- [ ] 🟡 **添加深色模式支持** (P3)
  - 头部主题切换
  - 持久化偏好设置
  - CSS 变量已准备好用于主题切换

### API 集成 ✅

- [x] 🟡 **添加学生 API 函数** (P1) ✅
  - 注册、登录、获取个人资料已实现
  - `frontend/src/services/api.ts` 已更新

- [x] 🟡 **添加提交 API 函数** (P1) ✅
  - 创建、列表、获取提交已实现
  - `frontend/src/services/api.ts` 已更新

- [x] 🟡 **添加作业 API 函数** (P1) ✅
  - CRUD 操作已实现
  - `frontend/src/services/api.ts` 已更新

### 性能优化 ✅

- [x] 🟢 **添加 API 响应缓存** (P2) ✅
  - 创建了 `frontend/src/utils/cache.ts`
  - 带 TTL 的简单内存缓存
  - 常用实体的缓存键生成器

- [x] 🟢 **添加加载骨架组件** (P2) ✅
  - 创建了 `frontend/src/components/common/Skeleton.tsx`
  - Skeleton、SkeletonCard、SkeletonTable 组件
  - 脉冲和波浪动画

---

## ⚙️ 后端增强

> **状态：** 核心 CRUD 已完成
> **优先级：** P1 - 高

### 评分标准管理

- [ ] 🟡 **创建 Rubric API 端点** (P1)
  - 创建 `backend/api/rubrics.py`
  - 评分标准的 CRUD 操作
  - 将评分标准链接到作业
  - **交付物：** 路由、schemas、测试

- [ ] 🟢 **创建评分标准 schemas** (P1)
  - 创建 `backend/schemas/rubric.py`
  - RubricCreate, RubricUpdate, RubricResponse

### 评分结果 API

- [ ] 🟡 **创建 GradingResult API 端点** (P1)
  - 创建 `backend/api/grading.py`
  - 按学生/作业获取成绩
  - 手动成绩覆盖
  - **交付物：** 路由、schemas、测试

- [ ] 🟢 **创建评分结果 schemas** (P1)
  - 创建 `backend/schemas/grading.py`

### Q&A 系统增强

- [ ] 🟡 **将 Q&A 持久化到数据库** (P1)
  - 更新 `backend/api/qa.py` 以使用数据库
  - 存储问题和答案
  - 链接到学生
  - **文件：** `backend/api/qa.py`, `backend/utils/crud.py`

- [ ] 🟢 **添加 Q&A CRUD 工具** (P1)
  - 在 `backend/utils/crud.py` 中添加 `CRUDQuestion` 和 `CRUDAnswer`

### 文件上传系统

- [ ] 🔴 **实现文件上传端点** (P1)
  - 创建 `backend/api/uploads.py`
  - 支持多种文件类型（.py, .pdf, .docx）
  - 病毒扫描（可选）
  - **验收标准：**
    - 强制执行最大文件大小（默认 10MB）
    - 验证允许的扩展名
    - 安全存储文件

- [ ] 🟡 **创建文件存储服务** (P1)
  - 创建 `backend/services/storage_service.py`
  - 开发环境使用本地存储
  - 生产环境使用 S3/云存储
  - **文件：** `backend/services/storage_service.py`

### 缓存与性能

- [ ] 🟡 **实现 Redis 缓存** (P2)
  - 缓存频繁访问的数据
  - 会话存储
  - 限流存储
  - **文件：** `backend/core/cache.py`

- [ ] 🟢 **添加数据库查询优化** (P2)
  - 在需要的地方添加索引
  - 实现关系的预加载
  - **文件：** 模型文件、Alembic 迁移

### 限流

- [ ] 🟡 **实现限流中间件** (P2)
  - 使用 slowapi 或自定义实现
  - 按端点配置限制
  - **文件：** `backend/core/rate_limit.py`

---

## 🧪 测试

> **状态：** 基础测试已存在
> **优先级：** P1 - 高
> **当前覆盖率：** ~30%（估计）

### 后端单元测试

- [ ] 🟢 **添加学生端点测试** (P1)
  - 创建 `backend/tests/test_students.py`
  - 测试所有 CRUD 操作
  - 测试验证错误
  - **目标覆盖率：** 90%

- [ ] 🟢 **添加提交端点测试** (P1)
  - 创建 `backend/tests/test_submissions.py`
  - 测试创建、列表、状态更新
  - **目标覆盖率：** 90%

- [ ] 🟢 **添加 CRUD 工具测试** (P1)
  - 创建 `backend/tests/test_crud.py`
  - 测试所有 CRUD 操作
  - **目标覆盖率：** 95%

- [ ] 🟡 **添加服务层测试** (P2)
  - 测试 AI 服务（使用 mock）
  - 测试评分服务
  - 测试抄袭检测服务
  - **文件：** `backend/tests/test_services/`

### 前端测试

- [ ] 🟡 **添加组件测试** (P1)
  - 测试 Dashboard 组件
  - 测试 CodeAnalysis 组件
  - 测试 QAInterface 组件
  - 使用 React Testing Library
  - **文件：** `frontend/src/components/**/*.test.tsx`

- [ ] 🟡 **添加 API 服务测试** (P2)
  - Mock axios 调用
  - 测试错误处理
  - **文件：** `frontend/src/services/api.test.ts`

- [ ] 🟢 **添加钩子测试** (P2)
  - 测试自定义钩子
  - **文件：** `frontend/src/hooks/*.test.ts`

### 集成测试

- [ ] 🔴 **创建端到端测试套件** (P2)
  - 使用 Playwright 或 Cypress
  - 测试完整用户流程
  - **验收标准：**
    - 学生注册 → 登录 → 提交 → 查看成绩
    - 教师登录 → 批改 → 提供反馈

- [ ] 🟡 **添加 API 集成测试** (P2)
  - 测试完整的请求/响应周期
  - 测试数据库交互
  - **文件：** `backend/tests/integration/`

### 测试基础设施

- [ ] 🟢 **设置测试数据库** (P1)
  - 使用 SQLite 内存数据库进行测试
  - 添加常用数据的 fixtures
  - **文件：** `backend/tests/conftest.py`

- [ ] 🟢 **添加 GitHub Actions CI** (P1)
  - 在 PR 时运行测试
  - 运行代码检查
  - **文件：** `.github/workflows/ci.yml`

- [ ] 🟢 **添加代码覆盖率报告** (P2)
  - 配置 pytest-cov
  - 在 README 中添加覆盖率徽章
  - **目标：** 80% 覆盖率

---

## 📚 文档

> **状态：** 基础 README 已存在
> **优先级：** P2 - 中

### API 文档

- [ ] 🟢 **添加 OpenAPI 描述** (P2)
  - 为所有端点添加详细描述
  - 添加请求/响应示例
  - **文件：** 所有路由文件

- [ ] 🟡 **创建 API 使用指南** (P2)
  - 创建 `docs/api-guide.md`
  - 包含认证流程
  - 包含常见用例
  - 多语言代码示例

### 开发者文档

- [ ] 🟢 **创建贡献指南** (P2)
  - 创建 `CONTRIBUTING.md`
  - 代码风格指南
  - PR 流程
  - 开发环境设置

- [ ] 🟢 **创建架构文档** (P2)
  - 创建 `docs/architecture.md`
  - 系统设计图
  - 数据流图
  - 组件关系

- [ ] 🟢 **添加内联代码文档** (P3)
  - 为所有函数添加 docstrings
  - 到处添加类型提示
  - **文件：** 所有 Python 文件

### 用户文档

- [ ] 🟡 **创建用户指南** (P3)
  - 创建 `docs/user-guide.md`
  - 学生使用说明
  - 教师使用说明
  - 截图和示例

---

## 🚀 DevOps 与部署

> **状态：** Dockerfile 已存在
> **优先级：** P2 - 中

### Docker 与容器化

- [ ] 🟢 **创建 docker-compose.yml** (P1)
  - Backend + Frontend + PostgreSQL
  - 开发配置
  - **文件：** `docker-compose.yml`

- [ ] 🟢 **创建生产环境 docker-compose** (P2)
  - 创建 `docker-compose.prod.yml`
  - Nginx 反向代理
  - SSL/TLS 配置

- [ ] 🟢 **优化 Docker 镜像** (P3)
  - 多阶段构建
  - 减小镜像大小
  - **文件：** `backend/Dockerfile`, `frontend/Dockerfile`

### CI/CD 流水线

- [ ] 🟡 **设置 GitHub Actions** (P1)
  - 创建 `.github/workflows/ci.yml`
  - 在 push/PR 时运行测试
  - 代码检查和类型检查
  - 构建 Docker 镜像

- [ ] 🟡 **添加部署工作流** (P2)
  - 创建 `.github/workflows/deploy.yml`
  - 合并到 develop 时部署到预发布环境
  - 发布时部署到生产环境

### 基础设施

- [ ] 🔴 **创建 Kubernetes 清单** (P3)
  - 创建 `k8s/` 目录
  - Deployment、Service、Ingress 配置
  - ConfigMaps 和 Secrets

- [ ] 🟡 **设置监控** (P2)
  - 添加 Prometheus 指标端点
  - 创建 Grafana 仪表板
  - **文件：** `backend/core/metrics.py`

- [ ] 🟡 **设置日志** (P2)
  - 结构化 JSON 日志
  - 日志聚合（ELK/Loki）
  - **文件：** `backend/core/logging.py`

### 环境管理

- [ ] 🟢 **创建环境模板** (P1)
  - `.env.development`
  - `.env.staging`
  - `.env.production`

- [ ] 🟢 **添加密钥管理** (P2)
  - 记录密钥轮换
  - 使用环境特定的密钥

---

## 🎯 未来增强功能

> **优先级：** P3 - 锦上添花

### AI/ML 改进

- [ ] 🔴 **微调评分模型** (P3)
  - 收集评分数据
  - 训练自定义模型
  - 与 GPT-4 进行 A/B 测试

- [ ] 🔴 **添加本地 LLM 支持** (P3)
  - 集成 llama.cpp
  - 支持 Ollama
  - 降低 API 成本

- [ ] 🟡 **改进抄袭检测** (P3)
  - 添加跨语言检测
  - 检测 AI 生成的内容
  - 与外部服务集成

### 功能

- [ ] 🟡 **添加课程管理** (P2)
  - 课程 CRUD
  - 注册管理
  - 课程分析

- [ ] 🟡 **添加通知系统** (P2)
  - 邮件通知
  - 应用内通知
  - 可配置的偏好设置

- [ ] 🟡 **添加分析仪表板** (P2)
  - 学生表现趋势
  - 作业难度分析
  - Q&A 主题聚类

- [ ] 🔴 **添加实时功能** (P3)
  - WebSocket 支持
  - 实时评分更新
  - 实时 Q&A

---

## 如何开始贡献

1. **选择一个任务** - 根据你的技能和兴趣从列表中选择
2. **检查依赖** - 某些任务需要先完成其他任务
3. **创建 issue** 或在现有 issue 上评论以认领任务
4. **从 `main` 创建功能分支**
5. **提交 PR** 并附带测试和文档

### 推荐给新贡献者的首选任务

| 任务 | 复杂度 | 所需技能 |
|------|--------|----------|
| 添加学生端点测试 | 🟢 简单 | Python, pytest |
| 创建贡献指南 | 🟢 简单 | Markdown |
| 添加 Toast 通知 | 🟢 简单 | React, TypeScript |
| 实现 React Router | 🟢 简单 | React |
| 添加 OpenAPI 描述 | 🟢 简单 | FastAPI |

---

## 有问题？

- 开一个 issue 寻求澄清
- 查看 `backend/README.md` 和 `README.md` 中的现有文档
- 开始之前先熟悉代码库结构

**祝贡献愉快！🎉**

