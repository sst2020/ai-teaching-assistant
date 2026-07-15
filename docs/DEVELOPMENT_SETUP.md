# Development Setup

This is the single setup and debugging guide for the repository. Older install summaries and separate debugging notes were retired so the active workflow lives here.

## Prerequisites

- Node.js 18+
- npm 9+
- Python 3.10+
- A virtual environment tool for backend work
- MySQL only if you want full integration instead of SQLite-based local checks

## Environment Files

Use the app-local templates as the source of truth:

- `backend/.env.example` -> copy to `backend/.env`
- `frontend/.env.example` -> copy to `frontend/.env`

Root `.env.development`, `.env.staging`, and `.env.production` are workspace or deployment presets for compose-style workflows. They are not read by `backend/core/config.py` during local backend startup.

## Quick Start

From the repository root:

```bash
npm run check:env
npm run dev
```

Manual startup:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```bash
cd frontend
npm install
npm start
```

## Recommended Local Configuration

Backend:

```env
DEBUG=true
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./teaching_assistant.db
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

Frontend:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_DEBUG_MODE=true
REACT_APP_ENABLE_DEBUG_PANEL=true
REACT_APP_ENABLE_API_LOGGING=true
REACT_APP_ENABLE_PERFORMANCE_MONITORING=true
```

## Verification Endpoints

- Frontend: `http://localhost:3000`
- Backend health: `http://localhost:8000/health`
- Backend OpenAPI docs: `http://localhost:8000/docs`

## Debugging Workflow

Frontend debugging is controlled by the optional `REACT_APP_*` flags in `frontend/.env.example`.

- `REACT_APP_ENABLE_DEBUG_PANEL=true` shows the in-app debug panel in development.
- `REACT_APP_ENABLE_API_LOGGING=true` enables verbose request and response logging in `frontend/src/services/api.ts`.
- `REACT_APP_ENABLE_PERFORMANCE_MONITORING=true` stores request timing data for the debug UI.
- `REACT_APP_AUTO_OPEN_DEVTOOLS=true` lets the debug panel request browser devtools where supported.

Backend debugging is driven by `backend/.env`.

- `DEBUG=true` and `LOG_LEVEL=INFO` or `DEBUG` are the main local toggles.
- `DATABASE_ECHO=true` is useful when you need SQLAlchemy query visibility.
- `USE_DEEPSEEK`, `USE_FASTCHAT`, and OpenAI-compatible settings are all surfaced in `backend/.env.example`.

## Troubleshooting

Port already in use:

```powershell
netstat -ano | findstr :3000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Frontend cannot reach backend:

- Confirm `REACT_APP_API_URL` matches the backend port.
- Confirm backend CORS origins include the frontend origin.
- Confirm the backend is serving `GET /health`.

Backend configuration not loading:

- Make sure the file is `backend/.env`, not a root `.env`.
- `backend/core/config.py` resolves its env file relative to the `backend/` directory.

Dependency reset:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
```

## Related Docs

- [Repository Structure](./REPOSITORY_STRUCTURE.md)
- [System Testing Report](./SYSTEM_TESTING_REPORT.md)
- [User Interface Guide](./USER_INTERFACE_GUIDE.md)
- [Backend README](../backend/README.md)
- [Frontend README](../frontend/README.md)
