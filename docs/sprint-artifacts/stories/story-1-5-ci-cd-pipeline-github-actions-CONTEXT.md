# Story 1.5 Technical Context - CI/CD Pipeline with GitHub Actions

**Generated:** 2025-11-28  
**For Story:** 1.5 - CI/CD Pipeline with GitHub Actions  
**Status:** ready-for-dev  

---

## Story Summary

**As a** developer building AutoResumeFiller  
**I want** automated testing and building via GitHub Actions workflows  
**So that** code quality is enforced on every commit and releases are automated with CI/CD best practices

---

## Acceptance Criteria

### AC1: CI Workflow Runs on Push/PR
- CI workflow triggers automatically within 30 seconds on push/PR
- Workflow appears in GitHub Actions tab with run status

### AC2: Backend Testing Job Passes
- Python 3.11 setup successful
- Dependencies installed from backend/requirements.txt and gui/requirements.txt
- pytest runs with coverage reporting (XML format)
- Coverage uploaded to codecov.io (optional, allow failure)
- Job passes if tests pass, fails if any test fails

### AC3: Backend Linting Job Enforces Code Quality
- black, pylint, mypy installed
- black checks formatting: `black --check backend/ gui/`
- pylint checks quality (8.0+ score): `pylint backend/ gui/ --fail-under=8.0`
- mypy checks types: `mypy backend/ gui/ --strict`
- Job fails on violations, low score, or type errors

### AC4: Extension Validation Job Checks JavaScript
- Node.js 18 setup successful
- eslint installed and runs on extension JavaScript
- manifest.json validated as valid JSON
- Job passes if no linting errors and valid manifest

### AC5: Release Workflow Triggers on Version Tags
- Release workflow triggers on git tags matching v* pattern
- build-windows and create-release jobs execute in sequence

### AC6: Windows Executable Build Succeeds
- Python 3.11 setup on Windows runner
- PyInstaller builds executable from gui/main.py
- dist/AutoResumeFiller.exe artifact created and uploaded

### AC7: GitHub Release Created with Artifacts
- Executable artifact downloaded and attached to GitHub release
- Release notes auto-generated from commits
- Release visible on repository Releases page

### AC8: README Badges Display Build Status
- Build status, coverage, license, Python version badges in README
- Badges link to appropriate services (Actions, codecov, etc.)

---

## Tasks Breakdown

### Task 1: Create CI Workflow Configuration
- [ ] Create `.github/workflows/ci.yml`
- [ ] Configure triggers (push, pull_request)
- [ ] Define test-backend job (Python 3.11, pytest, coverage)
- [ ] Define lint-backend job (black, pylint, mypy)
- [ ] Define test-extension job (Node.js 18, eslint, manifest validation)
- [ ] Configure pip dependency caching

### Task 2: Create Release Workflow Configuration
- [ ] Create `.github/workflows/release.yml`
- [ ] Configure tag trigger (v*)
- [ ] Define build-windows job (PyInstaller)
- [ ] Define create-release job (GitHub release with artifacts)

### Task 3: Configure Python Code Quality Tools
- [ ] Update `.pylintrc` (line-too-long, docstring rules, fail-under 8.0)
- [ ] Create `mypy.ini` or update `pyproject.toml` (strict mode)
- [ ] Add black, pylint, mypy to backend/requirements.txt

### Task 4: Add Status Badges to README
- [ ] Add badges for build status, coverage, license, Python version
- [ ] Update GitHub username in badge URLs

### Task 5: Validate CI/CD Pipeline End-to-End
- [ ] Test with intentional formatting issue
- [ ] Verify lint job fails correctly
- [ ] Fix and verify job passes
- [ ] Create test tag and verify release workflow
- [ ] Cleanup test artifacts

---

## Documentation Artifacts

### Primary References

**Epic 1 - Story 1.5 Specification:**
- **Path:** `docs/epics.md` (lines 399-465)
- **Section:** Story 1.5: CI/CD Pipeline with GitHub Actions
- **Relevant Content:**
  - 3 CI jobs: test-backend, lint-backend, test-extension
  - Release workflow with Windows executable build
  - GitHub Actions badges for README
  - Prerequisites: Stories 1.1-1.4 complete
  - Technical notes on caching, semantic-release, PyInstaller

**Architecture - Technology Stack:**
- **Path:** `docs/architecture.md` (Section 2)
- **Section:** Technology Stack
- **Relevant Content:**
  - Python 3.9+ → Use 3.11 in workflows
  - FastAPI backend → pytest for testing
  - PyQt5 GUI → Include gui/requirements.txt
  - Chrome Extension → eslint validation
  - Development tools: pytest, pytest-cov, black, pylint, mypy, pyinstaller

