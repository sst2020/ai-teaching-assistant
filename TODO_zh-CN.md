# AI 智能教学助手 - 项目待办事项清单

> **最后更新：** 2026年1月25日
> **项目状态：** MVP 已完成 ✅ + 增强调试环境 ✅ + 生产级 JWT 认证 ✅ + 认证监控 ✅ + Redis Cache ✅ + Grading API ✅ + 报告分析 DeepSeek 集成 ✅
> **复杂度指标：** 🟢 简单 | 🟡 中等 | 🔴 困难 | ⏱️ 耗时较长

本文档概述了 AI 智能教学助手项目的剩余任务、优先级和贡献机会。

## 🎉 MVP 状态

最小可行产品（MVP）已完成，包含以下核心功能：
- ✅ 用户认证（登录、注册、登出）
- ✅ **生产级 JWT 认证系统** (新增 - 2024年12月13日)
  - ✅ Bcrypt 密码哈希
  - ✅ JWT token 生成和验证
  - ✅ Refresh token 轮换
  - ✅ Token 黑名单机制
  - ✅ 基于角色的访问控制
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
- 📄 [认证测试结果](backend/TEST_RESULTS.md) (新增)

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
> **最后更新：** 2024年12月

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

### 增强代码分析系统 ✅

> **完成时间：** 2024年12月

#### 任务 2.1.1：高级代码质量分析 ✅

- [x] 🟡 **CodeQualityAnalyzer** - `backend/services/code_analyzer.py`
  - 使用 `radon` 库计算圈复杂度
  - 使用 AST 访问者模式检测认知复杂度
  - 使用 AST 规范化检测代码重复
  - 可维护性指数计算（A-F 评级）
  - 函数级复杂度指标

- [x] 🟢 **分析模式** - `backend/schemas/analysis.py`
  - 所有分析类型的 Pydantic 模型
  - 枚举：ComplexityGrade、MaintainabilityRating、IssueSeverity、SecuritySeverity、PerformanceIssueType
  - 质量、规范、安全、性能和综合分析的请求/响应模型

#### 任务 2.1.2：编程规范检查器 ✅

- [x] 🟡 **LinterService** - `backend/services/linter.py`
  - Pylint 集成用于 Python 代码检查
  - 可配置的规则系统
  - 200+ 条 Pylint 消息的中文翻译
  - 常见问题的修复建议

#### 任务 2.1.3：性能与安全分析 ✅

- [x] 🟡 **SecurityAnalyzer** - `backend/services/security_analyzer.py`
  - Bandit 集成用于安全扫描
  - Bandit 不可用时的回退模式匹配
  - 安全问题的中文翻译
  - 基于严重性的评分

- [x] 🟡 **PerformanceAnalyzer** - `backend/services/security_analyzer.py`
  - 性能反模式检测（嵌套循环、内存问题、阻塞操作）
  - 最佳实践评估系统
  - 所有建议的中文翻译

- [x] 🟢 **分析 API 端点** - `backend/api/analysis.py`
  - `POST /api/v1/analysis/quality` - 代码质量分析
  - `POST /api/v1/analysis/lint` - 编程规范检查
  - `POST /api/v1/analysis/security` - 安全漏洞分析
  - `POST /api/v1/analysis/performance` - 性能分析
  - `POST /api/v1/analysis/comprehensive` - 综合分析（包含以上所有）

- [x] 🟢 **测试** - `backend/tests/test_advanced_analysis.py`
  - 25 个全面的分析服务测试
  - CodeQualityAnalyzer、LinterService、SecurityAnalyzer、PerformanceAnalyzer 测试
  - 综合分析的集成测试

### 智能评语系统增强 ✅

> **完成时间：** 2024年12月

#### 任务 2.2.1：个性化评语生成 ✅

- [x] 🟡 **增强的 FeedbackGenerationService** - `backend/services/feedback_service.py`
  - 学生历史分析（趋势检测、水平判定）
  - 表现趋势计算（进步、退步、稳定）
  - 学生水平判定（初学者、中级、高级）
  - 改进速度计算
  - 基于历史的个性化消息生成
  - 渐进式建议（带难度等级）
  - 学习路径创建（带预估时间）
  - 所有反馈的中文翻译支持

