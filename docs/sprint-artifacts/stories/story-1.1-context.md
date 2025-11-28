# Story 1.1 Technical Context: Project Initialization & Repository Setup

**Story ID:** 1.1  
**Context Created:** 2025-11-28  
**Author:** SM Agent (Ragnar)  
**Context Type:** Just-In-Time Technical Guidance  
**Status:** Ready for Implementation

---

## Purpose

This document provides implementation-specific technical context for Story 1.1, bridging the gap between the epic tech spec and the story acceptance criteria. It clarifies ambiguities, provides code templates, documents tooling decisions, and addresses common pitfalls.

**When to use this document:**
- During story implementation (DEV agent reference)
- When acceptance criteria seem unclear
- When choosing between alternative implementations
- When debugging setup issues

---

## Quick Reference

### Critical Paths

**Existing Project State:**
```
AutoResumeFiller/
├── .bmad/                          # ✅ Exists (workflow files, excluded from git)
├── .github/
│   └── copilot-instructions.md     # ✅ Exists (excluded from git)
├── docs/
│   ├── PRD.md                      # ✅ Exists (committed)
│   ├── architecture.md             # ✅ Exists (committed)
│   ├── epics.md                    # ✅ Exists (committed)
│   └── sprint-artifacts/
│       ├── sprint-status.yaml      # ✅ Exists (committed)
│       ├── tech-spec-epic-*.md     # ✅ Exists (committed, 7 files)
│       └── stories/
│           └── story-1.1-*.md      # ✅ Exists (committed)
├── .gitignore                      # ✅ Exists (comprehensive, committed)
└── README.md                       # ❌ Create in this story (project-specific)
```

**Story 1.1 Will Create:**
```
AutoResumeFiller/
├── .github/
│   └── workflows/                  # NEW - CI/CD placeholders
│       ├── ci.yml
│       └── release.yml
├── backend/                        # NEW - Python backend structure
│   ├── api/
│   ├── services/
│   ├── config/
│   ├── utils/
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── gui/                            # NEW - PyQt5 GUI structure
│   ├── windows/
│   ├── widgets/
│   ├── services/
│   ├── resources/icons/
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── extension/                      # NEW - Chrome extension structure
│   ├── background/
│   ├── content/
│   ├── popup/
│   ├── lib/
│   └── icons/
├── tests/
│   └── integration/                # NEW - E2E test directory
├── .editorconfig                   # NEW
├── .pylintrc                       # NEW
├── pyproject.toml                  # NEW
├── pytest.ini                      # NEW
├── README.md                       # NEW (replace placeholder)
├── CONTRIBUTING.md                 # NEW
├── CODE_OF_CONDUCT.md              # NEW
└── LICENSE                         # NEW
```

---

## Implementation Guidance

### Step 1: Directory Creation Strategy

**Recommended Approach:** PowerShell script (Windows environment)

```powershell
# create-structure.ps1
$directories = @(
    ".github/workflows",
    "backend/api",
    "backend/services",
    "backend/config",
    "backend/utils",
    "backend/tests",
    "gui/windows",
    "gui/widgets",
    "gui/services",
    "gui/resources/icons",
    "gui/tests",
    "extension/background",
    "extension/content",
    "extension/popup",
    "extension/lib",
    "extension/icons",
    "tests/integration"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    
    # Add __init__.py for Python packages
    if ($dir -like "backend*" -or $dir -like "gui*") {
        New-Item -ItemType File -Force -Path "$dir/__init__.py" | Out-Null
    }
    
    # Add .gitkeep for empty directories
    New-Item -ItemType File -Force -Path "$dir/.gitkeep" | Out-Null
    
    Write-Host "✓ Created $dir"
}

Write-Host "`n✨ Project structure created successfully!"
```

**Execution:**
```powershell
# From project root
.\scripts\create-structure.ps1
```

**Alternative (Manual):**
```powershell
# Create directories one by one
mkdir -p backend/api, backend/services, backend/config, backend/utils, backend/tests
mkdir -p gui/windows, gui/widgets, gui/services, gui/resources/icons, gui/tests
mkdir -p extension/background, extension/content, extension/popup, extension/lib, extension/icons
mkdir -p .github/workflows, tests/integration

