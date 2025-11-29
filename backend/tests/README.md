# Backend Testing Guide

Complete guide for running, writing, and understanding tests for the AutoResumeFiller backend.

## Table of Contents

- [Running Tests](#running-tests)
- [Using Fixtures](#using-fixtures)
- [Coverage Interpretation](#coverage-interpretation)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)

---

## Running Tests

### Prerequisites

Ensure your virtual environment is activated and dependencies are installed:

```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### Basic Test Execution

```bash
# Run all backend tests
pytest backend/tests/ -v

# Run all tests in project
pytest

# Run specific test file
pytest backend/tests/test_main.py -v

# Run specific test class
pytest backend/tests/test_main.py::TestHealthCheckEndpoint -v

# Run specific test method
pytest backend/tests/test_main.py::TestHealthCheckEndpoint::test_health_check_success -v
```

### Coverage Reports

```bash
# Terminal coverage report with missing lines
pytest backend/tests/ --cov=backend --cov-report=term-missing

# HTML coverage report (open htmlcov/index.html in browser)
pytest backend/tests/ --cov=backend --cov-report=html

# Both terminal and HTML reports
pytest backend/tests/ --cov=backend --cov-report=html --cov-report=term-missing

# XML report for CI/CD
pytest backend/tests/ --cov=backend --cov-report=xml
```

### Test Filtering with Markers

```bash
# Run only unit tests (fast, isolated)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow

# Run everything except slow tests
pytest -m "not slow"

# Combine markers
pytest -m "unit and not slow"
```

### Other Useful Options

```bash
# Stop on first failure
pytest backend/tests/ -x

# Run last failed tests
pytest backend/tests/ --lf

# Show local variables on failure
pytest backend/tests/ -l

# Capture stdout/stderr
pytest backend/tests/ -s

# Run tests in parallel (requires pytest-xdist)
pytest backend/tests/ -n auto
```

---

## Using Fixtures

Fixtures are defined in `conftest.py` and automatically available to all tests in the backend/tests/ directory.

### Available Fixtures

#### 1. test_client

Provides a FastAPI TestClient for testing API endpoints.

**Usage:**
```python
@pytest.mark.unit
def test_health_check(test_client):
    """Test health check endpoint."""
    response = test_client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
```

**What it does:**
- Creates TestClient with FastAPI app
- Handles setup and teardown automatically
- In-memory testing (no actual HTTP server)

#### 2. temp_data_dir

Provides a temporary directory for file operations in tests.

**Usage:**
```python
@pytest.mark.unit
def test_file_operations(temp_data_dir):
    """Test file save and load."""
    test_file = temp_data_dir / "test.txt"
    test_file.write_text("Hello, World!")
    
    assert test_file.exists()
    assert test_file.read_text() == "Hello, World!"
    # Directory automatically cleaned up after test
```

**What it does:**
- Creates temporary directory using tempfile.TemporaryDirectory
- Returns Path object for easy file operations
- Automatically deletes directory and contents after test

#### 3. mock_ai_response

Provides a mock AI provider response for testing AI integration.

**Usage:**
```python
@pytest.mark.unit
def test_ai_processing(mock_ai_response):
    """Test AI response processing."""
    assert mock_ai_response["confidence"] > 0.8
    assert mock_ai_response["provider"] == "mock"
    assert "response" in mock_ai_response
    
    # Use in your code that processes AI responses
    result = process_ai_response(mock_ai_response)
    assert result is not None
```

**What it returns:**
```python
{
    "response": "Sample AI generated text for testing purposes",
    "confidence": 0.92,
    "provider": "mock",
    "model": "test-model-v1",
    "tokens_used": 50,
    "completion_time_ms": 120
}
```

#### 4. test_config_override

Provides test configuration settings.

**Usage:**
```python
@pytest.mark.unit
def test_with_config(test_config_override):
    """Test configuration-dependent code."""
    assert test_config_override["API_PORT"] == 8765
    assert test_config_override["LOG_LEVEL"] == "DEBUG"
    
    # Use to override settings in tests
    settings = Settings(**test_config_override)
    assert settings.API_PORT == 8765
```

**What it returns:**
```python
{
    "API_HOST": "127.0.0.1",
    "API_PORT": 8765,
    "LOG_LEVEL": "DEBUG",
    "CORS_ORIGINS": ["chrome-extension://*"],
    "DATA_DIR": "./test_data",
    "ENABLE_ANALYTICS": False
}
```

### Creating Custom Fixtures

Add new fixtures to `conftest.py`:

```python
import pytest

@pytest.fixture
def sample_user_data():
    """Provide sample user profile data."""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-0123",
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Software Engineer",
                "years": 3
            }
        ]
    }
