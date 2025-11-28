# Epic Technical Specification: Foundation & Core Infrastructure

Date: 2025-11-28
Author: Ragnar
Epic ID: 1
Status: Draft

---

## Overview

Epic 1 establishes the foundational infrastructure for AutoResumeFiller - a multi-component desktop application that automates job application form filling through AI-powered response generation. This epic delivers the project scaffolding, repository structure, build system, CI/CD pipeline, and deployment foundation required for all subsequent development work.

The foundation includes three core components: (1) Python FastAPI backend for AI orchestration and data management, (2) Chrome Extension (Manifest V3) for form detection and interaction, and (3) PyQt5 desktop GUI for real-time monitoring and configuration. All components communicate via HTTP REST API on localhost:8765, prioritizing local-first privacy and developer productivity.

While this epic delivers no user-facing features, it's essential for greenfield projects and enables Phase 4 implementation with quality standards, automated testing (80%+ coverage target), and professional development practices suitable for portfolio showcase.

## Objectives and Scope

**In Scope:**
- Project repository initialization with git, proper .gitignore, and license (MIT)
- Python package management via pyproject.toml with dependencies and dev tools
- FastAPI backend scaffolding with async/await patterns, CORS configuration, health check endpoint
- Chrome Extension Manifest V3 structure with content scripts, background service worker, and popup
- PyQt5 GUI application shell with tabbed interface (Monitor, Data, Settings, Chatbot) and system tray
- GitHub Actions CI/CD pipeline for automated testing (pytest, coverage), linting (black, pylint, mypy), and release builds
- Testing infrastructure with pytest, fixtures, mocks, and 70%+ initial coverage
- Comprehensive development documentation (README.md, CONTRIBUTING.md, setup instructions)

**Out of Scope:**
- Any form detection logic (Epic 4)
- AI provider integrations (Epic 3)
- Data management implementation (Epic 2)
- GUI tab implementations beyond placeholders (Epic 6)
- Production packaging and distribution (Epic 7)
- Actual user data or API keys

**Success Criteria:**
- All three components (backend, extension, GUI) run successfully in development mode
- CI/CD pipeline passes all checks (tests, linting, type checking) with green status
- Developer can clone repo and have working environment in <15 minutes
- Test coverage reaches 70%+ for scaffolded code (health check, basic utilities)
- Project demonstrates professional software engineering practices

## System Architecture Alignment

Epic 1 implements the foundational layer of the AutoResumeFiller architecture as defined in `docs/architecture.md`:

**Component Structure:**
- **Backend (FastAPI):** Runs on `localhost:8765` with async/await support for future AI API calls. CORS configured for `chrome-extension://*` origins to enable extension communication. Health check endpoint (`GET /api/status`) validates server availability.
- **Extension (Manifest V3):** Content scripts inject into job application pages, background service worker manages extension lifecycle and state, popup provides quick status/controls. All components communicate with backend via HTTP fetch().
- **GUI (PyQt5):** Tabbed interface (QTabWidget) with placeholders for Monitor, Data, Settings, and Chatbot tabs. System tray integration (QSystemTrayIcon) for minimize-to-tray behavior. QNetworkAccessManager for async HTTP to backend.

**Communication Pattern:**
```
Extension (content script) ──HTTP POST──> Backend (FastAPI)
GUI (PyQt5) ──────────────────HTTP GET──> Backend (FastAPI)
```

**Technology Stack Alignment:**
- Python 3.9+ (as specified in architecture)
- FastAPI + uvicorn (async ASGI server)
- PyQt5 (not Tkinter - architecture decision favors PyQt5 for professional appearance)
- Chrome Extension Manifest V3 (V2 deprecated)
- JSON/YAML for configuration (local filesystem)

**Architectural Constraints Addressed:**
- Localhost-only backend (`127.0.0.1:8765`) - no external network exposure (security requirement)
- No cloud dependencies - all execution local (privacy-first design)
- Async patterns throughout - enables concurrent operations in future epics
- Modular structure - backend/services/, gui/windows/, extension/content/ for clean separation

## Detailed Design

### Services and Modules