- [x] 🟢 **个性化反馈 Schemas** - `backend/schemas/feedback.py`
  - StudentLevel、PerformanceTrend、SuggestionDifficulty、FeedbackDetailLevel 枚举
  - StudentHistoryAnalysis、PersonalizedFeedbackRequest、PersonalizedFeedbackResponse 模型
  - ProgressiveSuggestion、LearningPathItem 模型

- [x] 🟢 **个性化反馈 API** - `backend/api/personalized_feedback.py`
  - `POST /api/v1/personalized-feedback/generate` - 生成个性化反馈
  - `GET /api/v1/personalized-feedback/history/{student_id}` - 获取学生历史分析
  - `GET /api/v1/personalized-feedback/learning-path/{student_id}` - 获取学习路径

- [x] 🟢 **测试** - `backend/tests/test_personalized_feedback.py`
  - 36 个个性化反馈生成的全面测试

#### 任务 2.2.2：多维度评价系统 ✅

- [x] 🟡 **MultiDimensionalEvaluator** - `backend/services/multi_dimensional_evaluator.py`
  - 6 个评价维度：正确性、效率、可读性、结构、最佳实践、文档
  - 雷达图数据生成（用于可视化）
  - 班级对比统计（百分位、排名、平均分）
  - 维度特定反馈生成
  - 所有评价的中文翻译

- [x] 🟢 **评价 Schemas** - `backend/schemas/evaluation.py`
  - EvaluationDimension 枚举
  - DimensionScore、RadarChartData、ClassComparisonStats 模型
  - MultiDimensionalEvaluationRequest、MultiDimensionalEvaluationResponse 模型

- [x] 🟢 **评价 API** - `backend/api/evaluation.py`
  - `POST /api/v1/evaluation/multi-dimensional` - 多维度评价
  - `GET /api/v1/evaluation/radar-chart/{submission_id}` - 获取雷达图数据
  - `GET /api/v1/evaluation/class-comparison/{student_id}` - 获取班级对比

- [x] 🟢 **测试** - `backend/tests/test_multi_dimensional_evaluation.py`
  - 25 个多维度评价的全面测试

### 生产级 JWT 认证系统 ✅

> **完成时间：** 2024年12月13日

#### 核心认证基础设施 ✅

- [x] 🔴 **独立 User 模型** - `backend/models/user.py`
  - 基于邮箱的认证，带唯一约束
  - 使用 bcrypt 进行密码哈希（成本因子 12）
  - 基于角色的访问控制（学生、教师、管理员）
  - 用户激活状态跟踪
  - 最后登录时间戳跟踪
  - 与 Student 模型的一对一关系

- [x] 🟡 **安全工具** - `backend/core/security.py`
  - Bcrypt 密码哈希和验证（处理 72 字节限制）
  - 使用 HS256 算法生成 JWT token
  - Token 验证和过期检查
  - JTI（JWT ID）提取用于黑名单
  - OAuth2 密码承载配置

- [x] 🟡 **Token 管理模型**
  - **RefreshToken** (`backend/models/refresh_token.py`)：7 天过期，支持轮换
  - **TokenBlacklist** (`backend/models/token_blacklist.py`)：失效 token 跟踪

- [x] 🟢 **认证 Schemas** - `backend/schemas/auth.py`
  - RegisterRequest 带密码验证（最少 8 个字符，字母数字）
  - LoginRequest、LoginResponse 带嵌套 token 结构
  - UserResponse、TokenRefreshRequest、ChangePasswordRequest
  - 全面的 Pydantic 验证

- [x] 🟡 **CRUD 操作** - `backend/utils/crud.py`
  - CRUDUser：get_by_email、create、authenticate、update_last_login、change_password
  - CRUDRefreshToken：create、get_valid_token、revoke、revoke_all_for_user
  - CRUDTokenBlacklist：add_token、is_blacklisted、cleanup_expired

