# AI Teaching Assistant Backend

A FastAPI-based backend service for an AI-powered teaching assistant that provides automated assignment grading, code analysis, plagiarism detection, and intelligent Q&A support. Built with SQLAlchemy ORM for robust database management.

## Features

- **Student Management**: Complete CRUD operations for student registration and management
- **Assignment Management**: Create, update, and manage course assignments
- **Submission Tracking**: Track and manage student submissions with status updates
- **Automated Assignment Grading**: AI-powered evaluation of code and report submissions
- **Code Static Analysis**: PEP 8 compliance, complexity metrics, and code smell detection
- **Plagiarism Detection**: AST-based code similarity detection that catches renamed variables
- **AI Q&A Triage**: Intelligent question answering with automatic categorization
- **OpenAI Integration**: GPT-4/GPT-3.5 support with local LLM fallback option
- **Database-Backed**: SQLAlchemy ORM with SQLite (development) or PostgreSQL (production)
- **Database Migrations**: Alembic for schema versioning and migrations

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- OpenAI API key (optional, for AI features)

### Installation

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and configure your settings
   ```

5. **Initialize the database**:
   ```bash
   # Run Alembic migrations
   alembic upgrade head

   # Or let the app auto-create tables on startup (development only)
   ```

6. **Run the development server**:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

7. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - ReDoc Documentation: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## API Endpoints

### Health & Status
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with API info |
| `/health` | GET | Health check with database status |

### Student Management (`/api/v1/students`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register` | POST | Register a new student |
| `/login` | POST | Student login/authentication |
| `/` | GET | List all students (paginated) |
| `/{student_id}` | GET | Get student by ID |
| `/{student_id}` | PUT | Update student information |
| `/{student_id}` | DELETE | Delete a student |

### Assignment Management (`/api/v1/assignments`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | POST | Create a new assignment |
| `/` | GET | List all assignments (paginated) |
| `/course/{course_id}` | GET | Get assignments by course |
| `/{assignment_id}` | GET | Get assignment by ID |
| `/{assignment_id}` | PUT | Update assignment |
| `/{assignment_id}` | DELETE | Delete assignment |
| `/grade` | POST | Grade a single assignment |
| `/grade/batch` | POST | Batch grade multiple assignments |
| `/analyze-code` | POST | Run static code analysis |
| `/plagiarism/check` | POST | Check submission for plagiarism |
| `/plagiarism/batch` | POST | Batch plagiarism check |
| `/upload` | POST | Upload and grade a file |

### Submission Management (`/api/v1/submissions`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | POST | Submit an assignment |
| `/{submission_id}` | GET | Get submission details |
| `/student/{student_id}` | GET | Get student's submissions |
| `/assignment/{assignment_id}` | GET | Get assignment submissions |
| `/{submission_id}/status` | PUT | Update submission status |

### Q&A Triage (`/api/v1/qa`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Submit a question for AI answering |
| `/escalate` | POST | Escalate question to teacher |
| `/analytics/{course_id}` | GET | Get Q&A analytics report |

## Configuration

All configuration is done through environment variables. See `.env.example` for all options.

### Key Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | (empty) |
| `AI_MODEL` | OpenAI model to use | `gpt-4` |
| `DATABASE_URL` | Database connection string | `sqlite:///./teaching_assistant.db` |
| `DATABASE_ECHO` | Log SQL queries | `false` |
| `DEBUG` | Enable debug mode | `true` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

### Database Configuration

The application supports multiple database backends:

**SQLite (Development)**:
```
DATABASE_URL=sqlite:///./teaching_assistant.db
```

**PostgreSQL (Production)**:
```
DATABASE_URL=postgresql://user:password@localhost:5432/teaching_assistant
```

**MySQL**:
```
DATABASE_URL=mysql://user:password@localhost:3306/teaching_assistant
```

## Database Schema

The application uses SQLAlchemy ORM with the following models:

### Core Models

| Model | Description |
|-------|-------------|
| `Student` | Student information (id, student_id, name, email, course_id) |
| `Assignment` | Assignment details (id, assignment_id, title, type, course_id, due_date) |
| `Submission` | Student submissions (id, submission_id, student_id, assignment_id, content, status) |
| `GradingResult` | Grading results with scores and feedback |
| `Question` | Student questions for Q&A system |
| `Answer` | AI-generated or teacher answers |
| `PlagiarismCheck` | Plagiarism detection results |
| `Rubric` | Grading rubrics for assignments |

### Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   Student   │       │  Assignment  │       │   Rubric    │
├─────────────┤       ├──────────────┤       ├─────────────┤
│ id          │       │ id           │       │ id          │
│ student_id  │       │ assignment_id│◄──────│ rubric_id   │
│ name        │       │ title        │       │ name        │
│ email       │       │ description  │       │ criteria    │
│ course_id   │       │ type         │       └─────────────┘
│ enrollment  │       │ course_id    │
└──────┬──────┘       │ due_date     │
       │              │ max_score    │
       │              └──────┬───────┘
       │                     │
       │    ┌────────────────┴────────────────┐
       │    │                                 │
       ▼    ▼                                 ▼