**Architecture - Testing Strategy:**
- **Path:** `docs/architecture.md` (Section 7)
- **Section:** Testing Strategy
- **Relevant Content:**
  - Unit tests with pytest and pytest-asyncio
  - Code coverage target: >80% (codecov integration)
  - Code formatting: black
  - Linting: pylint
  - Type checking: mypy --strict

**Architecture - Deployment Strategy:**
- **Path:** `docs/architecture.md` (Section 8)
- **Section:** Deployment Strategy
- **Relevant Content:**
  - GitHub as primary repository → GitHub Actions natural choice
  - PyInstaller for Windows .exe packaging
  - GitHub Releases for distribution
  - Semantic versioning (vMAJOR.MINOR.PATCH)

---

## Existing Code & Interfaces

### Placeholder Workflows (To Replace)

**1. CI Workflow Placeholder:**
- **Path:** `.github/workflows/ci.yml`
- **Current State:** Placeholder job echoing "CI pipeline to be implemented in Story 1.5"
- **Action:** Replace with complete CI workflow (test + lint jobs)

**2. Release Workflow Placeholder:**
- **Path:** `.github/workflows/release.yml`
- **Current State:** Placeholder job echoing "Release automation to be implemented in Epic 7"
- **Action:** Implement basic release workflow (build Windows exe, create GitHub release)

### Existing Configuration

**Pylint Configuration:**
- **Path:** `.pylintrc`
- **Current Settings:**
  - Python version: 3.9
  - Max line length: 100
  - Ignores: tests, .venv, build, dist, __pycache__
  - Disabled checks: C0111 (missing-docstring), C0103 (invalid-name), R0903 (too-few-public-methods), W0212 (protected-access)
- **Action:** Update for stricter checks, add fail-under=8.0 in CI workflow command

**Backend Dependencies:**
- **Path:** `backend/requirements.txt`
- **Current Packages:** fastapi, uvicorn, pydantic, pyyaml
- **Action:** Add development dependencies (black, pylint, mypy, pytest, pytest-cov)

**GUI Dependencies:**
- **Path:** `gui/requirements.txt`
- **Current Packages:** PyQt5==5.15.10, PyQt5-Qt5==5.15.2, PyQt5-sip==12.13.0, requests==2.31.0
- **Action:** Ensure installed in CI workflow for type checking

### Backend Code to Lint/Test

**Backend Entry Point:**
- **Path:** `backend/main.py`
- **Contents:** FastAPI app with /api/status health check endpoint
- **Validation:** pytest will test health check (Story 1.6 will add tests)
- **Linting:** Existing code should pass black/pylint checks

