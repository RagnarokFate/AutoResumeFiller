# Story 1.6 Technical Context: Testing Infrastructure & First Unit Tests

**Generated:** 2025-11-29  
**For Story:** 1.6 - Testing Infrastructure & First Unit Tests  
**Status:** ready-for-dev  

---

## Story Summary

**As a** developer maintaining AutoResumeFiller  
**I want** comprehensive pytest infrastructure with fixtures and coverage reporting  
**So that** I can write maintainable tests and ensure code quality throughout development

---

## Acceptance Criteria

### AC1: Pytest Configuration Consolidated
- pyproject.toml contains complete [tool.pytest.ini_options]
- pytest.ini removed to avoid duplication
- Custom markers defined (unit, integration, e2e, slow)
- Running `pytest --help` shows markers

### AC2: Reusable Test Fixtures Created
- backend/tests/conftest.py with 4 fixtures:
  * test_client (FastAPI TestClient)
  * temp_data_dir (temporary directory)
  * mock_ai_response (mock AI data)
  * test_config_override (test config)
- All fixtures documented with docstrings
- Proper cleanup with yield pattern

### AC3: Enhanced Test Coverage for Backend
- 5 new tests added to backend/tests/test_main.py:
  * test_invalid_endpoint_404
  * test_invalid_endpoint_json_error
  * test_cors_preflight_options
  * test_api_docs_accessible
  * test_api_redoc_accessible
- Existing 9 tests refactored to use fixtures
- All tests pass (14+ total)

### AC4: Coverage Reporting Configured
- [tool.coverage.run] in pyproject.toml
- [tool.coverage.report] in pyproject.toml
- HTML and terminal reports generated
- Branch coverage enabled

### AC5: Coverage Threshold Achieved
- backend/main.py >70% coverage
- backend/config/settings.py >70% coverage
- Overall backend >70% coverage
- Uncovered lines documented

### AC6: Test Documentation Created
- backend/tests/README.md with sections:
  * Running Tests
  * Using Fixtures
  * Coverage Interpretation
  * Writing New Tests
- Examples and best practices included

### AC7: Test Infrastructure Validated End-to-End
- `pytest` discovers and runs all tests
- 14+ tests passing in <5 seconds
- Coverage reports generated
- CI workflow runs tests automatically

---

## Tasks Breakdown

### Task 1: Consolidate Pytest Configuration
- [ ] Review existing pytest.ini and pyproject.toml
- [ ] Keep pyproject.toml as single source
- [ ] Remove pytest.ini
- [ ] Verify markers show in `pytest --help`

### Task 2: Create Reusable Test Fixtures
- [ ] Create/update backend/tests/conftest.py
- [ ] Implement test_client fixture
- [ ] Implement temp_data_dir fixture
- [ ] Implement mock_ai_response fixture
- [ ] Implement test_config_override fixture
- [ ] Add docstrings to fixtures

### Task 3: Enhance Test Coverage for Backend
- [ ] Add 5 new tests to test_main.py
- [ ] Refactor existing tests to use fixtures
- [ ] Add @pytest.mark.unit decorators
- [ ] Verify all tests pass

### Task 4: Configure Coverage Reporting
- [ ] Verify [tool.coverage.run] exists
- [ ] Verify [tool.coverage.report] exists
- [ ] Run pytest --cov --cov-report=html
- [ ] Inspect htmlcov/index.html

### Task 5: Achieve Coverage Threshold
- [ ] Run full coverage analysis
- [ ] Verify >70% for backend modules
- [ ] Add # pragma: no cover where appropriate
- [ ] Document uncovered lines

### Task 6: Create Test Documentation
- [ ] Create backend/tests/README.md
- [ ] Add Running Tests section
- [ ] Add Using Fixtures section
- [ ] Add Coverage Interpretation section
- [ ] Add Writing New Tests section

### Task 7: Validate End-to-End
- [ ] Run pytest from project root
- [ ] Verify 14+ tests passing
- [ ] Verify coverage report generation
- [ ] Push and verify CI runs tests

---

## Documentation Artifacts