```

---

## Coverage Interpretation

### Understanding Coverage Metrics

The coverage report shows how much of your code is tested:

```
Name                         Stmts   Miss Branch BrPart   Cover   Missing
-------------------------------------------------------------------------
backend\config\settings.py      16      0      0      0 100.00%
backend\main.py                 29      0      0      0 100.00%
-------------------------------------------------------------------------
TOTAL                           45      0      0      0 100.00%
```

**Column Definitions:**
- **Stmts**: Total statements in the file
- **Miss**: Statements not executed during tests
- **Branch**: Total conditional branches (if/else)
- **BrPart**: Partially covered branches
- **Cover**: Percentage of code executed (Stmts - Miss) / Stmts × 100
- **Missing**: Line numbers not covered

### Coverage Targets

**Current Status (Story 1.6):**
- `backend/main.py`: 100% ✅
- `backend/config/settings.py`: 100% ✅

**Project Standards:**
- **70-80%**: Good baseline for MVP
- **80-90%**: Excellent coverage for production
- **90-100%**: Outstanding, but diminishing returns
- **<70%**: Add tests for critical paths

### Excluded from Coverage

Configured in `pyproject.toml`:

```toml
[tool.coverage.run]
omit = [
    "*/tests/*",        # Test files themselves
    "*/test_*.py",      # Test files
    "*/__init__.py",    # Package init files
    "*/conftest.py",    # Pytest fixtures
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",           # Explicitly excluded
    "def __repr__",               # String representations
    "def __str__",
    "raise AssertionError",       # Defensive assertions
    "raise NotImplementedError",  # Abstract methods
    "if __name__ == .__main__.:", # Script entry points
    "if TYPE_CHECKING:",          # Type checking imports
    "class .*\\bProtocol\\):",    # Protocol definitions
    "@(abc\\.)?abstractmethod",   # Abstract methods
]
```

### Using pragma: no cover

Exclude specific lines from coverage:

```python
def debug_only_function():
    if DEBUG:  # pragma: no cover
        print("Debug info")
        
def main():
    app.run()
    
if __name__ == "__main__":  # pragma: no cover
    main()
```

### HTML Coverage Reports

View detailed coverage in browser:

```bash
# Generate HTML report
pytest --cov=backend --cov-report=html

# Open in browser (Windows)
start htmlcov\index.html

# Open in browser (Linux/Mac)
open htmlcov/index.html
```

The HTML report shows:
- File-by-file coverage breakdown
- Line-by-line highlighting (green = covered, red = missed)
- Branch coverage visualization
- Easy navigation through codebase

---

## Writing New Tests

### Test Structure (AAA Pattern)

Follow the **Arrange-Act-Assert** pattern:

```python
@pytest.mark.unit
def test_health_check_returns_correct_data(test_client):
    """Test health check endpoint returns expected structure."""
    # Arrange - Setup test data/conditions
    expected_fields = ["status", "version", "timestamp"]
    
    # Act - Execute the code under test
    response = test_client.get("/api/status")
    data = response.json()
    
    # Assert - Verify the results
    assert response.status_code == 200
    for field in expected_fields:
        assert field in data
    assert data["status"] == "healthy"
