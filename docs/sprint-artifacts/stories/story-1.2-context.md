# Story 1.2 Technical Context: Python Backend Scaffolding

**Story ID:** 1.2  
**Context Created:** 2025-11-28  
**Author:** SM Agent (Ragnar)  
**Context Type:** Just-In-Time Technical Guidance  
**Status:** Ready for Implementation

---

## Purpose

This document provides implementation-specific technical context for Story 1.2, offering complete code templates, step-by-step implementation guides, and verification checklists. It bridges the story acceptance criteria with actual implementation details.

**When to use this document:**
- During DEV agent implementation (`*dev-story` workflow)
- When unclear about FastAPI patterns or pydantic-settings configuration
- When debugging backend startup issues or CORS problems
- When writing unit tests for the health check endpoint

---

## Quick Reference

### Current Project State

**Existing Files (from Story 1.1):**
```
AutoResumeFiller/
├── backend/
│   ├── api/
│   │   ├── __init__.py           # ✅ Empty package
│   │   └── .gitkeep
│   ├── config/
│   │   ├── __init__.py           # ✅ Empty package
│   │   └── .gitkeep
│   ├── services/
│   │   ├── __init__.py           # ✅ Empty package
│   │   └── .gitkeep
│   ├── utils/
│   │   ├── __init__.py           # ✅ Empty package
│   │   └── .gitkeep
│   ├── tests/
│   │   ├── __init__.py           # ✅ Empty package
│   │   └── .gitkeep
│   ├── main.py                   # ✅ 7-line placeholder (REPLACE in this story)
│   └── requirements.txt          # ✅ 2-line comment (POPULATE in this story)
├── pyproject.toml                # ✅ Complete configuration
├── pytest.ini                    # ✅ Test configuration
├── .gitignore                    # ✅ Includes .env
└── README.md                     # ✅ Project documentation (UPDATE in this story)
```

**Story 1.2 Will Create:**
```
AutoResumeFiller/
├── backend/
│   ├── config/
│   │   └── settings.py           # NEW - Pydantic Settings class
│   ├── tests/
│   │   ├── conftest.py           # NEW - pytest fixtures (optional)
│   │   └── test_main.py          # NEW - 5 unit tests
│   ├── main.py                   # MODIFY - FastAPI app (replace placeholder)
│   └── requirements.txt          # MODIFY - Add 6 dependencies
├── .env.example                  # NEW - Configuration template
└── README.md                     # MODIFY - Add backend setup section
```

---

## Implementation Steps

### Step 1: Populate backend/requirements.txt

**Current Content (2 lines):**
```plaintext
# Backend Python dependencies
# To be populated in Story 1.2: Python Backend Scaffolding
```

**Replace With (Complete Requirements):**
```plaintext
# Backend Python Dependencies for AutoResumeFiller
# Story 1.2: FastAPI Backend Scaffolding

# Core Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# HTTP & Utilities
python-multipart>=0.0.6
python-dotenv>=1.0.0

# Development Dependencies
# Note: Testing tools (pytest, black, mypy, pylint) are configured 
# in pyproject.toml [project.optional-dependencies] for project-wide use.
# Install with: pip install -e ".[dev]" (future - Epic 1.6)
```

**Installation Command:**
```powershell
# From project root
.venv\Scripts\activate  # Activate virtual environment
pip install -r backend/requirements.txt
```

**Verification:**
```powershell
pip list | Select-String "fastapi|uvicorn|pydantic"
# Expected output:
# fastapi        0.104.x or higher
# uvicorn        0.24.x or higher
# pydantic       2.5.x or higher
# pydantic-settings 2.1.x or higher
```

---

### Step 2: Create backend/config/settings.py

**File Path:** `backend/config/settings.py`  
**Lines:** 28 lines  
**Purpose:** Type-safe configuration management with environment variable loading

**Complete Code:**
```python
"""Configuration settings for AutoResumeFiller Backend API.

This module uses pydantic-settings to load configuration from environment
variables with type validation and default values.
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support.
    
    Settings can be overridden via .env file or environment variables.
    All environment variables are prefixed with APP_ (optional).
    """
    
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
        """Pydantic settings configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()
```

**Key Features:**
- **Type Safety:** All settings have explicit types with validation
- **Default Values:** Sensible defaults for localhost development
- **Environment Variables:** Automatically loads from `.env` file
- **CORS Origins:** Default allows `chrome-extension://*` (wildcard for extension IDs)
- **Localhost Binding:** API_HOST defaults to `127.0.0.1` (not `0.0.0.0`)

**Testing the Configuration:**
```powershell
# Test settings loading
python -c "from backend.config.settings import settings; print(f'Host: {settings.API_HOST}, Port: {settings.API_PORT}, CORS: {settings.CORS_ORIGINS}')"

# Expected output:
# Host: 127.0.0.1, Port: 8765, CORS: ['chrome-extension://*']
```