- [x] 🟡 **依赖注入** - `backend/core/dependencies.py`
  - get_current_user：JWT 验证和用户检索
  - get_current_active_user：活跃用户验证
  - require_role：基于角色的访问控制装饰器
  - Token 黑名单检查

#### 认证 API 端点 ✅

- [x] 🔴 **7 个生产就绪端点** - `backend/api/auth.py`
  1. **POST /auth/register** - 用户注册并自动创建 Student
  2. **POST /auth/login** - 登录并获取 JWT tokens（access + refresh）
  3. **GET /auth/me** - 获取当前认证用户
  4. **POST /auth/refresh** - 刷新 access token 并轮换
  5. **POST /auth/change-password** - 修改密码并撤销所有会话
  6. **POST /auth/logout** - 登出并将当前 token 加入黑名单
  7. **POST /auth/revoke-all** - 撤销用户的所有 refresh tokens

#### 数据库迁移 ✅

- [x] 🟢 **生产认证迁移** - `backend/alembic/versions/20251213_000000_add_production_auth_system.py`
  - 创建 users 表，在 email 上建立索引
  - 创建 refresh_tokens 表，带 user_id 外键
  - 创建 token_blacklist 表，在 jti 上建立索引
  - 向 students 表添加 user_id 列
  - 使用 SQLite batch 模式进行 ALTER TABLE 操作

#### 安全特性 ✅

- [x] 🟢 **密码安全**
  - 使用成本因子 12 的 Bcrypt 哈希
  - 处理 72 字节密码长度限制
  - 密码强度验证（最少 8 个字符，字母数字）

- [x] 🟢 **Token 安全**
  - 使用 HS256 算法的标准 JWT
  - Access token：30 分钟过期
  - Refresh token：7 天过期
  - 登出时的 token 黑名单
  - Refresh token 轮换（一次性使用）
  - 基于 JTI 的 token 跟踪

- [x] 🟢 **访问控制**
  - 基于角色的权限（学生、教师、管理员）
  - 用户激活状态检查
  - 受保护路由依赖

#### 测试与验证 ✅

- [x] 🟡 **综合测试套件** - `backend/test_auth_api.py`
  - 12 个测试场景，100% 通过率
  - 用户注册和登录测试
  - Token 刷新和轮换测试
  - 密码修改和安全测试
  - Token 黑名单和撤销测试
  - 错误处理测试（无效凭据、重复邮箱）
  - **测试报告：** `backend/TEST_RESULTS.md`

- [x] 🟢 **测试期间的 Bug 修复**
  - 修复导入路径（backend.* → 相对导入）
  - 修复 bcrypt 兼容性（passlib → 直接使用 bcrypt）
  - 修复 SQLAlchemy 延迟加载（添加 db.refresh）
  - 修复 CRUD 参数类型（Pydantic → dict）

### 前后端协同调试环境 ✅

> **完成时间：** 2024年12月

#### 增强调试环境 + 一键启动系统 ✅

- [x] 🟡 **环境检查脚本** - `scripts/check-environment.js`
  - 自动化 Node.js、Python 和依赖验证
  - 彩色控制台输出和全面的系统检查
  - 跨平台兼容性检测

- [x] 🟢 **增强环境配置** - `frontend/.env`, `backend/.env`
  - 前端调试设置：DEBUG_MODE、API_LOGGING、PERFORMANCE_MONITORING
  - 后端调试设置：REQUEST_LOGGING、CORS 配置、LOG_LEVEL
  - 开发环境优化的环境变量

- [x] 🟡 **增强API客户端调试功能** - `frontend/src/services/api.ts`
  - 详细日志记录的请求/响应拦截器
  - 性能计时和请求ID关联
  - 错误分类和会话存储集成
  - Axios 元数据的 TypeScript 模块声明

- [x] 🟡 **实时调试面板** - `frontend/src/components/common/DebugPanel.tsx`
  - 带性能指标的实时API调用监控
  - 错误跟踪和分类
  - 响应式设计的选项卡界面
  - 持久化调试数据的会话存储集成

- [x] 🟡 **高级后端日志系统** - `backend/utils/logger.py`, `backend/app/main.py`
  - 带请求关联的彩色控制台格式化器
  - 带计时指标的性能监控
  - 带上下文变量的结构化日志
  - 详细跟踪的请求/响应中间件

