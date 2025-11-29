# AI Teaching Assistant

An AI-powered teaching assistant platform that provides automated assignment grading, code analysis, plagiarism detection, and intelligent Q&A support for educational institutions.

## Overview

This project consists of two main components:

- **Backend**: FastAPI-based REST API with SQLAlchemy ORM for database management
- **Frontend**: React-based web application for user interface

## Features

- 📚 **Student Management**: Register, authenticate, and manage student records
- 📝 **Assignment Management**: Create and manage course assignments with rubrics
- 📤 **Submission Tracking**: Track student submissions with status updates
- 🤖 **AI-Powered Grading**: Automated evaluation of code and essay submissions
- 🔍 **Code Analysis**: Static analysis with PEP 8 compliance and complexity metrics
- 🔒 **Plagiarism Detection**: AST-based similarity detection for code submissions
- 💬 **Q&A System**: AI-powered question answering with teacher escalation

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

The backend uses SQLAlchemy ORM with support for SQLite (development) and PostgreSQL (production).

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
| `DATABASE_URL` | Database connection string | `sqlite:///./teaching_assistant.db` |
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

## Roadmap & Contributing

See the TODO list for a comprehensive list of tasks:
- 📄 **[TODO.md](./TODO.md)** (English)
- 📄 **[TODO_zh-CN.md](./TODO_zh-CN.md)** (简体中文)

**Task Categories:**
- 🔐 Security & Authentication tasks
- 🖥️ Frontend development tasks
- ⚙️ Backend enhancement tasks
- 🧪 Testing requirements
- 📚 Documentation needs
- 🚀 DevOps & Deployment tasks

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
| Add student endpoint tests | Easy | `backend/tests/test_students.py` |
| Implement React Router | Easy | `frontend/src/App.tsx` |
| Add toast notifications | Easy | `frontend/src/components/` |
| Create contributing guide | Easy | `CONTRIBUTING.md` |

## License

GPL-3.0 License - See [LICENSE](./LICENSE) for details.