# Add __init__.py files
foreach ($d in @("backend/api", "backend/services", "backend/config", "backend/utils", "backend/tests", "gui/windows", "gui/widgets", "gui/services", "gui/tests")) {
    "" | Out-File -FilePath "$d/__init__.py" -Encoding UTF8
}
```

---

### Step 2: pyproject.toml Configuration

**Critical Decisions:**

1. **Python Version:** Use `>=3.9` (architecture requirement)
   - FastAPI requires Python 3.7+
   - PyQt5 supports Python 3.5+
   - Modern features: type hints, dict unions (`dict[str, Any]`)

2. **Build System:** Use `setuptools` (not poetry/flit)
   - Widely supported (PyInstaller compatibility for Epic 7)
   - Simple for monorepo structure
   - Standard in enterprise environments

3. **Tool Configurations:** Centralize in pyproject.toml (not separate files)
   - pytest, black, mypy, coverage all in one file
   - Easier to maintain consistency
   - Modern Python packaging standard (PEP 518)

**Complete Template:**
```toml
[project]
name = "autoresumefiller"
version = "1.0.0"
description = "Intelligent job application form auto-filling with AI assistance"
authors = [
    {name = "Ragnar", email = "your.email@example.com"}
]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.9"
keywords = ["job-application", "automation", "ai", "form-filling", "chrome-extension"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Office/Business",
    "Topic :: Utilities",
]

[project.urls]
Homepage = "https://github.com/yourusername/autoresumefiller"
Repository = "https://github.com/yourusername/autoresumefiller"
Issues = "https://github.com/yourusername/autoresumefiller/issues"
Documentation = "https://github.com/yourusername/autoresumefiller/blob/master/README.md"