| Module | Responsibility | Key Interfaces | Owner |
|--------|---------------|----------------|-------|
| **backend/main.py** | FastAPI app initialization, startup/shutdown handlers, health check endpoint | `GET /api/status` → `{"status": "healthy", "version": "1.0.0"}` | Backend |
| **backend/config/settings.py** | Environment configuration using pydantic-settings, load from .env | `Settings` class with `API_HOST`, `API_PORT`, `LOG_LEVEL`, `CORS_ORIGINS` | Backend |
| **backend/api/** | API route modules (placeholder for future endpoints) | Future: `/api/analyze-form`, `/api/generate-response`, `/api/user-data` | Backend |
| **backend/services/** | Business logic services (placeholder for AI, data management) | Future: `AIService`, `DataManager`, `FormAnalyzer` | Backend |
| **extension/background/service-worker.js** | Extension lifecycle, message routing between content scripts and backend | `chrome.runtime.onMessage` listener, `fetch()` to localhost:8765 | Extension |
| **extension/content/content-script.js** | DOM interaction, form detection (placeholder), message passing | `chrome.runtime.sendMessage()`, placeholder `detectJobApplicationForm()` | Extension |
| **extension/popup/popup.html** | Quick status display, link to GUI dashboard | Shows backend connection status (Connected/Disconnected) | Extension |
| **gui/main.py** | QApplication entry point, MainWindow initialization, system tray setup | `main()` function, application icon, exit handling | GUI |
| **gui/windows/main_window.py** | MainWindow(QMainWindow) with tabbed interface, system tray icon | 4 tabs (Monitor, Data, Settings, Chatbot), minimize to tray on close | GUI |

### Data Models and Contracts

**Configuration Model (Pydantic):**
```python
# backend/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8765
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["chrome-extension://*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

**Health Check Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-28T10:00:00Z"
}
```

**Extension Manifest Schema (manifest.json):**
```json
{
  "manifest_version": 3,
  "name": "AutoResumeFiller",
  "version": "1.0.0",
  "description": "Intelligent job application form auto-filling with AI assistance",
  "permissions": ["storage", "activeTab"],
  "host_permissions": ["http://localhost:8765/*"],
  "content_scripts": [{
    "matches": [
      "*://*.greenhouse.io/*",
      "*://*.workday.com/*",
      "*://*.lever.co/*",
      "*://linkedin.com/jobs/*"
    ],
    "js": ["content/content-script.js"]
  }],
  "background": {
    "service_worker": "background/service-worker.js"
  },
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  }
}
```

**Repository Structure (Directory Tree):**
```
autoresumefiller/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Test + lint on push/PR
│       └── release.yml         # Build + release on tag
├── backend/
│   ├── api/                    # API route modules
│   ├── services/               # Business logic
│   ├── config/
│   │   └── settings.py         # Configuration
│   ├── utils/                  # Utilities
│   ├── tests/
│   │   ├── conftest.py         # pytest fixtures
│   │   └── test_main.py        # Health check tests
│   ├── main.py                 # FastAPI app
│   └── requirements.txt
├── gui/
│   ├── windows/
│   │   └── main_window.py      # MainWindow class
│   ├── widgets/                # Custom widgets (future)
│   ├── services/               # GUI services
│   ├── resources/
│   │   └── icons/              # App icons
│   ├── tests/
│   ├── main.py                 # GUI entry point
│   └── requirements.txt
├── extension/
│   ├── manifest.json
│   ├── background/
│   │   └── service-worker.js
│   ├── content/
│   │   └── content-script.js
│   ├── popup/
│   │   ├── popup.html
│   │   ├── popup.css
│   │   └── popup.js
│   ├── lib/                    # Shared utilities
│   └── icons/
├── docs/                       # Documentation
├── tests/
│   └── integration/            # E2E tests (future)
├── .gitignore
├── .pylintrc
├── pyproject.toml              # Python project config
├── pytest.ini
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── LICENSE (MIT)
```

### APIs and Interfaces

**Backend REST API (FastAPI):**

**Health Check Endpoint:**
- **Method:** GET
- **Path:** `/api/status`
- **Request:** None
- **Response:** `200 OK`
  ```json
  {
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2025-11-28T10:00:00.000Z"
  }
  ```
- **Error:** `500 Internal Server Error` (server misconfigured)

**CORS Configuration:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*"],  # Only extension origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Extension Message Passing (chrome.runtime API):**

**Content Script → Background Worker:**
```javascript
// content/content-script.js
chrome.runtime.sendMessage({
  type: 'FORM_DETECTED',
  payload: { url: window.location.href }
}, (response) => {
  console.log('Background response:', response);
});
```

**Background Worker Message Listener:**
```javascript
// background/service-worker.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'FORM_DETECTED') {
    console.log('Form detected on:', message.payload.url);
    sendResponse({ received: true });
  }
});
```

**GUI → Backend HTTP (PyQt5 QNetworkAccessManager):**
```python
# gui/windows/main_window.py
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QUrl

self.network_manager = QNetworkAccessManager()
self.network_manager.finished.connect(self.handle_backend_response)

request = QNetworkRequest(QUrl("http://localhost:8765/api/status"))
self.network_manager.get(request)
```

### Workflows and Sequencing

**Developer Setup Workflow:**
1. Clone repository: `git clone <repo-url>`
2. Create Python virtual environment: `python -m venv venv`
3. Activate venv: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install backend dependencies: `pip install -r backend/requirements.txt`
5. Install GUI dependencies: `pip install -r gui/requirements.txt`
6. Start backend: `uvicorn backend.main:app --reload` (runs on `localhost:8765`)
7. Start GUI: `python gui/main.py` (opens PyQt5 dashboard)
8. Load extension: Chrome → Extensions → Developer Mode → Load Unpacked → `extension/` directory
9. Verify health check: Navigate to `http://localhost:8765/api/status` (should return JSON with "healthy" status)

**CI/CD Workflow (GitHub Actions):**
1. Developer pushes code to GitHub
2. GitHub Actions triggers `.github/workflows/ci.yml`
3. **test-backend job:**
   - Setup Python 3.11
   - Install dependencies from `backend/requirements.txt` + pytest
   - Run `pytest backend/tests/ --cov=backend --cov-report=term`
   - Fail if coverage <70% or tests fail
4. **lint-backend job:**
   - Run `black --check backend/ gui/` (formatting)
   - Run `pylint backend/ gui/` (linting, threshold 8.0+)
   - Run `mypy backend/ gui/ --strict` (type checking)
5. **test-extension job:**
   - Validate `manifest.json` schema (using JSON schema validator)
   - Run `eslint extension/**/*.js` (JavaScript linting)
6. All jobs must pass (green checkmark) for PR approval

**Release Workflow (triggered on git tag `v*`):**
1. Developer creates git tag: `git tag v1.0.0`
2. Push tag: `git push --tags`
3. GitHub Actions triggers `.github/workflows/release.yml`
4. Build Windows executable with PyInstaller (Epic 7 - placeholder in Epic 1)
5. Create GitHub Release with changelog
6. Attach artifacts (executable ZIP, extension folder)

## Non-Functional Requirements

### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Backend startup time | <3 seconds | Time from `uvicorn` launch to health check responding |
| Health check response | <50ms | Time from request to response (localhost) |
| GUI launch time | <5 seconds | Time from `python gui/main.py` to window visible |
| Extension load time | <2 seconds | Time from Chrome loading extension to initialization complete |
| CI pipeline duration | <5 minutes | Total time for all jobs (test + lint) |

**Rationale:** Foundation must be fast to not slow down development cycles. Quick startup times enable rapid iteration (test-debug-fix loop).

### Security

| Requirement | Implementation | Source |
|-------------|----------------|--------|
| Localhost-only backend | FastAPI binds to `127.0.0.1` (not `0.0.0.0`) | Architecture (privacy-first) |
| CORS restrictions | Only `chrome-extension://*` origins allowed | Architecture (prevent unauthorized access) |
| No secrets in repository | `.gitignore` excludes `*.key`, `.env`, API keys | Best practice |
| Secure dependencies | `pip install` uses known good versions, no wildcards | Supply chain security |

