# Frontend Source Directory

This directory contains the React TypeScript frontend application for the AI Teaching Assistant platform.

## Directory Structure

### `/components`
Reusable UI components organized by feature:
- **`/common`** - Shared components (LoadingSpinner, ErrorMessage, ProtectedRoute, Toast, ToastContainer, ConfirmDialog, Skeleton, SkeletonCard, SkeletonTable)
- **`/layout`** - Layout components (Header, Footer)
- **`/Dashboard`** - Dashboard feature components
- **`/CodeAnalysis`** - Code analysis feature components
- **`/QAInterface`** - Q&A interface components

### `/contexts`
React Context providers for global state management:
- **`AuthContext.tsx`** - Authentication state (user, tokens, login/logout/register)
- **`ToastContext.tsx`** - Toast notification system (showSuccess, showError, showInfo, showWarning)

### `/hooks`
Custom React hooks:
- **`useAuth.ts`** - Re-exports useAuth from AuthContext for convenience

### `/pages`
Page-level components (routed views):
- **`Login.tsx`** - User login page with form validation
- **`Register.tsx`** - Student registration page
- **`StudentDashboard.tsx`** - Student dashboard with stats, courses, assignments
- **`SubmitAssignment.tsx`** - Assignment submission with code editor and file upload
- **`Grades.tsx`** - View graded submissions and feedback

### `/services`
API service layer:
- **`api.ts`** - Axios-based API client with auth, student, submission, and assignment endpoints

### `/types`
TypeScript type definitions:
- **`api.ts`** - API 响应类型定义，包括：
  - `AIAnswer` - AI 回答结构（answer, confidence, sources, needs_teacher_review）
  - `QuestionResponse` - 问答响应（ai_answer 为 AIAnswer 对象或 null）
  - `CodeAnalysisResponse`, `GradingResult`, `PlagiarismResponse` 等
- **`auth.ts`** - User, LoginCredentials, RegisterData, AuthTokens, AuthState
- **`student.ts`** - Student, StudentProfile, Course, StudentStats
- **`submission.ts`** - Submission, CreateSubmissionRequest, SubmissionFilters
- **`assignment.ts`** - Assignment, AssignmentFilters, Rubric
- **`triage.ts`** - 分诊相关类型（TriageResponse, TriageDecision 等）
- **`reportAnalysis.ts`** - 报告分析类型（ReportFileType, ReportAnalysisResponse 等）

### `/utils`
Utility functions and helpers:
- **`cache.ts`** - Simple in-memory cache for API responses (apiCache, cachedFetch, invalidateCache)

### `/styles`
Material Design 3 (MD3) Expressive theme implementation:
- **`md3-tokens.css`** - Core design tokens (colors, typography, elevation, shape, motion, spacing, states)
- **`md3-components.css`** - Reusable MD3 component classes (buttons, cards, text fields, navigation, chips, dialogs, etc.)

## Key Files

- **`App.tsx`** - Main application component with React Router routes and context providers (TypeScript version)
- **`App.js`** - Main application component (JavaScript version) - **React 入口实际使用此文件**
- **`index.tsx`** - Application entry point with BrowserRouter wrapper
- **`index.js`** - Application entry point (JavaScript version)

### ⚠️ App.tsx 与 App.js 同步规则

**重要**：由于 React 入口使用的是 `App.js`，修改 `App.tsx` 时必须同步更新 `App.js`，反之亦然。

同步内容包括：
- 导入语句（imports）
- 路由配置（Routes）
- 组件逻辑（AuthenticatedLayout、getActiveTab 等）
- 状态管理（useState 等）
- 功能特性（DebugPanel 等）

TypeScript 差异：App.tsx 包含类型注解，App.js 使用纯 JavaScript 语法。

## Routing

The application uses React Router v7 with the following routes:
- `/login` - Public login page
- `/register` - Public registration page
- `/dashboard` - Main dashboard (authenticated)
- `/code-analysis` - Code analysis tool (authenticated)
- `/qa` - Q&A interface (authenticated)
- `/student-dashboard` - Student-specific dashboard (authenticated)
- `/submit/:assignmentId` - Assignment submission (authenticated)
- `/grades` - View grades and feedback (authenticated)

## Authentication

Authentication is managed via AuthContext with JWT tokens stored in localStorage.
The API client automatically attaches tokens to requests via interceptors.

## Toast Notifications

Global toast notifications are available via useToast hook:
```tsx
const { showSuccess, showError, showInfo, showWarning } = useToast();
showSuccess('Operation completed!');
```

## Confirmation Dialogs

Use the ConfirmDialog component for user confirmations:
```tsx
import { ConfirmDialog } from '../components/common';

<ConfirmDialog
  isOpen={showDialog}
  title="Confirm Action"
  message="Are you sure you want to proceed?"
  confirmText="Confirm"
  cancelText="Cancel"
  variant="default" // 'default' | 'danger' | 'warning'
  onConfirm={handleConfirm}
  onCancel={() => setShowDialog(false)}
/>
```

Features:
- Focus trap for accessibility
- Keyboard navigation (Escape to close, Tab to cycle)
- ARIA attributes for screen readers
- Three variants: default, danger, warning

