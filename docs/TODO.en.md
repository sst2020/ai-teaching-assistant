# AI Teaching Assistant - Project TODO List

> **Last Updated:** March 15, 2026
> **Project Status:** MVP Complete ✅ + Enhanced Debugging Environment ✅ + Production JWT Auth ✅ + Auth Monitoring ✅ + Redis Cache ✅ + Grading API ✅ + Report Analysis with DeepSeek ✅
> **Complexity Indicators:** 🟢 Easy | 🟡 Medium | 🔴 Hard | ⏱️ Time-consuming

This document outlines remaining tasks, priorities, and contribution opportunities for the AI Teaching Assistant project.

## 🎉 MVP Status

The MVP (Minimum Viable Product) is now complete with the following core features:
- ✅ User Authentication (Login, Registration, Logout)
- ✅ **Production-Grade JWT Authentication System** (NEW - Dec 13, 2024)
  - ✅ Bcrypt password hashing
  - ✅ JWT token generation and validation
  - ✅ Refresh token rotation
  - ✅ Token blacklist mechanism
  - ✅ Role-based access control
- ✅ Assignment Submission with Monaco Code Editor
- ✅ File Upload with Language Detection
- ✅ Grades Viewing with Filtering and Sorting
- ✅ Student Dashboard
- ✅ Frontend-Backend Integration
- ✅ API Documentation (Swagger UI)

**Documentation:**
- 📄 [User Interface Guide](./USER_INTERFACE_GUIDE.md)
- 📄 [System Testing Report](./SYSTEM_TESTING_REPORT.md)
- 📄 [Development Setup](./DEVELOPMENT_SETUP.md)
- 📄 [Authentication Test Results](../backend/TEST_RESULTS.md) (NEW)

---

## Table of Contents