**Threat Model (Epic 1 scope):**
- ❌ **Out of scope:** Data encryption (Epic 2), API key storage (Epic 3)
- ✅ **In scope:** Network isolation (localhost only), CORS protection, secret file exclusion

### Reliability/Availability

| Requirement | Implementation |
|-------------|----------------|
| Backend restarts on crash | Use process manager (systemd, PM2) in production - not Epic 1 concern |
| Graceful shutdown | FastAPI `@app.on_event("shutdown")` handler closes resources cleanly |
| Extension resilience | Content script errors don't crash browser (isolated execution context) |
| GUI crash recovery | Qt exception handler prevents full application exit on widget errors |

**Availability Target (Development):** Best-effort (developer manually restarts). Production availability handled in Epic 7 (systemd service, auto-restart).

### Observability

| Component | Logging Strategy | Output |
|-----------|-----------------|--------|
| Backend | Structured JSON logs with timestamps, log levels, request IDs | Stdout (captured by uvicorn) |
| GUI | Qt message handler logs to file (`~/.autoresumefiller/logs/gui.log`) | Rotating file (10MB max, 5 backups) |
| Extension | `console.log()` to Chrome DevTools console | Browser DevTools |

**Log Levels:**
- **DEBUG:** Verbose (function entry/exit, variable values)
- **INFO:** Normal operation (server started, request received)
- **WARNING:** Unexpected but handled (API call retried, deprecated config)
- **ERROR:** Operation failed (exception caught, API unavailable)
- **CRITICAL:** Service cannot continue (port in use, missing dependencies)