- [x] 🟡 **一键启动系统** - `scripts/dev-start.js`, `dev-start.bat`, `dev-start.sh`
  - 并行前后端服务启动
  - 自动浏览器打开和健康检查
  - 跨平台支持（Windows/Unix）
  - 优雅关闭和进程管理

- [x] 🟢 **开发文档** - `docs/DEVELOPMENT_SETUP.md`
  - 带故障排除的全面设置指南
  - 功能概述和使用说明
  - 系统要求和配置详情

#### 任务 2.2.3：扩展反馈模板库 ✅

- [x] 🟡 **扩展模板** - `backend/scripts/seed_feedback_templates.py`
  - 从 29 个扩展到 103 个模板
  - 语言特定模板：Python (10)、JavaScript/TypeScript (10)、Java (7)、C++ (7)
  - 性能模板 (8)
  - 错误处理模板 (7)
  - 测试模板 (5)
  - 算法模板 (5)
  - 语气变体：鼓励型 (4)、严格/专业型 (4)
  - 中文本地化模板 (12)

- [x] 🟢 **增强的模板模型** - `backend/models/feedback_template.py`
  - 添加 TemplateTone 枚举（NEUTRAL、ENCOURAGING、STRICT、PROFESSIONAL）
  - 添加新分类：PERFORMANCE、ERROR_HANDLING、TESTING、ALGORITHM
  - 添加 `tone` 和 `locale` 字段（带索引）

- [x] 🟢 **增强的模板 API** - `backend/api/feedback_templates.py`
  - `POST /api/v1/feedback-templates/search` - 高级搜索（多条件过滤）
  - `GET /api/v1/feedback-templates/tones/list` - 列出可用语气
  - `GET /api/v1/feedback-templates/stats/summary` - 模板统计
  - 增强的列表端点（支持语气、本地化和排序过滤）

### 查重与原创性分析系统 ✅

> **完成时间：** 2024年12月
> **任务文档：** `issues/plagiarism-detection-system.md`

#### 任务 2.3.1：代码相似度检测 ✅

- [x] 🟡 **相似度算法服务** - `backend/services/similarity_algorithms.py`
  - 编辑距离算法（Levenshtein）用于文本相似度
  - 余弦相似度（TF-IDF）用于语义比较
  - 基于 AST 的结构相似度分析
  - Token 序列相似度检测
  - 变量/函数重命名检测
  - 代码重构检测

- [x] 🟡 **增强的查重服务** - `backend/services/plagiarism_service.py`
  - 多算法相似度计算
  - 相似度矩阵生成
  - 原创性报告生成
  - 可配置的检测设置

- [x] 🟢 **查重 Schemas** - `backend/schemas/plagiarism.py`
  - SimilarityAlgorithm、CodeTransformationType 枚举
  - DetailedCodeMatch、SimilarityMatrixEntry、SimilarityMatrix 模型
  - OriginalityReport、BatchAnalysisRequest、BatchAnalysisResponse 模型
  - PlagiarismSettings 用于可配置阈值

#### 任务 2.3.2：批量查重引擎 ✅

- [x] 🟡 **批量分析 API** - `backend/api/assignments.py`
  - `POST /plagiarism/batch-analyze` - 批量相似度分析
  - `GET /plagiarism/originality-report/{submission_id}` - 获取原创性报告
  - `PUT /plagiarism/settings` - 更新检测设置
  - `GET /plagiarism/settings` - 获取当前设置

#### 任务 2.3.3：原创性报告生成 ✅

- [x] 🟢 **前端组件** - `frontend/src/components/PlagiarismCheck/`
  - `BatchUpload.tsx` - 拖拽多文件上传
  - `SimilarityMatrix.tsx` - 使用 recharts 的热力图可视化
  - `RelationshipGraph.tsx` - 相似度关系的节点-边图
  - `SuspiciousList.tsx` - 可排序/筛选的可疑提交表格
  - `OriginalityReport.tsx` - 带代码对比的评分仪表盘
  - `PlagiarismCheck.tsx` - 整合所有子组件的主组件