```

### Test Naming Conventions

**Good - Descriptive names:**
```python
def test_health_check_returns_200_when_backend_healthy():
    """Test health check endpoint returns 200 OK when backend is operational."""
    ...

def test_invalid_endpoint_returns_404_with_json_error():
    """Test that requests to non-existent endpoints return 404 with error details."""
    ...

def test_cors_allows_requests_from_chrome_extension_origin():
    """Test CORS middleware allows requests from chrome-extension:// origins."""
    ...
```

**Bad - Vague names:**
```python
def test_health():  # What about health?
    ...

def test_endpoint():  # Which endpoint?
    ...

def test_1():  # Meaningless
    ...
```

### Test Organization

**Group related tests in classes:**

```python
@pytest.mark.unit
class TestUserAuthentication:
    """Tests for user authentication endpoints."""
    
    def test_login_success(self, test_client):
        """Test successful login with valid credentials."""
        ...
    
    def test_login_invalid_credentials(self, test_client):
        """Test login fails with invalid credentials."""
        ...
    
    def test_logout_clears_session(self, test_client):
        """Test logout clears user session."""
        ...
```

### Using Markers

Mark tests for categorization and filtering:

```python
import pytest

@pytest.mark.unit
def test_fast_unit_test():
    """Fast, isolated unit test."""
    assert 1 + 1 == 2

@pytest.mark.integration
def test_database_integration():
    """Integration test with database."""
    ...

@pytest.mark.slow
def test_slow_operation():
    """Test that takes >1 second."""
    import time
    time.sleep(1.5)
    ...

@pytest.mark.e2e
def test_full_workflow():
    """End-to-end test of complete user workflow."""
    ...
```

### Async Tests

For testing async endpoints:

```python
import pytest

@pytest.mark.asyncio
@pytest.mark.unit
async def test_async_endpoint(test_client):
    """Test async endpoint."""
    response = await test_client.get("/api/async-endpoint")
    assert response.status_code == 200
```

### Parametrized Tests

Test multiple inputs with same logic:

```python
@pytest.mark.unit
@pytest.mark.parametrize("endpoint,expected_status", [
    ("/", 200),
    ("/api/status", 200),
    ("/docs", 200),
    ("/redoc", 200),
    ("/api/nonexistent", 404),
    ("/invalid", 404),
])
def test_endpoint_status_codes(test_client, endpoint, expected_status):
    """Test various endpoints return expected status codes."""
    response = test_client.get(endpoint)
    assert response.status_code == expected_status
```

### Testing Error Cases

Always test both success and failure paths:

```python
@pytest.mark.unit
class TestUserRegistration:
    """Tests for user registration."""
    
    def test_registration_success(self, test_client):
        """Test successful user registration."""
        response = test_client.post("/api/register", json={
            "email": "user@example.com",
            "password": "secure123"
        })
        assert response.status_code == 201
    
    def test_registration_duplicate_email(self, test_client):
        """Test registration fails with duplicate email."""
        # First registration
        test_client.post("/api/register", json={
            "email": "user@example.com",
            "password": "secure123"
        })
        
        # Duplicate registration
        response = test_client.post("/api/register", json={
            "email": "user@example.com",
            "password": "different456"
        })
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    def test_registration_invalid_email(self, test_client):
        """Test registration fails with invalid email format."""
        response = test_client.post("/api/register", json={
            "email": "not-an-email",
            "password": "secure123"
        })
        assert response.status_code == 422  # Validation error
