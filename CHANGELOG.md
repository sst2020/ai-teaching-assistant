# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2024-12-13

### Added - Production-Grade JWT Authentication System

#### Core Infrastructure
- **Independent User Model** (`backend/models/user.py`)
  - Email-based authentication with unique constraint
  - Bcrypt password hashing (cost factor 12)
  - Role-based access control (student, teacher, admin)
  - User activation status and last login tracking
  - One-to-one relationship with Student model

- **Security Utilities** (`backend/core/security.py`)
  - Bcrypt password hashing and verification
  - JWT token generation with HS256 algorithm
  - Token validation and expiration checking
  - OAuth2 password bearer configuration

- **Token Management Models**
  - RefreshToken model with 7-day expiration and rotation support
  - TokenBlacklist model for invalidated token tracking

- **Authentication Schemas** (`backend/schemas/auth.py`)
  - Comprehensive Pydantic validation for all auth operations
  - Password strength validation (min 8 chars, alphanumeric)

- **CRUD Operations** (`backend/utils/crud.py`)
  - CRUDUser, CRUDRefreshToken, CRUDTokenBlacklist classes
  - Complete authentication lifecycle management

- **Dependency Injection** (`backend/core/dependencies.py`)
  - JWT validation and user retrieval
  - Role-based access control decorators
  - Token blacklist checking

#### API Endpoints
- **7 Production-Ready Authentication Endpoints** (`backend/api/auth.py`)
  1. POST /api/v1/auth/register - User registration
  2. POST /api/v1/auth/login - Login with JWT tokens
  3. GET /api/v1/auth/me - Get current user
  4. POST /api/v1/auth/refresh - Refresh access token
  5. POST /api/v1/auth/change-password - Change password
  6. POST /api/v1/auth/logout - Logout and blacklist token
  7. POST /api/v1/auth/revoke-all - Revoke all refresh tokens

#### Database
- **Migration** (`backend/alembic/versions/20251213_000000_add_production_auth_system.py`)
  - Created users, refresh_tokens, token_blacklist tables
  - Added user_id foreign key to students table
  - SQLite batch mode for ALTER TABLE operations

#### Security Features
- Bcrypt password hashing (cost factor 12)
- Standard JWT with HS256 algorithm
- Access token: 30-minute expiration
- Refresh token: 7-day expiration
- Token blacklist mechanism
- Refresh token rotation (one-time use)
- Role-based access control

#### Testing
- **Comprehensive Test Suite** (`backend/test_auth_api.py`)
  - 12 test scenarios with 100% pass rate
  - User registration and login tests
  - Token refresh and rotation tests
  - Password change and security tests
  - Token blacklist and revocation tests
  - Error handling tests
- **Test Report** (`backend/TEST_RESULTS.md`)

### Changed
- Migrated from in-memory authentication to database-backed JWT system
- Updated Student model with user_id foreign key
- Completely rewrote authentication API endpoints

### Fixed
- Import path issues (backend.* → relative imports)
- Bcrypt compatibility (passlib → direct bcrypt)
- SQLAlchemy lazy loading (added db.refresh)
- CRUD parameter types (Pydantic → dict)

### Documentation
- Updated TODO.md with completed authentication tasks
- Added TEST_RESULTS.md with comprehensive test report
- Updated project status to "Production JWT Auth ✅"

---

## [1.1.0] - 2024-12-02

### Added - Enhanced Debugging Environment
- One-click startup system with parallel service launching
- Real-time debug panel with API monitoring
- Advanced backend logging with request correlation
- Environment check script with system validation
- Development documentation

### Added - Expanded Feedback Template Library
- Expanded from 29 to 103 templates
- Language-specific templates (Python, JavaScript, Java, C++)
- Performance, error handling, testing, and algorithm templates
- Tone variants (Encouraging, Strict, Professional)
- Chinese locale templates

---

## [1.0.0] - 2024-11-30

### Added - MVP Release
- User authentication (login, registration, logout)
- Assignment submission with Monaco Code Editor
- File upload with language detection
- Grades viewing with filtering and sorting
- Student dashboard
- Frontend-backend integration
- API documentation (Swagger UI)
- Intelligent feedback generation system
- Enhanced code analysis system
- Multi-dimensional evaluation system

---

[Unreleased]: https://github.com/sst2020/ai-teaching-assistant/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/sst2020/ai-teaching-assistant/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/sst2020/ai-teaching-assistant/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/sst2020/ai-teaching-assistant/releases/tag/v1.0.0