**Metrics (Future - Epic 6):**
- Health check call frequency
- API endpoint latency (p50, p95, p99)
- Error rates by endpoint

## Dependencies and Integrations

### Python Dependencies (backend/requirements.txt)

**Core Framework:**
```
fastapi>=0.104.0           # Web framework (async)
uvicorn[standard]>=0.24.0  # ASGI server with websocket support
pydantic>=2.5.0            # Data validation
pydantic-settings>=2.1.0   # Settings management from .env
```

**HTTP & Utilities:**
```
python-multipart>=0.0.6    # File upload support (future)
python-dotenv>=1.0.0       # .env file loading
```

**Development:**
```
pytest>=7.4.0
pytest-asyncio>=0.21.0     # Async test support
pytest-cov>=4.1.0          # Coverage reporting
pytest-mock>=3.12.0        # Mocking utilities
black>=23.11.0             # Code formatting
pylint>=3.0.0              # Linting
mypy>=1.7.0                # Type checking
```

### Python Dependencies (gui/requirements.txt)

```
PyQt5>=5.15.10
PyQt5-Qt5>=5.15.2
requests>=2.31.0           # HTTP client for backend
```

### Extension Dependencies

**No external dependencies** - vanilla JavaScript using browser APIs:
- `chrome.runtime` - Message passing
- `chrome.storage` - Local storage
- `fetch()` - HTTP requests to backend

### System Requirements

| Requirement | Minimum | Recommended | Notes |
|-------------|---------|-------------|-------|
| Python Version | 3.9 | 3.11 | Type hints, async improvements |
| Operating System | Windows 10, macOS 10.15, Ubuntu 20.04 | Windows 11, macOS 13+, Ubuntu 22.04 | PyQt5 cross-platform |
| RAM | 2GB available | 4GB available | Python + GUI + Browser |
| Disk Space | 500MB | 1GB | Dependencies + logs |
| Chrome Version | 110+ | Latest stable | Manifest V3 support |

### External Integrations (Epic 1)

**None.** Epic 1 has no external service dependencies:
- ❌ No AI APIs (Epic 3)
- ❌ No cloud storage (never - local-first design)
- ❌ No telemetry services (Epic 7 - optional, privacy-preserving)

**Future Integrations (reference only):**
- Epic 3: OpenAI API, Anthropic API, Google Gemini API (via HTTPS)
- Epic 7: GitHub Releases API (for update checks)

## Acceptance Criteria (Authoritative)

### AC1: Repository Structure Created
**Given** a developer clones the repository  
**When** they inspect the directory structure  
**Then** all required folders exist: `backend/`, `gui/`, `extension/`, `docs/`, `tests/`, `.github/workflows/`  
**And** all configuration files are present: `pyproject.toml`, `.gitignore`, `.pylintrc`, `pytest.ini`, `README.md`, `LICENSE`

### AC2: Backend Starts Successfully
**Given** backend dependencies are installed (`pip install -r backend/requirements.txt`)  
**When** developer runs `uvicorn backend.main:app --reload`  
**Then** server starts on `http://127.0.0.1:8765` within 3 seconds  
**And** no errors appear in console output  
**And** health check endpoint responds: `curl http://localhost:8765/api/status` returns `{"status": "healthy", "version": "1.0.0"}`

### AC3: Extension Loads Without Errors
**Given** Chrome browser is running in Developer Mode  
**When** developer loads unpacked extension from `extension/` directory  
**Then** extension appears in `chrome://extensions/` with green "Loaded" status  
**And** no errors appear in Chrome DevTools console  
**And** extension icon appears in browser toolbar

### AC4: GUI Launches Successfully
**Given** GUI dependencies are installed (`pip install -r gui/requirements.txt`)  
**When** developer runs `python gui/main.py`  
**Then** PyQt5 window opens within 5 seconds with title "AutoResumeFiller Dashboard"  
**And** 4 tabs are visible: "Monitor", "My Data", "Settings", "Chatbot"  
**And** system tray icon appears (on Windows/Linux) or menu bar icon (on macOS)  
**And** closing window minimizes to tray instead of exiting application

