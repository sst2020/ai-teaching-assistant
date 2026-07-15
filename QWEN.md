# AI Teaching Assistant - Project Documentation

## Project Overview

The AI Teaching Assistant is a comprehensive educational technology platform that provides automated assignment grading, code analysis, plagiarism detection, and intelligent Q&A support for educational institutions. The project consists of two main components:

- **Backend**: FastAPI-based REST API with SQLAlchemy ORM for database management
- **Frontend**: Vue 3 web application with Element Plus UI framework

The project is currently in a complete MVP state with full frontend-backend integration, featuring user authentication, assignment management, code editor integration, file uploads, grades viewing, and an intelligent Q&A system.

## Architecture & Technologies

### Backend Stack
- **Framework**: FastAPI (Python 3.10+)
- **Database**: SQLAlchemy ORM with support for SQLite (development) and PostgreSQL (production)
- **Authentication**: Production-grade JWT with bcrypt password hashing, refresh token rotation, and token blacklisting
- **AI/LLM Integration**: OpenAI API with local LLM fallback option
- **Code Analysis**: Pylint, Radon, Bandit for static analysis and quality metrics
- **Document Processing**: python-docx, PyPDF2
- **Testing**: pytest, pytest-asyncio
- **Development Tools**: black, isort, mypy, ruff

### Frontend Stack
- **Framework**: Vue 3 with TypeScript
- **Routing**: Vue Router
- **Styling**: Element Plus with CSS variables
- **Code Editor**: Monaco Editor with syntax highlighting for 10+ languages
- **HTTP Client**: Axios
- **State Management**: Pinia
- **Testing**: Vitest (待配置)

## Building and Running

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
npm run dev
```

### Quick Start with Scripts
The project includes cross-platform startup scripts:
```bash
# Unix/Linux/macOS
./dev-start.sh

# Windows
dev-start.bat
```

### Docker Deployment
```bash
# Using Docker Compose
docker-compose up --build
```

## Key Features

### Core Functionality
- **Student Management**: Complete CRUD operations for student registration and management
- **Assignment Management**: Create and manage course assignments with rubrics
- **Submission Tracking**: Track student submissions with status updates
- **AI-Powered Grading**: Automated evaluation of code and essay submissions
- **Code Static Analysis**: PEP 8 compliance, complexity metrics, and code smell detection
- **Plagiarism Detection**: AST-based code similarity detection that catches renamed variables
- **AI Q&A Triage**: Intelligent question answering with automatic categorization
- **OpenAI Integration**: GPT-4/GPT-3.5 support with local LLM fallback option

### Advanced Features
- **Intelligent Feedback Generation**: Context-aware feedback with multiple tones and categories
- **Enhanced Code Analysis**: Cyclomatic/cognitive complexity, maintainability index, code duplication detection
- **Security Analysis**: Bandit integration for vulnerability detection with Chinese translations
- **Performance Analysis**: Anti-pattern detection, best practices evaluation
- **Multi-Dimensional Evaluation**: 6 evaluation dimensions with radar chart visualization
- **Personalized Feedback**: Student history analysis with progressive suggestions

### User Interface
- **Modern UI**: Element Plus with accessibility features
- **Responsive Design**: Mobile-friendly layouts
- **Accessibility**: Screen reader support, keyboard navigation, focus indicators
- **Dark Mode**: Theme context with persistent preferences
- **Code Editor**: Monaco Editor with syntax highlighting for 10+ languages

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

## Database Schema

The application uses SQLAlchemy ORM with the following core models:
- **Student**: Student information and enrollment
- **Assignment**: Course assignments with rubrics
- **Submission**: Student submissions with status tracking
- **GradingResult**: AI and manual grading results
- **Question/Answer**: Q&A system data
- **PlagiarismCheck**: Plagiarism detection results
- **Rubric**: Grading rubrics for assignments
- **User**: Authentication and authorization
- **RefreshToken**: JWT refresh token management
- **TokenBlacklist**: Revoked token tracking
- **AuthLog**: Authentication event logging

## Configuration

### Backend Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./teaching_assistant.db` |
| `OPENAI_API_KEY` | OpenAI API key | (empty) |
| `AI_MODEL` | OpenAI model to use | `gpt-4` |
| `DEBUG` | Enable debug mode | `true` |
| `PORT` | Server port | `8000` |
| `SECRET_KEY` | JWT secret key | `change-this-in-production` |

### Frontend Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |
| `VITE_DEBUG_MODE` | Enable debug features | `false` |

## Development Practices

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
npm run format   # Format code
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Testing Structure
- Backend tests use pytest with conftest.py for fixtures
- Frontend tests use Vitest (待配置)

## Current Development Status

The project has completed its MVP with the following features:
- ✅ User Authentication (Login, Register, Logout)
- ✅ Frontend UI (Vue Router, Toast, Accessibility)
- ✅ Assignment Submission with Monaco Editor
- ✅ Grades Display with Charts and Filtering
- ✅ API Integration
- ✅ Production-grade JWT authentication
- ✅ Advanced code analysis capabilities
- ✅ Plagiarism detection system
- ✅ Intelligent feedback generation
- ✅ Multi-dimensional evaluation system

### Remaining Tasks
- 🔐 Production authentication with database storage
- 🔴 Role-based access control (RBAC)
- 🖥️ Teacher/Admin dashboards
- ⚙️ Real AI grading integration
- 🧪 Comprehensive test suite
- 🚀 CI/CD pipeline

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
├── frontend/                # Vue 3 frontend
│   ├── public/              # Static assets
│   └── src/                 # Vue components
├── scripts/                 # Development and deployment scripts
├── docs/                    # Documentation
└── docker-compose.yml       # Container orchestration
```

## Contribution Guidelines

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