### Primary References

**Epic 1 - Story 1.6 Specification:**
- **Path:** `docs/epics.md` (lines 451-480)
- **Section:** Story 1.6: Testing Infrastructure & First Unit Tests
- **Relevant Content:**
  - pytest configuration in pytest.ini or pyproject.toml
  - backend/tests/conftest.py with fixtures
  - Enhanced test_main.py with additional tests
  - Coverage >70% for tested modules

**Architecture - Testing Strategy:**
- **Path:** `docs/architecture.md` (Section 7)
- **Section:** Testing Strategy
- **Relevant Content:**
  - Unit tests with pytest and pytest-asyncio
  - Code coverage target: >80% (starting with >70% for MVP)
  - Test organization: backend/tests/, gui/tests/, tests/integration/
  - pytest fixtures for dependency injection

**Story 1.2 - Backend Tests:**
- **Path:** `docs/sprint-artifacts/stories/story-1.2-python-backend-scaffolding.md`
- **Section:** AC7: Unit Tests Implemented
- **Relevant Content:**
  - 9 existing tests in backend/tests/test_main.py
  - Tests for health check, CORS, root endpoint
  - TestClient usage pattern

**Story 1.5 - CI/CD Pipeline:**
- **Path:** `docs/sprint-artifacts/stories/story-1-5-ci-cd-pipeline-github-actions.md`
- **Section:** Dev Agent Record
- **Relevant Content:**
  - CI runs pytest with --cov=backend --cov=gui
  - Coverage baseline: 14.45% with 9 tests
  - Coverage uploaded to codecov (optional)

---

## Existing Code & Interfaces

### Current Test File

**backend/tests/test_main.py (Existing - 9 tests):**
```python
"""Unit tests for backend/main.py FastAPI endpoints."""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from backend.main import app

# Create test client
client = TestClient(app)

class TestHealthCheckEndpoint:
    """Tests for GET /api/status health check endpoint."""
    
    def test_health_check_success(self):
        response = client.get("/api/status")
        assert response.status_code == 200
    
    def test_health_check_response_structure(self):
        response = client.get("/api/status")
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
    
    def test_health_check_timestamp_format(self):
        response = client.get("/api/status")
        data = response.json()
        timestamp = data["timestamp"]
        assert timestamp.endswith("Z")
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert dt is not None
    
    def test_health_check_content_type(self):
        response = client.get("/api/status")
        assert response.headers["content-type"] == "application/json"
    
    def test_health_check_performance(self):
        import time
        start = time.time()
        response = client.get("/api/status")
        elapsed = (time.time() - start) * 1000
        assert response.status_code == 200
        assert elapsed < 100

class TestRootEndpoint:
    """Tests for GET / root endpoint."""
    
    def test_root_endpoint_success(self):
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_endpoint_structure(self):
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data

class TestCORSHeaders:
    """Tests for CORS middleware configuration."""
    
    def test_cors_headers_present(self):
        headers = {"Origin": "chrome-extension://abcdefghijklmnopqrstuvwxyz123456"}
        response = client.get("/api/status", headers=headers)
        assert response.status_code == 200
    
    def test_cors_allows_chrome_extension(self):
        headers = {"Origin": "chrome-extension://test123"}
        response = client.get("/api/status", headers=headers)
        assert response.status_code == 200
```

**Action for Story 1.6:**
- Refactor to use `test_client` fixture instead of module-level `client`
- Add 5 new test methods for error cases and API docs
- Add `@pytest.mark.unit` decorator to all tests

### Existing Pytest Configuration

**pytest.ini (Current - To be removed):**
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

**pyproject.toml (Current - Already complete):**
```toml
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
```

**Action for Story 1.6:**
- Remove pytest.ini (duplication)
- Keep pyproject.toml as single source of truth
- Verify all configuration works after pytest.ini removal

---

## Dependencies & Frameworks

### Python Testing Ecosystem

**Current Dependencies (Already Installed):**
```
# Testing (from backend/requirements.txt)
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
httpx>=0.24.0  # Required for FastAPI TestClient
```

