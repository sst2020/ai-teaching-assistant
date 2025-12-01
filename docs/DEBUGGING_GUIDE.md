# Frontend-Backend Debugging Guide

This guide provides comprehensive instructions for debugging the AI Teaching Assistant application, including setup, API endpoints, and troubleshooting.

## Quick Start

### Starting Both Servers

**Backend (Terminal 1):**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm start
```

### Verify Services
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

## Configuration

### Frontend Environment (`frontend/.env`)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_NAME=AI Teaching Assistant
REACT_APP_VERSION=1.0.0
```

### Backend Environment (`backend/.env`)
Key settings for debugging:
```env
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
HOST=0.0.0.0
PORT=8000
```

## API Endpoints Reference

### Health & Info
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check with DB status |

### Authentication (`/api/v1/auth`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/login` | POST | User login |
| `/register` | POST | User registration |
| `/me` | GET | Get current user |
| `/refresh` | POST | Refresh token |
| `/logout` | POST | Logout |

### Students (`/api/v1/students`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/profile` | GET/PUT | Student profile |
| `/stats` | GET | Student statistics |
| `/courses` | GET | Enrolled courses |

### Assignments (`/api/v1/assignments`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | List assignments |
| `/{id}` | GET | Get assignment |
| `/analyze-code` | POST | Analyze code |
| `/grade` | POST | Grade submission |

### Submissions (`/api/v1/submissions`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET/POST | List/Create submissions |
| `/{id}` | GET/PUT/DELETE | Manage submission |
| `/stats` | GET | Submission statistics |

### Q&A (`/api/v1/qa`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Ask a question |

## Debugging Tools

### 1. Browser DevTools (F12)

**Network Tab:**
- Filter by `XHR` to see API calls
- Check request/response headers
- Verify CORS headers in responses
- Monitor request timing

**Console Tab:**
- API calls are logged: `[API] GET /health`
- Response data is logged: `[API] Response 200: {...}`
- Error details are logged: `[API] Response error: ...`

### 2. Backend API Documentation
Visit http://localhost:8000/docs for interactive Swagger UI:
- Test endpoints directly
- View request/response schemas
- Check authentication requirements

### 3. Frontend API Logging
The API client (`frontend/src/services/api.ts`) includes built-in logging:
```typescript
// Request interceptor logs all outgoing requests
console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);

// Response interceptor logs all responses
console.log(`[API] Response ${response.status}:`, response.data);
```

## Common Issues & Solutions

### CORS Errors
**Symptom:** `Access-Control-Allow-Origin` errors in console

**Solution:**
1. Verify `CORS_ORIGINS` in `backend/.env` includes your frontend URL
2. Ensure backend is running on port 8000
3. Check that frontend uses `http://localhost:8000` (not `127.0.0.1`)

### Connection Refused
**Symptom:** `ERR_CONNECTION_REFUSED` or network errors

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `REACT_APP_API_URL` in `frontend/.env`
3. Ensure no firewall blocking ports 3000/8000

### Authentication Issues
**Symptom:** 401 Unauthorized errors

**Solution:**
1. Check token in localStorage: `localStorage.getItem('access_token')`
2. Verify token is being sent: Check `Authorization` header in Network tab
3. Token may be expired - try logging in again

### Database Errors
**Symptom:** 500 errors or "database_status: error" in health check

**Solution:**
1. Check `DATABASE_URL` in `backend/.env`
2. Ensure SQLite file exists: `backend/teaching_assistant.db`
3. Run migrations if needed

## Network Inspection Tips

### Using PowerShell
```powershell
# Test health endpoint
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get

# Test with headers
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/me" `
  -Method Get `
  -Headers @{"Authorization"="Bearer YOUR_TOKEN"}
```

### Using curl (Git Bash)
```bash
# Test health
curl http://localhost:8000/health

# Test with auth
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/auth/me
```

## Process Management

### List Running Servers
```powershell
# Find processes on port 8000 (backend)
netstat -ano | findstr :8000

# Find processes on port 3000 (frontend)
netstat -ano | findstr :3000
```

### Kill Stuck Processes
```powershell
# Kill by PID
taskkill /PID <pid> /F
```

