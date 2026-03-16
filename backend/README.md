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
- **Database-Backed**: SQLAlchemy ORM with MySQL 9 (default) and optional SQLite in-memory unit tests
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
| `DATABASE_URL` | Database connection string | `mysql+aiomysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant` |
| `DATABASE_ECHO` | Log SQL queries | `false` |
| `DEBUG` | Enable debug mode | `true` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

### Database Configuration

The application supports MySQL 9 as the default backend:

**MySQL 9 (Default, Async Runtime)**:
```
DATABASE_URL=mysql+aiomysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant
```

**MySQL 9 (Alembic/Sync Scripts)**:
```
DATABASE_URL=mysql+pymysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant
```

**SQLite (Optional Unit Tests Only)**:
```
DATABASE_URL=sqlite:///./teaching_assistant.db
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

To reseed on MySQL, reset the schema with migrations and then run the seed script:
```bash
alembic downgrade base
alembic upgrade head
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

### Running MySQL Integration Tests
```bash
# PowerShell
$env:TEST_DATABASE_URL="mysql+aiomysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant"
pytest tests/test_students.py tests/test_submissions.py tests/test_crud.py tests/test_qa.py tests/test_file_upload.py -q

# Linux/macOS
export TEST_DATABASE_URL="mysql+aiomysql://ai_teaching:ai_teaching_dev@localhost:3306/ai_teaching_assistant"
pytest tests/test_students.py tests/test_submissions.py tests/test_crud.py tests/test_qa.py tests/test_file_upload.py -q
```

Before running the MySQL suite, apply migrations:

```bash
alembic upgrade head
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

1. **MySQL connection refused**: Ensure MySQL is running and the connection string is correct.

2. **Migration issues**: Reset and re-run migrations if schemas drift:
   ```bash
   mysqladmin ping -h localhost -u <user> -p
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

### Docker Compose (with MySQL 9)
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+aiomysql://ai_teaching:ai_teaching_dev@mysql:3306/ai_teaching_assistant
    depends_on:
      - mysql

  mysql:
    image: mysql:9
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=teaching_assistant
      - MYSQL_USER=ai_teaching
      - MYSQL_PASSWORD=ai_teaching_dev
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

TODO:
请解决以下四个关键问题，按优先级顺序执行：

**优先级 1 - Q&A 功能修复和本地化**
1. 修复 Q&A 界面中 AI 功能无法正常工作的问题
   - 检查前端 QA 组件与后端 DeepSeek API 的集成
   - 确保 API 调用正确传递到已配置的 DeepSeek 服务
   - 测试问答功能的完整流程
2. 完成界面汉化工作
   - 识别所有未汉化的页面和组件
   - 将英文文本替换为对应的中文文本
   - 确保用户界面完全中文化

**优先级 2 - 用户认证系统改进**
3. 修改登录注册系统，从邮箱认证改为学号认证
   - 将用户标识从邮箱格式改为10位学号格式
   - 更新登录页面的输入验证规则
   - 修改注册页面的字段要求
   - 更新后端用户模型和验证逻辑

**优先级 3 - 功能完善**
4. 完成报告分析功能的开发
   - 实现报告分析的核心功能
   - 添加相应的前端界面
   - 集成后端分析服务

**优先级 4 - 界面架构优化**
5. 分离用户界面和管理界面
   - 创建独立的学生用户界面
   - 创建独立的教师/管理员界面
   - 实现基于角色的界面访问控制
   - 优化导航和用户体验

请先从优先级 1 开始，逐步解决每个问题，每完成一个优先级后请确认再继续下一个。

## License

MIT License