### AC5: CI Pipeline Passes All Checks
**Given** code is pushed to GitHub repository  
**When** GitHub Actions runs `.github/workflows/ci.yml`  
**Then** `test-backend` job passes with 70%+ coverage  
**And** `lint-backend` job passes (black, pylint 8.0+, mypy)  
**And** `test-extension` job passes (manifest validation)  
**And** all jobs show green checkmark on GitHub

### AC6: Tests Run Successfully
**Given** backend code with tests in `backend/tests/`  
**When** developer runs `pytest` from project root  
**Then** all tests pass (exit code 0)  
**And** coverage report shows 70%+ coverage for `backend/` module  
**And** HTML coverage report generated in `htmlcov/` directory

### AC7: Developer Setup Completes in <15 Minutes
**Given** a new developer with Python 3.11 and Chrome installed  
**When** following README.md instructions  
**Then** they successfully clone, install dependencies, start all 3 components (backend, GUI, extension) within 15 minutes  
**And** health check endpoint responds successfully  
**And** GUI displays placeholders for all tabs  
**And** extension loads without errors

### AC8: CORS Protection Works
**Given** backend is running on `localhost:8765`  
**When** making HTTP request from non-extension origin (e.g., `http://example.com`)  
**Then** request is blocked with CORS error  
**And** request from `chrome-extension://[extension-id]/` succeeds

### AC9: Documentation is Complete
**Given** developer reads `README.md`  
**When** reviewing documentation sections  
**Then** README includes: Overview, Features, Prerequisites, Installation (step-by-step), Running the Application, Development (testing/linting), Contributing, License  
**And** badges are present: Build status, Coverage, License, Python version  
**And** `CONTRIBUTING.md` exists with contribution guidelines

### AC10: Extension Popup Shows Backend Status
**Given** extension is loaded and backend is running  
**When** clicking extension icon in browser toolbar  
**Then** popup appears showing "Backend: Connected"  
**And** link to open GUI dashboard is present

## Traceability Mapping

| Acceptance Criteria | Spec Section(s) | Component(s) | Test Idea |
|---------------------|----------------|--------------|-----------|
| AC1: Repository Structure | Data Models → Repository Structure | All (repository) | Script to verify directory tree |
| AC2: Backend Starts | APIs and Interfaces → Health Check | backend/main.py | `test_health_check_endpoint()` |
| AC3: Extension Loads | Data Models → Extension Manifest | extension/manifest.json | Manual load in Chrome |
| AC4: GUI Launches | Services and Modules → gui/main.py | gui/windows/main_window.py | `test_gui_startup()` (Qt test) |
| AC5: CI Pipeline Passes | Workflows → CI/CD Workflow | .github/workflows/ci.yml | Run pipeline on test branch |
| AC6: Tests Run | Non-Functional → Observability | backend/tests/ | Execute `pytest` locally |
| AC7: Developer Setup | Workflows → Developer Setup | README.md | Fresh VM test |
| AC8: CORS Protection | APIs and Interfaces → CORS | backend/main.py | `test_cors_headers()` |
| AC9: Documentation | Detailed Design | docs/, README.md | Manual review checklist |
| AC10: Extension Popup | APIs and Interfaces → Extension | extension/popup/ | Manual test with running backend |

## Risks, Assumptions, Open Questions

### Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **R1: PyQt5 binary wheels unavailable for some platforms** | Medium | Document platform support in README; provide troubleshooting for manual PyQt5 build if needed |
| **R2: Chrome extension load fails on some Chromium variants** | Low | Test on Chrome, Edge, Brave; document supported browsers in README |
| **R3: Port 8765 already in use on developer machine** | Low | Make port configurable via .env file (`API_PORT`); health check detects port conflict |
| **R4: CI pipeline takes >5 minutes (slow dependency install)** | Medium | Cache pip dependencies using `actions/cache` in GitHub Actions |
| **R5: Developer skips setup steps, assumes components auto-start** | Medium | Clear README with numbered steps, visual indicators (✅ checkmarks), troubleshooting section |

### Assumptions

| Assumption | Validation | Impact if Wrong |
|------------|-----------|-----------------|
| **A1: Developer has Python 3.9+ installed** | README lists prerequisites | Setup fails immediately; add version check in setup script |
| **A2: Developer uses Chrome or Chromium-based browser** | README specifies Chrome requirement | Extension won't load; document Firefox support as future enhancement |
| **A3: Localhost (127.0.0.1) is accessible** | Standard networking assumption | Backend unreachable; document firewall troubleshooting |
| **A4: Developer is comfortable with command line** | Target audience is software engineers | Minimal impact; provide exact copy-paste commands |
| **A5: Git is installed for version control** | Standard developer tool | Cannot clone repo; add Git to prerequisites |

