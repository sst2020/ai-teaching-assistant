# AI Teaching Assistant - Frontend

A React-based frontend application for the AI Teaching Assistant platform, providing an intuitive interface for student learning support, including assignment submission, AI grading, plagiarism detection, and Q&A assistance.

## 🎯 System Overview

This system is **dedicated to student learning support** and works in conjunction with a separate **Assignment Management System** for teachers to create and manage assignments.

### System Responsibilities

**This System (Student Learning Support)**:
- ✅ Student assignment submission
- ✅ AI-powered automated grading
- ✅ Plagiarism detection and originality reports
- ✅ Code analysis and feedback
- ✅ Q&A assistance for programming topics
- ✅ Viewing grades and submission history

**External Management System** (`E:\Code\repo\管理系统`):
- 📋 Creating and editing assignments
- 📋 Managing courses and classes
- 📋 Task distribution and scheduling

## Features

### For Students
- 🏠 **Student Dashboard**: View courses, assignments, and submission history
- 📝 **Assignment Submission**: Submit code with Monaco editor or file upload
- 📊 **Grades View**: Check graded submissions with detailed feedback
- 💬 **Q&A Assistant**: AI-powered question answering for programming topics

### For Teachers
- 📈 **Teacher Dashboard**: Overview of assignments and grading statistics
- ✏️ **Grading Interface**: Review AI grading results and provide manual overrides
- 🔍 **Plagiarism Detection**: Batch upload and similarity analysis
- 📊 **Code Analysis**: Detailed code quality reports
- 🎯 **Question Queue**: Manage and respond to student questions

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Axios** - HTTP client for API communication
- **CSS Modules** - Component styling

## Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` if needed:

```env
REACT_APP_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm start
```

The app will open at `http://localhost:3000`.

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm start` | Start development server |
| `npm run build` | Build for production |
| `npm test` | Run tests |
| `npm run eject` | Eject from Create React App |

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   │   ├── common/      # Shared components (LoadingSpinner, ErrorMessage)
│   │   ├── layout/      # Layout components (Header)
│   │   ├── Dashboard/   # Dashboard feature
│   │   ├── CodeAnalysis/# Code analysis feature
│   │   └── QAInterface/ # Q&A feature
│   ├── services/        # API service layer
│   ├── types/           # TypeScript type definitions
│   ├── App.tsx          # Main application component
│   └── index.tsx        # Application entry point
├── .env                 # Environment variables
├── .env.example         # Example environment file
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies and scripts
```

## API Integration

The frontend communicates with the FastAPI backend through the API service layer.

### Key API Endpoints

#### Assignment Management (Read-Only)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/assignments` | GET | List assignments with pagination |
| `/api/v1/assignments/{id}` | GET | Get assignment details |
| `/api/v1/assignments/stats` | GET | Get assignment statistics |
| `/api/v1/sync/assignments` | POST | Sync assignments from management system |

#### Grading & Evaluation
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/assignments/grade` | POST | Grade a single assignment |
| `/api/v1/assignments/batch-grade` | POST | Batch grade multiple assignments |
| `/api/v1/grading` | GET | List grading results |

#### Plagiarism Detection
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/assignments/plagiarism/check` | POST | Check plagiarism |
| `/api/v1/assignments/plagiarism/report` | GET | Get plagiarism report |

#### Code Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/assignments/analyze-code` | POST | Analyze code quality |

#### Q&A System
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/qa/ask` | POST | Ask a question |
| `/api/v1/qa/logs` | GET | Get Q&A history |

#### Health & Info
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |

### Example API Call

```typescript
import { analyzeCode } from './services/api';

const result = await analyzeCode({
  code: 'def hello(): print("Hello")',
  language: 'python',
  include_style: true,
  include_complexity: true,
});
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000` |
| `REACT_APP_NAME` | Application name | `AI Teaching Assistant` |
| `REACT_APP_VERSION` | Application version | `1.0.0` |

## Development

### Running with Backend

1. Start the backend server:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Open `http://localhost:3000` in your browser

### CORS Configuration

The backend is configured to accept requests from `http://localhost:3000`. If you change the frontend port, update the backend's CORS settings in `backend/core/config.py`.

## Building for Production

```bash
npm run build
```

The build output will be in the `build/` directory.

## Troubleshooting

### Backend Connection Issues

1. Ensure the backend is running on port 8000
2. Check the browser console for CORS errors
3. Verify `REACT_APP_API_URL` in `.env`

### TypeScript Errors

Run `npm install` to ensure all type definitions are installed.

## License

MIT