```

---

## Troubleshooting

### Tests Not Discovered

**Problem:** pytest doesn't find your tests

**Solutions:**
- Check filename starts with `test_` or ends with `_test.py`
- Check function name starts with `test_`
- Check test class name starts with `Test`
- Ensure test file is in `backend/tests/` directory
- Check pytest configuration in `pyproject.toml`

```bash
# Debug test discovery
pytest --collect-only backend/tests/
```

### Import Errors

**Problem:** `ModuleNotFoundError` or `ImportError`

**Solutions:**
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r backend/requirements.txt

# Verify Python path
python -c "import sys; print('\n'.join(sys.path))"

# Run from project root
cd C:\Users\basha\Desktop\root\AutoResumeFiller
pytest backend/tests/
```

### Fixture Not Found

**Problem:** `fixture 'test_client' not found`

**Solutions:**
- Ensure `conftest.py` exists in `backend/tests/`
- Check fixture is defined with `@pytest.fixture` decorator
- Fixture name in test parameter must match fixture function name
- Don't import fixtures (pytest auto-discovers from conftest.py)

### Coverage Not Working

**Problem:** No coverage report generated

**Solutions:**
```bash
# Ensure pytest-cov installed
pip install pytest-cov

# Check pyproject.toml has [tool.coverage.run] section
cat pyproject.toml | grep coverage

# Verify source paths
pytest --cov=backend --cov-report=term-missing backend/tests/

# Debug coverage
pytest --cov=backend --cov-report=term --cov-report=html backend/tests/ -v
```

### Tests Pass Locally But Fail in CI

**Problem:** Tests succeed on your machine but fail in GitHub Actions

**Possible causes:**
- **Environment differences**: Different Python version, OS, or dependencies
- **Timing issues**: Tests with time.sleep() or timing assumptions
- **File paths**: Hardcoded paths that don't exist in CI
- **External dependencies**: Tests requiring network or external services

**Solutions:**
```python
# Use pathlib for cross-platform paths
from pathlib import Path
data_dir = Path(__file__).parent / "data"

# Use fixtures for temporary files
def test_with_temp_file(temp_data_dir):
    test_file = temp_data_dir / "test.txt"
    ...

# Mock external dependencies
@pytest.fixture
def mock_api_call():
    with patch('requests.get') as mock:
        mock.return_value.json.return_value = {"status": "ok"}
        yield mock
```

### Slow Tests

**Problem:** Test suite takes too long

**Solutions:**
```python
# Mark slow tests
@pytest.mark.slow
def test_slow_operation():
    ...

# Skip slow tests in development
pytest -m "not slow"

# Run tests in parallel
pip install pytest-xdist
pytest -n auto

# Profile slow tests
pytest --durations=10  # Show 10 slowest tests
```

### Test Isolation Issues

**Problem:** Tests pass individually but fail when run together

**Causes:**
- Shared state between tests
- Database not cleaned between tests
- Global variables modified

**Solutions:**
```python
# Use fixtures for setup/teardown
@pytest.fixture
def clean_database():
    """Ensure clean database for each test."""
    db.clear()
    yield
    db.clear()

# Use autouse=True for automatic cleanup
@pytest.fixture(autouse=True)
def reset_state():
    """Reset global state before each test."""
    yield
    global_state.reset()
```

---

## Additional Resources

- **pytest Documentation**: https://docs.pytest.org/
- **pytest-cov Documentation**: https://pytest-cov.readthedocs.io/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **pytest Fixtures**: https://docs.pytest.org/en/stable/fixture.html
- **Python Testing Best Practices**: https://docs.python-guide.org/writing/tests/

---

## Quick Reference

```bash
# Essential commands
pytest backend/tests/ -v                                    # Run all tests
pytest backend/tests/ --cov=backend --cov-report=html       # Coverage report
pytest -m unit                                              # Run unit tests only
pytest -k "health_check"                                    # Run tests matching pattern
pytest backend/tests/test_main.py::TestHealthCheckEndpoint  # Run specific class
pytest --lf                                                 # Run last failed
pytest -x                                                   # Stop on first failure
```

**Last Updated:** 2025-11-29 (Story 1.6)