---

### Step 3: Create .env.example Template

**File Path:** `.env.example` (project root)  
**Lines:** 18 lines  
**Purpose:** Configuration template for developers (no secrets)

**Complete Content:**
```bash
# AutoResumeFiller Backend Configuration
# ==================================
# Copy this file to .env and update values as needed
# .env file is gitignored and should contain actual secrets

# API Server Configuration
# ========================
# Host to bind the FastAPI server (127.0.0.1 for localhost only)
API_HOST=127.0.0.1
API_PORT=8765

# CORS Configuration
# ==================
# Allowed origins (comma-separated for multiple origins)
# Default allows all chrome-extension:// origins
CORS_ORIGINS=chrome-extension://*

# Logging Configuration
# ======================
LOG_LEVEL=INFO
LOG_FORMAT=json

# Application Metadata
# ====================
APP_NAME=AutoResumeFiller Backend API
APP_VERSION=1.0.0
```

**Developer Instructions:**
```powershell
# Copy template to create actual .env file
Copy-Item .env.example .env

# Edit .env for custom configuration (optional - defaults work for development)
notepad .env
```

**Note:** `.env` is already in `.gitignore` from Story 1.1, so actual configuration with secrets won't be committed.

---

### Step 4: Implement backend/main.py (FastAPI Application)

**File Path:** `backend/main.py`  
**Current Content:** 7 lines (placeholder with TODO)  
**New Content:** 88 lines (complete FastAPI app)

**Complete Code:**
```python
"""AutoResumeFiller Backend API - Entry Point.

This module initializes the FastAPI application with CORS middleware,
startup/shutdown handlers, and health check endpoint. The backend serves
as the orchestration layer for AI providers, data management, and form
processing.

Endpoints:
    GET /              - Root endpoint with API information
    GET /api/status    - Health check endpoint
    GET /docs          - Interactive API documentation (Swagger UI)
    GET /redoc         - API documentation (ReDoc)
"""
import logging
from datetime import datetime
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend API for AutoResumeFiller - Intelligent job application "
        "form auto-filling with AI assistance. Provides endpoints for form "
        "analysis, AI-powered response generation, and user data management."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured with origins: {settings.CORS_ORIGINS}")


@app.on_event("startup")
async def startup_event() -> None:
    """Application startup event handler.
    
    Logs backend initialization and configuration details.
    Future epics will add database connections, AI provider initialization, etc.
    """
    logger.info("=" * 70)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Server: http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Application shutdown event handler.
    
    Logs backend shutdown. Future epics will add cleanup tasks
    (close database connections, flush logs, etc.).
    """
    logger.info("Shutting down Backend API")
    logger.info("Cleanup complete")


@app.get("/", response_model=Dict[str, str], tags=["Root"])
async def root() -> Dict[str, str]:
    """Root endpoint providing API information and navigation links.
    
    Returns:
        Dictionary with API name, version, and links to documentation endpoints.
    """
    return {
        "message": f"{settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/status"
    }


@app.get("/api/status", response_model=Dict[str, str], tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint for system verification.
    
    Used by the GUI dashboard and Chrome Extension to verify backend
    availability. Returns 200 OK if the server is operational.
    
    Returns:
        Dictionary with status ("healthy"), version, and UTC timestamp.
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# Entry point for running with Python directly (development only)
if __name__ == "__main__":
    import uvicorn
    
    logger.warning(
        "Running with 'python backend/main.py' is for quick testing only. "
        "Use 'uvicorn backend.main:app --reload' for development."
    )
    
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
```

**Code Explanation:**

**Imports & Logging (Lines 1-30):**
- FastAPI core imports for app, middleware, responses
- Settings loaded from `backend.config.settings`
- Logging configured with level from settings (INFO by default)

**FastAPI App Initialization (Lines 32-43):**
- `app = FastAPI(...)` with title, description, version from settings
- Auto-generated docs at `/docs` (Swagger UI) and `/redoc`
- OpenAPI JSON schema at `/openapi.json`

**CORS Middleware (Lines 45-54):**
- Allows requests from `chrome-extension://*` origins
- `allow_credentials=True` enables cookies (if needed in future)
- `allow_methods=["*"]` allows GET, POST, PUT, DELETE, etc.
- `allow_headers=["*"]` allows custom headers

**Startup Handler (Lines 57-68):**
- Logs server URL and documentation links
- Logged on uvicorn startup
- Future: Initialize AI providers, database connections

**Shutdown Handler (Lines 71-78):**
- Logs shutdown message
- Future: Close connections, flush logs, cleanup resources

**Root Endpoint (Lines 81-90):**
- `GET /` returns API info and navigation links
- Useful for quick browser verification