- [x] 🟢 **前端类型** - `frontend/src/types/plagiarism.ts`
  - 与后端 schemas 对应的 TypeScript 类型定义

- [x] 🟢 **前端 API** - `frontend/src/services/api.ts`
  - `batchAnalyzePlagiarism()` - 批量分析 API 调用
  - `getOriginalityReport()` - 获取原创性报告
  - `getPlagiarismSettings()` / `updatePlagiarismSettings()` - 设置管理

- [x] 🟢 **路由集成** - `frontend/src/App.tsx`、`frontend/src/components/layout/Header.tsx`
  - 添加 `/plagiarism` 路由
  - 添加 "🔍 查重分析" 导航链接

#### 剩余设置步骤

- [x] 🟢 **运行数据库迁移** (P0) ✅ 2025-12-15
  ```bash
  cd backend
  python -m alembic revision --autogenerate -m "Add feedback_templates and ai_interactions tables"
  python -m alembic upgrade head
  ```

- [x] 🟢 **填充反馈模板** (P0) ✅ 2025-12-15
  ```bash
  cd backend
  python -m scripts.seed_feedback_templates
  ```
  > 已成功填充 103 个反馈模板

- [ ] 🟢 **配置 OPENAI_API_KEY**（可选）
  - 在 `.env` 文件中设置 `OPENAI_API_KEY` 以启用 AI 功能
  - 没有 API 密钥时，系统使用本地回退响应

- [x] 🟢 **运行反馈系统测试** (P1) ✅ 2025-12-22
  ```bash
  cd backend
  python -m pytest tests/test_feedback_system.py -v
  ```
  > 修复了所有 22 个测试，包括 schema 字段补全和测试 API 更新

---

## 🔐 安全与认证

> **状态：** 生产环境已完成 ✅
> **优先级：** P1 - 建议增强 RBAC
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

### 生产环境认证 ✅

> **完成时间：** 2024年12月13日

- [x] 🔴 **实现带数据库存储的生产 JWT** (P0) ✅
  - ✅ 创建了独立的 User 模型，包含 email、password_hash、role、is_active
  - ✅ 实现了 bcrypt 密码哈希（成本因子 12）
  - ✅ 实现了 JWT token 生成和验证（HS256，python-jose）
  - ✅ 实现了登出时的 token 黑名单
  - ✅ 实现了 refresh token 轮换机制
  - ✅ 创建了 3 个新模型：User、RefreshToken、TokenBlacklist
  - ✅ 创建了数据库迁移（20251213_000000_add_production_auth_system）
  - **验收标准：**
    - ✅ Access tokens 在 30 分钟后过期
    - ✅ Refresh tokens 在 7 天后过期
    - ✅ 每次刷新时轮换 refresh token
    - ✅ 使用 bcrypt 安全存储密码
    - ✅ Token 黑名单机制正常工作
  - **创建的文件：**
    - `backend/core/security.py` - 密码哈希和 JWT 工具
    - `backend/models/user.py` - User 模型
    - `backend/models/refresh_token.py` - RefreshToken 模型
    - `backend/models/token_blacklist.py` - TokenBlacklist 模型
    - `backend/schemas/auth.py` - 认证 schemas
    - `backend/core/dependencies.py` - 依赖注入函数
  - **修改的文件：**
    - `backend/models/student.py` - 添加了 user_id 外键
    - `backend/utils/crud.py` - 添加了 User、RefreshToken、TokenBlacklist 的 CRUD 类
    - `backend/core/config.py` - 添加了 JWT 配置
    - `backend/api/auth.py` - 完全重写，包含 7 个端点

- [x] 🟡 **为 Student 模型添加密码字段** (P1) ✅
  - ✅ 创建了独立的 User 模型而不是修改 Student
  - ✅ 向 Student 模型添加了 user_id 外键
  - ✅ 创建了 Alembic 迁移
  - ✅ 更新了注册端点以使用 bcrypt 哈希密码
  - **文件：** `backend/models/student.py`, `backend/models/user.py`

