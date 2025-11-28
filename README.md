# AutoResumeFiller

**Intelligent job application form auto-filling with AI assistance**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
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
cd backend
pip install -r requirements.txt
cd ..
```

**4. Install GUI Dependencies**
```bash
cd gui
pip install -r requirements.txt
cd ..
```

**5. Run Backend (Development)**
```bash
# From project root
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8765
```

Backend will be available at `http://localhost:8765`. Test with:
```bash
curl http://localhost:8765/api/status
# Expected: {"status":"healthy","version":"1.0.0"}
```

**6. Run GUI (Development)**
```bash
# In a new terminal
python gui/main.py
```

**7. Load Chrome Extension (Development)**
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select the `extension/` directory from the project
5. Extension should load with green checkmark

**Verification:**
- Backend responds at `http://localhost:8765/api/status`
- GUI opens and shows tabbed interface
- Extension icon appears in Chrome toolbar
- Click extension icon → should show "Backend: Connected"

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