### Open Questions

| Question | Owner | Resolution Target |
|----------|-------|------------------|
| **Q1: Should we support Firefox extension as well?** | Architect | Deferred to Epic 7; start Chrome-only for MVP |
| **Q2: What icon/logo should we use for the application?** | Designer (or Ragnar) | Placeholder colored square for Epic 1; design icon in Epic 6 |
| **Q3: Should CI pipeline deploy to staging automatically?** | DevOps (Ragnar) | No for Epic 1; manual deployment sufficient for solo developer |
| **Q4: How should we handle multiple developers running backend on same port?** | Architect | Low priority; configurable port (.env) sufficient |
| **Q5: Should we use Docker for consistent dev environment?** | Architect | Deferred to Epic 7; Python venv sufficient for MVP |

## Test Strategy Summary

### Test Levels

**Unit Tests (70%+ coverage target):**
- **Backend:** Health check endpoint, CORS middleware, settings loading
- **GUI:** Window initialization, tab creation, system tray setup
- **Extension:** Manifest schema validation (via JSON schema)

**Integration Tests (Epic 1 scope - minimal):**
- **Backend ↔ GUI:** GUI can successfully call `/api/status` and parse response
- **Extension ↔ Backend:** Extension can fetch from `http://localhost:8765/api/status`

**End-to-End Tests (out of scope for Epic 1):**
- Deferred to Epic 5 (form filling) and Epic 6 (full user workflows)

### Testing Frameworks

| Component | Framework | Rationale |
|-----------|-----------|-----------|
| Backend | pytest + pytest-asyncio | Standard Python testing, async support |
| GUI | pytest + pytest-qt | PyQt5 widget testing support |
| Extension | Manual testing + manifest schema validation | JavaScript unit testing deferred to Epic 4 |

### Test Execution

**Local Development:**
```bash
# Run all tests with coverage
pytest --cov=backend --cov=gui --cov-report=html --cov-report=term

# Run only backend tests
pytest backend/tests/

# Run only GUI tests
pytest gui/tests/

# Watch mode (re-run on file change)
pytest-watch
```

**CI/CD (GitHub Actions):**
```yaml
- name: Run tests with coverage
  run: pytest --cov=backend --cov=gui --cov-report=term --cov-fail-under=70
```

### Coverage Goals

| Module | Target Coverage | Rationale |
|--------|----------------|-----------|
| backend/main.py | 90% | Critical entry point |
| backend/config/settings.py | 80% | Configuration loading |
| gui/main.py | 80% | GUI entry point |
| gui/windows/main_window.py | 70% | Widget initialization |

### Edge Cases and Negative Tests

**Backend:**
- ✅ Health check returns 500 if server misconfigured
- ✅ CORS rejects requests from non-extension origins
- ✅ Invalid settings in .env raise validation error

**Extension:**
- ✅ Manifest missing required field fails validation
- ✅ Content script handles page without forms gracefully

**GUI:**
- ✅ Backend unavailable shows "Disconnected" status
- ✅ Window restores from tray when icon clicked
- ✅ Closing window minimizes to tray (does not exit)

### Manual Test Checklist (Epic 1)

**Pre-Commit Checklist:**
- [ ] Run `pytest` - all tests pass
- [ ] Run `black --check backend/ gui/` - formatting correct
- [ ] Run `pylint backend/ gui/` - score ≥8.0
- [ ] Run `mypy backend/ gui/ --strict` - no type errors
- [ ] Start backend - health check responds
- [ ] Start GUI - window opens, tabs visible
- [ ] Load extension - no console errors
- [ ] CI pipeline passes on GitHub

---

## Summary

Epic 1 delivers a production-ready foundation for AutoResumeFiller with professional development practices:
- ✅ Multi-component architecture (backend, extension, GUI)
- ✅ Automated testing and CI/CD (70%+ coverage)
- ✅ Developer-friendly setup (<15 minutes)
- ✅ Security-first design (localhost-only, CORS protection)
- ✅ Portfolio-quality documentation

**Next Epic:** Epic 2 (Local Data Management System) builds on this foundation to implement user data schemas, file parsing (PDF/DOCX), encryption, and conversational data updates.

**Status:** Ready for implementation. All acceptance criteria are testable, dependencies are specified, and integration points are clearly defined.
