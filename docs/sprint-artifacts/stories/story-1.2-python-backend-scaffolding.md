# Story 1.2: Python Backend Scaffolding

**Epic:** Epic 1 - Foundation & Core Infrastructure  
**Story ID:** 1.2  
**Title:** Python Backend Scaffolding  
**Status:** Drafted  
**Created:** 2025-11-28  
**Story Points:** 3  
**Priority:** High  
**Assigned To:** DEV Agent  

---

## Story Description

### User Story

**As a** developer setting up AutoResumeFiller  
**I want** a functional FastAPI backend with proper configuration and health check endpoint  
**So that** the Chrome Extension and GUI can communicate with the backend server and I can verify the system is running correctly

### Context

Story 1.1 established the repository structure with placeholder files. Story 1.2 implements the FastAPI backend scaffolding - the HTTP server that will orchestrate AI providers, manage user data, and process form-filling requests. This story delivers a minimal but functional backend that:

1. **Runs successfully** on `localhost:8765` with uvicorn ASGI server
2. **Provides health check endpoint** (`GET /api/status`) for system verification
3. **Configures CORS** to allow Chrome Extension (`chrome-extension://*`) communication
4. **Loads settings** from environment variables via pydantic-settings
5. **Establishes patterns** for async/await, logging, and error handling

While this story doesn't implement AI or data management features (those come in later epics), it creates the foundation that all future backend endpoints will build upon. The health check endpoint serves as a contract validator - if it responds with `{"status": "healthy"}`, the system is operational.

### Dependencies

- ✅ **Story 1.1:** Project Initialization & Repository Setup (COMPLETED)
  - Requires `backend/` directory structure
  - Requires `pyproject.toml` with tool configurations
  - Requires `.gitignore` for secrets exclusion

- 📦 **External Dependencies:**
  - Python 3.9+ installed on system
  - pip package manager
  - Virtual environment tooling (venv module)

### Technical Approach

**Implementation Strategy:**

1. **Populate `backend/requirements.txt`** with FastAPI + dependencies (fastapi, uvicorn, pydantic, pydantic-settings)
2. **Create `backend/config/settings.py`** with Pydantic `Settings` class loading from `.env`
3. **Implement `backend/main.py`** with:
   - FastAPI app initialization
   - CORS middleware configuration
   - Health check endpoint (`GET /api/status`)
   - Startup/shutdown event handlers
   - Logging setup
4. **Create `.env.example`** template file (no secrets, just structure)
5. **Write unit tests** in `backend/tests/test_main.py` for health check endpoint
6. **Validate** uvicorn can start server and health check responds correctly

**Key Design Decisions:**

- **pydantic-settings over python-dotenv alone:** Type-safe configuration with validation
- **Structured logging:** JSON format for future log aggregation (Epic 6)
- **CORS whitelist:** Only `chrome-extension://*` origins (security-first)
- **127.0.0.1 binding:** Not `0.0.0.0` to prevent external network access (privacy-first)
- **Async patterns from start:** Use `async def` for all endpoints to enable future concurrent operations

---

## Acceptance Criteria

### AC1: Backend Dependencies Installed

**Given** the repository cloned and Python 3.9+ available  
**When** running `pip install -r backend/requirements.txt` in a virtual environment  
**Then** all dependencies install successfully without errors:
- `fastapi>=0.104.0`
- `uvicorn[standard]>=0.24.0`
- `pydantic>=2.5.0`
- `pydantic-settings>=2.1.0`
- `python-multipart>=0.0.6`
- `python-dotenv>=1.0.0`

**Verification:**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
pip list | Select-String "fastapi|uvicorn|pydantic"
# Should show all packages with correct versions
```

---

### AC2: Settings Configuration Implemented

**Given** the backend dependencies installed  
**When** `backend/config/settings.py` is created  
**Then** it contains a Pydantic `Settings` class with:

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Server Configuration
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8765
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["chrome-extension://*"]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Application Metadata
    APP_NAME: str = "AutoResumeFiller Backend API"
    APP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
```

**Verification:**
```powershell
python -c "from backend.config.settings import Settings; s = Settings(); print(f'API_HOST: {s.API_HOST}, API_PORT: {s.API_PORT}')"
# Should print: API_HOST: 127.0.0.1, API_PORT: 8765
```

---

### AC3: FastAPI Application Initialized

**Given** `backend/config/settings.py` exists  
**When** `backend/main.py` is implemented  
**Then** it contains:

