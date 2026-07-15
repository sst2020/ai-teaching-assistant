# 技术栈重构验证清单

## 启动验证步骤

### 1. Docker 环境启动
```bash
docker-compose up -d
```

验证服务状态:
- [ ] MySQL (localhost:3306)
- [ ] Redis (localhost:6379)
- [ ] RabbitMQ (localhost:5672 / 管理界面 15672)
- [ ] Backend (localhost:8080)  **注意：后端端口已改为 8080，避免与 8000 端口冲突**
- [ ] Frontend (localhost:3000)

### 2. RabbitMQ 验证
访问 http://localhost:15672 (默认账号: ai_ta / ai_ta_dev)
- [ ] 管理界面可访问
- [ ] 队列 `task_queue` 已创建
- [ ] Exchange `ai_ta_exchange` 已创建

### 3. 前端开发模式
```bash
cd frontend
npm run dev
```
- [ ] Vite 服务器启动成功 (http://localhost:3000)
- [ ] 无编译错误
- [ ] 页面可正常加载

### 4. 前端生产构建
```bash
cd frontend
npm run build
```
- [ ] 构建成功完成
- [ ] `dist/` 目录生成

### 5. 后端 API 验证
```bash
# 健康检查
curl http://localhost:8080/health

# API 文档
curl http://localhost:8080/docs

# 任务队列 API
curl http://localhost:8080/api/v1/tasks/status/test-id
```

### 6. 功能验证

#### 认证流程
- [ ] 注册新用户
- [ ] 用户登录
- [ ] Token 刷新
- [ ] 登出

#### 角色权限
- [ ] 学生访问 Dashboard
- [ ] 学生提交作业
- [ ] 教师访问 Dashboard
- [ ] 教师创建作业
- [ ] 教师批改作业
- [ ] 403 页面权限拦截

#### 消息队列任务
- [ ] 提交自动批改任务
- [ ] 提交抄袭检测任务
- [ ] 提交批量批改任务
- [ ] 查询任务状态

## 文件清单

### 新增/修改的文件

#### 前端 (Vue 3)
```
frontend/
├── package.json              [新]
├── tsconfig.json           [新]
├── vite.config.ts          [新]
├── Dockerfile              [新]
├── nginx.conf              [新]
├── .eslintrc.cjs           [新]
├── src/
│   ├── main.ts             [新]
│   ├── App.vue             [新]
│   ├── router/index.ts     [新]
│   ├── stores/
│   │   ├── auth.ts         [新]
│   │   ├── toast.ts        [新]
│   │   └── theme.ts        [新]
│   ├── services/api.ts     [新]
│   ├── types/index.ts      [新]
│   ├── components/
│   │   ├── layout/AppHeader.vue    [新]
│   │   └── common/ToastContainer.vue [新]
│   └── views/
│       ├── auth/
│       │   ├── LoginView.vue       [新]
│       │   └── RegisterView.vue    [新]
│       ├── student/
│       │   ├── DashboardView.vue   [新]
│       │   ├── GradesView.vue      [新]
│       │   └── SubmitAssignmentView.vue [新]
│       ├── teacher/
│       │   ├── DashboardView.vue   [新]
│       │   ├── ManageAssignmentsView.vue [新]
│       │   ├── GradingView.vue     [新]
│       │   └── QuestionQueueView.vue [新]
│       ├── features/
│       │   ├── SmartQAView.vue     [新]
│       │   ├── KnowledgeBaseView.vue [新]
│       │   ├── CodeAnalysisView.vue [新]
│       │   ├── QAInterfaceView.vue  [新]
│       │   ├── PlagiarismView.vue   [新]
│       │   └── ReportAnalysisView.vue [新]
│       ├── common/
│       │   └── AccountView.vue     [新]
│       ├── dev/
│       │   ├── ApiTesterView.vue   [新]
│       │   └── PerformanceMonitorView.vue [新]
│       └── error/
│           └── ForbiddenView.vue   [新]
```

#### 后端 (FastAPI + RabbitMQ)
```
backend/
├── requirements.txt          [修改 - 添加 aio-pika]
├── core/messaging/
│   ├── __init__.py           [新]
│   ├── connection.py         [新]
│   ├── publisher.py          [新]
│   └── consumer.py           [新]
├── services/
│   └── task_processor.py     [新]
├── api/
│   └── tasks.py              [新]
└── app/main.py               [修改 - 添加 RabbitMQ 生命周期管理]
```

#### Docker 配置
```
├── docker-compose.yml        [修改 - 添加 RabbitMQ 服务]
```

## 问题排查

### 前端依赖错误
如果 IDE 显示 `找不到模块` 错误:
1. 确保已运行 `npm install`
2. 重启 IDE/TypeScript 服务
3. 检查 `node_modules` 是否存在

### RabbitMQ 连接失败
后端启动时如果 RabbitMQ 连接失败:
1. 检查 RabbitMQ 服务是否运行: `docker-compose ps`
2. 检查端口是否被占用: `netstat -an | findstr 5672`
3. 查看 RabbitMQ 日志: `docker logs ai-ta-rabbitmq`

### 构建失败
如果前端构建失败:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 技术栈对照

| 组件 | 旧技术栈 | 新技术栈 |
|-----|---------|---------|
| 前端框架 | React 19 (CRA) | Vue 3.4+ (Vite) |
| 构建工具 | react-scripts | Vite 5 |
| 状态管理 | React Context | Pinia |
| UI 库 | 自定义/CSS | Element Plus |
| HTTP 客户端 | Axios | Axios |
| 后端框架 | FastAPI | FastAPI (保持) |
| 数据库 | MySQL | MySQL (保持) |
| 消息队列 | 无 | RabbitMQ |
| 缓存 | Redis | Redis (保持) |