**No New Dependencies Needed** - Story 1.6 uses existing pytest stack

### FastAPI Testing

**TestClient Usage Pattern:**
```python
from fastapi.testclient import TestClient
from backend.main import app

# Current pattern (module-level client)
client = TestClient(app)

def test_something():
    response = client.get("/endpoint")
    assert response.status_code == 200

# New pattern with fixture (Story 1.6)
@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

def test_something(test_client):
    response = test_client.get("/endpoint")
    assert response.status_code == 200
```

**Benefits of Fixture Pattern:**
- Proper cleanup with context manager
- Consistent client configuration
- Easy to mock/override for specific tests
- Follows pytest best practices

### Pytest Fixtures

**Fixture Scope Options:**
```python
@pytest.fixture(scope="function")  # Default - new instance per test
def test_client():
    ...

@pytest.fixture(scope="class")  # Shared within test class
def test_client():
    ...

@pytest.fixture(scope="module")  # Shared across module
def test_client():
    ...

@pytest.fixture(scope="session")  # Shared across entire test session
def test_client():
    ...
```

**For Story 1.6:**
- Use `scope="function"` (default) for test_client
- Use `scope="function"` for temp_data_dir (isolation)
- Mock fixtures don't need scope (return data only)

---

## Development Constraints

### Testing Standards

**From Architecture (Section 7: Testing Strategy):**
- pytest for all Python testing
- pytest-asyncio for async endpoints
- Code coverage target: >80% (starting with >70% for MVP)
- Test organization: backend/tests/, gui/tests/, tests/integration/

### Coverage Requirements

**Module Coverage Targets:**
- backend/main.py: >70% (100% ideal for API endpoints)
- backend/config/settings.py: >80% (configuration critical)
- New modules: >70% minimum

**Excluded from Coverage:**
- __init__.py files
- Test files (test_*.py)
- Fixture files (conftest.py)
- Lines with `# pragma: no cover`

### Test Organization

**File Naming:**
- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*` (e.g., TestHealthCheckEndpoint)
- Test functions: `test_*` (e.g., test_health_check_success)

**Directory Structure:**
```
backend/tests/
├── __init__.py
├── conftest.py          # Shared fixtures (NEW in Story 1.6)
├── test_main.py         # API endpoint tests (ENHANCED in Story 1.6)
├── README.md            # Test documentation (NEW in Story 1.6)
└── __pycache__/
```

---

## Interfaces & APIs

### Pytest Fixture Interface

**Fixture Definition Pattern:**
```python
import pytest
from typing import Generator

@pytest.fixture
def fixture_name() -> Generator[ReturnType, None, None]:
    """Fixture docstring explaining purpose and usage.
    
    Yields:
        ReturnType: Description of what fixture provides
        
    Example:
        def test_something(fixture_name):
            # Use fixture
            result = fixture_name.do_something()
            assert result is not None
    """
    # Setup code
    resource = create_resource()
    
    yield resource  # Test runs here
    
    # Teardown code
    cleanup_resource(resource)
```

**Usage in Tests:**
```python
def test_with_fixture(fixture_name):
    """Test that uses fixture."""
    # fixture_name is automatically passed by pytest
    result = fixture_name.do_something()
    assert result == expected_value
```

### FastAPI TestClient Interface

**Basic Usage:**
```python
from fastapi.testclient import TestClient

client = TestClient(app)

# GET request
response = client.get("/api/endpoint")
assert response.status_code == 200
data = response.json()

# POST request
response = client.post("/api/endpoint", json={"key": "value"})

# With headers
response = client.get("/api/endpoint", headers={"Authorization": "Bearer token"})

# With query parameters
response = client.get("/api/endpoint?param=value")
```

### Coverage Reporting Interface

**Command Line:**
```bash
# Run tests with coverage
pytest --cov

# HTML report
pytest --cov --cov-report=html

# Terminal report with missing lines
pytest --cov --cov-report=term-missing

# XML report for CI
pytest --cov --cov-report=xml