[build-system]
requires = ["setuptools>=68.0", "wheel>=0.41"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["backend*", "gui*"]
exclude = ["tests*", "*.tests*"]

[tool.pytest.ini_options]
testpaths = ["backend/tests", "gui/tests", "tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = """
    -v
    --tb=short
    --strict-markers
    --cov=backend
    --cov=gui
    --cov-report=html
    --cov-report=term-missing:skip-covered
"""
markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (moderate speed, external dependencies)",
    "e2e: End-to-end tests (slow, full system)",
    "slow: Tests that take >1s to run",
]

[tool.coverage.run]
source = ["backend", "gui"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__init__.py",
    "*/conftest.py",
]
branch = true

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "def __str__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]

[tool.black]
line-length = 100
target-version = ["py39", "py310", "py311"]
include = '\\.pyi?$'
extend-exclude = '''
/(
    \\.git
  | \\.venv
  | build
  | dist
  | __pycache__
)/
'''

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true
show_error_codes = true
show_column_numbers = true

[[tool.mypy.overrides]]
module = "PyQt5.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "uvicorn.*"
ignore_missing_imports = true

[tool.pylint.main]
py-version = "3.9"
ignore = ["tests", ".venv", "build", "dist", "__pycache__"]
load-plugins = []

[tool.pylint.messages_control]
max-line-length = 100
disable = [
    "C0111",  # missing-docstring (too strict for small projects)
    "C0103",  # invalid-name (conflicts with common patterns like 'id', 'db')
    "R0903",  # too-few-public-methods (Pydantic models)
    "W0212",  # protected-access (needed for testing private methods)
]

[tool.pylint.format]
indent-string = "    "
expected-line-ending-format = "LF"

[tool.pylint.design]
max-args = 7
max-locals = 20
max-returns = 6
max-branches = 15
max-attributes = 12
```

**Validation Commands:**
```powershell
# Verify TOML syntax
python -c "import tomllib; print('✓ Valid TOML'); tomllib.load(open('pyproject.toml', 'rb'))"

# Verify setuptools recognizes package
python -m build --version

# Test tool configurations
pytest --version
black --version
mypy --version
pylint --version
```

---

### Step 3: .gitignore Updates

**Merge Strategy:** Preserve existing BMAD exclusions, add Python-specific patterns

**Existing Patterns to Keep:**
```gitignore
# BMAD Method v6 Workflow Files
.bmad/
.agent/
.cursor/
.claude/
.gemini/
.github/copilot-instructions.md
.github/chatmodes/
docs/bmm-workflow-status.yaml
```

**Add After BMAD Section:**
```gitignore
# =============================================================================
# Python Application Files
# =============================================================================

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environments
venv/
.venv/
env/
ENV/
env.bak/
venv.bak/
pythonenv*/

# Testing and Coverage
.tox/
.nox/
.coverage
.coverage.*
htmlcov/
.pytest_cache/
.hypothesis/
coverage.xml
*.cover
*.log

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json

# Pylint
.pylint.d/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.project
.pydevproject
.settings/

# OS Files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
desktop.ini

# Application Data
data/
logs/
backups/
*.db
*.sqlite
*.sqlite3

# Secrets
*.key
.env
.env.*
config.yaml
settings.json
secrets.json

# Build Artifacts
*.spec
*.zip
*.tar.gz
*.egg
AutoResumeFiller*.exe
AutoResumeFiller*.msi

# Extension Packaging
extension/*.crx
extension/*.pem
extension.zip
```

**Verification:**
```powershell
# Test .gitignore works
New-Item -ItemType File -Path "venv/test.txt" -Force
New-Item -ItemType File -Path "data/test.db" -Force
New-Item -ItemType File -Path ".env" -Force

git status  # Should NOT show these files

# Clean up
Remove-Item "venv/test.txt", "data/test.db", ".env"
```

---

### Step 4: README.md Template

**Structure:**
1. Project Title + Tagline
2. Overview (2-3 paragraphs)
3. Features (bullet list from PRD)
4. Architecture Diagram (ASCII art or link)
5. Installation (developer setup)
6. Usage (placeholder for future releases)
7. Contributing
8. License

**Complete Template:**
```markdown
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
```

**Customization Required:**
- Replace `yourusername` with actual GitHub username
- Replace `your.email@example.com` with actual email
- Update project URLs after creating GitHub repository

---

### Step 5: LICENSE (MIT)

**Template:**
```
MIT License

Copyright (c) 2025 Ragnar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**No modifications needed** - standard MIT template with current year (2025).

---

### Step 6: CONTRIBUTING.md

**Template:**
```markdown
# Contributing to AutoResumeFiller

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to AutoResumeFiller.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to your.email@example.com.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/autoresumefiller.git
   cd autoresumefiller
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/yourusername/autoresumefiller.git
   ```
4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Environment

### Prerequisites
- Python 3.9 or higher
- Google Chrome (for extension testing)
- Git

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r gui/requirements.txt

# Install development tools
pip install pytest pytest-cov black pylint mypy
```

### Running the Application
```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8765

# Terminal 2: GUI
python gui/main.py

# Chrome: Load extension from extension/ directory
```

## Code Style

### Python
We use [Black](https://black.readthedocs.io/) for code formatting and [Pylint](https://pylint.org/) for linting.

**Configuration:** See `pyproject.toml` for tool settings.

**Before committing:**
```bash
# Format code
black backend/ gui/

# Check linting
pylint backend/ gui/

# Type checking
mypy backend/ gui/
```

**Guidelines:**
- Maximum line length: 100 characters
- Use type hints for function signatures
- Write docstrings for public functions and classes
- Follow PEP 8 conventions
- Use `async/await` for async operations

### JavaScript (Chrome Extension)
- Use ES6+ features
- Use `const` and `let` (no `var`)
- Use arrow functions where appropriate
- Follow Airbnb JavaScript Style Guide (relaxed)

## Testing

### Writing Tests
- Place tests in `backend/tests/`, `gui/tests/`, or `tests/integration/`
- Use descriptive test names: `test_<function>_<scenario>_<expected_result>`
- Use pytest fixtures for test data
- Aim for >70% code coverage

### Running Tests
```bash
# All tests
pytest

# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# With coverage
pytest --cov --cov-report=html
```

### Test Markers
- `@pytest.mark.unit` - Fast, isolated tests
- `@pytest.mark.integration` - Tests with external dependencies
- `@pytest.mark.e2e` - Full system tests
- `@pytest.mark.slow` - Tests taking >1 second

## Pull Request Process

### Before Submitting
1. **Update from upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/master
   ```
2. **Run tests:** Ensure all tests pass
3. **Format code:** Run `black backend/ gui/`
4. **Check linting:** Run `pylint backend/ gui/`
5. **Update documentation:** If adding features, update README.md

### Submitting
1. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Create Pull Request on GitHub
3. Fill out PR template with:
   - Description of changes
   - Related issue number (if applicable)
   - Testing performed
   - Screenshots (if UI changes)

### PR Review Process
- Maintainers will review within 48 hours
- Address feedback in additional commits
- Once approved, maintainer will merge
- Delete your feature branch after merge

### Commit Message Guidelines
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic changes)
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat(backend): Add health check endpoint

Implements GET /api/status endpoint that returns:
- Server status (healthy/unhealthy)
- Version number
- Timestamp

Closes #42
```

## Issue Reporting

### Bug Reports
Include:
- Python version (`python --version`)
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error logs (if applicable)
- Screenshots (if UI bug)

### Feature Requests
Include:
- Use case / problem to solve
- Proposed solution
- Alternative solutions considered
- Mockups (if UI feature)

### Security Issues
**Do NOT open public issues for security vulnerabilities.**

Email security@example.com with:
- Description of vulnerability
- Steps to reproduce
- Potential impact

We will respond within 48 hours.

## Development Workflow

### Branch Strategy
- `master` - Production-ready code
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

### Release Process
1. Version bump in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v1.0.0`
4. Push tag: `git push --tags`
5. GitHub Actions builds and releases

## Questions?

- Check [Documentation](docs/)
- Search [Existing Issues](https://github.com/yourusername/autoresumefiller/issues)
- Ask in [Discussions](https://github.com/yourusername/autoresumefiller/discussions)

---

**Thank you for contributing to AutoResumeFiller!** 🎉
```

**Customization Required:**
- Replace `yourusername` with actual GitHub username
- Replace `your.email@example.com` and `security@example.com` with actual emails

---

### Step 7: CODE_OF_CONDUCT.md

**Template:** Use Contributor Covenant v2.1 (standard)

```markdown
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, caste, color, religion, or sexual
identity and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes,
  and learning from the experience
* Focusing on what is best not just for us as individuals, but for the overall
  community

Examples of unacceptable behavior include:

* The use of sexualized language or imagery, and sexual attention or advances of
  any kind
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or email address,
  without their explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

Community leaders have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for moderation
decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.
Examples of representing our community include using an official e-mail address,
posting via an official social media account, or acting as an appointed
representative at an online or offline event.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at
your.email@example.com.

All complaints will be reviewed and investigated promptly and fairly.

All community leaders are obligated to respect the privacy and security of the
reporter of any incident.

## Enforcement Guidelines

Community leaders will follow these Community Impact Guidelines in determining
the consequences for any action they deem in violation of this Code of Conduct:

### 1. Correction

**Community Impact**: Use of inappropriate language or other behavior deemed
unprofessional or unwelcome in the community.

**Consequence**: A private, written warning from community leaders, providing
clarity around the nature of the violation and an explanation of why the
behavior was inappropriate. A public apology may be requested.

### 2. Warning

**Community Impact**: A violation through a single incident or series of
actions.

**Consequence**: A warning with consequences for continued behavior. No
interaction with the people involved, including unsolicited interaction with
those enforcing the Code of Conduct, for a specified period of time. This
includes avoiding interactions in community spaces as well as external channels
like social media. Violating these terms may lead to a temporary or permanent
ban.

### 3. Temporary Ban

**Community Impact**: A serious violation of community standards, including
sustained inappropriate behavior.

**Consequence**: A temporary ban from any sort of interaction or public
communication with the community for a specified period of time. No public or
private interaction with the people involved, including unsolicited interaction
with those enforcing the Code of Conduct, is allowed during this period.
Violating these terms may lead to a permanent ban.

### 4. Permanent Ban

**Community Impact**: Demonstrating a pattern of violation of community
standards, including sustained inappropriate behavior, harassment of an
individual, or aggression toward or disparagement of classes of individuals.

**Consequence**: A permanent ban from any sort of public interaction within the
community.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.1, available at
[https://www.contributor-covenant.org/version/2/1/code_of_conduct.html][v2.1].

Community Impact Guidelines were inspired by
[Mozilla's code of conduct enforcement ladder][Mozilla CoC].

For answers to common questions about this code of conduct, see the FAQ at
[https://www.contributor-covenant.org/faq][FAQ]. Translations are available at
[https://www.contributor-covenant.org/translations][translations].

[homepage]: https://www.contributor-covenant.org
[v2.1]: https://www.contributor-covenant.org/version/2/1/code_of_conduct.html
[Mozilla CoC]: https://github.com/mozilla/diversity
[FAQ]: https://www.contributor-covenant.org/faq
[translations]: https://www.contributor-covenant.org/translations
```

**Customization Required:**
- Replace `your.email@example.com` with actual email for reporting violations

---

### Step 8: Configuration Files

**pytest.ini:**
```ini
[pytest]
testpaths = backend/tests gui/tests tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=backend
    --cov=gui
    --cov-report=html
    --cov-report=term-missing:skip-covered
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (moderate speed, external dependencies)
    e2e: End-to-end tests (slow, full system)
    slow: Tests that take >1s to run
```

**.pylintrc:**
```ini
[MASTER]
py-version=3.9
ignore=tests,.venv,build,dist,__pycache__
load-plugins=

[MESSAGES CONTROL]
max-line-length=100
disable=
    C0111,
    C0103,
    R0903,
    W0212

[FORMAT]
indent-string='    '
expected-line-ending-format=LF

[DESIGN]
max-args=7
max-locals=20
max-returns=6
max-branches=15
max-attributes=12
```

**.editorconfig:**
```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4
max_line_length = 100

[*.{js,json,yml,yaml}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

---

### Step 9: Placeholder Files

**backend/main.py:**
```python
"""AutoResumeFiller Backend API - Entry Point.

This module will be implemented in Story 1.2.
Placeholder for repository structure initialization.
"""
# TODO: Story 1.2 - Implement FastAPI application
pass
```

**gui/main.py:**
```python
"""AutoResumeFiller GUI Application - Entry Point.

This module will be implemented in Story 1.4.
Placeholder for repository structure initialization.
"""
# TODO: Story 1.4 - Implement PyQt5 application
pass
```

**backend/requirements.txt:**
```
# Backend Python dependencies
# To be populated in Story 1.2: Python Backend Scaffolding
```

**gui/requirements.txt:**
```
# GUI Python dependencies
# To be populated in Story 1.4: PyQt5 GUI Application Shell
```

**.github/workflows/ci.yml:**
```yaml
# CI/CD Pipeline - Placeholder
# To be implemented in Story 1.5: CI/CD Pipeline - GitHub Actions
name: CI

on:
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]

jobs:
  placeholder:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Placeholder
        run: echo "CI pipeline to be implemented in Story 1.5"
```

**.github/workflows/release.yml:**
```yaml
# Release Automation - Placeholder
# To be implemented in Epic 7: Production Readiness & Distribution
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  placeholder:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Placeholder
        run: echo "Release automation to be implemented in Epic 7"
```

---

## Common Pitfalls and Solutions

### Issue 1: .gitignore Not Working After Creation

**Problem:** Files still tracked by git after adding to .gitignore

**Solution:**
```powershell
# Clear git cache
git rm -r --cached .
git add .
git commit -m "Fix .gitignore: Remove cached files"
```

### Issue 2: pyproject.toml Parse Errors

**Problem:** `tomllib.load()` fails with parse error

**Common Causes:**
- Missing quotes around strings
- Invalid escape sequences
- Trailing commas in arrays

**Solution:**
```powershell
# Validate TOML syntax
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"
```

### Issue 3: pytest Not Finding Tests

**Problem:** `pytest --collect-only` shows 0 tests after creating test directories

**Expected:** This is correct for Story 1.1 (no test files created yet)

**Verification:**
```powershell
pytest --collect-only  # Should show "collected 0 items"
```

### Issue 4: Python Package Not Recognized

**Problem:** `ModuleNotFoundError` when importing backend or gui

**Solution:** Ensure `__init__.py` files exist in all package directories
```powershell
# Check for missing __init__.py
Get-ChildItem -Recurse -Directory | Where-Object { 
    ($_.FullName -like "*backend*" -or $_.FullName -like "*gui*") -and 
    -not (Test-Path "$($_.FullName)/__init__.py") 
}
```

### Issue 5: Line Ending Conflicts (CRLF vs LF)

**Problem:** Git shows files as modified due to line ending differences

**Solution:** Configure git to handle line endings automatically
```powershell
# Set git to auto-convert CRLF to LF
git config --global core.autocrlf true

# Normalize existing files
git add --renormalize .
git commit -m "Normalize line endings"
```

---

## Tool-Specific Notes

### Black Code Formatter

**Configuration:** `pyproject.toml` → `[tool.black]`

**Key Settings:**
- Line length: 100 (matches pylint)
- Target Python: 3.9, 3.10, 3.11
- Exclude: .git, .venv, build, dist

**Usage:**
```powershell
# Format all Python files
black backend/ gui/

# Check formatting without changes
black --check backend/ gui/

# Format specific file
black backend/main.py
```

### Pylint Linter

**Configuration:** `.pylintrc` or `pyproject.toml` → `[tool.pylint]`

**Disabled Checks:**
- C0111 (missing-docstring) - Too strict for small projects
- C0103 (invalid-name) - Conflicts with common patterns (id, db)
- R0903 (too-few-public-methods) - Pydantic models trigger this
- W0212 (protected-access) - Needed for testing private methods

**Usage:**
```powershell
# Lint all Python files
pylint backend/ gui/

# Lint specific module
pylint backend/main.py

# Generate reports
pylint --output-format=json backend/ > lint-report.json
```

### MyPy Type Checker

**Configuration:** `pyproject.toml` → `[tool.mypy]`

**Ignored Imports:**
- PyQt5.* (no type stubs available)
- uvicorn.* (optional dependency)

**Usage:**
```powershell
# Type check all files
mypy backend/ gui/

# Check specific file
mypy backend/main.py

# Generate HTML report
mypy --html-report mypy-report backend/ gui/
```

### Coverage.py

**Configuration:** `pyproject.toml` → `[tool.coverage]`

**Settings:**
- Source: backend/, gui/
- Omit: tests, __init__.py, conftest.py
- Branch coverage: Enabled
- Exclude: Pragma comments, __repr__, __main__ blocks

**Usage:**
```powershell
# Run tests with coverage
pytest --cov --cov-report=html

# View HTML report
Start-Process htmlcov/index.html  # Windows
open htmlcov/index.html            # macOS
xdg-open htmlcov/index.html        # Linux
```

---

## Verification Checklist

**Before marking Story 1.1 as complete:**

### Directory Structure
- [ ] All directories created per AC1
- [ ] All Python packages have `__init__.py` files
- [ ] Empty directories have `.gitkeep` files
- [ ] `tree /F` output matches expected structure

### Configuration Files
- [ ] `pyproject.toml` exists and validates with `tomllib.load()`
- [ ] `pytest.ini` exists and `pytest --version` works
- [ ] `.pylintrc` exists and `pylint --version` works
- [ ] `.editorconfig` exists and editor recognizes it
- [ ] `.gitignore` properly excludes test files (verified with `git status`)

### Documentation
- [ ] `README.md` exists with complete content (installation, usage, contributing)
- [ ] `LICENSE` exists (MIT template with 2025 copyright)
- [ ] `CONTRIBUTING.md` exists with development guidelines
- [ ] `CODE_OF_CONDUCT.md` exists (Contributor Covenant v2.1)

### Placeholder Files
- [ ] `backend/main.py` exists with TODO comment
- [ ] `gui/main.py` exists with TODO comment
- [ ] `backend/requirements.txt` exists (placeholder comment)
- [ ] `gui/requirements.txt` exists (placeholder comment)
- [ ] `.github/workflows/ci.yml` exists (placeholder workflow)
- [ ] `.github/workflows/release.yml` exists (placeholder workflow)

### Git Status
- [ ] All new files committed to git
- [ ] Commit message follows format in story document
- [ ] `git status` shows clean working directory (except .github/ with ignored contents)
- [ ] No untracked files (except intentionally ignored)

### Tool Verification
- [ ] `python --version` shows 3.9 or higher
- [ ] `pytest --collect-only` runs without errors (0 tests expected)
- [ ] `black --version` works
- [ ] `pylint --version` works
- [ ] `mypy --version` works

### Sprint Tracking
- [ ] `sprint-status.yaml` updated: `1-1-project-initialization-repository-setup: backlog → done`
- [ ] Story document committed to `docs/sprint-artifacts/stories/`
- [ ] Context document committed alongside story

---

## Next Steps After Story 1.1

**Immediate:**
1. Run `*code-review` workflow for SM review
2. SM approves → Update sprint status to "done"
3. Commit sprint status update

**Following Stories:**
1. **Story 1.2:** Python Backend Scaffolding
   - Populate `backend/main.py` with FastAPI app
   - Create `backend/requirements.txt` with dependencies
   - Implement health check endpoint
   - Configure CORS middleware

2. **Story 1.3:** Chrome Extension Manifest & Basic Structure
   - Create `extension/manifest.json` (Manifest V3)
   - Implement `extension/background/service-worker.js`
   - Implement `extension/content/content-script.js`
   - Create `extension/popup/` files (HTML/CSS/JS)

3. **Story 1.4:** PyQt5 GUI Application Shell
   - Populate `gui/main.py` with QApplication
   - Create `gui/requirements.txt` with PyQt5
   - Implement tabbed interface (Monitor, Data, Settings, Chatbot)
   - Add system tray integration

---

## Summary

This technical context document provides:
- **Complete code templates** for all configuration files
- **Step-by-step implementation guidance** (9 steps)
- **PowerShell scripts** for directory creation
- **Verification checklists** (pre/during/post)
- **Common pitfalls** with solutions
- **Tool-specific notes** (Black, Pylint, MyPy, Coverage)

**Key Decisions:**
1. Use PowerShell for directory creation (Windows environment)
2. Centralize tool configurations in `pyproject.toml` (modern Python standard)
3. Merge .gitignore patterns (preserve BMAD exclusions)
4. Use MIT License (portfolio-friendly)
5. Follow Contributor Covenant v2.1 for Code of Conduct

**Estimated Implementation Time:** 2-4 hours

**Ready for `*dev-story` workflow** ✅
