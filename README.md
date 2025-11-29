# AutoResumeFiller

**Intelligent job application form auto-filling with AI assistance**

![Build Status](https://github.com/RagnarokFate/AutoResumeFiller/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/gh/RagnarokFate/AutoResumeFiller/branch/main/graph/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## Overview

AutoResumeFiller is a desktop application that automates job application form filling by intelligently extracting information from your resume and generating AI-powered responses to open-ended questions. The system consists of three integrated components:

1. **Chrome Extension (Manifest V3):** Detects job application forms and interacts with form fields
2. **Python Backend (FastAPI):** Orchestrates AI providers (OpenAI, Anthropic, Google) and manages local data
3. **PyQt5 GUI Dashboard:** Real-time monitoring, confirmation workflow, and data management

All data is stored locally on your machine with AES-256-GCM encryption. API keys are stored securely using your operating system's credential manager (Windows Credential Manager, macOS Keychain, Linux Secret Service).

**Project Status:** 🚧 Alpha - Active Development

---

## Features

### Core Functionality
- ✅ **Local Data Management:** Store resume, work history, education, skills locally in JSON/YAML
- ✅ **Multi-AI Provider Support:** OpenAI (GPT-4), Anthropic (Claude 3), Google (Gemini)
- ✅ **Intelligent Form Detection:** Auto-detect job application pages on common ATS platforms
- ✅ **Smart Field Mapping:** Classify form fields by purpose (name, email, experience, etc.)
- ✅ **AI-Powered Responses:** Generate contextual answers to open-ended questions
- ✅ **Real-Time Confirmation:** Review and approve/edit all responses before submission
- ✅ **Multi-Stage Applications:** Track progress across multi-page application flows
- ✅ **File Upload Handling:** Auto-attach resume/cover letter files
- ✅ **Conversational Updates:** Update your data via natural language chatbot

### Privacy & Security
- 🔒 **Local-First:** All data stored on your computer, never uploaded to external servers
- 🔒 **Encrypted Storage:** AES-256-GCM encryption for sensitive data at rest
- 🔒 **Secure API Keys:** OS-level credential storage (keyring)
- 🔒 **No Telemetry:** Zero analytics or tracking by default (opt-in only)

### Platform Support
- **Operating Systems:** Windows 10/11, macOS 12+, Linux (Ubuntu 20.04+)
- **Browsers:** Chrome 88+, Edge 88+ (Chromium-based)
- **ATS Platforms:** Workday, Greenhouse, Lever, LinkedIn Easy Apply, generic forms

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User's Computer                          │
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Chrome     │      │    PyQt5     │      │   FastAPI    │ │
│  │  Extension   │◄────►│     GUI      │◄────►│   Backend    │ │
│  │   (MV3)      │ HTTP │  Dashboard   │ HTTP │ (localhost)  │ │
│  └──────────────┘      └──────────────┘      └───────┬──────┘ │
│         │                                              │        │
│         │                                              │        │
│         │                                              ▼        │
│         │                                     ┌─────────────┐  │
│         │                                     │  Local Data │  │
│         │                                     │ (Encrypted) │  │
│         │                                     └─────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────┐                                          │
│  │  Job Application│                                          │
│  │  Form (DOM)     │                                          │
│  └─────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │ HTTPS (API calls only)
                               ▼
                    ┌─────────────────────┐
                    │   AI Providers      │
                    │ OpenAI / Anthropic  │
                    │ / Google            │
                    └─────────────────────┘
```

**Communication:** All components communicate via HTTP REST API on `localhost:8765`. The backend never exposes external network interfaces - all operations are local-first.

---

## Installation (Developer Setup)

### Prerequisites
- **Python 3.9+** (download from [python.org](https://www.python.org/downloads/))
- **Node.js 16+** (optional, for extension development tools)
- **Google Chrome** or **Microsoft Edge** (Chromium-based)
- **Git** (for cloning repository)

### Quick Start (< 15 minutes)

**1. Clone Repository**
```bash
git clone https://github.com/yourusername/autoresumefiller.git
cd autoresumefiller
```

**2. Set Up Python Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Unix/macOS)
source venv/bin/activate
```

**3. Install Backend Dependencies**
```bash
# Install backend dependencies
pip install -r backend/requirements.txt
```

**4. Install GUI Dependencies**
```bash
# Install GUI dependencies
pip install -r gui/requirements.txt
```

**5. Configure Environment (Optional)**

The backend works with default settings. For custom configuration:

```bash
# Copy environment template
cp .env.example .env  # Unix/macOS
copy .env.example .env  # Windows

# Edit .env to customize settings (optional)
```

Default configuration:
- API Host: `127.0.0.1` (localhost only)
- API Port: `8765`
- CORS Origins: `chrome-extension://*` (all extensions)

**6. Run Backend (Development)**
```bash
# From project root, with auto-reload
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8765
```

Backend will be available at `http://localhost:8765`. 

**Verify Backend:**
- **Health Check:** http://localhost:8765/api/status  
  Expected: `{"status": "healthy", "version": "1.0.0", "timestamp": "..."}`
- **API Documentation:** http://localhost:8765/docs (Swagger UI)
- **Alternative Docs:** http://localhost:8765/redoc

**7. Run Backend Tests**
```bash
# Run all backend tests
pytest backend/tests/ -v

# Run with coverage report
pytest backend/tests/ --cov=backend --cov-report=term-missing
```

Expected: 9/9 tests passing with >90% coverage on `backend/main.py`

**8. Run Desktop GUI Application**

The PyQt5 desktop application provides a central dashboard for monitoring form-filling activity, managing your data, configuring settings, and interacting with the chatbot.

**Prerequisites:**
- Backend running on `http://localhost:8765` (see step 6)
- PyQt5 dependencies installed: `pip install -r gui/requirements.txt`

**Launch GUI:**
```bash
python gui/main.py
```

**Expected Behavior:**
- Window opens within 5 seconds with title "AutoResumeFiller Dashboard"
- 4 tabs displayed: Monitor, My Data, Settings, Chatbot
- System tray icon appears in taskbar notification area
- Status bar shows "Backend: Connected ✅" if backend is running

**Features:**
- **Minimize to Tray**: Clicking close button (X) minimizes to system tray instead of exiting
- **Restore from Tray**: Double-click system tray icon to restore window
- **Exit Application**: Right-click tray icon → "Exit Application" to quit completely
- **Window Persistence**: Window size, position, and selected tab are remembered between sessions

**Troubleshooting GUI:**

| Issue | Solution |
|-------|----------|
| "Backend: Disconnected ❌" | Start backend: `uvicorn backend.main:app --host 127.0.0.1 --port 8765` |
| No system tray icon | Check taskbar notification area settings (Windows) |
| Import error: PyQt5 | Install dependencies: `pip install -r gui/requirements.txt` |
| Window doesn't restore size | Delete QSettings: `reg delete HKEY_CURRENT_USER\Software\AutoResumeFiller /f` (Windows) |

**9. Load Chrome Extension (Development)**
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select the `extension/` directory from the project
5. Extension should load with green checkmark

**Verify Extension:**
- Backend responds at `http://localhost:8765/api/status`
- Extension icon appears in Chrome toolbar
- Click extension icon → popup shows "Backend: Connected"
- Navigate to `https://boards.greenhouse.io/embed/job_board`
- Open DevTools (F12) → Console should show content script logs

**Supported Job Sites:**
- **Greenhouse:** `*.greenhouse.io/*`
- **Workday:** `*.workday.com/*`
- **Lever:** `*.lever.co/*`
- **LinkedIn:** `www.linkedin.com/jobs/*`

**Troubleshooting Extension:**

| Issue | Solution |
|-------|----------|
| Extension won't load | Verify `manifest.json` is valid JSON (use jsonlint.com) |
| Service worker inactive | Check JavaScript syntax: `node --check extension/background/service-worker.js` |
| Content script not injecting | Verify URL matches patterns in manifest.json |
| Popup shows "Disconnected" | Ensure backend is running and CORS configured for `chrome-extension://*` |
| Icon not displaying | Verify icon files exist: `extension/icons/icon16.png`, etc. |

---

## Troubleshooting

Common issues and solutions for development environment setup.

### Backend Issues

**❌ Issue: Backend won't start - "Address already in use" error**

```
OSError: [WinError 10048] Only one usage of each socket address (protocol/network address/port) is normally permitted
```

**✅ Solution:**

Another process is using port 8765. Kill the process or use a different port.

**Find process using port 8765:**
```bash
# Windows (PowerShell)
netstat -ano | findstr :8765

# Unix/macOS
lsof -i :8765
```

**Kill process:**
```bash
# Windows (PowerShell) - Replace <PID> with process ID from netstat
Stop-Process -Id <PID> -Force

# Unix/macOS - Replace <PID> with process ID from lsof
kill -9 <PID>
```

**Alternative: Use different port:**
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8766
```

---

**❌ Issue: Import errors - "ModuleNotFoundError: No module named 'fastapi'"**

```
ModuleNotFoundError: No module named 'fastapi'
```

**✅ Solution:**

Dependencies not installed or virtual environment not activated.

**Verify virtual environment is activated:**
```bash
# Windows (PowerShell) - Should show (venv) prefix in prompt
# If not activated, run:
.\venv\Scripts\activate

# Unix/macOS - Should show (venv) prefix in prompt
# If not activated, run:
source venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r backend/requirements.txt
```

**Verify installation:**
```bash
python -c "from fastapi import FastAPI; print('FastAPI installed successfully')"
```

---

**❌ Issue: Health check fails - "Connection refused" or "ERR_CONNECTION_REFUSED"**

**✅ Solution:**

Backend is not running or not listening on correct host/port.

**Verify backend is running:**
- Check terminal where you ran `uvicorn` command
- Look for: `Uvicorn running on http://127.0.0.1:8765 (Press CTRL+C to quit)`

**If not running, start backend:**
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8765
```

**Test health check:**
```bash
# Command line
curl http://localhost:8765/api/status

# Or open in browser
# http://localhost:8765/api/status
```

**Expected response:**
```json
{"status":"healthy","version":"1.0.0","timestamp":"2025-11-29T12:34:56.789Z"}
```

---

### Python Environment Issues

**❌ Issue: venv activation fails (Windows) - "Execution policy" error**

```
.\venv\Scripts\activate : File cannot be loaded because running scripts is disabled on this system
```

**✅ Solution:**

Windows PowerShell execution policy prevents script execution.

**Fix (Run PowerShell as Administrator):**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Explanation:**
- `RemoteSigned`: Allows local scripts to run, requires downloaded scripts to be signed
- `CurrentUser`: Only affects your user account (doesn't require admin for future use)

**Verify fix:**
```bash
Get-ExecutionPolicy -Scope CurrentUser
# Should show: RemoteSigned
```

**Now activate venv:**
```bash
.\venv\Scripts\activate
```

---

**❌ Issue: pytest command not found**

```
pytest: The term 'pytest' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

**✅ Solution:**

pytest not installed in virtual environment.

**Install pytest:**
```bash
pip install pytest pytest-cov
```

**Verify installation:**
```bash
pytest --version
# Should show: pytest 7.4.3 or similar
```

---

### GUI Issues

**❌ Issue: GUI doesn't show system tray icon**

**✅ Solution:**

Windows notification area settings may be hiding the icon.

**Windows 10/11:**
1. Right-click taskbar → "Taskbar settings"
2. Scroll to "Notification area"
3. Click "Select which icons appear on the taskbar"
4. Find "AutoResumeFiller" and toggle ON

**Alternative:**
- Click the "^" arrow in notification area to expand hidden icons
- Look for AutoResumeFiller icon there

---

**❌ Issue: GUI shows "Backend: Disconnected ❌"**

**✅ Solution:**

Backend is not running or not reachable.

**Verify backend is running:**
```bash
# Open new terminal and check health
curl http://localhost:8765/api/status
```

**If health check fails, start backend:**
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8765
```

**If health check succeeds but GUI still shows disconnected:**
- Restart GUI: Close window (or right-click tray → Exit), then `python gui/main.py`
- Check firewall settings (ensure localhost connections allowed)

---

**❌ Issue: Import error - "ModuleNotFoundError: No module named 'PyQt5'"**

**✅ Solution:**

GUI dependencies not installed.

**Install GUI dependencies:**
```bash
pip install -r gui/requirements.txt
```

**Verify installation:**
```bash
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 installed successfully')"
```

---

### Extension Issues

**❌ Issue: Extension won't load - "Failed to load extension"**

**✅ Solution:**

`manifest.json` may have syntax errors.

**Validate manifest.json:**
```bash
# Use JSON validator (online: jsonlint.com)
# Or use Node.js
node -e "console.log(JSON.parse(require('fs').readFileSync('extension/manifest.json')))"
```

**Common errors:**
- Trailing comma in last object property
- Missing quotes around property names
- Invalid JSON structure

**Fix:**
- Open `extension/manifest.json` in VS Code
- Check for syntax errors (red underlines)
- Save file and reload extension in Chrome

---

**❌ Issue: Extension popup shows "Backend: Disconnected"**

**✅ Solution:**

Backend is not running or CORS not configured for extension.

**Verify backend health check:**
```bash
curl http://localhost:8765/api/status
```

**If backend is running, check CORS configuration:**

Open `backend/config/settings.py` and verify:
```python
CORS_ORIGINS: str = "chrome-extension://*"  # Should allow all Chrome extensions
```

**Restart backend after CORS changes:**
```bash
# Stop backend (Ctrl+C in terminal)
# Start backend again
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8765
```

**Reload extension:**
1. Go to `chrome://extensions/`
2. Click refresh icon for AutoResumeFiller extension
3. Open extension popup again

---

**❌ Issue: Service worker inactive - "Service worker registration failed"**

**✅ Solution:**

JavaScript syntax error in service worker.

**Check service worker syntax:**
```bash
# Validate JavaScript syntax (requires Node.js)
node --check extension/background/service-worker.js
```

**Check Chrome extension errors:**
1. Go to `chrome://extensions/`
2. Find AutoResumeFiller
3. Click "Errors" button (if present)
4. Review error messages

**Common errors:**
- Syntax error in service-worker.js
- Missing import or export statements
- Invalid manifest.json configuration

---

**❌ Issue: Content script not injecting on job sites**

**✅ Solution:**

URL pattern in `manifest.json` doesn't match the page.

**Verify URL matches in manifest.json:**

Open `extension/manifest.json` and check `content_scripts.matches`:
```json
"matches": [
  "*://*.greenhouse.io/*",
  "*://*.workday.com/*",
  "*://*.lever.co/*",
  "*://www.linkedin.com/jobs/*"
]
```

**If your test page URL doesn't match:**
- Add pattern to matches array
- Reload extension in Chrome
- Refresh job site page

**Debug content script:**
1. Open DevTools (F12) on job site
2. Go to Console tab
3. Look for content script console.log messages
4. If no messages, content script not injecting

---

### General Issues

**❌ Issue: Git clone fails - "Permission denied" or "Repository not found"**

**✅ Solution:**

Repository URL is incorrect or access permissions issue.

**Verify repository URL:**
```bash
# Check repository exists and is public
# Visit https://github.com/RagnarokFate/AutoResumeFiller in browser
```

**If using SSH:**
```bash
# Clone with HTTPS instead
git clone https://github.com/RagnarokFate/AutoResumeFiller.git
```

---

**❌ Issue: Commands work in terminal but fail in VS Code integrated terminal**

**✅ Solution:**

VS Code terminal may not have virtual environment activated.

**Activate venv in VS Code terminal:**
```bash
# Windows (PowerShell)
.\venv\Scripts\activate

# Unix/macOS
source venv/bin/activate
```

**Verify venv is activated:**
- Prompt should show `(venv)` prefix

**Set default Python interpreter in VS Code:**
1. Open Command Palette (Ctrl+Shift+P)
2. Type "Python: Select Interpreter"
3. Choose `./venv/bin/python` (Unix) or `.\venv\Scripts\python.exe` (Windows)

---

### Still Having Issues?

If you encounter an issue not listed here:

1. **Check existing GitHub Issues:** [GitHub Issues](https://github.com/RagnarokFate/AutoResumeFiller/issues)
2. **Search for error message:** Copy exact error message and search GitHub Issues
3. **Open new issue:** If no existing issue found, [open a new issue](https://github.com/RagnarokFate/AutoResumeFiller/issues/new) with:
   - Operating System (Windows 10, macOS 13, Ubuntu 22.04, etc.)
   - Python version: `python --version`
   - Exact error message (copy from terminal)
   - Steps to reproduce the issue
   - What you've already tried

---

## Usage

**Current Status:** Infrastructure setup complete. Feature development in progress.

**Coming Soon:**
- Resume data import (PDF/DOCX parsing)
- AI provider configuration
- Form detection on job sites
- Auto-fill with confirmation workflow
- Real-time monitoring dashboard

**Progress Tracking:** See [Sprint Status](docs/sprint-artifacts/sprint-status.yaml)

---

## Development

### Running Tests
```bash
# All tests
pytest

# Unit tests only
pytest -m unit

# With coverage report
pytest --cov --cov-report=html
open htmlcov/index.html  # View coverage
```

**Testing Best Practices:**
- Run tests before committing: `pytest -m unit` (fast, <1 second)
- Check coverage for modified files: `pytest --cov=backend.main --cov-report=term-missing`
- Target coverage: >70% for backend modules (currently 100% for main.py and settings.py)

**Test Organization:**
- Unit tests marked with `@pytest.mark.unit` (test single functions/methods)
- Integration tests marked with `@pytest.mark.integration` (test component interactions)
- E2E tests marked with `@pytest.mark.e2e` (test full user workflows)

**Run Specific Tests:**
```bash
# Run specific test file
pytest backend/tests/test_main.py

# Run specific test class
pytest backend/tests/test_main.py::TestHealthCheckEndpoint

# Run specific test method
pytest backend/tests/test_main.py::TestHealthCheckEndpoint::test_health_check_success
```

**For detailed testing guide, see [backend/tests/README.md](backend/tests/README.md)** (comprehensive guide with fixtures, AAA pattern, parametrized tests, and troubleshooting).

---

### Code Quality

**Code Formatting (Black):**
```bash
# Auto-format Python code to PEP 8 style
black backend/ gui/

# Check formatting without modifying files
black --check backend/ gui/
```

Black enforces consistent code style across the project. Configuration in `pyproject.toml` [tool.black] section.

**Static Code Analysis (Pylint):**
```bash
# Lint code for errors, code smells, and style issues
pylint backend/ gui/

# Lint specific file
pylint backend/main.py
```

Pylint performs static code analysis to catch bugs and enforce coding standards. Configuration in `.pylintrc` file.

**Type Checking (Mypy):**
```bash
# Check Python type hints (Python 3.9+ type annotations)
mypy backend/ gui/

# Check specific file with verbose output
mypy backend/main.py --show-error-codes
```

Mypy validates type hints to catch type-related bugs before runtime. Configuration in `pyproject.toml` [tool.mypy] section.

**Pre-Commit Hooks (Optional):**
```bash
# Install pre-commit framework
pip install pre-commit

# Enable pre-commit hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

Pre-commit hooks automatically run black, pylint, and mypy before each commit to ensure code quality.

---

### Project Structure

```
autoresumefiller/
├── backend/        # FastAPI REST API (Python 3.9+)
│   ├── api/        # API route handlers
│   ├── services/   # Business logic services
│   ├── config/     # Configuration (settings.py)
│   ├── utils/      # Utility functions
│   ├── tests/      # Unit tests with pytest
│   └── main.py     # FastAPI application entry point
├── gui/            # PyQt5 Desktop Dashboard (Python 3.9+)
│   ├── windows/    # Main window and dialogs
│   ├── widgets/    # Custom PyQt5 widgets
│   ├── services/   # Backend communication services
│   ├── resources/  # UI resources (icons, styles)
│   └── main.py     # GUI application entry point
├── extension/      # Chrome Extension Manifest V3 (JavaScript)
│   ├── manifest.json   # Extension configuration
│   ├── background/     # Service worker background script
│   ├── content/        # Content scripts (form detection)
│   ├── popup/          # Extension popup UI
│   └── lib/            # Shared JavaScript libraries
├── docs/           # Project Documentation
│   ├── PRD.md             # Product Requirements Document
│   ├── architecture.md    # System Architecture
│   ├── epics.md           # Epic Breakdown
│   └── sprint-artifacts/  # Sprint planning and stories
├── tests/          # Integration and E2E Tests (future)
├── .github/        # GitHub Actions CI/CD Workflows
│   └── workflows/
│       └── ci.yml  # Continuous Integration pipeline
└── .bmad/          # BMAD Method v6 (AI-driven agile framework)
```

**Key Directories:**
- `backend/`: FastAPI REST API for AI orchestration and data management
- `gui/`: PyQt5 desktop application for user interface and monitoring
- `extension/`: Chrome Extension (Manifest V3) for form detection and filling
- `docs/`: Comprehensive project documentation (PRD, architecture, epics)
- `.github/workflows/`: CI/CD pipelines with pytest, black, pylint

**For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).**

---

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting pull requests.

**Development Process:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Issue Reporting:** Use [GitHub Issues](https://github.com/yourusername/autoresumefiller/issues) for bug reports and feature requests.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Why MIT?**
- Portfolio-friendly (demonstrates open source contribution)
- Commercial use allowed
- Minimal restrictions
- Industry standard for developer tools

---

## Roadmap

**Phase 1: Foundation (Current)**
- [x] Project structure and scaffolding
- [ ] Backend API implementation
- [ ] Chrome extension manifest
- [ ] GUI application shell

**Phase 2: Core Features**
- [ ] Local data management
- [ ] AI provider integration
- [ ] Form detection algorithms
- [ ] Auto-fill implementation

**Phase 3: User Experience**
- [ ] Real-time monitoring dashboard
- [ ] Confirmation workflow
- [ ] Conversational chatbot

**Phase 4: Production**
- [ ] PyInstaller packaging
- [ ] Setup wizard
- [ ] Documentation
- [ ] Distribution (GitHub Releases)

See [Epics Document](docs/epics.md) for detailed breakdown.

---

## Support

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/yourusername/autoresumefiller/issues)
- **Email:** your.email@example.com

---

**Built with ❤️ using Python, FastAPI, PyQt5, and Chrome Extension APIs**