# Multiple reports
pytest --cov --cov-report=html --cov-report=term
```

**Coverage API (Programmatic):**
```python
# In pyproject.toml
[tool.coverage.run]
source = ["backend", "gui"]  # Packages to measure
omit = ["*/tests/*"]         # Patterns to exclude
branch = true                # Measure branch coverage

[tool.coverage.report]
precision = 2                # Decimal places
show_missing = true          # Show missing line numbers
exclude_lines = [            # Lines to exclude from coverage
    "pragma: no cover",
    "if __name__ == .__main__.:",
]
```

---

## Testing Standards & Ideas

### Test Structure Pattern (AAA)

**Arrange-Act-Assert Pattern:**
```python
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

### Test Naming Convention

**Descriptive Test Names:**
```python
# Good - Describes what is tested and expected outcome
def test_health_check_returns_200_when_backend_healthy():
    ...

def test_invalid_endpoint_returns_404_with_json_error():
    ...

def test_cors_allows_requests_from_chrome_extension_origin():
    ...

# Bad - Vague names
def test_health():
    ...

def test_endpoint():
    ...

def test_1():
    ...
```

### Test Ideas for Story 1.6

**Error Cases (NEW):**
```python
@pytest.mark.unit
def test_invalid_endpoint_404(test_client):
    """Test that invalid endpoints return 404."""
    response = test_client.get("/api/nonexistent")
    assert response.status_code == 404

@pytest.mark.unit
def test_invalid_endpoint_json_error(test_client):
    """Test that 404 responses include JSON error details."""
    response = test_client.get("/api/invalid")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
```

**CORS Preflight (NEW):**
```python
@pytest.mark.unit
def test_cors_preflight_options(test_client):
    """Test CORS preflight OPTIONS requests."""
    response = test_client.options(
        "/api/status",
        headers={
            "Origin": "chrome-extension://test123",
            "Access-Control-Request-Method": "GET",
        }
    )
    # CORS middleware should handle OPTIONS
    assert response.status_code in [200, 204]
```

**API Documentation (NEW):**
```python
@pytest.mark.unit
def test_api_docs_accessible(test_client):
    """Test Swagger UI docs are accessible."""
    response = test_client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "html" in response.text.lower()

@pytest.mark.unit
def test_api_redoc_accessible(test_client):
    """Test ReDoc docs are accessible."""
    response = test_client.get("/redoc")
    assert response.status_code == 200
```

**Fixture Usage Examples:**
```python
def test_with_mock_ai_response(test_client, mock_ai_response):
    """Test using mock AI response fixture."""
    # mock_ai_response = {"response": "Sample AI text", "confidence": 0.9}
    assert mock_ai_response["confidence"] > 0.8

def test_with_temp_directory(temp_data_dir):
    """Test file operations with temporary directory."""
    test_file = temp_data_dir / "test.txt"
    test_file.write_text("test content")
    assert test_file.exists()
    # Directory auto-cleaned up after test
```

---

## Learnings from Previous Stories

### From Story 1.2 (Python Backend Scaffolding)

**Testing Pattern Established:**
- 9 unit tests for FastAPI endpoints
- Tests use TestClient(app) directly (module-level client)
- Tests organized in classes (TestHealthCheckEndpoint, TestRootEndpoint, TestCORSHeaders)
- Each test method tests one specific aspect

**Implications for Story 1.6:**
- Build on existing test structure
- Refactor to use fixtures for better maintainability
- Add error case tests (404, invalid requests)
- Maintain class-based organization

[Source: Story 1.2 context and test_main.py]

### From Story 1.5 (CI/CD Pipeline)

**CI/CD Integration:**
- pytest runs in CI with --cov=backend --cov=gui
- Coverage report generated with --cov-report=xml
- Coverage uploaded to codecov (optional)
- All tests must pass for CI to succeed

**Coverage Baseline:**
- 9 tests established 14.45% coverage baseline
- Story 1.6 aims to increase to >70% for tested modules
- Coverage improvement demonstrates testing infrastructure value

**Implications for Story 1.6:**
- Tests run automatically in CI (no manual setup needed)
- Coverage reports visible in CI logs
- HTML coverage reports help identify gaps
- Story 1.6 improvements immediately visible in CI

