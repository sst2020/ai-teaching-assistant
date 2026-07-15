# 2026-05-07 技术栈重构执行计划

## Internal Grade

**XL** - 需要多步骤协调执行，涉及前端完整重写和基础设施变更

## Wave Structure

### Wave 1: 基础设施准备
1. **创建输出目录结构**
   - `outputs/runtime/vibe-sessions/` 治理文件
   
2. **备份现有前端**
   - 重命名 `frontend/` → `frontend-react-backup/`

3. **更新 docker-compose.yml**
   - 添加 RabbitMQ 服务
   - 准备新前端服务配置

### Wave 2: Vue 3 项目脚手架
1. **初始化 Vue 3 + Vite 项目**
   - 使用 `npm create vue@latest`
   - 选择 TypeScript、Pinia、Vue Router
   
2. **安装依赖**
   - Axios, Element Plus (UI库)
   - 开发依赖：TypeScript, ESLint, Prettier

3. **项目结构搭建**
   ```
   frontend-new/
   ├── src/
   │   ├── assets/        # 静态资源
   │   ├── components/    # 公共组件
   │   ├── views/         # 页面组件
 │   ├── stores/        # Pinia 状态
   │   ├── services/      # API 服务
   │   ├── composables/   # 组合式函数
   │   ├── router/        # 路由配置
   │   └── utils/         # 工具函数
   ├── public/
   └── package.json
   ```

### Wave 3: 核心基础设施迁移
1. **路由系统** (`src/router/index.ts`)
   - 映射所有 React Router 路由到 Vue Router
   - 实现路由守卫（认证、权限）

2. **状态管理** (`src/stores/`)
   - `auth.ts` - 认证状态（替换 AuthContext）
   - `theme.ts` - 主题状态
   - `toast.ts` - 通知状态

3. **API 服务层** (`src/services/`)
   - 迁移 `api.ts` 和 `authService.ts`
   - 保持 Axios 配置一致

4. **工具函数**
   - 迁移 `utils/` 目录内容

### Wave 4: 页面组件迁移（按优先级）

**Phase 4.1: 认证相关**
- [ ] `views/auth/Login.vue` ← `pages/Login.tsx`
- [ ] `views/auth/Register.vue` ← `pages/Register.tsx`
- [ ] `views/error/Forbidden.vue` ← `pages/Forbidden.tsx`

**Phase 4.2: 学生端页面**
- [ ] `views/student/Dashboard.vue` ← `pages/StudentDashboard.tsx`
- [ ] `views/student/Grades.vue` ← `pages/Grades.tsx`
- [ ] `views/student/SubmitAssignment.vue` ← `pages/SubmitAssignment.tsx`

**Phase 4.3: 教师端页面**
- [ ] `views/teacher/Dashboard.vue` ← `pages/TeacherDashboard.tsx`
- [ ] `views/teacher/ManageAssignments.vue` ← `pages/ManageAssignments.tsx`
- [ ] `views/teacher/GradingInterface.vue` ← `pages/GradingInterface.tsx`
- [ ] `views/teacher/QuestionQueue.vue` ← `components/TeacherDashboard/TeacherDashboard.tsx`

**Phase 4.4: 公共功能页面**
- [ ] `views/common/Account.vue` ← `pages/Account.tsx`
- [ ] `views/common/SmartQA.vue` ← `components/QATriage/QATriage.tsx`
- [ ] `views/common/KnowledgeBase.vue` ← `components/KnowledgeBase/KnowledgeBase.tsx`

**Phase 4.5: 高级功能页面**
- [ ] `views/features/CodeAnalysis.vue` ← `components/CodeAnalysis/CodeAnalysis.tsx`
- [ ] `views/features/QAInterface.vue` ← `components/QAInterface/QAInterface.tsx`
- [ ] `views/features/PlagiarismCheck.vue` ← `components/PlagiarismCheck/PlagiarismCheck.tsx`
- [ ] `views/features/ReportAnalysis.vue` ← `components/ReportAnalysis/ReportAnalysis.tsx`

**Phase 4.6: 开发工具**
- [ ] `views/dev/ApiTester.vue` ← `components/DevTools/ApiTester.tsx`
- [ ] `views/dev/PerformanceMonitor.vue` ← `components/DevTools/PerformanceMonitor.tsx`

### Wave 5: 共享组件迁移
- [ ] `components/layout/Header.vue` ← `components/layout/Header/Header.tsx`
- [ ] `components/layout/Sidebar.vue` （如需要）
- [ ] `components/common/ErrorBoundary.vue` ← `components/common/ErrorBoundary.tsx`
- [ ] `components/common/ProtectedRoute.vue` - 路由守卫替代
- [ ] `components/common/DebugPanel.vue` ← `components/common/DebugPanel.tsx`

### Wave 6: 后端消息队列集成
1. **添加依赖**
   - `aio-pika` (RabbitMQ 异步客户端)

2. **创建消息队列模块**
   - `core/messaging/` 目录
   - `connection.py` - 连接管理
   - `publisher.py` - 消息发布
   - `consumer.py` - 消息消费

3. **实现异步任务示例**
   - `services/task_queue.py` - 任务队列服务
   - 集成到批量作业提交流程

4. **API 端点增强**
   - 添加 `/api/v1/tasks/status/{task_id}` 查询异步任务状态

### Wave 7: 集成与验证
1. **Docker 配置**
   - 更新 `frontend/Dockerfile`
   - 验证 docker-compose 全栈启动

2. **构建验证**
   - 前端生产构建 `npm run build`
   - 后端启动验证

3. **功能验证**
   - 登录/注册流程
   - 学生作业提交流程
   - 教师批改流程
   - 消息队列任务执行

### Wave 8: 清理与交付
1. **删除备份**
   - 删除 `frontend-react-backup/`

2. **更新文档**
   - 更新 `README.md`
   - 更新 `DEVELOPMENT_SETUP.md`

3. **生成验证报告**
   - 功能对照表
   - 已知问题清单（如有）

## Verification Commands

```bash
# 1. 启动完整环境
docker-compose up -d

# 2. 验证 RabbitMQ 健康
curl http://localhost:15672/api/health  # 管理界面

# 3. 前端构建验证
cd frontend && npm install && npm run build

# 4. 后端健康检查
curl http://localhost:8000/health

# 5. API 测试
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <token>"
```

## Completion Language Rules

- ✅ "Vue 3 前端项目已创建并运行"
- ✅ "所有页面组件已迁移完成"
- ✅ "RabbitMQ 已集成并运行"
- ✅ "Docker 构建验证通过"
- ❌ 不使用 "重构完成" 等模糊表述

## Rollback Rules

- 每个 Wave 完成时检查点，失败可回滚到上一 Wave
- 保留备份直至最终验收完成

## Ownership Boundaries

- **本计划**: 前端迁移 + 消息队列基础设施
- **不涉及**: 后端业务逻辑变更、数据库 Schema 变更