- [x] 🟢 **实现 7 个认证 API 端点** (P0) ✅
  - ✅ POST /api/v1/auth/register - 用户注册并自动创建 Student
  - ✅ POST /api/v1/auth/login - 登录并生成 JWT token
  - ✅ GET /api/v1/auth/me - 获取当前用户信息
  - ✅ POST /api/v1/auth/refresh - 刷新 access token 并轮换
  - ✅ POST /api/v1/auth/change-password - 修改密码并撤销所有 tokens
  - ✅ POST /api/v1/auth/logout - 登出并将 token 加入黑名单
  - ✅ POST /api/v1/auth/revoke-all - 撤销所有 refresh tokens
  - **测试：** 所有 12 个测试场景通过（100% 成功率）
  - **测试报告：** `backend/TEST_RESULTS.md`

### 前端集成 ✅

> **完成时间：** 2024年12月14日

- [x] 🟡 **更新前端类型定义** (P1) ✅
  - ✅ 更新 `User` 接口,添加生产环境字段（is_active、last_login、updated_at）
  - ✅ 修复 `RegisterResponse`,添加 tokens 字段
  - ✅ 添加 `RefreshTokenResponse`、`ChangePasswordRequest`、`ChangePasswordResponse`、`RevokeAllTokensResponse`
  - **文件：** `frontend/src/types/auth.ts`

- [x] 🟡 **更新 API 服务** (P1) ✅
  - ✅ 更新 `refreshToken` 函数以处理新的响应结构
  - ✅ 添加 `changePassword` API 函数
  - ✅ 添加 `revokeAllTokens` API 函数
  - **文件：** `frontend/src/services/api.ts`

- [x] 🔴 **更新 AuthContext** (P1) ✅
  - ✅ 更新 `register` 函数,直接使用注册响应中的 tokens
  - ✅ 更新 `logout` 函数,调用后端 API 将 token 加入黑名单
  - ✅ 更新 `refreshToken` 函数以处理新的响应结构
  - ✅ 实现自动 token 刷新机制（过期前 5 分钟自动刷新）
  - ✅ 添加 `changePassword` 方法
  - ✅ 添加 `revokeAllTokens` 方法
  - **文件：** `frontend/src/contexts/AuthContext.tsx`

### 认证监控与日志 ✅

> **完成时间：** 2024年12月14日

- [x] 🔴 **实现认证事件日志记录** (P1) ✅
  - ✅ 创建 `AuthLog` 模型用于跟踪所有认证事件
  - ✅ 事件类型：login、logout、register、token_refresh、password_change、token_revoke、login_failed
  - ✅ 跟踪：user_id、email、event_type、status、ip_address、user_agent、failure_reason、extra_data
  - ✅ 优化查询性能的索引
  - **文件：** `backend/models/auth_log.py`

- [x] 🔴 **实现认证监控服务** (P1) ✅
  - ✅ 创建 `AuthMonitorService` 用于检测可疑活动
  - ✅ 账户锁定机制（5次失败尝试 = 锁定15分钟）
  - ✅ 可疑活动检测（多个IP、过度尝试）
  - ✅ 将日志集成到所有认证端点
  - **文件：** `backend/services/auth_monitor.py`

- [x] 🟡 **更新认证端点添加日志记录** (P1) ✅
  - ✅ 添加 IP 地址和 User-Agent 提取辅助函数
  - ✅ 将日志集成到 register 端点
  - ✅ 将日志集成到 login 端点,包含锁定检查
  - ✅ 将日志集成到 refresh 端点
  - ✅ 将日志集成到 logout 端点
  - ✅ 将日志集成到 change-password 端点
  - ✅ 将日志集成到 revoke-all 端点
  - **文件：** `backend/api/auth.py`

- [x] 🟢 **创建数据库迁移** (P1) ✅
  - ✅ 为 auth_logs 表创建迁移
  - ✅ MySQL 兼容的迁移脚本
  - ✅ 成功创建所有索引
  - **文件：** `backend/alembic/versions/20251214_000000_add_auth_log_model.py`