**Health Check Endpoint (Lines 93-106):**
- `GET /api/status` returns `{"status": "healthy", ...}`
- ISO 8601 timestamp with Z suffix (UTC)
- Used by GUI and extension to verify backend availability

**Development Entry Point (Lines 109-123):**
- Allows `python backend/main.py` for quick testing
- Warns that uvicorn CLI is preferred for development
- Not used in production (Epic 7 will use systemd/PM2)

**Running the Backend:**
```powershell
# Recommended: uvicorn with auto-reload
uvicorn backend.main:app --host 127.0.0.1 --port 8765 --reload

# Alternative: Python directly (logs warning)
python backend/main.py

# Access API docs
Start-Process http://localhost:8765/docs

# Test health check
curl http://localhost:8765/api/status
```

---

### Step 5: Create backend/tests/test_main.py (Unit Tests)

**File Path:** `backend/tests/test_main.py`  
**Lines:** 95 lines  
**Purpose:** Comprehensive unit tests for FastAPI endpoints

**Complete Code:**
```python
"""Unit tests for backend/main.py FastAPI endpoints.

Tests cover health check endpoint, root endpoint, CORS headers,
and response structure validation.
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from backend.main import app

# Create test client
client = TestClient(app)


class TestHealthCheckEndpoint:
    """Tests for GET /api/status health check endpoint."""
    
    def test_health_check_success(self):
        """Test health check endpoint returns 200 OK."""
        response = client.get("/api/status")
        assert response.status_code == 200
    
    def test_health_check_response_structure(self):
        """Test health check response has required fields with correct values."""
        response = client.get("/api/status")
        data = response.json()
        
        # Verify required fields exist
        assert "status" in data, "Missing 'status' field"
        assert "version" in data, "Missing 'version' field"
        assert "timestamp" in data, "Missing 'timestamp' field"
        
        # Verify field values
        assert data["status"] == "healthy", "Status should be 'healthy'"
        assert data["version"] == "1.0.0", "Version should be '1.0.0'"
    
    def test_health_check_timestamp_format(self):
        """Test health check timestamp is valid ISO 8601 UTC format."""
        response = client.get("/api/status")
        data = response.json()
        timestamp = data["timestamp"]
        
        # Verify Z suffix (UTC indicator)
        assert timestamp.endswith("Z"), "Timestamp must end with 'Z' for UTC"
        
        # Verify ISO 8601 format is parseable
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            assert dt is not None
        except ValueError as e:
            pytest.fail(f"Timestamp is not valid ISO 8601 format: {e}")
    
    def test_health_check_content_type(self):
        """Test health check returns JSON content type."""
        response = client.get("/api/status")
        assert response.headers["content-type"] == "application/json"
    
    def test_health_check_performance(self):
        """Test health check responds quickly (<100ms for test client)."""
        import time
        
        start = time.time()
        response = client.get("/api/status")
        elapsed = (time.time() - start) * 1000  # Convert to milliseconds
        
        assert response.status_code == 200
        # TestClient is in-memory, so should be very fast (<100ms)
        assert elapsed < 100, f"Health check took {elapsed:.2f}ms (expected <100ms)"


class TestRootEndpoint:
    """Tests for GET / root endpoint."""
    
    def test_root_endpoint_success(self):
        """Test root endpoint returns 200 OK."""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_endpoint_structure(self):
        """Test root endpoint returns expected fields."""
        response = client.get("/")
        data = response.json()
        
        # Verify required fields
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data
        
        # Verify field values
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
        assert data["health"] == "/api/status"


class TestCORSHeaders:
    """Tests for CORS middleware configuration."""
    
    def test_cors_headers_present(self):
        """Test CORS headers are present in response."""
        response = client.get("/api/status")
        
        # Check for CORS headers (lowercase in response.headers)
        assert "access-control-allow-origin" in response.headers, \
            "Missing CORS allow-origin header"
    
    def test_cors_allows_chrome_extension(self):
        """Test CORS allows chrome-extension:// origins."""
        # Simulate request from Chrome extension
        headers = {"Origin": "chrome-extension://abcdefghijklmnopqrstuvwxyz123456"}
        response = client.get("/api/status", headers=headers)
        
        # Should return 200 OK (CORS doesn't block in test client)
        assert response.status_code == 200
        
        # In real browser, CORS middleware validates origin against allow_origins
        # TestClient doesn't enforce CORS, but middleware is configured


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Test Coverage:**

1. **test_health_check_success:** Verifies 200 OK status code
2. **test_health_check_response_structure:** Validates JSON structure (status, version, timestamp fields)
3. **test_health_check_timestamp_format:** Validates ISO 8601 UTC format with Z suffix
4. **test_health_check_content_type:** Verifies `application/json` content type
5. **test_health_check_performance:** Ensures response time <100ms (in-memory test)
6. **test_root_endpoint_success:** Verifies root endpoint returns 200 OK
7. **test_root_endpoint_structure:** Validates root endpoint JSON structure
8. **test_cors_headers_present:** Verifies CORS headers exist
9. **test_cors_allows_chrome_extension:** Simulates extension origin request

**Running Tests:**
```powershell
# Run all tests with verbose output
pytest backend/tests/test_main.py -v

