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
