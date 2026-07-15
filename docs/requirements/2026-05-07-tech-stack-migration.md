# 2026-05-07 技术栈重构需求文档

## Summary

将 AI Teaching Assistant 项目的技术栈进行重构：后端保持 FastAPI，前端从 React 迁移至 Vue 3，数据库保持 MySQL，新增 Kafka/RabbitMQ 消息队列支持。

## Goal

完成前端框架迁移和消息队列基础设施集成，确保功能等价迁移，系统可正常构建和运行。

## Deliverable

1. **Vue 3 前端项目**
   - 使用 Vue 3 + TypeScript + Vite
   - 使用 Pinia 状态管理
   - 使用 Vue Router 路由管理
   - 使用 Axios 与后端通信
   - 完整迁移现有页面和组件功能

2. **消息队列基础设施**
   - docker-compose 新增 Kafka 或 RabbitMQ 服务
   - FastAPI 后端集成消息队列客户端
   - 实现异步任务处理示例（如批量作业评分、 plagiarism 检测任务队列）

3. **构建和部署配置**
   - 更新 docker-compose.yml
   - 更新 CI/CD 工作流（如有需要）

## Constraints

- 保持后端 API 契约不变，确保向后兼容
- 前端功能需完全等价迁移，不丢失现有特性
- 消息队列引入不能影响现有同步 API 的可用性

## Acceptance Criteria

### 前端迁移验收
- [ ] Vue 3 项目可正常启动 (`npm run dev`)
- [ ] 所有现有路由和页面功能正常
- [ ] 用户认证流程（登录/注册/Token 刷新）工作正常
- [ ] 角色权限控制（Student/Teacher/Admin）功能正常
- [ ] 核心功能页面正常工作：
  - Dashboard（学生/教师）
  - 作业提交和批改
  - Code Analysis
  - QA 智能问答
  - Plagiarism 检测
  - Report Analysis
  - Knowledge Base
- [ ] Docker 构建成功

### 消息队列验收
- [ ] Kafka 或 RabbitMQ 服务在 docker-compose 中正常启动
- [ ] FastAPI 可成功连接消息队列
- [ ] 至少一个异步任务场景实现（如批量提交处理）
- [ ] 消息队列故障不影响主 API 可用性

## Non-Goals

- 后端业务逻辑重构（保持现有 FastAPI 实现）
- 数据库 Schema 变更（保持现有 MySQL 结构）
- 新增业务功能（仅做技术栈迁移）
- 前端 UI 重新设计（保持现有界面风格和交互）

## Technology Choices

### 前端
- **Framework**: Vue 3.4+ (Composition API)
- **Build Tool**: Vite 5+
- **Language**: TypeScript 5+
- **State Management**: Pinia 2+
- **Router**: Vue Router 4+
- **HTTP Client**: Axios
- **UI Library**: 可选 Element Plus / Ant Design Vue（根据现有 React 组件风格选择）

### 消息队列
- **方案 A (Kafka)**: Kafka + Zookeeper，适合高吞吐、多消费者场景
- **方案 B (RabbitMQ)**: 单节点部署，适合路由复杂、可靠性优先场景
- **推荐**: RabbitMQ（考虑到教学场景的消息量和学习曲线）

## Migration Mapping

| React 组件/页面 | Vue 对应 |
|----------------|----------|
| `src/App.tsx` | `src/App.vue` |
| `src/pages/*.tsx` | `src/views/*.vue` |
| `src/components/*/*.tsx` | `src/components/*.vue` |
| `src/contexts/*.tsx` | `src/stores/*.ts` (Pinia) |
| `src/hooks/*.ts` | `src/composables/*.ts` |
| `src/services/*.ts` | `src/services/*.ts` |
| `react-router-dom` | `vue-router` |
| `useState/useEffect` | `ref/reactive/watch` |

## Verification Plan

1. 启动完整 docker-compose 环境
2. 运行前端构建 `npm run build`
3. 访问各功能页面，验证核心流程
4. 检查后端日志，确认消息队列连接正常
5. 测试消息队列场景（如批量提交）

## Rollback Plan

- 保留原 `frontend/` 目录为 `frontend-react/` 备份（完成后删除）
- 如迁移失败，可快速切换回 React 版本

## Assumptions

- 用户接受 Vue 3 作为新前端框架
- 消息队列主要用于异步任务，不要求实时双向通信
- 现有后端 API 无需修改即可支持 Vue 前端