┌──────────────────┐                 ┌─────────────────┐
│   Submission     │                 │ PlagiarismCheck │
├──────────────────┤                 ├─────────────────┤
│ id               │                 │ id              │
│ submission_id    │                 │ submission_id   │
│ student_id (FK)  │                 │ similarity_score│
│ assignment_id(FK)│                 │ flagged         │
│ content          │                 └─────────────────┘
│ status           │
│ submitted_at     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  GradingResult   │
├──────────────────┤
│ id               │
│ submission_id(FK)│
│ score            │
│ feedback         │
│ graded_by        │
└──────────────────┘
```

## Project Structure

```
backend/
├── alembic/                 # Database migrations
│   ├── versions/            # Migration scripts
│   └── env.py               # Alembic configuration
├── app/
│   └── main.py              # FastAPI application entry point
├── api/
│   ├── health.py            # Health check endpoints
│   ├── students.py          # Student management endpoints
│   ├── assignments.py       # Assignment CRUD & grading endpoints
│   ├── submissions.py       # Submission management endpoints
│   └── qa.py                # Q&A triage endpoints
├── core/
│   ├── config.py            # Application configuration
│   └── database.py          # Database engine & session management
├── models/
│   ├── base.py              # Base model with timestamps
│   ├── student.py           # Student model
│   ├── assignment.py        # Assignment model
│   ├── submission.py        # Submission model
│   ├── grading_result.py    # Grading result model
│   ├── question.py          # Question model
│   ├── answer.py            # Answer model
│   ├── plagiarism_check.py  # Plagiarism check model
│   └── rubric.py            # Rubric model
├── schemas/
│   ├── student.py           # Student request/response schemas
│   ├── assignment.py        # Assignment grading schemas
│   ├── assignment_crud.py   # Assignment CRUD schemas
│   ├── submission.py        # Submission schemas
│   ├── code_analysis.py     # Code analysis schemas
│   ├── plagiarism.py        # Plagiarism detection schemas
│   └── qa.py                # Q&A schemas
├── services/
│   ├── ai_service.py        # AI/LLM integration
│   ├── code_analysis_service.py  # Static code analysis
│   ├── grading_service.py   # Assignment grading logic
│   ├── plagiarism_service.py    # Plagiarism detection
│   └── qa_service.py        # Q&A handling
├── utils/
│   └── crud.py              # CRUD utility functions
├── scripts/
│   └── seed_database.py     # Database seeding script
├── alembic.ini              # Alembic configuration
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
└── README.md                # This file
```

## Database Migrations

The project uses Alembic for database migrations.

### Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# Create a new migration
alembic revision --autogenerate -m "Description of changes"
```

### Initial Setup

On first run, the application will automatically create all database tables. For production, use migrations:

```bash
# Initialize database with migrations
alembic upgrade head
```

### Seeding the Database

For development and testing, you can populate the database with sample data:

```bash
# Run the seeding script
python -m scripts.seed_database
```

This creates:
- 5 sample students
- 3 sample assignments (code, essay, quiz)
- 3 sample submissions

To reseed, delete the database file first:
```bash
rm teaching_assistant.db
python -m scripts.seed_database
```

## API Examples

### Register a Student

```bash
curl -X POST "http://localhost:8000/api/v1/students/register" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU001",
    "name": "John Doe",
    "email": "john@example.com",
    "course_id": "CS101"
  }'
```

**Response:**
```json
{
  "id": 1,
  "student_id": "STU001",
  "name": "John Doe",
  "email": "john@example.com",
  "course_id": "CS101",
  "enrollment_date": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Create an Assignment

```bash
curl -X POST "http://localhost:8000/api/v1/assignments" \
  -H "Content-Type: application/json" \
  -d '{
    "assignment_id": "ASN001",
    "title": "Python Basics",
    "description": "Introduction to Python programming",
    "assignment_type": "code",
    "course_id": "CS101",
    "max_score": 100.0
  }'
```

### Submit an Assignment

```bash
curl -X POST "http://localhost:8000/api/v1/submissions" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU001",
    "assignment_id": "ASN001",
    "content": "print(\"Hello, World!\")"
  }'
```

### List Students with Pagination

```bash
curl "http://localhost:8000/api/v1/students?page=1&page_size=20&course_id=CS101"
```

**Response:**
```json
{
  "items": [...],
  "total": 50,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### Health Check

```bash
curl "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00",
  "database_status": "connected"
}
```

## Development

### Running Tests
```bash
pytest
```

### Running Tests with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Code Formatting
```bash
black .
isort .
```

### Type Checking
```bash
mypy .
```

### Linting
```bash
ruff check .
```

## Troubleshooting

### Database Connection Issues

1. **SQLite "database is locked"**: This usually happens with concurrent access. For production, use PostgreSQL.

2. **PostgreSQL connection refused**: Ensure PostgreSQL is running and the connection string is correct:
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   ```

3. **Migration errors**: If migrations fail, try:
   ```bash
   # Reset migrations (development only!)
   alembic downgrade base
   alembic upgrade head
   ```

### Common Issues

- **Import errors**: Ensure you're in the `backend` directory and virtual environment is activated
- **Port already in use**: Change the port in `.env` or kill the existing process
- **OpenAI API errors**: Check your API key and rate limits

## Docker

Build and run with Docker:
```bash
docker build -t ai-teaching-assistant-backend .
docker run -p 8000:8000 --env-file .env ai-teaching-assistant-backend
```

### Docker Compose (with PostgreSQL)
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/teaching_assistant
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=teaching_assistant
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## License

MIT License