**Required Components:**
1. **FastAPI app instance** with title, description, version from settings
2. **CORS middleware** configured with `settings.CORS_ORIGINS`
3. **Startup event handler** logging "Backend API started" with host/port
4. **Shutdown event handler** logging "Backend API shutting down"
5. **Health check endpoint** at `GET /api/status` returning:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "timestamp": "2025-11-28T10:00:00.000Z"
   }
   ```
6. **Root endpoint** at `GET /` with API documentation redirect

**Code Template:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from backend.config.settings import Settings

# Initialize settings
settings = Settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for AutoResumeFiller - Intelligent job application form auto-filling",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Log backend startup."""
    logger.info(f"Backend API started on {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")

@app.on_event("shutdown")
async def shutdown_event():
    """Log backend shutdown."""
    logger.info("Backend API shutting down")

@app.get("/")
async def root():
    """Root endpoint - redirect to API docs."""
    return {
        "message": "AutoResumeFiller Backend API",
        "docs": "/docs",
        "health": "/api/status"
    }

@app.get("/api/status")
async def health_check():
    """Health check endpoint for system verification."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
```

**Verification:**
```powershell
python -c "from backend.main import app; print(f'App title: {app.title}')"
# Should print: App title: AutoResumeFiller Backend API
```

---

### AC4: Backend Server Runs Successfully

**Given** `backend/main.py` implemented  
**When** running `uvicorn backend.main:app --host 127.0.0.1 --port 8765`  
**Then** the server:
1. Starts without errors
2. Logs "Backend API started on 127.0.0.1:8765"
3. Responds to HTTP requests on `http://localhost:8765`
4. Does NOT respond on external interfaces (only localhost)

**Verification:**
```powershell
# Terminal 1: Start server
uvicorn backend.main:app --host 127.0.0.1 --port 8765 --reload

# Terminal 2: Test health check
curl http://localhost:8765/api/status
# Should return: {"status":"healthy","version":"1.0.0","timestamp":"..."}

# Test external access blocked (from another machine on network)
curl http://<your-ip>:8765/api/status
# Should fail to connect (connection refused)
```

---

### AC5: Health Check Endpoint Validated

**Given** the backend server running  
**When** sending `GET /api/status` request  
**Then** the response:
1. HTTP status code: `200 OK`
2. Content-Type: `application/json`
3. Body structure:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "timestamp": "2025-11-28T10:00:00.000Z"
   }
   ```
4. `timestamp` is valid ISO 8601 UTC format with 'Z' suffix
5. Response time: <50ms (localhost)

**Verification:**
```powershell
# Using curl with timing
curl -w "\nTime: %{time_total}s\n" http://localhost:8765/api/status

# Using Python requests
python -c "import requests; r = requests.get('http://localhost:8765/api/status'); print(f'Status: {r.status_code}, JSON: {r.json()}')"
```

---

### AC6: Environment Configuration File Created

**Given** the project root directory  
**When** creating `.env.example` template file  
**Then** it contains:

```bash
# AutoResumeFiller Backend Configuration
# Copy this file to .env and update values as needed

# API Server Configuration
API_HOST=127.0.0.1
API_PORT=8765

# CORS Configuration (comma-separated origins)
CORS_ORIGINS=chrome-extension://*

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Application Metadata
APP_NAME=AutoResumeFiller Backend API
APP_VERSION=1.0.0
```

**Additional Requirements:**
- `.env` file is in `.gitignore` (already done in Story 1.1)
- `.env.example` is committed to repository
- README.md includes note about copying `.env.example` to `.env`

**Verification:**
```powershell
Test-Path .env.example
# Should return: True

Get-Content .gitignore | Select-String ".env"
# Should show: .env (excluded from git)
```

---

### AC7: Unit Tests Implemented

**Given** pytest installed in virtual environment  
**When** `backend/tests/test_main.py` is created  
**Then** it contains tests for:

1. **test_health_check_success:** Verify health check returns 200 with correct JSON structure
2. **test_health_check_response_structure:** Validate all required fields present (status, version, timestamp)
3. **test_health_check_timestamp_format:** Verify timestamp is valid ISO 8601 UTC
4. **test_root_endpoint:** Verify root endpoint returns API information
5. **test_cors_headers:** Verify CORS headers present in response

**Code Template:**
```python
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from backend.main import app

client = TestClient(app)

def test_health_check_success():
    """Test health check endpoint returns 200 OK."""
    response = client.get("/api/status")
    assert response.status_code == 200

