# Story 1.1: Project Initialization & Repository Setup

**Epic:** Epic 1 - Foundation & Core Infrastructure  
**Story ID:** 1.1  
**Status:** Drafted  
**Created:** 2025-11-28  
**Author:** SM Agent (Ragnar)  
**Estimated Effort:** 2-4 hours  
**Sprint:** Sprint 1

---

## User Story

**As a** developer  
**I want** a properly structured repository with Python package management  
**So that** the codebase is maintainable and follows best practices from day one

---

## Business Context

This story establishes the foundational project structure for AutoResumeFiller, a desktop application that automates job application form filling using AI. It creates the repository scaffolding, directory structure, configuration files, and initial documentation that all subsequent development depends on.

**Business Value:**
- Enables professional software development workflow from the start
- Reduces onboarding time for future contributors (<15 minutes to working environment)
- Demonstrates portfolio-quality project structure and best practices
- Establishes quality standards (testing, linting, type checking) from day one

**User Impact:** None (internal infrastructure story)

**Dependencies:**
- None (first story in the project)

**Related Stories:**
- Story 1.2: Python Backend Scaffolding (requires this structure)
- Story 1.3: Chrome Extension Manifest & Basic Structure (requires this structure)
- Story 1.4: PyQt5 GUI Application Shell (requires this structure)

---

## Acceptance Criteria

### AC1: Repository Directory Structure Created

**Given** starting a new project  
**When** initializing the repository structure  
**Then** the following directory tree is created:

```
autoresumefiller/
├── .github/
│   └── workflows/
│       ├── ci.yml                  # CI/CD pipeline (placeholder)
│       └── release.yml             # Release automation (placeholder)
├── backend/
│   ├── api/                        # API route modules (empty)
│   ├── services/                   # Business logic services (empty)
│   ├── config/                     # Configuration module (empty)
│   ├── utils/                      # Utility functions (empty)
│   ├── tests/                      # Backend tests (empty)
│   ├── main.py                     # FastAPI entry point (placeholder)
│   └── requirements.txt            # Backend dependencies (empty)
├── gui/
│   ├── windows/                    # PyQt5 windows (empty)
│   ├── widgets/                    # Custom widgets (empty)
│   ├── services/                   # GUI services (empty)
│   ├── resources/                  # Icons and assets (empty)
│   │   └── icons/
│   ├── tests/                      # GUI tests (empty)
│   ├── main.py                     # GUI entry point (placeholder)
│   └── requirements.txt            # GUI dependencies (empty)
├── extension/
│   ├── background/                 # Extension background worker (empty)
│   ├── content/                    # Content scripts (empty)
│   ├── popup/                      # Extension popup UI (empty)
│   ├── lib/                        # Shared utilities (empty)
│   └── icons/                      # Extension icons (empty)
├── docs/                           # Additional documentation (keep existing)
├── tests/
│   └── integration/                # End-to-end tests (empty)
├── .gitignore                      # Git exclusions
├── .editorconfig                   # Editor configuration
├── .pylintrc                       # Pylint configuration
├── pyproject.toml                  # Python project metadata
├── pytest.ini                      # Pytest configuration
├── README.md                       # Project documentation
├── CONTRIBUTING.md                 # Contribution guidelines
├── CODE_OF_CONDUCT.md              # Community guidelines
└── LICENSE                         # MIT License
```

**Verification:**
- Run `tree /F` (Windows) or `tree -a` (Unix) to verify structure matches
- All directories contain `__init__.py` where appropriate (Python packages)
- No missing directories or extra files

---

### AC2: pyproject.toml Configured

**Given** the repository structure  
**When** creating the Python project configuration  
**Then** `pyproject.toml` contains:

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
]

[project.urls]
Homepage = "https://github.com/yourusername/autoresumefiller"
Repository = "https://github.com/yourusername/autoresumefiller"
Issues = "https://github.com/yourusername/autoresumefiller/issues"

