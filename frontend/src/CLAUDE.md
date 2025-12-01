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
- **`auth.ts`** - User, LoginCredentials, RegisterData, AuthTokens, AuthState
- **`student.ts`** - Student, StudentProfile, Course, StudentStats
- **`submission.ts`** - Submission, CreateSubmissionRequest, SubmissionFilters
- **`assignment.ts`** - Assignment, AssignmentFilters, Rubric

### `/utils`
Utility functions and helpers:
- **`cache.ts`** - Simple in-memory cache for API responses (apiCache, cachedFetch, invalidateCache)

### `/styles`
Material Design 3 (MD3) Expressive theme implementation:
- **`md3-tokens.css`** - Core design tokens (colors, typography, elevation, shape, motion, spacing, states)
- **`md3-components.css`** - Reusable MD3 component classes (buttons, cards, text fields, navigation, chips, dialogs, etc.)

## Key Files

- **`App.tsx`** - Main application component with React Router routes and context providers
- **`index.tsx`** - Application entry point with BrowserRouter wrapper

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

