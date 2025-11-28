# Epic Technical Specification: Production Readiness & Distribution

Date: 2025-11-28
Author: Ragnar
Epic ID: 7
Status: Draft

---

## Overview

Epic 7 transforms AutoResumeFiller from a development prototype into a production-ready, distributable application that non-technical users can install and use. This epic covers PyInstaller packaging, first-run setup wizard, comprehensive documentation, security hardening, update management, optional privacy-preserving analytics, and automated GitHub release workflows.

The result is a polished, professional application ready for portfolio showcase, community distribution, and potential commercial deployment.

This epic enables 14 functional requirements (FR75-FR93) and finalizes the MVP for public release.

## Objectives and Scope

**In Scope:**
- PyInstaller build configuration (Windows executable)
- First-run setup wizard (QWizard: data directory, AI provider, resume import, extension install)
- Comprehensive user documentation (README, installation guide, user manual, troubleshooting)
- Developer documentation (architecture, API reference, contributing guide)
- Security hardening (dependency scanning, input validation, CORS enforcement, API key protection)
- Update management (version checking, GitHub Releases API, changelog display)
- Optional privacy-preserving analytics (anonymous usage statistics, opt-in)
- Automated GitHub release workflow (tag → build → release with changelog)

**Out of Scope:**
- macOS/Linux builds (deferred to post-MVP)
- Code signing certificates (optional for MVP)
- Auto-update mechanism (manual download for MVP)
- Windows installer (MSI/EXE installer vs ZIP distribution)

**Success Criteria:**
- Executable launches on Windows 10/11 without Python installed
- Setup wizard completes in <5 minutes
- Documentation covers 90%+ of user questions
- Security audit passes with zero critical issues
- Automated releases work end-to-end (tag → build → publish)

## System Architecture Alignment

Epic 7 finalizes the **Distribution & Deployment Layer**:

**Build Architecture:**
```
build.spec (PyInstaller)
    ↓
Compiles backend + GUI into executables
    ↓
dist/AutoResumeFiller/
    ├── AutoResumeFiller.exe          # Main GUI (starts backend subprocess)
    ├── autoresumefiller-backend.exe  # FastAPI backend
    ├── extension/                    # Chrome extension folder
    ├── README.md
    ├── LICENSE
    └── [dependencies]
    ↓
ZIP archive: AutoResumeFiller-Windows-v1.0.0.zip
    ↓
GitHub Release with changelog
```

**Security Architecture:**
- Input validation on all API endpoints
- CORS restricted to chrome-extension://*
- API keys never in config files (OS keyring only)
- Dependency scanning (Safety, Bandit)
- Rate limiting on backend endpoints

## Detailed Design

### Component 1: PyInstaller Build Configuration