- [x] 🟢 **测试和验证** (P1) ✅
  - ✅ 测试所有认证事件日志记录
  - ✅ 验证账户锁定机制（5次尝试,15分钟锁定）
  - ✅ 验证 IP 地址和 User-Agent 跟踪
  - ✅ 验证数据库架构和索引
  - **测试结果：** 所有监控功能正常工作

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

- [x] 🟡 **添加深色模式支持** (P3) ✅ 已完成
  - ✅ 创建 `frontend/src/contexts/ThemeContext.tsx` (主题上下文)
  - ✅ 头部主题切换按钮
  - ✅ 持久化偏好设置 (localStorage)
  - ✅ CSS 变量主题切换支持

### 开发工具增强

- [x] 🟡 **创建API测试工具页面** (P2) ✅ 已完成
  - ✅ 创建 `frontend/src/components/DevTools/ApiTester.tsx`
  - ✅ 在线API测试和请求构建器
  - ✅ 响应查看器和历史记录
  - ✅ 路由: `/api-tester`
  - **文件：** `frontend/src/components/DevTools/ApiTester.tsx`

- [ ] 🟡 **添加性能监控组件** (P2)
  - 创建 `frontend/src/components/DevTools/PerformanceMonitor.tsx`
  - 实时API响应时间监控
  - 内存使用和渲染性能跟踪
  - **文件：** `frontend/src/components/DevTools/PerformanceMonitor.tsx`

- [ ] 🟢 **增强错误边界组件** (P2)
  - 升级 `frontend/src/components/common/ErrorBoundary.tsx`
  - 添加错误报告和重试机制
  - 调试信息显示
  - **文件：** `frontend/src/components/common/ErrorBoundary.tsx`

- [ ] 🟢 **添加服务健康检查自动化** (P2)
  - 创建 `scripts/health-check.js`
  - 定期前后端服务状态检查
  - 失败时自动服务重启
  - **文件：** `scripts/health-check.js`

- [ ] 🟢 **优化package.json脚本** (P2)
  - 更新 `frontend/package.json` 和根目录 `package.json`
  - 添加调试相关的npm脚本
  - 标准化开发命令
  - **文件：** `frontend/package.json`, `package.json`

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

- [x] 🟢 **添加 OpenAPI 描述** (P2) ✅ 已完成
  - ✅ 为所有端点添加详细中文描述
  - ✅ 添加请求/响应示例
  - **已增强文件：**
    - `backend/api/health.py`
    - `backend/api/knowledge_base.py`
    - `backend/api/report_analysis.py`
    - `backend/api/students.py`
    - `backend/api/submissions.py`

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

- [x] 🟡 **查重与原创性分析系统** (P1) ✅ 2024年12月
  - ✅ 多算法相似度检测（AST、编辑距离、余弦相似度、Token）
  - ✅ 批量分析和相似度矩阵
  - ✅ 原创性报告生成
  - ✅ 前端可视化（热力图、关系图）
  - **未来增强：**
    - [ ] 添加跨语言检测
    - [ ] 检测 AI 生成的内容
    - [ ] 与外部服务集成（Moss 等）

### 功能

- [x] 🟡 **Q&A 系统持久化与分析** (P1) ✅ 2024年12月
  - ✅ 将问答记录持久化到数据库（QALog 模型）
  - ✅ 学生提问历史跟踪（`GET /qa/history/{student_id}`）
  - ✅ 知识薄弱点分析与报告（`GET /qa/weakness/{student_id}`）
  - ✅ 智能问答与分诊（`POST /qa/smart-ask`）
  - ✅ 问答统计（`GET /qa/stats`）
  - **文件：** `backend/models/qa_log.py`、`backend/api/qa.py`、`backend/services/qa_service.py`

- [x] 🟡 **项目报告智能分析** (P2) ✅ 2024年12月
  - ✅ 分析学生项目报告（PDF、DOCX、Markdown）
  - ✅ 评估完整性和创新性
  - ✅ 生成改进建议
  - ✅ 批量分析支持（`POST /analysis/report/batch-analyze`）
  - **文件：** `backend/services/report_analysis_service.py`、`backend/api/analysis.py`
  - **Schemas：** `backend/schemas/report_analysis.py`

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