[Source: Story 1.5 Dev Agent Record]

### From Architecture Document

**Testing Strategy Guidelines:**
- Unit tests: Fast, isolated, no external dependencies
- Integration tests: Moderate speed, test component interactions
- E2E tests: Slow, test full system workflows

**Coverage Philosophy:**
- 70%+ baseline for MVP
- 80%+ target for production
- Focus on critical business logic
- Don't obsess over 100% (diminishing returns)

**pytest Best Practices:**
- Use fixtures for shared setup
- Organize tests by feature/module
- Use markers for test categorization
- Keep tests fast (<100ms per unit test)

[Source: Architecture Document Section 7]

---

## Implementation Notes

### File Creation Order

**Step 1: Create/Update conftest.py**
```python
# backend/tests/conftest.py
"""Pytest fixtures for backend tests."""
import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def test_client():
    """Provide FastAPI test client for all backend tests.
    
    Yields:
        TestClient: FastAPI test client instance
        
    Example:
        def test_health_check(test_client):
            response = test_client.get("/api/status")
            assert response.status_code == 200
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture
def temp_data_dir():
    """Provide temporary directory for data tests.
    
    Yields:
        Path: Temporary directory path (auto-cleaned after test)
        
    Example:
        def test_file_operations(temp_data_dir):
            test_file = temp_data_dir / "test.txt"
            test_file.write_text("content")
            assert test_file.exists()
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_ai_response():
    """Provide mock AI provider response for testing.
    
    Returns:
        dict: Mock AI response with response, confidence, provider fields
        
    Example:
        def test_ai_processing(mock_ai_response):
            assert mock_ai_response["confidence"] > 0.8
    """
    return {
        "response": "Sample AI generated text for testing",
        "confidence": 0.9,
        "provider": "mock",
        "model": "test-model",
        "tokens_used": 50
    }


@pytest.fixture
def test_config_override():
    """Provide test configuration overrides.
    
    Returns:
        dict: Configuration overrides for testing
        
    Example:
        def test_with_config(test_config_override):
            assert test_config_override["API_PORT"] == 8765
    """
    return {
        "API_HOST": "127.0.0.1",
        "API_PORT": 8765,
        "LOG_LEVEL": "DEBUG",
        "CORS_ORIGINS": ["chrome-extension://*"]
    }
```

**Step 2: Remove pytest.ini**
```bash
# Simply delete the file
rm pytest.ini

# Verify pytest still works with pyproject.toml
pytest --help  # Should show markers
pytest --markers  # Should list unit, integration, e2e, slow
```

**Step 3: Enhance test_main.py**
- Refactor existing tests to use `test_client` fixture
- Add `@pytest.mark.unit` decorator to all tests
- Add 5 new test methods for error cases and API docs

**Step 4: Create test documentation**
```markdown
# backend/tests/README.md

# Backend Testing Guide

## Running Tests

### Run All Tests
\`\`\`bash
pytest backend/tests/ -v
\`\`\`

### Run with Coverage
\`\`\`bash
# Terminal report
pytest backend/tests/ --cov --cov-report=term-missing

# HTML report (open htmlcov/index.html)
pytest backend/tests/ --cov --cov-report=html

# Both
pytest backend/tests/ --cov --cov-report=html --cov-report=term
\`\`\`

### Run Specific Tests
\`\`\`bash
# Single test file
pytest backend/tests/test_main.py -v

# Single test class
pytest backend/tests/test_main.py::TestHealthCheckEndpoint -v

# Single test method
pytest backend/tests/test_main.py::TestHealthCheckEndpoint::test_health_check_success -v
\`\`\`

### Run by Marker
\`\`\`bash
# Run only unit tests
pytest -m unit

# Run only slow tests
pytest -m slow

# Run everything except slow tests
pytest -m "not slow"
\`\`\`

## Using Fixtures

Fixtures are defined in `conftest.py` and automatically available to all tests.

### test_client Fixture
\`\`\`python
def test_health_check(test_client):
    """Test using test_client fixture."""
    response = test_client.get("/api/status")
    assert response.status_code == 200
\`\`\`

### temp_data_dir Fixture
\`\`\`python
def test_file_operations(temp_data_dir):
    """Test using temporary directory."""
    test_file = temp_data_dir / "test.txt"
    test_file.write_text("content")
    assert test_file.exists()
    # Directory auto-cleaned after test
\`\`\`

### mock_ai_response Fixture
\`\`\`python
def test_ai_processing(mock_ai_response):
    """Test using mock AI response."""
    assert mock_ai_response["confidence"] > 0.8
    assert mock_ai_response["provider"] == "mock"
\`\`\`

## Coverage Interpretation

### Coverage Targets
- **70-80%**: Good baseline
- **80-90%**: Excellent coverage
- **90-100%**: Great, but diminishing returns
- **<70%**: Add tests for critical paths

### Excluded from Coverage
- `__init__.py` files
- Test files (`test_*.py`)
- Fixture files (`conftest.py`)
- Lines with `# pragma: no cover`