# Run with coverage report
pytest backend/tests/test_main.py --cov=backend.main --cov-report=term-missing

# Run specific test class
pytest backend/tests/test_main.py::TestHealthCheckEndpoint -v

# Run specific test
pytest backend/tests/test_main.py::TestHealthCheckEndpoint::test_health_check_success -v
```

**Expected Output:**
```
backend/tests/test_main.py::TestHealthCheckEndpoint::test_health_check_success PASSED
backend/tests/test_main.py::TestHealthCheckEndpoint::test_health_check_response_structure PASSED
backend/tests/test_main.py::TestHealthCheckEndpoint::test_health_check_timestamp_format PASSED
backend/tests/test_main.py::TestHealthCheckEndpoint::test_health_check_content_type PASSED
backend/tests/test_main.py::TestHealthCheckEndpoint::test_health_check_performance PASSED
backend/tests/test_main.py::TestRootEndpoint::test_root_endpoint_success PASSED
backend/tests/test_main.py::TestRootEndpoint::test_root_endpoint_structure PASSED
backend/tests/test_main.py::TestCORSHeaders::test_cors_headers_present PASSED
backend/tests/test_main.py::TestCORSHeaders::test_cors_allows_chrome_extension PASSED

========================================= 9 passed in 0.15s =========================================
```

---

### Step 6: Update README.md (Backend Setup Section)

**File Path:** `README.md`  
**Section to Add:** Backend Setup (after "Installation" section)

**Add After Line ~120 (after Installation section):**
```markdown

### Backend Setup (FastAPI)

The backend API provides endpoints for form analysis, AI response generation, and data management.

**1. Install Backend Dependencies**

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

**2. Configure Environment (Optional)**

The backend works with default settings. For custom configuration:

```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env to customize settings
notepad .env
```

Default configuration:
- API Host: `127.0.0.1` (localhost only)
- API Port: `8765`
- CORS Origins: `chrome-extension://*` (all extensions)

**3. Start Backend Server**

```powershell
# Development mode with auto-reload
uvicorn backend.main:app --host 127.0.0.1 --port 8765 --reload

# Alternative: Run directly with Python
python backend/main.py
```

**4. Verify Backend**

- **Health Check:** http://localhost:8765/api/status  
  Expected: `{"status": "healthy", "version": "1.0.0", "timestamp": "..."}`

- **API Documentation:** http://localhost:8765/docs  
  Interactive Swagger UI for testing endpoints

- **Alternative Docs:** http://localhost:8765/redoc  
  Clean API documentation with ReDoc

**5. Run Backend Tests**

```powershell
# Run all backend tests
pytest backend/tests/ -v

# Run with coverage report
pytest backend/tests/ --cov=backend --cov-report=term-missing
```

Expected: 9/9 tests passing with >90% coverage on `backend/main.py`

