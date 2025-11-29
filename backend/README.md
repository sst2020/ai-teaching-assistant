# AI Teaching Assistant Backend

A FastAPI-based backend service for an AI-powered teaching assistant that provides automated assignment grading, code analysis, plagiarism detection, and intelligent Q&A support.

## Features

- **Automated Assignment Grading**: AI-powered evaluation of code and report submissions
- **Code Static Analysis**: PEP 8 compliance, complexity metrics, and code smell detection
- **Plagiarism Detection**: AST-based code similarity detection that catches renamed variables
- **AI Q&A Triage**: Intelligent question answering with automatic categorization
- **OpenAI Integration**: GPT-4/GPT-3.5 support with local LLM fallback option

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
   
   # Edit .env and add your OpenAI API key (optional)
   ```

5. **Run the development server**:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

6. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### Health & Status
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with API info |
| `/health` | GET | Health check endpoint |

### Assignment Review (`/api/v1/assignments`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/grade` | POST | Grade a single assignment |
| `/grade/batch` | POST | Batch grade multiple assignments |
| `/analyze-code` | POST | Run static code analysis |
| `/plagiarism/check` | POST | Check submission for plagiarism |
| `/plagiarism/batch` | POST | Batch plagiarism check |
| `/upload` | POST | Upload and grade a file |

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
| `DEBUG` | Enable debug mode | `true` |
| `PORT` | Server port | `8000` |

## Project Structure

```
backend/
├── app/
│   └── main.py              # FastAPI application entry point
├── api/
│   ├── health.py            # Health check endpoints
│   ├── assignments.py       # Assignment grading endpoints
│   └── qa.py                # Q&A triage endpoints
├── core/
│   └── config.py            # Application configuration
├── models/                  # Database models (future)
├── schemas/
│   ├── assignment.py        # Assignment schemas
│   ├── code_analysis.py     # Code analysis schemas
│   ├── plagiarism.py        # Plagiarism detection schemas
│   └── qa.py                # Q&A schemas
├── services/
│   ├── ai_service.py        # AI/LLM integration
│   ├── code_analysis_service.py  # Static code analysis
│   ├── grading_service.py   # Assignment grading logic
│   ├── plagiarism_service.py    # Plagiarism detection
│   └── qa_service.py        # Q&A handling
├── utils/                   # Utility functions
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
└── README.md                # This file
```

## Development

### Running Tests
```bash
pytest
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

## Docker

Build and run with Docker:
```bash
docker build -t ai-teaching-assistant-backend .
docker run -p 8000:8000 --env-file .env ai-teaching-assistant-backend
```

## License

MIT License