### Example Coverage Report
\`\`\`
Name                      Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------
backend\__init__.py           0      0      0      0   100%
backend\main.py              45      3      8      1    91%   23, 67-68
backend\config\settings.py   15      0      2      0   100%
---------------------------------------------------------------------
TOTAL                        60      3     10      1    93%
\`\`\`

## Writing New Tests

### Test Naming
\`\`\`python
# Good - Descriptive names
def test_health_check_returns_200_when_backend_healthy():
    ...

def test_invalid_endpoint_returns_404_with_json_error():
    ...

# Bad - Vague names
def test_health():
    ...

def test_1():
    ...
\`\`\`

### Test Structure (AAA Pattern)
\`\`\`python
def test_something(test_client):
    # Arrange - Setup test data
    expected_status = "healthy"
    
    # Act - Execute code under test
    response = test_client.get("/api/status")
    data = response.json()
    
    # Assert - Verify results
    assert response.status_code == 200
    assert data["status"] == expected_status
\`\`\`

### Using Markers
\`\`\`python
import pytest

@pytest.mark.unit
def test_fast_unit_test():
    \"\"\"Fast, isolated unit test.\"\"\"
    assert 1 + 1 == 2

@pytest.mark.integration
def test_database_integration():
    \"\"\"Integration test with database.\"\"\"
    ...

@pytest.mark.slow
def test_slow_operation():
    \"\"\"Test that takes >1 second.\"\"\"
    ...
\`\`\`

### Async Tests
\`\`\`python
import pytest

@pytest.mark.asyncio
async def test_async_endpoint(test_client):
    \"\"\"Test async endpoint.\"\"\"
    response = await test_client.get("/api/async-endpoint")
    assert response.status_code == 200
\`\`\`

## Troubleshooting

### Tests Not Discovered
- Check filename starts with `test_` or ends with `_test.py`
- Check function name starts with `test_`
- Check test class name starts with `Test`

### Import Errors
- Ensure virtual environment is activated
- Run `pip install -r backend/requirements.txt`
- Check PYTHONPATH includes project root

### Coverage Not Working
- Ensure pytest-cov installed: `pip install pytest-cov`
- Check pyproject.toml has [tool.coverage.run] section
- Verify source paths are correct

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
\`\`\`
```

---

## Success Criteria Checklist

### Pre-Implementation Checks

- [x] Story 1.1 completed (project structure exists)
- [x] Story 1.2 completed (backend/tests/test_main.py with 9 tests exists)
- [x] Story 1.5 completed (CI runs pytest with coverage)
- [x] pytest.ini and pyproject.toml exist (choose pyproject.toml)
- [x] pytest, pytest-cov, pytest-asyncio installed in requirements.txt

### Implementation Checklist

**Task 1: Consolidate Pytest Configuration**
- [ ] Remove pytest.ini file
- [ ] Verify pyproject.toml has complete [tool.pytest.ini_options]
- [ ] Run `pytest --help` and verify markers shown
- [ ] Run `pytest --markers` and verify unit, integration, e2e, slow listed

