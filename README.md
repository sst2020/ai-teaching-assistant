# AI Teaching Assistant

An AI-powered teaching assistant platform that provides automated assignment grading, code analysis, plagiarism detection, and intelligent Q&A support for educational institutions.

## 🎉 MVP Status: Complete

The Minimum Viable Product (MVP) is now complete with full frontend-backend integration.

| Feature | Status |
|---------|--------|
| User Authentication | ✅ Complete |
| Assignment Submission | ✅ Complete |
| Code Editor (Monaco) | ✅ Complete |
| File Upload | ✅ Complete |
| Grades Viewing | ✅ Complete |
| Student Dashboard | ✅ Complete |
| API Documentation | ✅ Complete |
| Enhanced Code Analysis | ✅ Complete |
| Security Analysis | ✅ Complete |
| Performance Analysis | ✅ Complete |

**Quick Start:**
```bash
# Backend: http://localhost:8000
cd backend && python -m uvicorn app.main:app --reload --port 8000

# Frontend: http://localhost:3000
cd frontend && npm start
```

**Test Credentials:** `test@example.com` / `password123`

## Overview

This project consists of two main components:

- **Backend**: FastAPI-based REST API with SQLAlchemy ORM for database management
- **Frontend**: React 19 web application with Material Design 3 theme

## Features

- 📚 **Student Management**: Register, authenticate, and manage student records
- 📝 **Assignment Management**: Create and manage course assignments with rubrics
- 📤 **Submission Tracking**: Track student submissions with status updates
- 🤖 **AI-Powered Grading**: Automated evaluation of code and essay submissions
- 🔍 **Code Analysis**: Static analysis with PEP 8 compliance and complexity metrics
- 📊 **Advanced Quality Metrics**: Cyclomatic/cognitive complexity, maintainability index, code duplication detection
- 🛡️ **Security Analysis**: Bandit integration for vulnerability detection with Chinese translations
- ⚡ **Performance Analysis**: Anti-pattern detection, best practices evaluation
- 🔒 **Plagiarism Detection**: AST-based similarity detection for code submissions
- 💬 **Q&A System**: AI-powered question answering with teacher escalation
- 🎨 **Modern UI**: Material Design 3 with accessibility features
- ⚡ **Code Editor**: Monaco Editor with syntax highlighting for 10+ languages

## Quick Start

### Prerequisites

- Python 3.10+ (Backend)
- Node.js 18+ (Frontend)
- OpenAI API key (optional, for AI features)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start the server
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## API Documentation

Once the backend is running, access the API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key API Endpoints

| Category | Endpoint | Description |
|----------|----------|-------------|
| Health | `GET /health` | Health check with database status |
| Students | `POST /api/v1/students/register` | Register a new student |
| Students | `GET /api/v1/students/{id}` | Get student information |
| Assignments | `POST /api/v1/assignments` | Create an assignment |
| Assignments | `GET /api/v1/assignments` | List assignments |
| Submissions | `POST /api/v1/submissions` | Submit an assignment |
| Grading | `POST /api/v1/assignments/grade` | Grade a submission |
| Q&A | `POST /api/v1/qa/ask` | Ask a question |

## Project Structure

```
ai-teaching-assistant/
├── backend/                 # FastAPI backend
│   ├── alembic/             # Database migrations
│   ├── api/                 # API route handlers
│   ├── app/                 # Application entry point
│   ├── core/                # Configuration & database
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── frontend/                # React frontend
│   ├── public/              # Static assets
│   └── src/                 # React components
└── docs/                    # Documentation
```

## Database Schema

The backend uses SQLAlchemy ORM with MySQL 9 as the default database backend.

### Core Models

- **Student**: Student information and enrollment
- **Assignment**: Course assignments with rubrics
- **Submission**: Student submissions with status tracking
- **GradingResult**: AI and manual grading results
- **Question/Answer**: Q&A system data
- **PlagiarismCheck**: Plagiarism detection results

## Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `mysql+aiomysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant` |
| `OPENAI_API_KEY` | OpenAI API key | (empty) |
| `AI_MODEL` | OpenAI model to use | `gpt-4` |
| `DEBUG` | Enable debug mode | `true` |
| `PORT` | Server port | `8000` |

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Backend MySQL integration tests
$env:TEST_DATABASE_URL="mysql+aiomysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant"  # Windows PowerShell
# export TEST_DATABASE_URL="mysql+aiomysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant"  # Linux/macOS
pytest tests/test_students.py tests/test_submissions.py tests/test_crud.py tests/test_qa.py tests/test_file_upload.py

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend
cd backend
black .          # Format code
isort .          # Sort imports
ruff check .     # Lint code
mypy .           # Type check

# Frontend
cd frontend
npm run lint     # Lint code
```

## Docker

### Build and Run

```bash
# Backend
cd backend
docker build -t ai-ta-backend .
docker run -p 8000:8000 --env-file .env ai-ta-backend

# Frontend
cd frontend
docker build -t ai-ta-frontend .
docker run -p 3000:3000 ai-ta-frontend
```

## Documentation

| Document | Description |
|----------|-------------|
| [User Interface Guide](docs/USER_INTERFACE_GUIDE.md) | Pages, workflows, accessibility, MD3 theme |
| [System Testing Report](docs/SYSTEM_TESTING_REPORT.md) | Test results, API testing, performance metrics |
| [Debugging Guide](docs/DEBUGGING_GUIDE.md) | Setup, API reference, troubleshooting |

## Roadmap & Contributing

See the TODO list for a comprehensive list of tasks:
- 📄 **[TODO.md](./TODO.md)** (English)
- 📄 **[TODO_zh-CN.md](./TODO_zh-CN.md)** (简体中文)

**Completed (MVP):**
- ✅ User Authentication (Login, Register, Logout)
- ✅ Frontend UI (React Router, Toast, Accessibility)
- ✅ Assignment Submission with Monaco Editor
- ✅ Grades Display with Charts and Filtering
- ✅ API Integration

**Remaining Tasks:**
- 🔐 Production authentication with database storage
- 🔴 Role-based access control (RBAC)
- 🖥️ Teacher/Admin dashboards
- ⚙️ Real AI grading integration
- 🧪 Comprehensive test suite
- 🚀 CI/CD pipeline

### How to Contribute

1. Check [TODO.md](./TODO.md) or [TODO_zh-CN.md](./TODO_zh-CN.md) for available tasks
2. Fork the repository
3. Create a feature branch (`git checkout -b feature/your-feature`)
4. Make your changes with tests
5. Run tests (`pytest` for backend, `npm test` for frontend)
6. Submit a pull request

### Recommended First Tasks

| Task | Complexity | File |
|------|------------|------|
| Add production JWT auth | Medium | `backend/core/security.py` |
| Add dark mode support | Easy | `frontend/src/contexts/ThemeContext.tsx` |
| Create Teacher dashboard | Medium | `frontend/src/pages/TeacherDashboard.tsx` |
| Add E2E tests | Medium | `tests/e2e/` |

## License

MIT License - See [LICENSE](./LICENSE) for details.
