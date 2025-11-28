# AutoResumeFiller

**Intelligent job application form auto-filling with AI assistance**

![Build Status](https://github.com/RagnarokFate/AutoResumeFiller/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/gh/RagnarokFate/AutoResumeFiller/branch/main/graph/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
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

### Code Quality
```bash
# Format code
black backend/ gui/

# Lint
pylint backend/ gui/

# Type checking
mypy backend/ gui/
```

### Project Structure
```
autoresumefiller/
├── backend/        # FastAPI backend (Python)
├── gui/            # PyQt5 desktop GUI (Python)
├── extension/      # Chrome extension (JavaScript)
├── docs/           # Documentation (PRD, Architecture, Epics)
├── tests/          # Integration and E2E tests
└── .github/        # CI/CD workflows
```

For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

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