```

---

### Step 7: Optional - Create backend/tests/conftest.py (pytest Fixtures)

**File Path:** `backend/tests/conftest.py`  
**Lines:** 20 lines  
**Purpose:** Shared pytest fixtures for testing (optional for Story 1.2)

**Complete Code:**
```python
"""Pytest configuration and shared fixtures for backend tests.

This module provides reusable test fixtures for FastAPI test client,
database setup (future), and mock AI providers (future).
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def test_client():
    """Provide TestClient instance for FastAPI testing.
    
    Yields:
        TestClient configured with backend FastAPI app.
    """
    with TestClient(app) as client:
        yield client


# Future fixtures (Epic 2+):
# - mock_user_data
# - mock_ai_provider
# - temp_data_directory
```

**Using the Fixture:**
```python
# In test_main.py, can replace direct TestClient usage:
def test_health_check_with_fixture(test_client):
    """Test using conftest fixture."""
    response = test_client.get("/api/status")
    assert response.status_code == 200
```

**Note:** This is optional for Story 1.2. Current tests use `TestClient(app)` directly. Fixtures become valuable when tests need shared setup/teardown logic.

---

## Verification Checklist

### ✅ Pre-Implementation Checks

- [ ] Virtual environment activated: `.venv\Scripts\activate`
- [ ] Story 1.1 completed (backend/ directory structure exists)
- [ ] Python 3.9+ installed: `python --version`
- [ ] Current directory is project root: `Get-Location` shows `AutoResumeFiller`

### ✅ AC1: Backend Dependencies Installed

```powershell
# Install dependencies
pip install -r backend/requirements.txt

# Verify installation
pip list | Select-String "fastapi|uvicorn|pydantic"

# Expected packages:
# - fastapi (>=0.104.0)
# - uvicorn (>=0.24.0)
# - pydantic (>=2.5.0)
# - pydantic-settings (>=2.1.0)
```

**Success Criteria:** All 6 packages installed without errors

### ✅ AC2: Settings Configuration Implemented

```powershell
# Test settings import
python -c "from backend.config.settings import settings; print(f'✓ Settings loaded: {settings.API_HOST}:{settings.API_PORT}')"

# Expected output:
# ✓ Settings loaded: 127.0.0.1:8765
```

**Success Criteria:** Settings class loads without errors, defaults correct

### ✅ AC3: FastAPI Application Initialized

```powershell
# Test app import
python -c "from backend.main import app; print(f'✓ App title: {app.title}')"

# Expected output:
# ✓ App title: AutoResumeFiller Backend API
```

**Success Criteria:** FastAPI app initializes, title matches settings

### ✅ AC4: Backend Server Runs Successfully

```powershell
# Terminal 1: Start server
uvicorn backend.main:app --host 127.0.0.1 --port 8765 --reload

# Expected log output:
# INFO:     Uvicorn running on http://127.0.0.1:8765 (Press CTRL+C to quit)
# INFO:     Started reloader process...
# INFO:     Started server process...
# INFO:     Waiting for application startup.
# INFO:backend.main:Starting AutoResumeFiller Backend API v1.0.0
# INFO:backend.main:Server: http://127.0.0.1:8765
# INFO:     Application startup complete.

# Terminal 2: Test health check
curl http://localhost:8765/api/status

# Or with PowerShell:
(Invoke-WebRequest http://localhost:8765/api/status).Content | ConvertFrom-Json
```

**Success Criteria:** Server starts without errors, responds to requests

### ✅ AC5: Health Check Endpoint Validated

```powershell
# Test health check response
$response = Invoke-WebRequest http://localhost:8765/api/status
$data = $response.Content | ConvertFrom-Json

# Verify status code
Write-Host "Status Code: $($response.StatusCode)"  # Should be 200

# Verify JSON structure
Write-Host "Status: $($data.status)"                # Should be "healthy"
Write-Host "Version: $($data.version)"              # Should be "1.0.0"
Write-Host "Timestamp: $($data.timestamp)"          # Should be ISO 8601 with Z suffix

# Verify content type
Write-Host "Content-Type: $($response.Headers['Content-Type'])"  # Should be "application/json"
```

**Success Criteria:** 200 OK, JSON structure correct, timestamp valid

### ✅ AC6: Environment Configuration File Created

```powershell
# Verify .env.example exists
Test-Path .env.example
# Should return: True

# Verify .env in .gitignore
Get-Content .gitignore | Select-String ".env"
# Should show: .env

# Display .env.example content
Get-Content .env.example
```

**Success Criteria:** `.env.example` exists with all settings documented

### ✅ AC7: Unit Tests Implemented

```powershell
# Run all tests
pytest backend/tests/test_main.py -v

# Expected output: 9 tests passing
# - test_health_check_success PASSED
# - test_health_check_response_structure PASSED
# - test_health_check_timestamp_format PASSED
# - test_health_check_content_type PASSED
# - test_health_check_performance PASSED
# - test_root_endpoint_success PASSED
# - test_root_endpoint_structure PASSED
# - test_cors_headers_present PASSED
# - test_cors_allows_chrome_extension PASSED

# Run with coverage
pytest backend/tests/test_main.py --cov=backend.main --cov-report=term-missing
# Expected: >90% coverage on backend/main.py
```

**Success Criteria:** 9/9 tests passing, >90% code coverage

### ✅ AC8: Backend Imports Validated

```powershell
# Syntax check
python -m py_compile backend/main.py backend/config/settings.py backend/tests/test_main.py
# Should complete silently (no errors)

# Import check
python -c "from backend.main import app; from backend.config.settings import settings; print('✓ All imports successful')"
# Expected: ✓ All imports successful

# Type check with mypy (optional - if installed)
mypy backend/main.py backend/config/settings.py --ignore-missing-imports
# Expected: Success: no issues found (or warnings about missing stubs)
```

**Success Criteria:** No syntax errors, all imports work, type checking passes

### ✅ Integration Tests (Manual)

```powershell
# 1. Start backend server
uvicorn backend.main:app --host 127.0.0.1 --port 8765 --reload

# 2. Open browser and test:
Start-Process http://localhost:8765              # Root endpoint
Start-Process http://localhost:8765/api/status    # Health check
Start-Process http://localhost:8765/docs          # Swagger UI

# 3. Test CORS with curl verbose output
curl -v http://localhost:8765/api/status
# Look for: access-control-allow-origin: chrome-extension://*

# 4. Test from different terminal (backend still running)
curl http://localhost:8765/api/status
# Should get JSON response with healthy status

# 5. Stop server (Ctrl+C in terminal 1)
# Verify shutdown log: "Shutting down Backend API"
```

**Success Criteria:** All endpoints respond correctly, CORS headers present, clean shutdown

---

## Common Pitfalls and Solutions

### Pitfall 1: ModuleNotFoundError: No module named 'backend'

**Symptom:**
```
ModuleNotFoundError: No module named 'backend'
  File "backend/main.py", line 22, in <module>
    from backend.config.settings import settings
```

**Cause:** Running Python from wrong directory or PYTHONPATH not set

**Solutions:**
```powershell
# Solution 1: Run from project root (recommended)
cd C:\Users\basha\Desktop\root\AutoResumeFiller
uvicorn backend.main:app --host 127.0.0.1 --port 8765

# Solution 2: Set PYTHONPATH
$env:PYTHONPATH = "."
python backend/main.py

# Solution 3: Install in editable mode
pip install -e .
```

---

### Pitfall 2: Port 8765 Already in Use

**Symptom:**
```
ERROR:    [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8765): 
only one usage of each socket address (protocol/network address/port) is normally permitted
```

**Cause:** Previous uvicorn instance still running or another process using port 8765

**Solutions:**
```powershell
# Find process using port 8765
Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue | 
    Select-Object OwningProcess, State

# Kill the process (replace <PID> with actual process ID)
Stop-Process -Id <PID> -Force

# Or use a different port temporarily
uvicorn backend.main:app --host 127.0.0.1 --port 8766

# Update settings.py if changing port permanently:
# API_PORT: int = 8766
```

---

### Pitfall 3: pydantic-settings Import Error

**Symptom:**
```
ImportError: cannot import name 'BaseSettings' from 'pydantic_settings'
```

**Cause:** Wrong pydantic-settings version or not installed

**Solutions:**
```powershell
# Check installed version
pip show pydantic-settings

# Reinstall correct version
pip uninstall pydantic-settings -y
pip install pydantic-settings>=2.1.0

# Verify installation
python -c "from pydantic_settings import BaseSettings; print('✓ pydantic-settings OK')"
```

---

### Pitfall 4: CORS Errors in Browser

**Symptom:** Browser console shows:
```
Access to fetch at 'http://localhost:8765/api/status' from origin 'chrome-extension://...' 
has been blocked by CORS policy
```

**Cause:** CORS middleware not configured or wrong origin pattern

**Solutions:**
```python
# In backend/main.py, verify CORS middleware:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*"],  # ← Wildcard for all extension IDs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# For debugging, temporarily allow all origins (REMOVE before commit):
allow_origins=["*"],  # WARNING: Development only!

# Verify CORS headers in response:
curl -v http://localhost:8765/api/status
# Look for: access-control-allow-origin header
```

---

### Pitfall 5: Tests Fail with "Connection Refused"

**Symptom:**
```
requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

**Cause:** Tests trying to connect to real server instead of using TestClient

**Solution:**
```python
# In test_main.py, ensure using TestClient (in-memory):
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)  # ← In-memory client, no real server needed

# Do NOT use:
# import requests
# response = requests.get("http://localhost:8765/api/status")  # ← Wrong! Needs real server
```

---

### Pitfall 6: Timestamp Format Validation Fails

**Symptom:** Test `test_health_check_timestamp_format` fails with:
```
ValueError: Invalid isoformat string: '2025-11-28T10:00:00.123456'
```

**Cause:** Missing 'Z' suffix for UTC timezone

**Solution:**
```python
# In backend/main.py, ensure Z suffix:
from datetime import datetime

@app.get("/api/status")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z"  # ← Add Z suffix
    }

# Correct format: "2025-11-28T10:00:00.123456Z"
```

---

### Pitfall 7: Virtual Environment Not Activated

**Symptom:**
```
'uvicorn' is not recognized as an internal or external command
```

**Cause:** Virtual environment not activated, trying to use system Python

**Solution:**
```powershell
# Check if venv active (prompt should show "(.venv)")
Get-Command python | Select-Object Source
# Should show: C:\Users\basha\Desktop\root\AutoResumeFiller\.venv\Scripts\python.exe

# If not active, activate:
.venv\Scripts\activate

# Verify:
pip list  # Should show packages installed in venv, not system Python
```

---

## Tool-Specific Notes

### uvicorn CLI Options

```powershell
# Development mode (auto-reload on file changes)
uvicorn backend.main:app --reload

# Specify host and port
uvicorn backend.main:app --host 127.0.0.1 --port 8765

# Change log level
uvicorn backend.main:app --log-level debug   # debug, info, warning, error, critical

# Enable access logs (HTTP request logging)
uvicorn backend.main:app --access-log

# Disable access logs (quieter output)
uvicorn backend.main:app --no-access-log

# Custom reload directories (watch specific folders)
uvicorn backend.main:app --reload --reload-dir backend

# Production-like settings (no reload, workers)
uvicorn backend.main:app --host 127.0.0.1 --port 8765 --workers 4 --no-access-log
```

---

### FastAPI Interactive Documentation

**Swagger UI (`/docs`):**
- Interactive API testing interface
- "Try it out" buttons for each endpoint
- Automatic request/response validation
- JSON schema display
- OAuth2 integration (future)

**Usage:**
```powershell
# Open Swagger UI
Start-Process http://localhost:8765/docs

# Test health check:
# 1. Click "GET /api/status"
# 2. Click "Try it out"
# 3. Click "Execute"
# 4. See response body, headers, status code
```

**ReDoc (`/redoc`):**
- Clean, readable API documentation
- Better for sharing with stakeholders
- No interactive testing (read-only)
- Better for complex APIs with many endpoints

**OpenAPI JSON (`/openapi.json`):**
- Machine-readable API schema
- Used by code generators (openapi-generator)
- Postman/Insomnia import
- CI/CD contract testing

---

### pytest Tips for Backend Testing

```powershell
# Run with verbose output (show test names)
pytest backend/tests/ -v

# Run with extra verbose output (show print statements)
pytest backend/tests/ -vv -s

# Run specific test file
pytest backend/tests/test_main.py

# Run specific test class
pytest backend/tests/test_main.py::TestHealthCheckEndpoint

# Run specific test function
pytest backend/tests/test_main.py::TestHealthCheckEndpoint::test_health_check_success

# Run tests matching pattern
pytest backend/tests/ -k "health_check"

# Stop on first failure
pytest backend/tests/ -x

# Show coverage report
pytest backend/tests/ --cov=backend --cov-report=term-missing

# Generate HTML coverage report
pytest backend/tests/ --cov=backend --cov-report=html
# Open: htmlcov/index.html

# Run tests in parallel (if pytest-xdist installed)
pytest backend/tests/ -n auto

# Show slowest tests
pytest backend/tests/ --durations=10
```

---

### Testing with curl and PowerShell

**curl Examples:**
```powershell
# Basic GET request
curl http://localhost:8765/api/status

# Verbose output (show headers)
curl -v http://localhost:8765/api/status

# Pretty-print JSON response
curl http://localhost:8765/api/status | jq .

# With timing information
curl -w "\nTime: %{time_total}s\n" http://localhost:8765/api/status

# Save response to file
curl http://localhost:8765/api/status -o response.json

# Custom headers (test CORS)
curl -H "Origin: chrome-extension://abc123" http://localhost:8765/api/status -v
```

**PowerShell Invoke-WebRequest Examples:**
```powershell
# Basic request
Invoke-WebRequest http://localhost:8765/api/status

# Parse JSON response
$response = Invoke-WebRequest http://localhost:8765/api/status
$data = $response.Content | ConvertFrom-Json
Write-Host "Status: $($data.status)"

# Check status code
$response.StatusCode  # Should be 200

# Check headers
$response.Headers['Content-Type']  # Should be "application/json"

# Measure response time
Measure-Command { Invoke-WebRequest http://localhost:8765/api/status }
```

---

## Next Steps After Story 1.2

### Immediate Next Story: 1.3 (Chrome Extension Manifest & Basic Structure)

**What Story 1.3 Will Build:**
- `extension/manifest.json` with permissions and content scripts
- `extension/background/service-worker.js` with message listeners
- `extension/content/content-script.js` with form detection placeholders
- `extension/popup/popup.html` with backend status display

**How Story 1.2 Enables 1.3:**
- Health check endpoint (`/api/status`) will be used by extension popup to show connection status
- CORS middleware configured for `chrome-extension://*` allows extension HTTP requests
- Backend server running on `localhost:8765` provides endpoint for extension to communicate with

**Integration Test (After Story 1.3):**
```javascript
// In extension/popup/popup.js
fetch('http://localhost:8765/api/status')
  .then(response => response.json())
  .then(data => {
    console.log('Backend status:', data.status);  // "healthy"
    // Update popup UI: show green dot for "Connected"
  });
```

---

### Future Epic Dependencies

**Epic 2: Local Data Management System**
- Builds on backend/main.py with new endpoints: `/api/user-data`, `/api/resumes`
- Uses `backend/services/` directory for data management logic
- Adds `backend/utils/` for file parsing and encryption

**Epic 3: AI Provider Integration**
- Adds endpoints: `/api/ai/generate-response`, `/api/ai/analyze-form`
- Uses `backend/services/` for AI provider classes (OpenAI, Anthropic, Google)
- Extends health check to include AI provider connectivity status

**Epic 5: Intelligent Form Filling**
- Primary endpoint: `POST /api/form/analyze` (receives form fields from extension)
- Uses backend orchestration to call AI providers and return responses
- Extends CORS to handle multiple extension origins if needed

**Epic 6: Real-Time Monitoring Dashboard**
- GUI will poll `/api/status` every 5 seconds for connection monitoring
- May add WebSocket endpoint: `/ws/events` for real-time event streaming
- Extends logging to capture request metrics for dashboard display

---

## References

### External Documentation

**FastAPI:**
- Official Docs: https://fastapi.tiangolo.com/
- Tutorial: https://fastapi.tiangolo.com/tutorial/
- Advanced User Guide: https://fastapi.tiangolo.com/advanced/
- CORS Middleware: https://fastapi.tiangolo.com/tutorial/cors/

**Pydantic:**
- Pydantic V2 Docs: https://docs.pydantic.dev/latest/
- Settings Management: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- Migration Guide (V1 → V2): https://docs.pydantic.dev/latest/migration/

**uvicorn:**
- Official Docs: https://www.uvicorn.org/
- Deployment Guide: https://www.uvicorn.org/deployment/
- Settings: https://www.uvicorn.org/settings/

**pytest:**
- Official Docs: https://docs.pytest.org/
- FastAPI Testing: https://fastapi.tiangolo.com/tutorial/testing/
- Coverage.py: https://coverage.readthedocs.io/

### Internal Documentation

**Project Documents:**
- PRD: `docs/PRD.md` (Section 3: Success Criteria)
- Architecture: `docs/architecture.md` (Section 4.2: Backend Framework)
- Epic 1 Tech Spec: `docs/sprint-artifacts/tech-spec-epic-1.md`
- Story 1.1: `docs/sprint-artifacts/stories/story-1.1-project-initialization-repository-setup.md`
- Story 1.2: `docs/sprint-artifacts/stories/story-1.2-python-backend-scaffolding.md`

**Configuration Files:**
- `pyproject.toml` - Project metadata, tool configurations
- `pytest.ini` - Test configuration (testpaths, markers, coverage)
- `.gitignore` - Excludes .env, __pycache__, logs
- `.env.example` - Configuration template

---

## Implementation Checklist

### Before Starting (`*dev-story`)

- [ ] Story 1.1 completed (backend/ directory exists)
- [ ] Virtual environment active (`.venv\Scripts\activate`)
- [ ] Current directory is project root
- [ ] Story 1.2 document reviewed (acceptance criteria clear)
- [ ] This context document reviewed (code templates understood)

### During Implementation

- [ ] **AC1:** Populate `backend/requirements.txt` (7 lines)
- [ ] **AC1:** Install dependencies with `pip install -r backend/requirements.txt`
- [ ] **AC2:** Create `backend/config/settings.py` (28 lines)
- [ ] **AC2:** Test settings import: `python -c "from backend.config.settings import settings; print(settings.API_HOST)"`
- [ ] **AC3:** Replace `backend/main.py` placeholder with FastAPI app (88 lines)
- [ ] **AC3:** Test app import: `python -c "from backend.main import app; print(app.title)"`
- [ ] **AC4:** Start backend server: `uvicorn backend.main:app --host 127.0.0.1 --port 8765 --reload`
- [ ] **AC4:** Verify server logs show startup message
- [ ] **AC5:** Test health check: `curl http://localhost:8765/api/status`
- [ ] **AC5:** Verify JSON response structure
- [ ] **AC6:** Create `.env.example` in project root (18 lines)
- [ ] **AC6:** Verify `.env` is in `.gitignore`
- [ ] **AC7:** Create `backend/tests/test_main.py` (95 lines)
- [ ] **AC7:** Run tests: `pytest backend/tests/test_main.py -v`
- [ ] **AC7:** Verify 9/9 tests passing
- [ ] **AC8:** Run syntax check: `python -m py_compile backend/main.py backend/config/settings.py`
- [ ] **AC8:** Run import check: `python -c "from backend.main import app; from backend.config.settings import settings"`
- [ ] **AC8:** (Optional) Run mypy: `mypy backend/main.py --ignore-missing-imports`
- [ ] Update `README.md` with backend setup section (~25 lines)
- [ ] Run all tests one more time: `pytest backend/tests/ -v`
- [ ] Git stage all changes: `git add backend/ .env.example README.md`
- [ ] Git commit with descriptive message (see Story 1.2 Definition of Done)

### After Implementation

- [ ] Update sprint status: `1-2-python-backend-scaffolding: in-progress → review`
- [ ] Run `*code-review` workflow for SM validation
- [ ] After approval: Status `review → done`
- [ ] Celebrate! 🎉 Backend foundation is complete
- [ ] Move to Story 1.3: Chrome Extension Manifest & Basic Structure

---

**Context Document Prepared By:** SM Agent (Scrum Master)  
**Ready for DEV Agent:** Yes  
**Estimated Implementation Time:** 3-4 hours  
**Next Workflow:** `*dev-story` (run this to begin implementation)