- [Priority Legend](#priority-legend)
- [✅ Completed Features](#-completed-features)
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

## ✅ Completed Features

> **Status:** Implemented
> **Last Updated:** December 2024

### Intelligent Feedback Generation System ✅

> **Completed:** November 2024

#### Deliverable 1: Feedback Generation Service ✅

- [x] 🟡 **FeedbackGenerationService** - `backend/services/feedback_service.py`
  - Context-aware feedback generation based on code analysis results
  - Multiple feedback tones: ENCOURAGING, PROFESSIONAL, DETAILED, CONCISE, FRIENDLY, STRICT
  - Language-specific best practices for Python, JavaScript, Java, TypeScript, C, C++
  - Categorized feedback: CODE_QUALITY, LOGIC_EFFICIENCY, STYLE_READABILITY, SECURITY, BEST_PRACTICES, SUGGESTIONS, ENCOURAGEMENT
  - Strengths/improvements/next-steps identification

- [x] 🟢 **Feedback Schemas** - `backend/schemas/feedback.py`
  - Pydantic models for all feedback operations
  - FeedbackTone, FeedbackCategory, TemplateCategory enums
  - Request/Response models for all endpoints

- [x] 🟢 **FeedbackTemplate Model** - `backend/models/feedback_template.py`
  - SQLAlchemy model for storing feedback templates
  - Category, severity, tags, and variable support

#### Deliverable 2: AI Integration Interface ✅

- [x] 🔴 **AIService** - `backend/services/ai_service.py`
  - OpenAI/Claude integration with configurable provider
  - Fallback to local responses when API key not configured
  - Interaction tracking and statistics

- [x] 🟢 **AIInteraction Model** - `backend/models/ai_interaction.py`
  - Tracks AI interaction history
  - Stores prompts, responses, tokens used, and latency

- [x] 🟡 **AI API Endpoints** - `backend/api/ai.py`
  - `POST /api/v1/ai/generate-feedback` - Generate comprehensive feedback
  - `POST /api/v1/ai/explain-code` - Explain code to students
  - `POST /api/v1/ai/suggest-improvements` - Suggest code improvements
  - `POST /api/v1/ai/answer-question` - Answer student questions
  - `GET /api/v1/ai/config` - Get AI configuration
  - `GET /api/v1/ai/stats` - Get interaction statistics
  - `GET /api/v1/ai/health` - Check AI service health

#### Deliverable 3: Feedback Template Library ✅

- [x] 🟡 **Feedback Templates API** - `backend/api/feedback_templates.py`
  - `GET /api/v1/feedback-templates` - List templates with filtering
  - `POST /api/v1/feedback-templates` - Create new template
  - `GET /api/v1/feedback-templates/{id}` - Get template by ID
  - `PUT /api/v1/feedback-templates/{id}` - Update template
  - `DELETE /api/v1/feedback-templates/{id}` - Delete template
  - `GET /api/v1/feedback-templates/categories/list` - List all categories
  - `POST /api/v1/feedback-templates/{id}/increment-usage` - Track template usage

- [x] 🟢 **CRUD Operations** - `backend/utils/crud.py`
  - CRUDFeedbackTemplate with get_by_category, get_by_tags, increment_usage, search
  - CRUDAIInteraction with get_by_user, get_by_type, get_stats, log_interaction

- [x] 🟢 **Seed Script** - `backend/scripts/seed_feedback_templates.py`
  - 29 default templates across 7 categories:
    - Common Issues (5 templates)
    - Naming (3 templates)
    - Style (3 templates)
    - Complexity (3 templates)
    - Security (4 templates)
    - Encouragement (6 templates)
    - Language-Specific (5 templates)

- [x] 🟢 **Tests** - `backend/tests/test_feedback_system.py`
  - Comprehensive tests for feedback generation, AI service, and templates

### Enhanced Code Analysis System ✅

> **Completed:** December 2024

#### Task 2.1.1: Advanced Code Quality Analysis ✅

- [x] 🟡 **CodeQualityAnalyzer** - `backend/services/code_analyzer.py`
  - Cyclomatic complexity calculation using `radon` library
  - Cognitive complexity detection with AST visitor pattern
  - Code duplication detection using AST normalization
  - Maintainability index calculation with A-F ratings
  - Function-level complexity metrics

- [x] 🟢 **Analysis Schemas** - `backend/schemas/analysis.py`
  - Pydantic models for all analysis types
  - Enums: ComplexityGrade, MaintainabilityRating, IssueSeverity, SecuritySeverity, PerformanceIssueType
  - Request/Response models for quality, lint, security, performance, and comprehensive analysis

#### Task 2.1.2: Programming Standards Checker ✅

- [x] 🟡 **LinterService** - `backend/services/linter.py`
  - Pylint integration for Python linting
  - Configurable rules system
  - 200+ Chinese translations for Pylint messages
  - Fix suggestions for common issues

#### Task 2.1.3: Performance & Security Analysis ✅

- [x] 🟡 **SecurityAnalyzer** - `backend/services/security_analyzer.py`
  - Bandit integration for security scanning
  - Fallback pattern matching when Bandit unavailable
  - Chinese translations for security issues
  - Severity-based scoring

- [x] 🟡 **PerformanceAnalyzer** - `backend/services/security_analyzer.py`
  - Performance anti-pattern detection (nested loops, memory issues, blocking operations)
  - Best practices evaluation system
  - Chinese translations for all recommendations

- [x] 🟢 **Analysis API Endpoints** - `backend/api/analysis.py`
  - `POST /api/v1/analysis/quality` - Code quality analysis
  - `POST /api/v1/analysis/lint` - Programming standards check
  - `POST /api/v1/analysis/security` - Security vulnerability analysis
  - `POST /api/v1/analysis/performance` - Performance analysis
  - `POST /api/v1/analysis/comprehensive` - Combined analysis (all types)

- [x] 🟢 **Tests** - `backend/tests/test_advanced_analysis.py`
  - 25 comprehensive tests for all analysis services
  - Tests for CodeQualityAnalyzer, LinterService, SecurityAnalyzer, PerformanceAnalyzer
  - Integration tests for combined analysis

### Intelligent Feedback System Enhancement ✅

> **Completed:** December 2024

#### Task 2.2.1: Personalized Feedback Generation ✅

- [x] 🟡 **Enhanced FeedbackGenerationService** - `backend/services/feedback_service.py`
  - Student history analysis (trend detection, level determination)
  - Performance trend calculation (improving, declining, stable)
  - Student level determination (beginner, intermediate, advanced)
  - Improvement rate calculation
  - Personalized message generation based on history
  - Progressive suggestions with difficulty levels
  - Learning path creation with estimated time
  - Chinese translation support for all feedback

- [x] 🟢 **Personalized Feedback Schemas** - `backend/schemas/feedback.py`
  - StudentLevel, PerformanceTrend, SuggestionDifficulty, FeedbackDetailLevel enums
  - StudentHistoryAnalysis, PersonalizedFeedbackRequest, PersonalizedFeedbackResponse models
  - ProgressiveSuggestion, LearningPathItem models

- [x] 🟢 **Personalized Feedback API** - `backend/api/personalized_feedback.py`
  - `POST /api/v1/personalized-feedback/generate` - Generate personalized feedback
  - `GET /api/v1/personalized-feedback/history/{student_id}` - Get student history analysis
  - `GET /api/v1/personalized-feedback/learning-path/{student_id}` - Get learning path

- [x] 🟢 **Tests** - `backend/tests/test_personalized_feedback.py`
  - 36 comprehensive tests for personalized feedback generation

#### Task 2.2.2: Multi-Dimensional Evaluation System ✅

- [x] 🟡 **MultiDimensionalEvaluator** - `backend/services/multi_dimensional_evaluator.py`
  - 6 evaluation dimensions: correctness, efficiency, readability, structure, best_practices, documentation
  - Radar chart data generation for visualization
  - Class comparison statistics (percentile, rank, average)
  - Dimension-specific feedback generation
  - Chinese translations for all evaluations

- [x] 🟢 **Evaluation Schemas** - `backend/schemas/evaluation.py`
  - EvaluationDimension enum
  - DimensionScore, RadarChartData, ClassComparisonStats models
  - MultiDimensionalEvaluationRequest, MultiDimensionalEvaluationResponse models

- [x] 🟢 **Evaluation API** - `backend/api/evaluation.py`
  - `POST /api/v1/evaluation/multi-dimensional` - Multi-dimensional evaluation
  - `GET /api/v1/evaluation/radar-chart/{submission_id}` - Get radar chart data
  - `GET /api/v1/evaluation/class-comparison/{student_id}` - Get class comparison

- [x] 🟢 **Tests** - `backend/tests/test_multi_dimensional_evaluation.py`
  - 25 comprehensive tests for multi-dimensional evaluation

### Production-Grade JWT Authentication System ✅

> **Completed:** December 13, 2024

#### Core Authentication Infrastructure ✅

- [x] 🔴 **Independent User Model** - `backend/models/user.py`
  - Email-based authentication with unique constraint
  - Password hashing with bcrypt (cost factor 12)
  - Role-based access control (student, teacher, admin)
  - User activation status tracking
  - Last login timestamp tracking
  - One-to-one relationship with Student model

- [x] 🟡 **Security Utilities** - `backend/core/security.py`
  - Bcrypt password hashing and verification (72-byte limit handling)
  - JWT token generation with HS256 algorithm
  - Token validation and expiration checking
  - JTI (JWT ID) extraction for blacklisting
  - OAuth2 password bearer configuration

- [x] 🟡 **Token Management Models**
  - **RefreshToken** (`backend/models/refresh_token.py`): 7-day expiration, rotation support
  - **TokenBlacklist** (`backend/models/token_blacklist.py`): Invalidated token tracking

- [x] 🟢 **Authentication Schemas** - `backend/schemas/auth.py`
  - RegisterRequest with password validation (min 8 chars, alphanumeric)
  - LoginRequest, LoginResponse with nested token structure
  - UserResponse, TokenRefreshRequest, ChangePasswordRequest
  - Comprehensive Pydantic validation

- [x] 🟡 **CRUD Operations** - `backend/utils/crud.py`
  - CRUDUser: get_by_email, create, authenticate, update_last_login, change_password
  - CRUDRefreshToken: create, get_valid_token, revoke, revoke_all_for_user
  - CRUDTokenBlacklist: add_token, is_blacklisted, cleanup_expired

- [x] 🟡 **Dependency Injection** - `backend/core/dependencies.py`
  - get_current_user: JWT validation and user retrieval
  - get_current_active_user: Active user verification
  - require_role: Role-based access control decorator
  - Token blacklist checking

#### Authentication API Endpoints ✅

- [x] 🔴 **7 Production-Ready Endpoints** - `backend/api/auth.py`
  1. **POST /auth/register** - User registration with auto Student creation
  2. **POST /auth/login** - Login with JWT tokens (access + refresh)
  3. **GET /auth/me** - Get current authenticated user
  4. **POST /auth/refresh** - Refresh access token with rotation
  5. **POST /auth/change-password** - Change password and revoke all sessions
  6. **POST /auth/logout** - Logout and blacklist current token
  7. **POST /auth/revoke-all** - Revoke all refresh tokens for user

#### Database Migration ✅

- [x] 🟢 **Production Auth Migration** - `backend/alembic/versions/20251213_000000_add_production_auth_system.py`
  - Created users table with indexes on email
  - Created refresh_tokens table with user_id foreign key
  - Created token_blacklist table with jti index
  - Added user_id column to students table
  - SQLite batch mode for ALTER TABLE operations

#### Security Features ✅

- [x] 🟢 **Password Security**
  - Bcrypt hashing with cost factor 12
  - 72-byte password length handling
  - Password strength validation (min 8 chars, alphanumeric)

- [x] 🟢 **Token Security**
  - Standard JWT with HS256 algorithm
  - Access token: 30-minute expiration
  - Refresh token: 7-day expiration
  - Token blacklist for logout
  - Refresh token rotation (one-time use)
  - JTI-based token tracking

- [x] 🟢 **Access Control**
  - Role-based permissions (student, teacher, admin)
  - User activation status checking
  - Protected route dependencies

#### Testing & Validation ✅

- [x] 🟡 **Comprehensive Test Suite** - `backend/test_auth_api.py`
  - 12 test scenarios with 100% pass rate
  - User registration and login tests
  - Token refresh and rotation tests
  - Password change and security tests
  - Token blacklist and revocation tests
  - Error handling tests (invalid credentials, duplicate email)
  - **Test Report:** `backend/TEST_RESULTS.md`

- [x] 🟢 **Bug Fixes During Testing**
  - Fixed import paths (backend.* → relative imports)
  - Fixed bcrypt compatibility (passlib → direct bcrypt)
  - Fixed SQLAlchemy lazy loading (added db.refresh)
  - Fixed CRUD parameter types (Pydantic → dict)

### Frontend-Backend Collaborative Debugging Environment ✅

> **Completed:** December 2024

#### Enhanced Debugging Environment + One-Click Startup ✅

- [x] 🟡 **Environment Check Script** - `scripts/check-environment.js`
  - Automated Node.js, Python, and dependency validation
  - Colored console output with comprehensive system checks
  - Cross-platform compatibility detection

- [x] 🟢 **Enhanced Environment Configuration** - `frontend/.env`, `backend/.env`
  - Frontend debug settings: DEBUG_MODE, API_LOGGING, PERFORMANCE_MONITORING
  - Backend debug settings: REQUEST_LOGGING, CORS configuration, LOG_LEVEL
  - Development-optimized environment variables

- [x] 🟡 **Enhanced API Client with Debug Features** - `frontend/src/services/api.ts`
  - Request/response interceptors with detailed logging
  - Performance timing and request ID correlation
  - Error categorization and session storage integration
  - TypeScript module declarations for Axios metadata

- [x] 🟡 **Real-time Debug Panel** - `frontend/src/components/common/DebugPanel.tsx`
  - Live API call monitoring with performance metrics
  - Error tracking and categorization
  - Tabbed interface with responsive design
  - Session storage integration for persistent debugging data

- [x] 🟡 **Advanced Backend Logging** - `backend/utils/logger.py`, `backend/app/main.py`
  - Colored console formatters with request correlation
  - Performance monitoring with timing metrics
  - Structured logging with context variables
  - Request/response middleware with detailed tracking

- [x] 🟡 **One-Click Startup System** - `scripts/dev-start.js`, `scripts/check-environment.js`
  - Parallel frontend/backend service launching
  - Environment validation from the repository root
  - Workspace-level entry points through `npm run dev` and `npm run check:env`
  - Graceful shutdown and process management

- [x] 🟢 **Development Documentation** - `docs/DEVELOPMENT_SETUP.md`
  - Comprehensive setup guide with troubleshooting
  - Feature overview and usage instructions
  - System requirements and configuration details

#### Task 2.2.3: Expanded Feedback Template Library ✅

- [x] 🟡 **Expanded Templates** - `backend/scripts/seed_feedback_templates.py`
  - Expanded from 29 to 103 templates
  - Language-specific templates: Python (10), JavaScript/TypeScript (10), Java (7), C++ (7)
  - Performance templates (8)
  - Error handling templates (7)
  - Testing templates (5)
  - Algorithm templates (5)
  - Tone variants: Encouraging (4), Strict/Professional (4)
  - Chinese locale templates (12)

- [x] 🟢 **Enhanced Template Model** - `backend/models/feedback_template.py`
  - Added TemplateTone enum (NEUTRAL, ENCOURAGING, STRICT, PROFESSIONAL)
  - Added new categories: PERFORMANCE, ERROR_HANDLING, TESTING, ALGORITHM
  - Added `tone` and `locale` fields with indexes

- [x] 🟢 **Enhanced Template API** - `backend/api/feedback_templates.py`
  - `POST /api/v1/feedback-templates/search` - Advanced search with multiple filters
  - `GET /api/v1/feedback-templates/tones/list` - List available tones
  - `GET /api/v1/feedback-templates/stats/summary` - Template statistics
  - Enhanced list endpoint with tone, locale, and sorting filters

### Plagiarism Detection & Originality Analysis System ✅

> **Completed:** December 2024
> **Task Document:** `issues/plagiarism-detection-system.md`

#### Task 2.3.1: Code Similarity Detection ✅

- [x] 🟡 **SimilarityAlgorithms** - `backend/services/similarity_algorithms.py`
  - Levenshtein distance algorithm for text similarity
  - Cosine similarity with TF-IDF for semantic comparison
  - AST-based structural similarity analysis
  - Token sequence similarity detection
  - Variable/function renaming detection
  - Code refactoring detection

- [x] 🟡 **EnhancedPlagiarismService** - `backend/services/plagiarism_service.py`
  - Multi-algorithm similarity calculation
  - Similarity matrix generation
  - Originality report generation
  - Configurable detection settings

- [x] 🟢 **Plagiarism Schemas** - `backend/schemas/plagiarism.py`
  - SimilarityAlgorithm, CodeTransformationType enums
  - DetailedCodeMatch, SimilarityMatrixEntry, SimilarityMatrix models
  - OriginalityReport, BatchAnalysisRequest, BatchAnalysisResponse models
  - PlagiarismSettings for configurable thresholds

#### Task 2.3.2: Batch Plagiarism Engine ✅

- [x] 🟡 **Batch Analysis API** - `backend/api/assignments.py`
  - `POST /plagiarism/batch-analyze` - Batch similarity analysis
  - `GET /plagiarism/originality-report/{submission_id}` - Get originality report
  - `PUT /plagiarism/settings` - Update detection settings
  - `GET /plagiarism/settings` - Get current settings

#### Task 2.3.3: Originality Report Generation ✅

- [x] 🟢 **Frontend Components** - `frontend/src/components/PlagiarismCheck/`
  - `BatchUpload.tsx` - Drag-and-drop multi-file upload
  - `SimilarityMatrix.tsx` - Heatmap visualization with recharts
  - `RelationshipGraph.tsx` - Node-edge graph for similarity relationships
  - `SuspiciousList.tsx` - Sortable/filterable suspicious submissions table
  - `OriginalityReport.tsx` - Score dashboard with code comparison
  - `PlagiarismCheck.tsx` - Main component integrating all sub-components

- [x] 🟢 **Frontend Types** - `frontend/src/types/plagiarism.ts`
  - TypeScript type definitions matching backend schemas

- [x] 🟢 **Frontend API** - `frontend/src/services/api.ts`
  - `batchAnalyzePlagiarism()` - Batch analysis API call
  - `getOriginalityReport()` - Get originality report
  - `getPlagiarismSettings()` / `updatePlagiarismSettings()` - Settings management

- [x] 🟢 **Route Integration** - `frontend/src/App.tsx`, `frontend/src/components/layout/Header.tsx`
  - Added `/plagiarism` route
  - Added "🔍 查重分析" navigation link

#### Remaining Setup Steps

- [x] 🟢 **Run Database Migration** (P0) ✅ 2025-12-15
  ```bash
  cd backend
  python -m alembic revision --autogenerate -m "Add feedback_templates and ai_interactions tables"
  python -m alembic upgrade head
  ```

- [x] 🟢 **Seed Feedback Templates** (P0) ✅ 2025-12-15
  ```bash
  cd backend
  python -m scripts.seed_feedback_templates
  ```
  > 已成功填充 103 个反馈模板

- [ ] 🟢 **Configure OPENAI_API_KEY** (Optional)
  - Set `OPENAI_API_KEY` in `.env` file to enable AI-powered features
  - Without API key, the system uses local fallback responses

- [x] 🟢 **Run Feedback System Tests** (P1) ✅ 2025-12-22
  ```bash
  cd backend
  python -m pytest tests/test_feedback_system.py -v
  ```
  > 修复了所有 22 个测试，包括 schema 字段补全和测试 API 更新

---

## 🔐 Security & Authentication

> **Status:** Production Complete ✅
> **Priority:** P1 - RBAC Enhancements Recommended
> **Dependencies:** None

### JWT Authentication System ✅ (MVP)

- [x] 🟡 **Create authentication middleware** (P0) ✅
  - Created `backend/api/auth.py` router
  - Implemented `/auth/login` endpoint (returns JWT)
  - Implemented `/auth/logout` endpoint
  - Implemented `/auth/refresh` endpoint
  - Implemented `/auth/register` endpoint
  - Implemented `/auth/me` endpoint
  - **Note:** Currently uses in-memory storage for development

- [x] 🟢 **Frontend authentication context** (P0) ✅
  - Created `frontend/src/contexts/AuthContext.tsx`
  - JWT stored in localStorage
  - Auto-refresh tokens on API calls
  - Protected route wrapper implemented

### Production Authentication ✅

> **Completed:** December 13, 2024

- [x] 🔴 **Implement production JWT with database storage** (P0) ✅
  - ✅ Created independent User model with email, password_hash, role, is_active
  - ✅ Implemented bcrypt password hashing (cost factor 12)
  - ✅ Implemented JWT token generation and validation (HS256, python-jose)
  - ✅ Implemented token blacklisting for logout
  - ✅ Implemented refresh token rotation mechanism
  - ✅ Created 3 new models: User, RefreshToken, TokenBlacklist
  - ✅ Created database migration (20251213_000000_add_production_auth_system)
  - **Acceptance Criteria:**
    - ✅ Access tokens expire after 30 minutes
    - ✅ Refresh tokens expire after 7 days
    - ✅ Refresh token rotation on each refresh
    - ✅ Secure password storage with bcrypt
    - ✅ Token blacklist mechanism working
  - **Files Created:**
    - `backend/core/security.py` - Password hashing and JWT utilities
    - `backend/models/user.py` - User model
    - `backend/models/refresh_token.py` - RefreshToken model
    - `backend/models/token_blacklist.py` - TokenBlacklist model
    - `backend/schemas/auth.py` - Authentication schemas
    - `backend/core/dependencies.py` - Dependency injection functions
  - **Files Modified:**
    - `backend/models/student.py` - Added user_id foreign key
    - `backend/utils/crud.py` - Added CRUD classes for User, RefreshToken, TokenBlacklist
    - `backend/core/config.py` - Added JWT configuration
    - `backend/api/auth.py` - Completely rewritten with 7 endpoints

- [x] 🟡 **Add password field to Student model** (P1) ✅
  - ✅ Created independent User model instead of modifying Student
  - ✅ Added user_id foreign key to Student model
  - ✅ Created Alembic migration
  - ✅ Updated registration endpoint to hash passwords with bcrypt
  - **Files:** `backend/models/student.py`, `backend/models/user.py`

- [x] 🟢 **Implement 7 Authentication API Endpoints** (P0) ✅
  - ✅ POST /api/v1/auth/register - User registration with auto Student creation
  - ✅ POST /api/v1/auth/login - Login with JWT token generation
  - ✅ GET /api/v1/auth/me - Get current user information
  - ✅ POST /api/v1/auth/refresh - Refresh access token with rotation
  - ✅ POST /api/v1/auth/change-password - Change password and revoke all tokens
  - ✅ POST /api/v1/auth/logout - Logout and blacklist token
  - ✅ POST /api/v1/auth/revoke-all - Revoke all refresh tokens
  - **Testing:** All 12 test scenarios passed (100% success rate)
  - **Test Report:** `backend/TEST_RESULTS.md`

### Frontend Integration ✅

> **Completed:** December 14, 2024

- [x] 🟡 **Update Frontend Types** (P1) ✅
  - ✅ Updated `User` interface with production fields (is_active, last_login, updated_at)
  - ✅ Fixed `RegisterResponse` to include tokens field
  - ✅ Added `RefreshTokenResponse`, `ChangePasswordRequest`, `ChangePasswordResponse`, `RevokeAllTokensResponse`
  - **File:** `frontend/src/types/auth.ts`

- [x] 🟡 **Update API Services** (P1) ✅
  - ✅ Updated `refreshToken` function to handle new response structure
  - ✅ Added `changePassword` API function
  - ✅ Added `revokeAllTokens` API function
  - **File:** `frontend/src/services/api.ts`

- [x] 🔴 **Update AuthContext** (P1) ✅
  - ✅ Updated `register` function to use tokens from registration response
  - ✅ Updated `logout` function to call backend API for token blacklisting
  - ✅ Updated `refreshToken` function to handle new response structure
  - ✅ Implemented automatic token refresh mechanism (5 minutes before expiration)
  - ✅ Added `changePassword` method
  - ✅ Added `revokeAllTokens` method
  - **File:** `frontend/src/contexts/AuthContext.tsx`

### Authentication Monitoring & Logging ✅

> **Completed:** December 14, 2024

- [x] 🔴 **Implement Authentication Event Logging** (P1) ✅
  - ✅ Created `AuthLog` model for tracking all authentication events
  - ✅ Event types: login, logout, register, token_refresh, password_change, token_revoke, login_failed
  - ✅ Tracks: user_id, email, event_type, status, ip_address, user_agent, failure_reason, extra_data
  - ✅ Optimized indexes for query performance
  - **File:** `backend/models/auth_log.py`

- [x] 🔴 **Implement Authentication Monitoring Service** (P1) ✅
  - ✅ Created `AuthMonitorService` for detecting suspicious activity
  - ✅ Account lockout mechanism (5 failed attempts = 15 minute lockout)
  - ✅ Suspicious activity detection (multiple IPs, excessive attempts)
  - ✅ Integrated logging into all authentication endpoints
  - **File:** `backend/services/auth_monitor.py`

- [x] 🟡 **Update Authentication Endpoints with Logging** (P1) ✅
  - ✅ Added IP address and User-Agent extraction helpers
  - ✅ Integrated logging into register endpoint
  - ✅ Integrated logging into login endpoint with lockout check
  - ✅ Integrated logging into refresh endpoint
  - ✅ Integrated logging into logout endpoint
  - ✅ Integrated logging into change-password endpoint
  - ✅ Integrated logging into revoke-all endpoint
  - **File:** `backend/api/auth.py`

- [x] 🟢 **Create Database Migration** (P1) ✅
  - ✅ Created migration for auth_logs table
  - ✅ MySQL compatible migration script
  - ✅ All indexes created successfully
  - **File:** `backend/alembic/versions/20251214_000000_add_auth_log_model.py`

- [x] 🟢 **Testing and Validation** (P1) ✅
  - ✅ Tested all authentication events logging
  - ✅ Verified account lockout mechanism (5 attempts, 15 min lockout)
  - ✅ Verified IP address and User-Agent tracking
  - ✅ Verified database schema and indexes
  - **Test Results:** All monitoring features working correctly

### Role-Based Access Control (RBAC) ✅

> **Completed:** 2025 (implemented via string-based roles instead of separate Role/Permission models)

- [x] 🔴 **Design and implement user roles** (P1) ✅
  - ✅ `User` model with role field (student, teacher, admin) - `backend/models/user.py`
  - ✅ Role-based access control via `require_role()` and `require_roles()` decorators
  - ✅ Permission checking via `check_permissions()` in `backend/api/deps.py`
  - **Note:** Uses string-based roles instead of separate Role/Permission models (simpler approach)
  - **Acceptance Criteria:**
    - ✅ Students: Submit assignments, view own grades, ask questions
    - ✅ Teachers: Grade assignments, view all submissions, answer questions
    - ✅ Admins: Full access, user management

- [x] 🟡 **Create Teacher model and endpoints** (P1) ✅
  - ✅ Created `backend/models/teacher.py` - Teacher model with user_id FK
  - ✅ Created `backend/api/teachers.py` - Full CRUD router (register, list, get, update, delete)
  - ✅ Created `backend/schemas/teacher.py` - TeacherCreate, TeacherUpdate, TeacherResponse, TeacherListResponse
  - ✅ Added `crud_teacher` to `backend/utils/crud.py`
  - **Deliverables:** Model ✅, schemas ✅, router ✅

- [x] 🟡 **Implement permission decorators** (P2) ✅
  - ✅ `require_role("teacher")` decorator in `backend/core/dependencies.py`
  - ✅ `require_roles(["teacher", "admin"])` decorator in `backend/core/dependencies.py`
  - ✅ `check_permissions()` in `backend/api/deps.py`
  - **Note:** Implemented in `dependencies.py` and `deps.py` instead of separate `permissions.py`

---

## 🖥️ Frontend Development

> **Status:** MVP Complete ✅
> **Priority:** P2 - Enhancements
> **Current State:** All core pages implemented

### Authentication UI ✅

- [x] 🟡 **Create Login page** (P0) ✅
  - Created `frontend/src/pages/Login.tsx`
  - Form with email and password
  - Error handling and validation
  - Redirect to dashboard on success
  - Toast notifications for feedback

- [x] 🟡 **Create Registration page** (P0) ✅
  - Created `frontend/src/pages/Register.tsx`
  - Student registration form with validation
  - Role selection (student/teacher)

- [x] 🟢 **Implement auth context and hooks** (P0) ✅
  - Created `frontend/src/contexts/AuthContext.tsx`
  - JWT stored in localStorage
  - Auto-refresh tokens on API calls

- [x] 🟢 **Add protected route wrapper** (P1) ✅
  - Created `frontend/src/components/common/ProtectedRoute.tsx`
  - Redirects unauthenticated users to login

### Student Management UI ✅

- [x] 🟡 **Create Student Dashboard page** (P1) ✅
  - Created `frontend/src/pages/StudentDashboard.tsx`
  - View enrolled courses
  - View assignments and due dates
  - View submission history and grades
  - Statistics summary

- [x] 🟡 **Create Assignment Submission page** (P1) ✅
  - Created `frontend/src/pages/SubmitAssignment.tsx`
  - Monaco Code Editor integration with syntax highlighting
  - File upload with drag-and-drop
  - Language auto-detection
  - Auto-save drafts to localStorage
  - Rubric display panel
  - Confirmation dialogs

- [x] 🟢 **Create Grades page** (P2) ✅
  - Created `frontend/src/pages/Grades.tsx`
  - Grade distribution chart
  - Sortable and filterable table
  - Detailed submission modal
  - Grade letter badges (A, B, C, D, F)
  - URL deep linking to submissions

### Teacher/Admin UI ✅

> **Completed:** December 27, 2024

- [x] 🔴 **Create Teacher Dashboard** (P1) ✅
  - ✅ Created `frontend/src/pages/TeacherDashboard.tsx`
  - ✅ View assignment statistics and overview
  - ✅ Quick action cards for navigation
  - ✅ Recent assignments table
  - ✅ Urgent alerts for pending questions
  - ✅ Responsive design with CSS Grid
  - **Routes:** `/teacher`

- [x] 🟡 **Create Assignment Management page** (P1) ✅
  - ✅ Created `frontend/src/pages/ManageAssignments.tsx`
  - ✅ Assignment list with pagination
  - ✅ Filter by type and status
  - ✅ Create/edit assignment modal form
  - ✅ Delete confirmation
  - ✅ Due date and late submission settings
  - **Routes:** `/manage-assignments`

- [x] 🟡 **Create Grading Interface** (P1) ✅
  - ✅ Created `frontend/src/pages/GradingInterface.tsx`
  - ✅ Assignment selector dropdown
  - ✅ Grading statistics panel (average, distribution)
  - ✅ Submission list with score badges
  - ✅ Detailed grading view with feedback
  - ✅ Teacher override modal with reason
  - ✅ AI vs Teacher grading indicators
  - **Routes:** `/grading`

- [ ] 🔴 **Create Admin Panel** (P2)
  - User management (CRUD)
  - System settings
  - Analytics dashboard
  - **File:** `frontend/src/pages/AdminPanel.tsx`

### UI/UX Improvements ✅

- [x] 🟢 **Implement React Router** (P0) ✅
  - Using React Router v7
  - All pages properly routed
  - **File:** `frontend/src/App.tsx`

- [x] 🟢 **Add toast notifications** (P2) ✅
  - Created `frontend/src/components/common/Toast.tsx`
  - Created `frontend/src/contexts/ToastContext.tsx`
  - Success/error/info/warning notifications

- [x] 🟢 **Improve responsive design** (P2) ✅
  - Mobile-friendly layouts
  - Material Design 3 responsive breakpoints
  - **Files:** All CSS files with MD3 design tokens

- [x] 🟢 **Add accessibility features** (P2) ✅
  - Created `frontend/src/components/common/ConfirmDialog.tsx`
  - Focus trap and keyboard navigation
  - ARIA attributes for screen readers
  - Visible focus indicators

- [x] 🟡 **Add dark mode support** (P3) ✅ 2026-01-25
  - ✅ Created `frontend/src/contexts/ThemeContext.tsx`
  - ✅ Theme toggle in header
  - ✅ Persist preference to localStorage
  - ✅ CSS variables for light/dark themes

- [x] 🟡 **Add Web Animation Effects (添加网页动画效果)** (P2) ✅
  - ✅ Added smooth page transitions and interaction animations for the frontend
  - ✅ Page-level entrance animations (fadeIn, slideIn) for TeacherDashboard, StudentDashboard, ManageAssignments, GradingInterface, SubmitAssignment
  - ✅ Card/button feedback animations with staggered delays
  - ✅ List and empty state animations
  - ✅ Dialog open/close transitions (ConfirmDialog)
  - ✅ Uses CSS transitions/animations aligned with MD3 motion tokens
  - **Files:** `frontend/src/pages/*.css`, `frontend/src/index.css`
  - **Verified:** `npm run build` passed successfully

### Development Tools Enhancement

- [x] 🟡 **Create API Testing Tool Page** (P2) ✅ 2026-01-25
  - ✅ Created `frontend/src/components/DevTools/ApiTester.tsx`
  - ✅ Online API testing with request builder
  - ✅ Response viewer with JSON formatting
  - ✅ Request history with localStorage persistence
  - ✅ Support for all HTTP methods and custom headers
  - **Route:** `/api-tester`

- [ ] 🟡 **Add Performance Monitoring Component** (P2)
  - Create `frontend/src/components/DevTools/PerformanceMonitor.tsx`
  - Real-time API response time monitoring
  - Memory usage and rendering performance tracking
  - **File:** `frontend/src/components/DevTools/PerformanceMonitor.tsx`

- [x] 🟢 **Enhance Error Boundary Component** (P2) ✅ 2026-04-12
  - Upgrade `frontend/src/components/common/ErrorBoundary.tsx`
  - ✅ Error reporting: auto-generated errorId + ISO timestamp + structured console.group logs
  - ✅ Retry mechanism: "Retry" button resets state and increments retryCount; "Reload" as fallback
  - ✅ Debug info display: collapsible error stack + component stack (shown by default in development)
  - ✅ Optional `onError` callback (for Sentry / custom monitoring integration)
  - ✅ Optional `fallback` render prop (custom degraded UI)
  - ✅ Optional `showDebugInfo` prop (force-control debug panel visibility)
  - ✅ Fully backward compatible: existing `<ErrorBoundary>` usage in App.tsx needs no changes
  - **File:** `frontend/src/components/common/ErrorBoundary.tsx`

- [x] 🟢 **Add Service Health Check Automation** (P2) ✅ 2026-04-12
  - Create `scripts/health-check.js`
  - ✅ Periodic HTTP ping of frontend (3000) and backend (8000/health), default interval 10s
  - ✅ Failure count accumulation; alert when threshold (default 3) is exceeded
  - ✅ `--restart` flag: auto-spawn the corresponding service process on threshold breach
  - ✅ Colored console output consistent with dev-start.js style
  - ✅ CLI args: `--interval <seconds>` `--threshold <count>` `--restart`
  - ✅ Graceful exit (SIGINT/SIGTERM) with automatic cleanup of managed processes
  - **File:** `scripts/health-check.js`

- [ ] 🟢 **Optimize package.json Scripts** (P2)
  - Update `frontend/package.json` and root `package.json`
  - Add debugging-related npm scripts
  - Standardize development commands
  - **Files:** `frontend/package.json`, `package.json`

### API Integration ✅

- [x] 🟡 **Add student API functions** (P1) ✅
  - Register, login, get profile implemented
  - `frontend/src/services/api.ts` updated

- [x] 🟡 **Add submission API functions** (P1) ✅
  - Create, list, get submissions implemented
  - `frontend/src/services/api.ts` updated

- [x] 🟡 **Add assignment API functions** (P1) ✅
  - CRUD operations implemented
  - `frontend/src/services/api.ts` updated

### Performance Optimizations ✅

- [x] 🟢 **Add API response caching** (P2) ✅
  - Created `frontend/src/utils/cache.ts`
  - Simple in-memory cache with TTL
  - Cache key generators for common entities

- [x] 🟢 **Add loading skeleton components** (P2) ✅
  - Created `frontend/src/components/common/Skeleton.tsx`
  - Skeleton, SkeletonCard, SkeletonTable components
  - Pulse and wave animations

---

## ⚙️ Backend Enhancements

> **Status:** Core CRUD complete
> **Priority:** P1 - High

### Rubric Management

- [x] 🟡 **Create Rubric API endpoints** (P1) ✅
  - ✅ Created `backend/api/rubrics.py`
  - ✅ CRUD operations for rubrics
  - ✅ Link rubrics to assignments
  - ✅ Route registered in `backend/app/main.py`
  - **Deliverables:** Router, schemas, tests

- [x] 🟢 **Create rubric schemas** (P1) ✅
  - ✅ Created `backend/schemas/rubric.py`
  - ✅ `RubricCreate`, `RubricUpdate`, `RubricResponse`, `RubricListResponse`

### Grading Results API ✅

> **Completed:** December 27, 2024

- [x] 🟡 **Create GradingResult API endpoints** (P1) ✅
  - ✅ Created `backend/api/grading.py`
  - ✅ Get grades by student/assignment/submission
  - ✅ Manual grade override with teacher feedback
  - ✅ Grading statistics endpoint
  - ✅ Redis cache integration
  - **Endpoints:**
    - `POST /api/v1/grading` - Create grading result
    - `GET /api/v1/grading/{id}` - Get grading result with submission details
    - `GET /api/v1/grading/submission/{submission_id}` - Get by submission
    - `GET /api/v1/grading/student/{student_id}` - Get by student (paginated)
    - `GET /api/v1/grading/assignment/{assignment_id}` - Get by assignment (paginated)
    - `GET /api/v1/grading/assignment/{assignment_id}/statistics` - Get statistics
    - `PUT /api/v1/grading/{id}/override` - Teacher override
    - `DELETE /api/v1/grading/{id}` - Delete grading result

- [x] 🟢 **Create grading result schemas** (P1) ✅
  - ✅ Created `backend/schemas/grading.py`
  - ✅ GradingResultCreate, GradingResultUpdate, GradingResultOverride
  - ✅ GradingResultResponse, GradingResultWithSubmission
  - ✅ GradingResultListResponse, GradingStatistics
  - ✅ BatchGradingRequest, BatchGradingResponse

### Q&A System Enhancements ✅

> **Completed:** December 2024 (see Future Enhancements section for details)

- [x] 🟡 **Persist Q&A to database** (P1) ✅
  - ✅ `backend/models/qa_log.py` - QALog model for persistence
  - ✅ `backend/api/qa.py` - Full Q&A API with database storage
  - ✅ `backend/services/qa_service.py` - Q&A service layer
  - ✅ Student question history, weakness analysis, smart Q&A with triage
  - **Files:** `backend/api/qa.py`, `backend/models/qa_log.py`, `backend/services/qa_service.py`

- [x] 🟢 **Add Q&A CRUD utilities** (P1) ✅
  - ✅ Q&A operations integrated via qa_service.py
  - ✅ Tests in `backend/tests/test_qa.py`

### File Upload System

- [x] 🔴 **Implement file upload endpoint** (P1) ✅
  - ✅ Implemented by extending `backend/api/files.py`
  - ✅ Supports multiple file types (.py, .php, .pdf, .docx, .txt)
  - ✅ Max file size enforced (10MB default)
  - ✅ Allowed extensions validated
  - ✅ Files stored securely via storage service
  - ℹ️ Virus scanning remains optional / not enabled by default

- [x] 🟡 **Create file storage service** (P1) ✅
  - ✅ Created `backend/services/storage_service.py`
  - ✅ Local storage for development
  - ✅ S3/cloud storage for production
  - **File:** `backend/services/storage_service.py`

### Caching & Performance ✅

> **Completed:** December 27, 2024

- [x] 🟡 **Implement Redis caching** (P2) ✅
  - ✅ Created `backend/core/cache.py`
  - ✅ Cache frequently accessed data with TTL support
  - ✅ Session storage functionality
  - ✅ Rate limiting storage support
  - ✅ Graceful fallback to in-memory cache when Redis unavailable
  - ✅ Cache decorators for easy integration
  - ✅ Cache key generators for common entities
  - **Features:**
    - `CacheService` - Unified cache interface
    - `MemoryCache` - In-memory fallback backend
    - `RedisCache` - Redis backend with connection pooling
    - `@cached` decorator for automatic caching
    - `CacheKeys` - Standardized key generators

- [ ] 🟢 **Add database query optimization** (P2)
  - Add indexes where needed
  - Implement eager loading for relationships
  - **Files:** Model files, Alembic migrations

### Rate Limiting ✅

- [x] 🟡 **Implement rate limiting middleware** (P2) ✅
  - ✅ Created `backend/core/rate_limit.py` with `SimpleRateLimitMiddleware`
  - ✅ In-memory sliding window per client IP
  - ✅ Configurable via `RATE_LIMIT_ENABLED`, `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_PERIOD` settings
  - **Note:** For production, consider upgrading to Redis-backed distributed limiter

---

## 🧪 Testing

> **Status:** Basic tests exist
> **Priority:** P1 - High
> **Current Coverage:** ~30% (estimated)

### Backend Unit Tests

- [x] 🟢 **Add student endpoint tests** (P1) ✅
  - ✅ Created `backend/tests/test_students.py` (559 lines)
  - ✅ Tests all CRUD operations with factory fixtures
  - ✅ Tests validation errors and edge cases
  - **File:** `backend/tests/test_students.py`

- [x] 🟢 **Add submission endpoint tests** (P1) ✅
  - ✅ Created `backend/tests/test_submissions.py` (333 lines)
  - ✅ Tests: create, get, student/assignment submissions, status updates
  - ✅ Tests: auto-id, duplicate, not-found, missing fields, pagination, invalid status

- [x] 🟢 **Add CRUD utility tests** (P1) ✅
  - ✅ Created `backend/tests/test_crud.py` (420+ lines, async)
  - ✅ Tests: CRUDBase (get, get_multi, count, create, update, delete)
  - ✅ Tests: CRUDStudent, CRUDAssignment, CRUDSubmission, CRUDTeacher
  - ✅ Tests: generate_unique_id uniqueness

- [ ] 🟡 **Add service layer tests** (P2)
  - Test AI service (with mocks)
  - Test grading service
  - Test plagiarism service
  - **Files:** `backend/tests/test_services/`

- [ ] 🟡 **Add feedback-style tests for other core systems** (P2)
  - Mirror the coverage level of `backend/tests/test_feedback_system.py` for analysis, evaluation, and auth modules
  - Ensure cross-module flows (analysis → feedback → evaluation) are covered end-to-end

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

- [x] 🟢 **Set up test database** (P1) ✅
  - ✅ SQLite in-memory database by default for unit tests (`backend/tests/conftest.py`)
  - ✅ Supports MySQL test database via `TEST_DATABASE_URL` for integration validation
  - ✅ Test utilities in `backend/tests/test_utils.py` (override_get_db, init_test_db, dispose_test_db)
  - ✅ Sync and async test client fixtures
  - **File:** `backend/tests/conftest.py`, `backend/tests/test_utils.py`

- [x] 🟢 **Add GitHub Actions CI** (P1) ✅
  - ✅ Created `.github/workflows/ci.yml`
  - ✅ Run backend/frontend tests on push and pull requests
  - ✅ Run linting, type checks, coverage, and build validation
  - **File:** `.github/workflows/ci.yml`

- [ ] 🟢 **Add code coverage reporting** (P2)
  - Configure pytest-cov
  - Add coverage badge to README
  - **Target:** 80% coverage

- [ ] 🟡 **Fix Pydantic deprecation warnings** (P2)
  - Migrate class-based `Config` to `ConfigDict` in Pydantic models
  - Ensure test runs are free of Pydantic V2 deprecation warnings

---

## 📚 Documentation

> **Status:** Basic README exists
> **Priority:** P2 - Medium

### API Documentation

- [x] 🟢 **Add OpenAPI descriptions** (P2) ✅ 2026-01-25
  - ✅ Enhanced 5 API files with detailed Chinese descriptions
  - ✅ `health.py` - Health check endpoints
  - ✅ `knowledge_base.py` - Knowledge base management
  - ✅ `report_analysis.py` - Report analysis with DeepSeek
  - ✅ `students.py` - Student management
  - ✅ `submissions.py` - Submission management

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

- [x] 🟢 **Create docker-compose.yml** (P1) ✅ 2025-12-15
  - Backend + Frontend + MySQL 9 + Redis
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

- [x] 🟡 **Set up GitHub Actions** (P1) ✅
  - ✅ Created `.github/workflows/ci.yml`
  - ✅ Run tests on push/PR
  - ✅ Lint and type check
  - ✅ Build Docker images

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

- [x] 🟢 **Create environment templates** (P1) ✅ 2025-12-15
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

- [x] 🟡 **Plagiarism detection system** (P1) ✅ 2024-12
  - ✅ Multi-algorithm similarity detection (AST, Levenshtein, Cosine, Token)
  - ✅ Batch analysis and similarity matrix
  - ✅ Originality report generation
  - ✅ Frontend visualization (heatmap, relationship graph)
  - **Future enhancements:**
    - [ ] Add cross-language detection
    - [ ] Detect AI-generated content
    - [ ] Integration with external services (Moss, etc.)

### Features

- [x] 🟡 **Q&A System Persistence & Analytics** (P1) ✅ 2024-12
  - ✅ Persist Q&A records to database (QALog model)
  - ✅ Student question history tracking (`GET /qa/history/{student_id}`)
  - ✅ Knowledge weakness analysis and reporting (`GET /qa/weakness/{student_id}`)
  - ✅ Smart Q&A with triage (`POST /qa/smart-ask`)
  - ✅ Q&A statistics (`GET /qa/stats`)
  - **Files:** `backend/models/qa_log.py`, `backend/api/qa.py`, `backend/services/qa_service.py`

- [x] 🟡 **Project Report Analysis** (P2) ✅ 2024-12, Enhanced 2026-01-25
  - ✅ Analyze student project reports (PDF, DOCX, Markdown)
  - ✅ Evaluate completeness and innovation
  - ✅ Generate improvement suggestions
  - ✅ Batch analysis support (`POST /analysis/report/batch-analyze`)
  - ✅ **DeepSeek API Integration** (2026-01-25):
    - AI-powered logic analysis (`analyze_logic_with_ai`)
    - AI-powered innovation analysis (`analyze_innovation_with_ai`)
    - AI-powered improvement suggestions (`generate_improvement_suggestions_with_ai`)
    - AI-powered language quality evaluation (`evaluate_language_quality_with_ai`)
  - **Files:** `backend/services/report_analysis_service.py`, `backend/api/analysis.py`
  - **Schemas:** `backend/schemas/report_analysis.py`

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