**build.spec:**
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Backend Analysis
backend_a = Analysis(
    ['backend/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend/config', 'config'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops.auto',
        'uvicorn.protocols.http.auto',
        'pydantic',
        'cryptography',
        'keyring.backends',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# GUI Analysis
gui_a = Analysis(
    ['gui/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('gui/resources', 'resources'),
    ],
    hiddenimports=[
        'PyQt5.sip',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtNetwork',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Merge backend and GUI
MERGE((backend_a, 'backend', 'backend'), (gui_a, 'gui', 'gui'))

backend_pyz = PYZ(backend_a.pure, backend_a.zipped_data, cipher=block_cipher)
gui_pyz = PYZ(gui_a.pure, gui_a.zipped_data, cipher=block_cipher)

# Backend executable (subprocess)
backend_exe = EXE(
    backend_pyz,
    backend_a.scripts,
    [],
    exclude_binaries=True,
    name='autoresumefiller-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Main GUI executable
gui_exe = EXE(
    gui_pyz,
    gui_a.scripts,
    [],
    exclude_binaries=True,
    name='AutoResumeFiller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='gui/resources/icons/app.ico'
)

# Collect all files
coll = COLLECT(
    gui_exe,
    gui_a.binaries,
    gui_a.zipfiles,
    gui_a.datas,
    backend_exe,
    backend_a.binaries,
    backend_a.zipfiles,
    backend_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoResumeFiller',
)
```

**Build Script (scripts/build.py):**
```python
import subprocess
import shutil
from pathlib import Path

def build_executable():
    print("Building AutoResumeFiller...")
    
    # Clean previous builds
    if Path('dist').exists():
        shutil.rmtree('dist')
    if Path('build').exists():
        shutil.rmtree('build')
    
    # Run PyInstaller
    subprocess.run(['pyinstaller', 'build.spec'], check=True)
    
    # Copy extension
    shutil.copytree('extension', 'dist/AutoResumeFiller/extension')
    
    # Copy documentation
    shutil.copy('README.md', 'dist/AutoResumeFiller/')
    shutil.copy('LICENSE', 'dist/AutoResumeFiller/')
    shutil.copy('docs/INSTALLATION.md', 'dist/AutoResumeFiller/')
    
    # Create ZIP
    shutil.make_archive('AutoResumeFiller-Windows-v1.0.0', 'zip', 'dist/AutoResumeFiller')
    
    print("✓ Build complete: AutoResumeFiller-Windows-v1.0.0.zip")

if __name__ == '__main__':
    build_executable()
```

### Component 2: First-Run Setup Wizard

**QWizard Pages:**

1. **Welcome Page:** Introduction and estimated time (5 minutes)
2. **Data Directory Page:** Choose storage location (default: `%APPDATA%\AutoResumeFiller`)
3. **AI Provider Page:** Select provider (OpenAI/Anthropic/Google), enter API key, test connection
4. **Import Data Page:** Import resume PDF/DOCX (optional, can skip)
5. **Extension Page:** Instructions to install Chrome extension with "Open Folder" and "Open chrome://extensions/" buttons
6. **Completion Page:** Success message, next steps, "Launch Dashboard" checkbox

**Implementation (gui/windows/setup_wizard.py):**
```python
class SetupWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoResumeFiller Setup")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setFixedSize(600, 500)
        
        self.addPage(WelcomePage())
        self.addPage(DataDirectoryPage())
        self.addPage(AIProviderPage())
        self.addPage(ImportDataPage())
        self.addPage(ExtensionPage())
        self.addPage(CompletionPage())
    
    def accept(self):
        # Save configuration
        config = {
            'data_directory': self.field('data_dir'),
            'preferred_provider': self.field('provider').lower(),
        }
        
        # Initialize backend
        requests.post('http://localhost:8765/api/setup/initialize', json=config)
        
        # Store API key in keyring
        api_key = self.field('api_key')
        provider = self.field('provider').lower()
        keyring.set_password("AutoResumeFiller", f"{provider}_api_key", api_key)
        
        # Import resume if provided
        resume_path = self.field('resume_path')
        if resume_path:
            with open(resume_path, 'rb') as f:
                files = {'file': f}
                requests.post('http://localhost:8765/api/parse-resume', files=files)
        
        super().accept()
```

### Component 3: Documentation Suite

**README.md:**
```markdown
# AutoResumeFiller

AI-powered job application automation tool that fills forms with your data.

## Features
- Automatic form field detection on major platforms (WorkDay, Greenhouse, Lever)
- AI-generated responses using OpenAI, Anthropic, or Google
- Real-time monitoring dashboard
- Conversational profile updates via chatbot
- Local data storage with AES-256 encryption
- Multi-stage application support

## Installation
1. Download `AutoResumeFiller-Windows-v1.0.0.zip` from Releases
2. Extract to a folder (e.g., `C:\Program Files\AutoResumeFiller`)
3. Run `AutoResumeFiller.exe`
4. Follow the setup wizard
5. Install Chrome extension (instructions in wizard)

## Quick Start
1. Open AutoResumeFiller dashboard
2. Navigate to Data Management tab
3. Import your resume or fill profile manually
4. Configure AI provider in Configuration tab
5. Open a job application in Chrome
6. Click the AutoResumeFiller extension icon
7. Review and approve generated responses
8. Submit application!

## Documentation
- [Installation Guide](docs/INSTALLATION.md)
- [User Manual](docs/USER_MANUAL.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Privacy Policy](docs/PRIVACY.md)

## Requirements
- Windows 10 or Windows 11 (64-bit)
- Google Chrome browser
- AI provider API key (OpenAI, Anthropic, or Google)
- 2GB RAM, 500MB disk space

## License
MIT License - See LICENSE file

## Support
- GitHub Issues: https://github.com/username/autoresumefiller/issues
- Discord: https://discord.gg/...
```

**docs/INSTALLATION.md:**
- System requirements
- Step-by-step installation with screenshots
- Firewall/antivirus configuration
- Chrome extension installation (Developer Mode)
- Troubleshooting common install issues

**docs/USER_MANUAL.md:**
- Dashboard tour (each tab explained with screenshots)
- Form filling walkthrough
- Data management best practices
- AI provider comparison
- Advanced features (chatbot, multi-stage navigation)

**docs/TROUBLESHOOTING.md:**
- Backend not starting → Check port 8765, restart application
- Extension not detecting forms → Check permissions, reload page
- AI responses not generating → Verify API key, check internet connection
- File upload fails → Check file size (<5MB), PDF/DOCX format

### Component 4: Security Hardening

**Input Validation:**
```python
from pydantic import BaseModel, validator, EmailStr

class UserProfileUpdate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr  # Validates email format
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if len(v) < 1 or len(v) > 100:
            raise ValueError('Name must be 1-100 characters')
        if not v.replace('-', '').replace(' ', '').isalpha():
            raise ValueError('Name must contain only letters, hyphens, spaces')
        return v
```

**CORS Enforcement:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["chrome-extension://*"],  # Only extension
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Rate Limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/generate-response")
@limiter.limit("100/minute")  # Max 100 requests per minute
async def generate_response(request: Request, field: FieldData):
    # ...
```

**Dependency Scanning (CI/CD):**
```yaml
# .github/workflows/security.yml
name: Security Audit

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - name: Install security tools
        run: pip install safety bandit
      - name: Check for known vulnerabilities
        run: safety check --json
      - name: Static code analysis
        run: bandit -r backend/ gui/ -f json
```

### Component 5: Update Management

**Version Checker (gui/services/update_checker.py):**
```python
import requests
from packaging import version

class UpdateChecker:
    CURRENT_VERSION = "1.0.0"
    RELEASES_URL = "https://api.github.com/repos/username/autoresumefiller/releases/latest"
    
    def check_for_updates(self):
        try:
            response = requests.get(self.RELEASES_URL, timeout=5)
            if response.ok:
                latest = response.json()
                latest_version = latest['tag_name'].lstrip('v')
                
                if version.parse(latest_version) > version.parse(self.CURRENT_VERSION):
                    return {
                        'update_available': True,
                        'latest_version': latest_version,
                        'download_url': latest['assets'][0]['browser_download_url'],
                        'changelog': latest['body']
                    }
        except:
            pass
        
        return {'update_available': False}
    
    def show_update_notification(self, update_info):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Update Available")
        msg_box.setText(f"Version {update_info['latest_version']} is available!")
        msg_box.setInformativeText("Download now?")
        msg_box.setDetailedText(f"What's New:\n{update_info['changelog']}")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg_box.exec_() == QMessageBox.Yes:
            webbrowser.open(update_info['download_url'])
```

### Component 6: GitHub Release Automation

**.github/workflows/release.yml:**
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r gui/requirements.txt
          pip install pyinstaller
      
      - name: Build executable
        run: python scripts/build.py
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: AutoResumeFiller-Windows
          path: AutoResumeFiller-Windows-*.zip
      
      - name: Generate changelog
        id: changelog
        uses: mikepenz/release-changelog-builder-action@v3
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: AutoResumeFiller-Windows-*.zip
          body: ${{ steps.changelog.outputs.changelog }}
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Release Process:**
1. Update version in `__version__ = "1.1.0"` (backend and GUI)
2. Commit: `git commit -m "Bump version to 1.1.0"`
3. Tag: `git tag v1.1.0`
4. Push: `git push && git push --tags`
5. GitHub Actions automatically builds and publishes release

## Non-Functional Requirements

### Performance

| Metric | Target |
|--------|--------|
| Executable launch time | <5 seconds (cold start) |
| Setup wizard completion | <5 minutes |
| Build time (CI/CD) | <10 minutes |

### Security

| Requirement | Implementation |
|-------------|----------------|
| Dependency vulnerabilities | Zero critical, <5 medium |
| Code security score | Bandit passes with no issues |
| API key protection | Never in config files, logs redacted |
| CORS enforcement | chrome-extension://* only |

### Usability

- Installation requires zero command-line usage
- Setup wizard uses plain language (no technical jargon)
- Documentation searchable (Ctrl+F friendly)
- Error messages actionable ("Do X to fix Y")

## Acceptance Criteria (Authoritative)

### AC1: Executable Builds Successfully
**Given** source code and build.spec  
**When** running `python scripts/build.py`  
**Then** dist/AutoResumeFiller/ created with all files  
**And** AutoResumeFiller.exe launches without errors  
**And** Backend subprocess starts automatically  
**And** No Python installation required

### AC2: Setup Wizard Works
**Given** first application launch (no config)  
**When** setup wizard displayed  
**Then** user completes all 6 pages  
**And** data directory created  
**And** API key saved to keyring  
**And** Config.yaml generated  
**And** wizard completes in <5 minutes

### AC3: Documentation Complete
**Given** documentation suite  
**Then** README.md covers installation, quick start, requirements  
**And** INSTALLATION.md has step-by-step screenshots  
**And** USER_MANUAL.md explains all features  
**And** TROUBLESHOOTING.md addresses top 10 issues

### AC4: Security Audit Passes
**Given** codebase  
**When** running `safety check` and `bandit`  
**Then** zero critical vulnerabilities  
**And** fewer than 5 medium issues  
**And** all API endpoints validate input

### AC5: Update Check Works
**Given** new version released on GitHub  
**When** application launches  
**Then** update checker queries GitHub Releases API  
**And** notification shown if newer version available  
**And** changelog displayed  
**And** download link opens in browser

### AC6: Automated Release Works
**Given** tag pushed: `v1.0.0`  
**When** GitHub Actions workflow runs  
**Then** Windows executable built  
**And** ZIP artifact uploaded  
**And** GitHub Release created with changelog  
**And** Release visible at github.com/.../releases

### AC7: Privacy-Preserving Analytics (Optional)
**Given** telemetry enabled (opt-in)  
**When** user fills application  
**Then** anonymous event logged (no personal data)  
**And** can view collected data in GUI  
**And** can opt-out anytime

## Traceability Mapping

| Acceptance Criteria | Component(s) | Test Idea |
|---------------------|--------------|-----------|
| AC1: Executable Builds | build.spec, build.py | `test_build_executable()` (run on CI) |
| AC2: Setup Wizard | setup_wizard.py | Manual testing with screenshots |
| AC3: Documentation | docs/*.md | Manual review checklist |
| AC4: Security Audit | All code | CI security workflow |
| AC5: Update Check | update_checker.py | Mock GitHub API responses |
| AC6: Automated Release | .github/workflows/release.yml | Test with pre-release tags |
| AC7: Analytics | analytics.py | Test with telemetry enabled/disabled |

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| **R1: PyInstaller build fails on CI** | Test locally, use Docker for reproducible builds, pin pyinstaller version |
| **R2: Windows antivirus flags executable** | Code signing certificate, VirusTotal submission, whitelist instructions in docs |
| **R3: Users can't install extension** | Detailed screenshots, video tutorial, troubleshooting section |
| **R4: GitHub API rate limits** | Cache update checks (once per day), use conditional requests (If-None-Match) |

## Summary

Epic 7 delivers production-ready distribution with:
- ✅ Windows executable (PyInstaller, no Python required)
- ✅ First-run setup wizard (<5 minutes)
- ✅ Comprehensive documentation (README, install guide, user manual, troubleshooting)
- ✅ Security hardening (dependency scanning, input validation, CORS)
- ✅ Update management (GitHub Releases API, changelog display)
- ✅ Automated CI/CD (tag → build → release)
- ✅ Optional privacy-preserving analytics (opt-in)

**Application Status:** MVP complete, ready for public beta release.

**Next Steps:**
1. Run complete test suite (unit, integration, E2E)
2. Security audit review
3. User testing with 10+ beta testers
4. Tag v1.0.0 and publish first release
5. Monitor GitHub Issues for bug reports
6. Plan v1.1 features based on feedback

**Status:** Ready for implementation and release.