def test_health_check_response_structure():
    """Test health check response has required fields."""
    response = client.get("/api/status")
    data = response.json()
    
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data
    
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"

def test_health_check_timestamp_format():
    """Test health check timestamp is valid ISO 8601 UTC."""
    response = client.get("/api/status")
    data = response.json()
    timestamp = data["timestamp"]
    
    # Verify ISO 8601 format with Z suffix
    assert timestamp.endswith("Z")
    
    # Verify parseable as datetime
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert dt is not None
    except ValueError:
        pytest.fail("Timestamp is not valid ISO 8601 format")

def test_root_endpoint():
    """Test root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert "health" in data

def test_cors_headers():
    """Test CORS headers are present in response."""
    response = client.get("/api/status")
    assert "access-control-allow-origin" in response.headers
```

**Verification:**
```powershell
pytest backend/tests/test_main.py -v
# Should show: 5 tests passed
```

---

### AC8: Backend Imports Validated

**Given** all backend Python files created  
**When** running Python syntax and import checks  
**Then** no errors occur:

```powershell
# Syntax check
python -m py_compile backend/main.py backend/config/settings.py

# Import check
python -c "from backend.main import app; from backend.config.settings import Settings; print('✓ Imports successful')"

# Type check with mypy
mypy backend/main.py backend/config/settings.py --ignore-missing-imports
# Should show: Success: no issues found
```

---

## Definition of Done

### Code Complete
- ✅ `backend/requirements.txt` populated with 6 dependencies
- ✅ `backend/config/settings.py` implemented with Pydantic Settings class
- ✅ `backend/main.py` implemented with FastAPI app, CORS, health check
- ✅ `.env.example` created with configuration template
- ✅ `backend/tests/test_main.py` implemented with 5 unit tests

### Quality Gates
- ✅ All unit tests pass: `pytest backend/tests/test_main.py -v` (5/5 passing)
- ✅ Python syntax valid: `python -m py_compile backend/main.py backend/config/settings.py`
- ✅ Type checking passes: `mypy backend/main.py backend/config/settings.py --ignore-missing-imports`
- ✅ Backend starts: `uvicorn backend.main:app --host 127.0.0.1 --port 8765` (no errors)
- ✅ Health check responds: `curl http://localhost:8765/api/status` (200 OK)

### Documentation
- ✅ README.md updated with:
  - Backend setup instructions (install dependencies, run server)
  - Health check verification command
  - `.env` configuration note
- ✅ Code comments added to `backend/main.py` (docstrings for app, endpoints, event handlers)
- ✅ `.env.example` includes inline comments explaining each setting

### Testing
- ✅ Manual test: Start backend, verify health check in browser (`http://localhost:8765/api/status`)
- ✅ Manual test: Access API docs (`http://localhost:8765/docs`) - should show Swagger UI
- ✅ Manual test: Verify CORS headers using browser DevTools or curl with `-v` flag
- ✅ Automated tests: Run `pytest backend/tests/` and confirm 5/5 tests passing

### Version Control
- ✅ All changes committed to git with descriptive message:
  ```
  Story 1.2: Implement Python Backend Scaffolding
  
  - Populated backend/requirements.txt with FastAPI + dependencies
  - Created backend/config/settings.py with Pydantic Settings class
  - Implemented backend/main.py with FastAPI app, CORS, health check
  - Created .env.example configuration template
  - Added 5 unit tests in backend/tests/test_main.py
  - Updated README.md with backend setup instructions
  
  All tests passing (5/5), backend runs successfully on localhost:8765
  Health check endpoint verified: GET /api/status returns 200 OK
  
  Story Status: ready-for-dev → in-progress → review
  ```

---

## Technical Implementation Details

### File Changes Summary

**Files Created:**
1. `.env.example` (17 lines) - Configuration template
2. `backend/config/settings.py` (25 lines) - Pydantic Settings class
3. `backend/tests/conftest.py` (15 lines) - pytest fixtures (optional)
4. `backend/tests/test_main.py` (75 lines) - Unit tests

**Files Modified:**
1. `backend/requirements.txt` (7 lines added) - Add FastAPI dependencies
2. `backend/main.py` (75 lines replaced) - Implement FastAPI app (was 7-line placeholder)
3. `README.md` (20 lines added) - Backend setup section

**Total Changes:** ~234 lines added/modified across 7 files

---

### Dependencies (backend/requirements.txt)

```plaintext
# Backend Python Dependencies for AutoResumeFiller

# Core Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# HTTP & Utilities
python-multipart>=0.0.6
python-dotenv>=1.0.0

# Note: Development dependencies (pytest, black, mypy, pylint) 
# are in pyproject.toml [project.optional-dependencies]
```

---

### Testing Strategy

**Test Pyramid for Story 1.2:**
- **Unit Tests (5 tests):** Health check endpoint logic, CORS configuration, settings loading
- **Integration Tests (0 tests):** Not applicable for this story (no external integrations yet)
- **E2E Tests (0 tests):** Will be added in Story 1.6 (Testing Infrastructure)

**Coverage Target:** 90%+ for `backend/main.py` and `backend/config/settings.py`

**pytest Configuration (already in pytest.ini from Story 1.1):**
```ini
[pytest]
testpaths = backend/tests gui/tests tests
markers =
    unit: Unit tests (fast, isolated)
```

**Running Tests:**
```powershell
# Run all backend tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=term-missing

# Run specific test
pytest backend/tests/test_main.py::test_health_check_success -v
```

---

### Common Pitfalls and Solutions

**Pitfall 1: uvicorn not found after pip install**
- **Symptom:** `uvicorn: command not found` or `'uvicorn' is not recognized`
- **Cause:** Virtual environment not activated
- **Solution:** 
  ```powershell
  .venv\Scripts\activate  # Activate venv first
  pip install -r backend/requirements.txt
  uvicorn backend.main:app --host 127.0.0.1 --port 8765
  ```

**Pitfall 2: Port 8765 already in use**
- **Symptom:** `OSError: [Errno 48] Address already in use`
- **Cause:** Previous uvicorn instance still running
- **Solution:**
  ```powershell
  # Find process using port 8765
  Get-NetTCPConnection -LocalPort 8765 | Select-Object OwningProcess
  
  # Kill process
  Stop-Process -Id <PID> -Force
  
  # Or use different port temporarily
  uvicorn backend.main:app --host 127.0.0.1 --port 8766
  ```

**Pitfall 3: ModuleNotFoundError: No module named 'backend'**
- **Symptom:** Import errors when running tests or starting server
- **Cause:** Python not recognizing `backend/` as package, or PYTHONPATH not set
- **Solution:**
  ```powershell
  # Run from project root (not from backend/ directory)
  cd C:\Users\basha\Desktop\root\AutoResumeFiller
  
  # Install in editable mode (optional, for cleaner imports)
  pip install -e .
  
  # Or set PYTHONPATH
  $env:PYTHONPATH = "."
  uvicorn backend.main:app --host 127.0.0.1 --port 8765
  ```

**Pitfall 4: CORS errors when testing from browser**
- **Symptom:** "Access-Control-Allow-Origin" error in browser console
- **Cause:** Testing from non-extension origin (e.g., `http://localhost:3000`)
- **Solution:** 
  - For development testing, temporarily add origin to settings:
    ```python
    CORS_ORIGINS: List[str] = ["chrome-extension://*", "http://localhost:3000"]
    ```
  - Remove extra origins before committing (security requirement)

**Pitfall 5: Timestamp format inconsistencies**
- **Symptom:** Test `test_health_check_timestamp_format` fails
- **Cause:** Missing 'Z' suffix or incorrect ISO 8601 format
- **Solution:**
  ```python
  # Correct format in backend/main.py
  from datetime import datetime
  timestamp = datetime.utcnow().isoformat() + "Z"  # Add Z suffix for UTC
  ```

---

### Tool-Specific Notes

**uvicorn Development Mode:**
```powershell
# With auto-reload (watches for file changes)
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8765

# With custom log level
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8765 --log-level debug

# Access logs (HTTP request logging)
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8765 --access-log
```

**FastAPI Interactive Docs:**
- **Swagger UI:** `http://localhost:8765/docs` - Interactive API testing
- **ReDoc:** `http://localhost:8765/redoc` - API documentation with better readability
- **OpenAPI JSON:** `http://localhost:8765/openapi.json` - Machine-readable API schema

**Testing with curl:**
```powershell
# Health check
curl http://localhost:8765/api/status

# With verbose output (shows headers)
curl -v http://localhost:8765/api/status

# With timing
curl -w "\nTime: %{time_total}s\n" http://localhost:8765/api/status

# Pretty-print JSON (PowerShell)
(curl http://localhost:8765/api/status).Content | ConvertFrom-Json | ConvertTo-Json
```

**pytest Tips:**
```powershell
# Run with verbose output
pytest backend/tests/ -v

# Run with coverage and show missing lines
pytest backend/tests/ --cov=backend --cov-report=term-missing

# Run tests matching pattern
pytest backend/tests/ -k "health_check"

# Stop on first failure
pytest backend/tests/ -x

# Show print statements
pytest backend/tests/ -s
```

---

## Traceability

### Links to Requirements
- **PRD Section 3.1 (System Architecture):** FastAPI backend for AI orchestration and data management
- **Architecture Section 4.2 (Backend Framework):** FastAPI chosen for async/await support and auto-generated docs
- **Architecture Section 5.3 (Communication Pattern):** HTTP REST API on localhost:8765

### Links to Architecture
- **Architecture Decision 3 (Backend Framework):** FastAPI with uvicorn ASGI server
- **Architecture Section 6.1 (Security):** Localhost-only binding (127.0.0.1), CORS whitelist
- **Architecture Section 8.2 (Backend Structure):** `backend/main.py` as FastAPI entry point

### Links to Epic
- **Epic 1 Tech Spec Section 4.1 (Services and Modules):** `backend/main.py` with health check endpoint
- **Epic 1 Tech Spec Section 4.2 (Data Models):** Health check response JSON structure
- **Epic 1 Tech Spec Section 4.3 (APIs):** `GET /api/status` endpoint specification

### Related Stories
- **Story 1.1:** Project Initialization & Repository Setup (PREREQUISITE - provides directory structure)
- **Story 1.3:** Chrome Extension Manifest & Basic Structure (NEXT - will communicate with this backend)
- **Story 1.4:** PyQt5 GUI Application Shell (NEXT - will query this backend's health check)
- **Story 1.6:** Testing Infrastructure & First Unit Tests (BUILDS ON - will expand test coverage)

---

## Estimates

**Story Points:** 3  
**Estimated Time:** 3-4 hours

**Breakdown:**
- Backend dependencies + requirements.txt: 20 minutes
- Settings configuration (pydantic-settings): 30 minutes
- FastAPI app implementation: 60 minutes
- Health check endpoint + CORS: 30 minutes
- Unit tests (5 tests): 45 minutes
- Documentation (README update, .env.example): 20 minutes
- Manual testing and verification: 30 minutes
- Git commit and code review prep: 15 minutes

**Risk Factors:**
- ⚠️ First time using pydantic-settings (v2.x) - may need extra time for learning curve
- ⚠️ CORS configuration nuances with chrome-extension:// protocol
- ✅ FastAPI fundamentals well-documented (low risk)
- ✅ Health check endpoint is simple (low complexity)

**Confidence:** High (80%) - Well-defined scope, clear acceptance criteria, minimal unknowns

---

## Notes

### Implementation Tips
1. **Start with dependencies:** Install `fastapi` and `uvicorn` first, verify server can start with minimal app
2. **Incremental development:** Implement health check endpoint first (simplest), then add CORS, then settings
3. **Test frequently:** After each AC implementation, run `python -c "from backend.main import app"` to catch import errors early
4. **Use FastAPI docs:** Leverage auto-generated Swagger UI (`/docs`) to test endpoints interactively
5. **Git commits:** Consider one commit per AC for clean history (or batch related ACs)

### Future Enhancements (Out of Scope)
- ❌ WebSocket support for real-time communication (Epic 6)
- ❌ Request logging middleware (Epic 6 - Observability)
- ❌ Rate limiting (Epic 7 - Production readiness)
- ❌ API authentication (not required - localhost-only application)
- ❌ Database connections (Epic 2 - Local Data Management)
- ❌ AI provider integrations (Epic 3)

### Open Questions
- ✅ **Q:** Should we use structured JSON logging in this story?  
  **A:** No, use standard logging for now. Structured logging will be added in Epic 6 (Dashboard & Monitoring).

- ✅ **Q:** Do we need environment variable validation (e.g., port range checks)?  
  **A:** Pydantic handles basic validation. Additional validation can be added later if needed.

- ✅ **Q:** Should health check include system resource info (CPU, memory)?  
  **A:** No, keep it simple for Story 1.2. Advanced health metrics will be added in Epic 6.

---

**Story Drafted By:** SM Agent (Scrum Master)  
**Reviewed By:** PM Agent (Product Manager) [Pending]  
**Approved By:** Ragnar [Pending]  
**Ready for Development:** Yes (Story 1.1 completed)