**GUI Entry Point:**
- **Path:** `gui/main.py`
- **Contents:** QApplication with system tray integration (Story 1.4)
- **Validation:** Linters will check PyQt5 code quality
- **Note:** QNetworkAccessManager may have type hint challenges (use # type: ignore if needed)

**Extension Code:**
- **Path:** `extension/background/service-worker.js`
- **Contents:** Background service worker with message handling
- **Validation:** eslint will check JavaScript quality

- **Path:** `extension/content/content-script.js`
- **Contents:** Content script with form detection placeholders
- **Validation:** eslint will check JavaScript quality

- **Path:** `extension/manifest.json`
- **Contents:** Chrome Extension Manifest V3
- **Validation:** JSON.parse validation to ensure valid JSON structure

---

## Dependencies & Frameworks

### Python Ecosystem (Backend & GUI)

**Current Dependencies:**
```
# Backend (backend/requirements.txt)
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0
pyyaml>=6.0

# GUI (gui/requirements.txt)
PyQt5==5.15.10
PyQt5-Qt5==5.15.2
PyQt5-sip==12.13.0
requests==2.31.0
```

**Development Dependencies to Add:**
```
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0

# Code Quality
black>=23.11.0
pylint>=3.0.0
mypy>=1.7.0

# Build/Distribution
pyinstaller>=6.3.0
```

### JavaScript/Node.js Ecosystem (Extension)

**No package.json currently** - Extension uses vanilla JavaScript

**Dev Dependencies Needed:**
```
eslint (global install in CI: npm install -g eslint)
```

### GitHub Actions Ecosystem

**Actions to Use:**
- `actions/checkout@v4` - Check out repository
- `actions/setup-python@v4` - Setup Python environment
- `actions/setup-node@v3` - Setup Node.js for eslint
- `actions/cache@v3` - Cache pip dependencies
- `codecov/codecov-action@v3` - Upload coverage reports
- `actions/upload-artifact@v3` - Upload build artifacts
- `actions/download-artifact@v3` - Download artifacts for release
- `softprops/action-gh-release@v1` - Create GitHub releases

---

## Development Constraints

### Code Quality Standards

**From Architecture (Section 7.5: Code Quality):**
- **Black formatting:** All Python code must pass `black --check`
- **Pylint score:** Minimum 8.0/10 for backend and GUI code
- **Type checking:** mypy strict mode for all Python modules
- **Line length:** Maximum 100 characters (from existing .pylintrc)

### CI/CD Best Practices

**From Epic 1 Story 1.5:**
- Use pinned action versions (@v4, @v3) to prevent supply chain attacks
- Cache pip dependencies for faster workflow runs
- Run test, lint, and extension jobs in parallel
- Use Ubuntu runners for CI (faster, cheaper)
- Use Windows runner only for .exe builds
- Continue-on-error: true for optional steps (codecov upload)

### Testing Requirements

**From Architecture (Section 7: Testing Strategy):**
- Pytest for all Python testing
- pytest-asyncio for async FastAPI endpoints
- Coverage target: >80% (starting with >70% for MVP)
- Test organization: `backend/tests/`, `gui/tests/`, `tests/integration/`

### Release Process

**From Architecture (Section 8: Deployment):**
- Semantic versioning: vMAJOR.MINOR.PATCH
- Tags trigger release workflow automatically
- Windows executable built with PyInstaller
- GitHub Releases for distribution
- Auto-generated release notes from commits

---

## Interfaces & APIs

### GitHub Actions Workflow Syntax

**CI Workflow Interface:**
```yaml
name: CI
on: [push, pull_request]
jobs:
  job-name:
    runs-on: ubuntu-latest | windows-latest
    steps:
      - uses: actions/action-name@vX
      - name: Step Name
        run: |
          command1
          command2
```

**Release Workflow Interface:**
```yaml
name: Release
on:
  push:
    tags:
      - 'v*'
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/upload-artifact@v3
        with:
          name: artifact-name
          path: path/to/file
  release:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v3
      - uses: softprops/action-gh-release@v1
        with:
          files: path/to/files
```

### Backend Health Check Endpoint

**Existing API (from Story 1.2):**
```python
# GET /api/status
Response: {"status": "healthy", "version": "1.0.0"}
Status: 200 OK
```

**Test Coverage:** Story 1.6 will add pytest test for this endpoint

### PyInstaller Build Interface

**Command (Basic):**
```bash
pyinstaller --name AutoResumeFiller --onefile gui/main.py
```

**Output:** `dist/AutoResumeFiller.exe`

**Note:** Story 7.1 will create full `.spec` file with icon, hidden imports, etc.

---

## Testing Standards & Ideas

### Testing Framework

**Pytest with Coverage:**
- Framework: pytest >= 7.4.0
- Async support: pytest-asyncio for FastAPI
- Coverage: pytest-cov with HTML and XML reports
- Configuration: pytest.ini or pyproject.toml

**Current State:**
- No tests exist yet (Story 1.6 will create test infrastructure)
- CI workflow prepared to run tests when available
- pytest will report "0 tests collected" initially (not a failure)

### Test Locations

**Python Tests:**
- `backend/tests/` - Backend unit/integration tests
- `backend/tests/test_main.py` - Health check endpoint test (Story 1.6)
- `gui/tests/` - GUI unit tests
- `tests/` - Cross-component integration tests

**Extension Tests:**
- `extension/tests/` - JavaScript unit tests (future)
- No tests required for Story 1.5 (only linting)

### Test Ideas for CI/CD Validation

**AC1: CI Workflow Triggers**
- Manual test: Push commit, verify workflow appears in GitHub Actions tab
- Validation: Check workflow run status within 30 seconds

**AC2: Backend Testing Job**
- Test idea: Create intentional test failure, verify job fails with red X
- Test idea: Fix test, verify job passes with green checkmark
- Validation: Check pytest output shows test count and coverage percentage

**AC3: Backend Linting Job**
- Test idea: Add unformatted code (missing spaces), verify black fails
- Test idea: Add code violation (long line >100 chars), verify pylint fails
- Test idea: Remove type hint, verify mypy fails in strict mode
- Validation: Each linter failure shows clear error message

**AC4: Extension Validation**
- Test idea: Add JavaScript syntax error, verify eslint fails
- Test idea: Break manifest.json with invalid JSON, verify validation fails
- Validation: Error messages point to specific file and line number

**AC5-7: Release Workflow**
- Test idea: Create tag v0.0.1-test, verify release workflow triggers
- Test idea: Verify Windows executable artifact uploaded
- Test idea: Verify GitHub release created with attached .exe
- Validation: Download .exe file, check size >10MB (PyQt5 + dependencies)

**AC8: README Badges**
- Test idea: Check badge image loads (not 404)
- Test idea: Click badge, verify links to Actions/codecov/license page
- Validation: Build status badge shows passing (green) after successful CI run

---

## Learnings from Previous Stories

### From Story 1.4 (PyQt5 GUI Application Shell)

**New Files Created:**
- `gui/requirements.txt` - PyQt5 5.15.10 dependencies (exists)
- `gui/windows/main_window.py` - QMainWindow with async HTTP
- `gui/main.py` - QApplication entry point

**Implications for Story 1.5:**
- Include `gui/requirements.txt` in CI dependency installation
- Lint both backend AND gui directories
- QNetworkAccessManager type hints may need `# type: ignore` for mypy
- Logging uses print() - configure .pylintrc to allow (or suppress warnings)

**Code Quality from Story 1.4:**
- Review grade: 9.5/10 ⭐
- Black formatting: Passed
- Comprehensive docstrings: Present
- Type hints: Some needed for mypy strict mode

**Technical Debt:**
- Logging framework migration deferred to Story 7.4
- May need `.pylintrc` adjustments to allow print() statements

### From Story 1.3 (Chrome Extension)

**Extension Files:**
- `extension/manifest.json` - Manifest V3 structure
- `extension/background/service-worker.js` - Background logic
- `extension/content/content-script.js` - DOM interaction

**Implications for Story 1.5:**
- Validate manifest.json with JSON.parse
- Run eslint on all `.js` files in extension/
- No package.json - eslint installed globally in CI

### From Story 1.2 (Backend Scaffolding)

**Backend Structure:**
- `backend/main.py` - FastAPI app with /api/status endpoint
- `backend/requirements.txt` - FastAPI, uvicorn, pydantic, pyyaml

**Implications for Story 1.5:**
- Backend code exists to lint and test
- Health check endpoint ready for pytest testing (Story 1.6)
- Install backend dependencies in test-backend job

### From Story 1.1 (Project Initialization)

**Repository Structure:**
- `.github/workflows/` directory exists
- Placeholder CI and release workflows present
- `.pylintrc` exists with base configuration
- README.md present for badge addition

**Implications for Story 1.5:**
- Replace placeholder workflows with complete implementations
- Update .pylintrc for stricter checks
- Add badges to README "after" title line

---

## Implementation Notes

### Workflow Execution Order

**CI Workflow (Parallel):**
1. Checkout code (all jobs)
2. Setup environments (Python 3.11, Node 18)
3. Install dependencies
4. Run jobs in parallel:
   - test-backend: pytest → coverage upload
   - lint-backend: black → pylint → mypy
   - test-extension: eslint → manifest validation

**Release Workflow (Sequential):**
1. build-windows: Checkout → Python setup → PyInstaller → Upload artifact
2. create-release (needs: build-windows): Download artifact → Create release

### Expected Durations

- **CI workflow:** 3-5 minutes (parallel jobs)
- **Release workflow:** 8-12 minutes (Windows runner slower, PyInstaller build time)

### Pip Dependency Caching

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

**Benefit:** Reduces install time from ~60s to ~10s on cache hit

### Badge URLs

```markdown
![Build Status](https://github.com/USERNAME/autoresumefiller/actions/workflows/ci.yml/badge.svg)
![Coverage](https://codecov.io/gh/USERNAME/autoresumefiller/branch/main/graph/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
```

Replace `USERNAME` with actual GitHub username.

---

## Success Criteria Checklist

- [ ] CI workflow file created with 3 jobs (test, lint, extension)
- [ ] Release workflow file created with 2 jobs (build, release)
- [ ] All jobs use pinned action versions (@v4, @v3)
- [ ] Pip dependencies cached for performance
- [ ] Pylint fail-under 8.0 enforced
- [ ] Mypy strict mode enabled
- [ ] Windows executable builds without errors
- [ ] GitHub release created with artifacts
- [ ] README badges added and functional
- [ ] Workflow runs complete within expected duration
- [ ] Manual validation: Intentional failures caught correctly
- [ ] Manual validation: Tag creation triggers release workflow
- [ ] Manual validation: All badges display correctly on GitHub

---

**Context Generated:** 2025-11-28  
**Ready for Implementation:** Yes  
**Next Step:** Run `*dev-story` to implement Story 1.5