**Task 2: Create Reusable Test Fixtures**
- [ ] Create/update backend/tests/conftest.py
- [ ] Implement test_client fixture with TestClient and yield
- [ ] Implement temp_data_dir fixture with tempfile.TemporaryDirectory
- [ ] Implement mock_ai_response fixture returning dict
- [ ] Implement test_config_override fixture returning dict
- [ ] Add docstrings to all fixtures with usage examples
- [ ] Test fixtures work: `pytest backend/tests/test_main.py -v`

**Task 3: Enhance Test Coverage for Backend**
- [ ] Add test_invalid_endpoint_404 to test_main.py
- [ ] Add test_invalid_endpoint_json_error to test_main.py
- [ ] Add test_cors_preflight_options to test_main.py
- [ ] Add test_api_docs_accessible to test_main.py
- [ ] Add test_api_redoc_accessible to test_main.py
- [ ] Refactor existing 9 tests to use test_client fixture
- [ ] Add @pytest.mark.unit to all test methods
- [ ] Run `pytest backend/tests/test_main.py -v` and verify 14+ passing

**Task 4: Configure Coverage Reporting**
- [ ] Verify [tool.coverage.run] exists in pyproject.toml
- [ ] Verify source, omit, branch settings correct
- [ ] Verify [tool.coverage.report] exists in pyproject.toml
- [ ] Run `pytest --cov --cov-report=html`
- [ ] Verify htmlcov/ directory created
- [ ] Open htmlcov/index.html in browser

**Task 5: Achieve Coverage Threshold**
- [ ] Run `pytest --cov --cov-report=term-missing`
- [ ] Verify backend/main.py >70% coverage
- [ ] Verify backend/config/settings.py >70% coverage
- [ ] Add `# pragma: no cover` to untestable lines
- [ ] Document intentionally uncovered code in Dev Notes

**Task 6: Create Test Documentation**
- [ ] Create backend/tests/README.md
- [ ] Add "Running Tests" section
- [ ] Add "Using Fixtures" section with examples
- [ ] Add "Coverage Interpretation" section
- [ ] Add "Writing New Tests" section with conventions
- [ ] Add "Troubleshooting" section

**Task 7: Validate End-to-End**
- [ ] Run `pytest` from project root
- [ ] Verify 14+ tests discovered and passing
- [ ] Verify execution <5 seconds
- [ ] Run `pytest -v` for verbose output
- [ ] Run `pytest -m unit` for marker filtering
- [ ] Run `pytest --cov --cov-report=html`
- [ ] Push and verify CI runs tests successfully

---

## Next Steps After Story 1.6

### Immediate Next Story: 1.7 (Development Environment Documentation)

**What Story 1.7 Will Build:**
- Comprehensive README.md sections
- Installation instructions
- Development workflow documentation
- Contributing guidelines
- Troubleshooting section

**How Story 1.6 Enables 1.7:**
- Test documentation provides testing instructions for README
- Coverage metrics demonstrate code quality
- Fixtures show testing best practices

**Integration with Story 1.7:**
- README.md will reference backend/tests/README.md for detailed testing info
- Developer setup will include running tests
- CI status badges already show test results

### Future Testing Expansion

**Epic 2 (Data Management) Will Add:**
- Tests for UserDataManager (file I/O, encryption)
- Tests for resume parser (PDF/DOCX parsing)
- Tests for data validation (Pydantic models)
- Fixture: `mock_user_profile` for user data tests

**Epic 3 (AI Providers) Will Add:**
- Tests for AI provider implementations
- Tests for response generation
- Tests for batch processing
- Fixtures: `mock_openai_client`, `mock_anthropic_client`

**Epic 6 (GUI Dashboard) Will Add:**
- GUI tests with PyQt5 (gui/tests/)
- Tests for Qt widgets and windows
- Tests for backend communication
- Fixtures: `qt_app`, `main_window`

---

**Context Generated:** 2025-11-29  
**Ready for Implementation:** Yes  
**Next Step:** Run `*dev-story` to implement Story 1.6