[build-system]
requires = ["setuptools>=68.0", "wheel>=0.41"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["backend*", "gui*"]
exclude = ["tests*"]

[tool.pytest.ini_options]
testpaths = ["backend/tests", "gui/tests", "tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Tests that take >1s to run",
]

[tool.coverage.run]
source = ["backend", "gui"]
omit = ["*/tests/*", "*/test_*.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]

[tool.black]
line-length = 100
target-version = ["py39", "py310", "py311"]
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | build
  | dist
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

[[tool.mypy.overrides]]
module = "PyQt5.*"
ignore_missing_imports = true

[tool.pylint.main]
py-version = "3.9"
ignore = ["tests", ".venv", "build", "dist"]
load-plugins = ["pylint.extensions.docparams"]

[tool.pylint.messages_control]
max-line-length = 100
disable = [
    "C0111",  # missing-docstring
    "C0103",  # invalid-name
    "R0903",  # too-few-public-methods
]
```

**Verification:**
- Run `python -m build --version` to verify build system works
- Validate TOML syntax with `python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"`
- Verify all tool configurations are valid

---

### AC3: .gitignore Properly Configured

**Given** the repository structure  
**When** creating the .gitignore file  
**Then** it excludes (in addition to existing BMAD exclusions):

```gitignore
# Python Development Artifacts
__pycache__/
*.py[cod]
*$py.class
*.so
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
*.egg-info/
.installed.cfg
*.egg

# Virtual Environments
venv/
.venv/
env/
ENV/
env.bak/
venv.bak/

# Testing and Coverage
.coverage
.coverage.*
htmlcov/
.tox/
.pytest_cache/
.hypothesis/
coverage.xml
*.cover

# IDEs and Editors
.vscode/
.idea/
*.swp
*.swo
*~

# Application-Specific Data
data/
logs/
backups/
*.db
*.sqlite

# Secrets and Configuration
*.key
.env
.env.*
config.yaml
settings.json

# OS Files
.DS_Store
Thumbs.db
desktop.ini

# Build Artifacts
*.spec
*.zip
*.tar.gz
AutoResumeFiller-*.exe
```

**Verification:**
- Run `git status --ignored` to verify patterns work
- Test with `echo "test" > venv/test.txt; git status` (should not show venv/)
- Verify existing BMAD exclusions remain intact

---

### AC4: README.md Created

**Given** the repository structure  
**When** creating the project README  
**Then** `README.md` contains:

- Project title and description (1-2 paragraphs)
- Key features list (bullet points from PRD)
- Technology stack (Python 3.9+, FastAPI, PyQt5, Chrome Extension)
- Architecture diagram (ASCII or link to docs/architecture.md)
- Installation instructions (developer setup)
  - Clone repository
  - Install Python dependencies
  - Set up Chrome extension
  - Run backend and GUI
- Usage instructions (placeholder - "Coming in future releases")
- Contributing guidelines (link to CONTRIBUTING.md)
- License information (MIT)
- Contact/Support information

**Verification:**
- README renders correctly on GitHub (preview in VS Code or push to GitHub)
- All links are valid (CONTRIBUTING.md, LICENSE, docs/)
- Installation instructions can be followed successfully (<15 minutes)

---

### AC5: License and Community Files Created

**Given** the repository structure  
**When** creating community files  
**Then** the following files exist:

**LICENSE (MIT):**
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

**CONTRIBUTING.md:**
- Development environment setup
- Code style guidelines (black, pylint, mypy)
- Testing requirements (pytest, 70%+ coverage)
- Pull request process
- Issue reporting guidelines

**CODE_OF_CONDUCT.md:**
- Contributor Covenant Code of Conduct v2.1 (standard template)
- Contact information for reporting violations

**Verification:**
- LICENSE is recognized by GitHub (displays in repository header)
- CONTRIBUTING.md renders correctly
- CODE_OF_CONDUCT.md follows standard format

---

### AC6: pytest.ini and .pylintrc Configured

**Given** the repository structure  
**When** creating testing and linting configuration  
**Then** the following files exist:

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
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Tests that take >1s to run
```

**.pylintrc:**
```ini
[MASTER]
py-version=3.9
ignore=tests,.venv,build,dist
load-plugins=pylint.extensions.docparams

[MESSAGES CONTROL]
max-line-length=100
disable=
    C0111,  # missing-docstring
    C0103,  # invalid-name
    R0903,  # too-few-public-methods
    W0212,  # protected-access (needed for testing)

[FORMAT]
indent-string='    '
expected-line-ending-format=LF

[DESIGN]
max-args=7
max-locals=20
max-returns=6
max-branches=15
```

**Verification:**
- Run `pytest --collect-only` (should collect 0 tests, no errors)
- Run `pylint --version` to verify pylint works
- Verify configurations are valid

---

### AC7: .editorconfig Created

**Given** the repository structure  
**When** creating editor configuration  
**Then** `.editorconfig` contains:

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

**Verification:**
- EditorConfig plugin recognizes file in VS Code/PyCharm
- Test formatting consistency across editors

---

### AC8: Placeholder Files Created

**Given** the repository structure  
**When** creating placeholder files  
**Then** the following files exist with basic content:

**backend/main.py:**
```python
"""AutoResumeFiller Backend API - Entry Point (Placeholder)."""
# TODO: Implement FastAPI application in Story 1.2
pass
```

**gui/main.py:**
```python
"""AutoResumeFiller GUI - Entry Point (Placeholder)."""
# TODO: Implement PyQt5 application in Story 1.4
pass
```

**backend/requirements.txt:**
```
# Backend dependencies - to be populated in Story 1.2
```

**gui/requirements.txt:**
```
# GUI dependencies - to be populated in Story 1.4
```

**All empty directories contain `.gitkeep` files** to ensure they're tracked by git

**Verification:**
- All placeholder files contain valid Python/text content
- No syntax errors when running `python -m py_compile backend/main.py gui/main.py`
- Git tracks all directories via .gitkeep files

---

## Technical Implementation Details

### Directory Creation Script

Create all directories and placeholder files using Python script or shell commands:

**Python script (create_structure.py):**
```python
#!/usr/bin/env python3
"""Create project directory structure for AutoResumeFiller."""
import os
from pathlib import Path

STRUCTURE = {
    ".github/workflows": [],
    "backend/api": [],
    "backend/services": [],
    "backend/config": [],
    "backend/utils": [],
    "backend/tests": [],
    "gui/windows": [],
    "gui/widgets": [],
    "gui/services": [],
    "gui/resources/icons": [],
    "gui/tests": [],
    "extension/background": [],
    "extension/content": [],
    "extension/popup": [],
    "extension/lib": [],
    "extension/icons": [],
    "tests/integration": [],
}

def create_structure(base_path: Path = Path(".")):
    """Create directory structure with __init__.py and .gitkeep files."""
    for dir_path in STRUCTURE.keys():
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        
        # Add __init__.py for Python packages
        if dir_path.startswith(("backend", "gui")):
            (full_path / "__init__.py").touch()
        
        # Add .gitkeep for empty directories
        (full_path / ".gitkeep").touch()
        
        print(f"✓ Created {dir_path}")

if __name__ == "__main__":
    create_structure()
    print("\n✨ Project structure created successfully!")
```

**Run:** `python scripts/create_structure.py`

---

### Git Initialization

**Commands:**
```bash
# Initialize git repository (if not already done)
git init

# Create initial commit with structure
git add .
git commit -m "Story 1.1: Initialize project structure and configuration

- Created directory structure for backend, GUI, and Chrome extension
- Added pyproject.toml with project metadata and tool configurations
- Configured pytest, black, pylint, mypy in pyproject.toml
- Added comprehensive .gitignore for Python, IDEs, and secrets
- Created README.md with project overview and installation guide
- Added MIT LICENSE for open source distribution
- Created CONTRIBUTING.md and CODE_OF_CONDUCT.md for community
- Added .editorconfig for consistent formatting across editors
- Created placeholder files for backend/main.py and gui/main.py
- Added .gitkeep files to track empty directories

This establishes the foundational project structure for AutoResumeFiller,
enabling all subsequent development work with professional best practices."
```

---

### Verification Checklist

**Pre-implementation:**
- [ ] Read Epic 1 tech spec (`docs/sprint-artifacts/tech-spec-epic-1.md`)
- [ ] Review architecture document (`docs/architecture.md`)
- [ ] Understand story dependencies (none for Story 1.1)

**During implementation:**
- [ ] Create all directories per AC1
- [ ] Configure pyproject.toml per AC2
- [ ] Update .gitignore per AC3 (merge with existing)
- [ ] Write comprehensive README.md per AC4
- [ ] Create LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md per AC5
- [ ] Configure pytest.ini and .pylintrc per AC6
- [ ] Create .editorconfig per AC7
- [ ] Add placeholder files per AC8

**Post-implementation:**
- [ ] Run `tree /F` to verify directory structure
- [ ] Run `python -m build --version` to verify build system
- [ ] Run `pytest --collect-only` (should show 0 tests, no errors)
- [ ] Run `pylint --version` to verify linting works
- [ ] Run `git status` to verify .gitignore works correctly
- [ ] Test README instructions (<15 minutes to set up environment)
- [ ] Validate all TOML/INI files have correct syntax
- [ ] Create git commit with descriptive message

---

## Definition of Done

- [ ] All 8 acceptance criteria met and verified
- [ ] Directory structure matches Epic 1 tech spec exactly
- [ ] All configuration files (pyproject.toml, pytest.ini, .pylintrc, .editorconfig) are valid
- [ ] README.md is comprehensive and accurate
- [ ] LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md created
- [ ] .gitignore properly excludes Python artifacts, secrets, IDE files
- [ ] All placeholder files created with no syntax errors
- [ ] Git repository initialized with descriptive initial commit
- [ ] Developer can clone and set up environment in <15 minutes
- [ ] No linting errors: `pylint --version` runs successfully
- [ ] No test errors: `pytest --collect-only` runs successfully
- [ ] Story reviewed and approved by SM (code-review workflow)
- [ ] Sprint status updated: `1-1-project-initialization-repository-setup: backlog → done`

---

## Notes and Considerations

### Design Decisions

1. **MIT License Choice:**
   - Portfolio-friendly, allows commercial use
   - Most permissive open source license
   - Industry standard for developer tools

2. **pyproject.toml over setup.py:**
   - Modern Python packaging (PEP 517/518)
   - Single configuration file for all tools
   - Better dependency management

3. **Monorepo Structure:**
   - Single repository for backend, GUI, and extension
   - Easier dependency management and versioning
   - Simplified CI/CD pipeline

4. **Directory Organization:**
   - Follows Python best practices (src layout avoided for simplicity)
   - Clear separation of concerns (api/, services/, windows/)
   - Test directories parallel to source code

### Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Directory structure changes later | Medium | Document structure rationale in tech spec |
| .gitignore misses important files | High | Test with actual development workflow |
| Configuration conflicts between tools | Medium | Test all tool configurations before commit |
| README becomes outdated | Low | Update README in each story that adds features |

### Future Considerations

- **Story 1.2:** Will populate backend/requirements.txt and backend/main.py
- **Story 1.3:** Will create extension/manifest.json and JavaScript files
- **Story 1.4:** Will populate gui/requirements.txt and gui/main.py
- **Story 1.5:** Will populate .github/workflows/ci.yml and release.yml
- **Epic 7:** Will add PyInstaller configuration and build scripts

---

## Testing Strategy

### Unit Tests

**Not applicable** - This story only creates structure and configuration files.

### Integration Tests

**Not applicable** - No integration points yet.

### Manual Testing

**Test Case 1: Verify Directory Structure**
1. Run `tree /F` (Windows) or `tree -a` (Unix)
2. Compare output to AC1 directory tree
3. **Expected:** All directories present, no extra files

**Test Case 2: Verify Configuration Files**
1. Run `python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"`
2. Run `pytest --collect-only`
3. Run `pylint --version`
4. **Expected:** All commands succeed, no errors

**Test Case 3: Verify .gitignore**
1. Create test files: `touch venv/test.txt data/test.db .env`
2. Run `git status`
3. **Expected:** None of these files appear in untracked list

**Test Case 4: Verify README Instructions**
1. Clone repository fresh
2. Follow README.md installation instructions
3. Time the setup process
4. **Expected:** Complete setup in <15 minutes, no errors

---

## Traceability

### PRD Requirements

- **FR75:** Install from GitHub with manual setup → Addresses via README.md instructions
- **FR79:** Provide clear installation instructions → Addresses via README.md and CONTRIBUTING.md

### Architecture Alignment

- **Repository Structure:** Implements directory layout from `docs/architecture.md` Section 3.1
- **Technology Stack:** Enforces Python 3.9+ requirement from architecture decisions
- **Modularity:** Creates separate backend/, gui/, extension/ directories as specified

### Epic Tech Spec Alignment

- **AC1 (Epic 1):** Repository structure created → Directly implements this AC
- **Detailed Design - Repository Structure:** Matches directory tree exactly
- **Success Criteria:** Developer can set up environment in <15 minutes → Verified in manual tests

---

## Dependencies

**Upstream Dependencies:** None (first story)

**Downstream Dependencies:**
- Story 1.2: Python Backend Scaffolding (requires this structure)
- Story 1.3: Chrome Extension Manifest & Basic Structure (requires this structure)
- Story 1.4: PyQt5 GUI Application Shell (requires this structure)
- Story 1.5: CI/CD Pipeline - GitHub Actions (requires .github/workflows/)
- Story 1.6: Testing Infrastructure & First Unit Tests (requires test directories)
- Story 1.7: Development Environment Documentation (builds on README.md)

---

## Implementation Order

1. **Create directory structure** (AC1) - Use Python script or manual commands
2. **Configure pyproject.toml** (AC2) - Copy template and customize
3. **Update .gitignore** (AC3) - Merge with existing BMAD exclusions
4. **Write README.md** (AC4) - Start with template, customize for project
5. **Create LICENSE** (AC5) - Use MIT template with current year
6. **Create CONTRIBUTING.md and CODE_OF_CONDUCT.md** (AC5) - Use standard templates
7. **Configure pytest.ini and .pylintrc** (AC6) - Copy from tech spec
8. **Create .editorconfig** (AC7) - Standard configuration
9. **Add placeholder files** (AC8) - Touch files with minimal content
10. **Git commit** - Single commit with all changes

**Estimated Time:** 2-4 hours (including testing and documentation)

---

**Story Status:** Drafted ✅  
**Next Step:** Run `*story-context` to add just-in-time technical context before development  
**Assigned To:** DEV Agent (Ragnar)  
**Sprint Priority:** P0 (Must complete first)
