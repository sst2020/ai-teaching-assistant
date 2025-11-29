# AI Teaching Assistant - Project TODO List

> **Last Updated:** November 2024  
> **Project Status:** Active Development  
> **Complexity Indicators:** 🟢 Easy | 🟡 Medium | 🔴 Hard | ⏱️ Time-consuming

This document outlines remaining tasks, priorities, and contribution opportunities for the AI Teaching Assistant project.

---

## Table of Contents

- [Priority Legend](#priority-legend)
- [🔐 Security & Authentication](#-security--authentication)
- [🖥️ Frontend Development](#️-frontend-development)
- [⚙️ Backend Enhancements](#️-backend-enhancements)
- [🧪 Testing](#-testing)
- [📚 Documentation](#-documentation)
- [🚀 DevOps & Deployment](#-devops--deployment)
- [🎯 Future Enhancements](#-future-enhancements)

---

## Priority Legend

| Priority | Description |
|----------|-------------|
| **P0** | Critical - Blocking other work |
| **P1** | High - Core functionality |
| **P2** | Medium - Important features |
| **P3** | Low - Nice to have |

---

## 🔐 Security & Authentication

> **Status:** Not Started  
> **Priority:** P0 - Critical  
> **Dependencies:** None

### JWT Authentication System

- [ ] 🔴 **Implement JWT token generation and validation** (P0)
  - Create `backend/core/security.py` with JWT utilities
  - Use `python-jose` (already in requirements.txt)
  - Implement token creation, verification, and refresh
  - **Acceptance Criteria:**
    - Tokens expire after configurable time (default: 30 min)
    - Refresh tokens supported
    - Token blacklisting for logout

- [ ] 🟡 **Create authentication middleware** (P0)
  - Create `backend/api/auth.py` router
  - Implement `/auth/login` endpoint (returns JWT)
  - Implement `/auth/logout` endpoint
  - Implement `/auth/refresh` endpoint
  - **Acceptance Criteria:**
    - Secure password hashing with bcrypt
    - Rate limiting on login attempts

- [ ] 🟡 **Add password field to Student model** (P0)
  - Update `backend/models/student.py`
  - Create Alembic migration
  - Update registration endpoint to hash passwords
  - **Files:** `backend/models/student.py`, `backend/schemas/student.py`

- [ ] 🟢 **Create authentication dependency** (P1)
  - Create `get_current_user` dependency
  - Apply to protected endpoints
  - **File:** `backend/core/security.py`

### Role-Based Access Control (RBAC)

- [ ] 🔴 **Design and implement user roles** (P1)
  - Create `User` model with roles (student, teacher, admin)
  - Create `Role` and `Permission` models
  - **Acceptance Criteria:**
    - Students: Submit assignments, view own grades, ask questions
    - Teachers: Grade assignments, view all submissions, answer questions
    - Admins: Full access, user management

- [ ] 🟡 **Create Teacher model and endpoints** (P1)
  - Create `backend/models/teacher.py`
  - Create `backend/api/teachers.py` router
  - Implement teacher CRUD operations
  - **Deliverables:** Model, schemas, router, tests

- [ ] 🟡 **Implement permission decorators** (P2)
  - Create `@require_role("teacher")` decorator
  - Create `@require_permission("grade_assignments")` decorator
  - **File:** `backend/core/permissions.py`

---

## 🖥️ Frontend Development

> **Status:** Basic components exist  
> **Priority:** P1 - High  
> **Current State:** Dashboard, CodeAnalysis, QAInterface components exist

### Authentication UI

- [ ] 🟡 **Create Login page** (P0)
  - Create `frontend/src/pages/Login.tsx`
  - Form with student_id/email and password
  - Error handling and validation
  - Redirect to dashboard on success
  - **Acceptance Criteria:**
    - Form validation
    - Loading states
    - Error messages displayed

- [ ] 🟡 **Create Registration page** (P0)
  - Create `frontend/src/pages/Register.tsx`
  - Student registration form
  - Email verification flow (optional)

- [ ] 🟢 **Implement auth context and hooks** (P0)
  - Create `frontend/src/contexts/AuthContext.tsx`
  - Create `frontend/src/hooks/useAuth.ts`
  - Store JWT in localStorage/cookies
  - Auto-refresh tokens

- [ ] 🟢 **Add protected route wrapper** (P1)
  - Create `frontend/src/components/ProtectedRoute.tsx`
  - Redirect unauthenticated users to login

### Student Management UI

- [ ] 🟡 **Create Student Dashboard page** (P1)
  - View enrolled courses
  - View assignments and due dates
  - View submission history and grades
  - **File:** `frontend/src/pages/StudentDashboard.tsx`

- [ ] 🟡 **Create Assignment Submission page** (P1)
  - File upload for code/documents
  - Code editor for inline submissions
  - Preview before submit
  - **File:** `frontend/src/pages/SubmitAssignment.tsx`

- [ ] 🟢 **Create Grades page** (P2)
  - View all graded submissions
  - Detailed feedback display
  - Grade history chart
  - **File:** `frontend/src/pages/Grades.tsx`

### Teacher/Admin UI

- [ ] 🔴 **Create Teacher Dashboard** (P1)
  - View all students
  - View all submissions
  - Grading queue
  - Analytics overview
  - **File:** `frontend/src/pages/TeacherDashboard.tsx`

- [ ] 🟡 **Create Assignment Management page** (P1)
  - Create/edit/delete assignments
  - Set due dates and rubrics
  - Bulk operations
  - **File:** `frontend/src/pages/ManageAssignments.tsx`

- [ ] 🟡 **Create Grading Interface** (P1)
  - View submission content
  - AI-suggested grade with override
  - Feedback editor
  - Batch grading support
  - **File:** `frontend/src/pages/GradingInterface.tsx`

- [ ] 🔴 **Create Admin Panel** (P2)
  - User management (CRUD)
  - System settings
  - Analytics dashboard
  - **File:** `frontend/src/pages/AdminPanel.tsx`

### UI/UX Improvements

- [ ] 🟢 **Implement React Router** (P0)
  - Replace hash-based navigation with React Router
  - Add proper routing for all pages
  - **File:** `frontend/src/App.tsx`

- [ ] 🟢 **Add toast notifications** (P2)
  - Success/error/info notifications
  - Use react-toastify or similar
  - **File:** `frontend/src/components/common/Toast.tsx`

- [ ] 🟢 **Improve responsive design** (P2)
  - Mobile-friendly layouts
  - Tablet optimization
  - **Files:** All CSS files

- [ ] 🟡 **Add dark mode support** (P3)
  - Theme toggle in header
  - Persist preference
  - **Files:** `frontend/src/styles/`, `frontend/src/contexts/ThemeContext.tsx`

### API Integration

- [ ] 🟡 **Add student API functions** (P1)
  - Register, login, get profile
  - Update `frontend/src/services/api.ts`
  - **Acceptance Criteria:** All student endpoints covered

- [ ] 🟡 **Add submission API functions** (P1)
  - Create, list, get submissions
  - Update `frontend/src/services/api.ts`

- [ ] 🟡 **Add assignment API functions** (P1)
  - CRUD operations for assignments
  - Update `frontend/src/services/api.ts`

---

## ⚙️ Backend Enhancements

> **Status:** Core CRUD complete
> **Priority:** P1 - High

### Rubric Management

- [ ] 🟡 **Create Rubric API endpoints** (P1)
  - Create `backend/api/rubrics.py`
  - CRUD operations for rubrics
  - Link rubrics to assignments
  - **Deliverables:** Router, schemas, tests

- [ ] 🟢 **Create rubric schemas** (P1)
  - Create `backend/schemas/rubric.py`
  - RubricCreate, RubricUpdate, RubricResponse

### Grading Results API

- [ ] 🟡 **Create GradingResult API endpoints** (P1)
  - Create `backend/api/grading.py`
  - Get grades by student/assignment
  - Manual grade override
  - **Deliverables:** Router, schemas, tests

- [ ] 🟢 **Create grading result schemas** (P1)
  - Create `backend/schemas/grading.py`

### Q&A System Enhancements

- [ ] 🟡 **Persist Q&A to database** (P1)
  - Update `backend/api/qa.py` to use database
  - Store questions and answers
  - Link to students
  - **Files:** `backend/api/qa.py`, `backend/utils/crud.py`

- [ ] 🟢 **Add Q&A CRUD utilities** (P1)
  - Add `CRUDQuestion` and `CRUDAnswer` to `backend/utils/crud.py`

### File Upload System

- [ ] 🔴 **Implement file upload endpoint** (P1)
  - Create `backend/api/uploads.py`
  - Support multiple file types (.py, .pdf, .docx)
  - Virus scanning (optional)
  - **Acceptance Criteria:**
    - Max file size enforced (10MB default)
    - Allowed extensions validated
    - Files stored securely

- [ ] 🟡 **Create file storage service** (P1)
  - Create `backend/services/storage_service.py`
  - Local storage for development
  - S3/cloud storage for production
  - **File:** `backend/services/storage_service.py`

### Caching & Performance

- [ ] 🟡 **Implement Redis caching** (P2)
  - Cache frequently accessed data
  - Session storage
  - Rate limiting storage
  - **File:** `backend/core/cache.py`

- [ ] 🟢 **Add database query optimization** (P2)
  - Add indexes where needed
  - Implement eager loading for relationships
  - **Files:** Model files, Alembic migrations

### Rate Limiting

- [ ] 🟡 **Implement rate limiting middleware** (P2)
  - Use slowapi or custom implementation
  - Configure limits per endpoint
  - **File:** `backend/core/rate_limit.py`

---

## 🧪 Testing

> **Status:** Basic tests exist
> **Priority:** P1 - High
> **Current Coverage:** ~30% (estimated)

### Backend Unit Tests

- [ ] 🟢 **Add student endpoint tests** (P1)
  - Create `backend/tests/test_students.py`
  - Test all CRUD operations
  - Test validation errors
  - **Target Coverage:** 90%

- [ ] 🟢 **Add submission endpoint tests** (P1)
  - Create `backend/tests/test_submissions.py`
  - Test create, list, status update
  - **Target Coverage:** 90%

- [ ] 🟢 **Add CRUD utility tests** (P1)
  - Create `backend/tests/test_crud.py`
  - Test all CRUD operations
  - **Target Coverage:** 95%

- [ ] 🟡 **Add service layer tests** (P2)
  - Test AI service (with mocks)
  - Test grading service
  - Test plagiarism service
  - **Files:** `backend/tests/test_services/`

### Frontend Tests

- [ ] 🟡 **Add component tests** (P1)
  - Test Dashboard component
  - Test CodeAnalysis component
  - Test QAInterface component
  - Use React Testing Library
  - **Files:** `frontend/src/components/**/*.test.tsx`

- [ ] 🟡 **Add API service tests** (P2)
  - Mock axios calls
  - Test error handling
  - **File:** `frontend/src/services/api.test.ts`

- [ ] 🟢 **Add hook tests** (P2)
  - Test custom hooks
  - **Files:** `frontend/src/hooks/*.test.ts`

### Integration Tests

- [ ] 🔴 **Create end-to-end test suite** (P2)
  - Use Playwright or Cypress
  - Test complete user flows
  - **Acceptance Criteria:**
    - Student registration → login → submit → view grade
    - Teacher login → grade → provide feedback

- [ ] 🟡 **Add API integration tests** (P2)
  - Test full request/response cycles
  - Test database interactions
  - **File:** `backend/tests/integration/`

### Test Infrastructure

- [ ] 🟢 **Set up test database** (P1)
  - Use SQLite in-memory for tests
  - Add fixtures for common data
  - **File:** `backend/tests/conftest.py`

- [ ] 🟢 **Add GitHub Actions CI** (P1)
  - Run tests on PR
  - Run linting
  - **File:** `.github/workflows/ci.yml`

- [ ] 🟢 **Add code coverage reporting** (P2)
  - Configure pytest-cov
  - Add coverage badge to README
  - **Target:** 80% coverage

---

## 📚 Documentation

> **Status:** Basic README exists
> **Priority:** P2 - Medium

### API Documentation

- [ ] 🟢 **Add OpenAPI descriptions** (P2)
  - Add detailed descriptions to all endpoints
  - Add request/response examples
  - **Files:** All router files

- [ ] 🟡 **Create API usage guide** (P2)
  - Create `docs/api-guide.md`
  - Include authentication flow
  - Include common use cases
  - Code examples in multiple languages

### Developer Documentation

- [ ] 🟢 **Create contributing guide** (P2)
  - Create `CONTRIBUTING.md`
  - Code style guidelines
  - PR process
  - Development setup

- [ ] 🟢 **Create architecture documentation** (P2)
  - Create `docs/architecture.md`
  - System design diagrams
  - Data flow diagrams
  - Component relationships

- [ ] 🟢 **Add inline code documentation** (P3)
  - Add docstrings to all functions
  - Add type hints everywhere
  - **Files:** All Python files

### User Documentation

- [ ] 🟡 **Create user guide** (P3)
  - Create `docs/user-guide.md`
  - Student instructions
  - Teacher instructions
  - Screenshots and examples

---

## 🚀 DevOps & Deployment

> **Status:** Dockerfiles exist
> **Priority:** P2 - Medium

### Docker & Containerization

- [ ] 🟢 **Create docker-compose.yml** (P1)
  - Backend + Frontend + PostgreSQL
  - Development configuration
  - **File:** `docker-compose.yml`

- [ ] 🟢 **Create production docker-compose** (P2)
  - Create `docker-compose.prod.yml`
  - Nginx reverse proxy
  - SSL/TLS configuration

- [ ] 🟢 **Optimize Docker images** (P3)
  - Multi-stage builds
  - Reduce image sizes
  - **Files:** `backend/Dockerfile`, `frontend/Dockerfile`

### CI/CD Pipeline

- [ ] 🟡 **Set up GitHub Actions** (P1)
  - Create `.github/workflows/ci.yml`
  - Run tests on push/PR
  - Lint and type check
  - Build Docker images

- [ ] 🟡 **Add deployment workflow** (P2)
  - Create `.github/workflows/deploy.yml`
  - Deploy to staging on merge to develop
  - Deploy to production on release

### Infrastructure

- [ ] 🔴 **Create Kubernetes manifests** (P3)
  - Create `k8s/` directory
  - Deployment, Service, Ingress configs
  - ConfigMaps and Secrets

- [ ] 🟡 **Set up monitoring** (P2)
  - Add Prometheus metrics endpoint
  - Create Grafana dashboards
  - **File:** `backend/core/metrics.py`

- [ ] 🟡 **Set up logging** (P2)
  - Structured JSON logging
  - Log aggregation (ELK/Loki)
  - **File:** `backend/core/logging.py`

### Environment Management

- [ ] 🟢 **Create environment templates** (P1)
  - `.env.development`
  - `.env.staging`
  - `.env.production`

- [ ] 🟢 **Add secrets management** (P2)
  - Document secret rotation
  - Use environment-specific secrets

---

## 🎯 Future Enhancements

> **Priority:** P3 - Nice to Have

### AI/ML Improvements

- [ ] 🔴 **Fine-tune grading model** (P3)
  - Collect grading data
  - Train custom model
  - A/B test against GPT-4

- [ ] 🔴 **Add local LLM support** (P3)
  - Integrate llama.cpp
  - Support Ollama
  - Reduce API costs

- [ ] 🟡 **Improve plagiarism detection** (P3)
  - Add cross-language detection
  - Detect AI-generated content
  - Integration with external services

### Features

- [ ] 🟡 **Add course management** (P2)
  - Course CRUD
  - Enrollment management
  - Course analytics

- [ ] 🟡 **Add notification system** (P2)
  - Email notifications
  - In-app notifications
  - Configurable preferences

- [ ] 🟡 **Add analytics dashboard** (P2)
  - Student performance trends
  - Assignment difficulty analysis
  - Q&A topic clustering

- [ ] 🔴 **Add real-time features** (P3)
  - WebSocket support
  - Live grading updates
  - Real-time Q&A

---

## Getting Started as a Contributor

1. **Pick a task** from this list based on your skills and interests
2. **Check dependencies** - Some tasks require others to be completed first
3. **Create an issue** or comment on existing one to claim the task
4. **Create a feature branch** from `main`
5. **Submit a PR** with tests and documentation

### Recommended First Tasks for New Contributors

| Task | Complexity | Skills Needed |
|------|------------|---------------|
| Add student endpoint tests | 🟢 Easy | Python, pytest |
| Create contributing guide | 🟢 Easy | Markdown |
| Add toast notifications | 🟢 Easy | React, TypeScript |
| Implement React Router | 🟢 Easy | React |
| Add OpenAPI descriptions | 🟢 Easy | FastAPI |

---

## Questions?

- Open an issue for clarification
- Check existing documentation in `backend/README.md` and `README.md`
- Review the codebase structure before starting

**Happy Contributing! 🎉**

