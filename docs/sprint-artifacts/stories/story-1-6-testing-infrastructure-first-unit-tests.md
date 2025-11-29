# Story 1.6: Testing Infrastructure & First Unit Tests

**Epic:** Epic 1 - Foundation & Core Infrastructure  
**Story ID:** 1.6  
**Title:** Testing Infrastructure & First Unit Tests  
**Status:** Drafted  
**Created:** 2025-11-29  
**Story Points:** 2  
**Priority:** High  
**Assigned To:** DEV Agent  

---

## Story Description

### User Story

**As a** developer maintaining AutoResumeFiller  
**I want** comprehensive pytest infrastructure with fixtures and coverage reporting  
**So that** I can write maintainable tests and ensure code quality throughout development

### Context

Stories 1.1-1.5 established the project foundation with backend, extension, GUI, and CI/CD pipeline. Story 1.2 created 9 basic unit tests for the health check endpoint. Story 1.6 completes the testing infrastructure by:

1. **Organizing pytest configuration** - Consolidate pytest.ini and pyproject.toml configuration
2. **Creating reusable fixtures** - Shared test setup in conftest.py for cleaner test code
3. **Expanding test coverage** - Add tests for error cases, edge conditions, and 404 responses
4. **Establishing coverage standards** - Achieve >70% coverage baseline for tested modules
5. **Documenting testing patterns** - Set examples for future test development

This story establishes the testing foundation that will support Epic 2 (data management), Epic 3 (AI providers), and all subsequent feature development. The pytest fixtures created here (test client, mock providers, temp directories) will be reused across 50+ future tests.

Key integration point: Story 1.5's CI workflow automatically runs these tests on every push, ensuring continuous quality validation.

### Dependencies

- ✅ **Story 1.1:** Project Initialization & Repository Setup (COMPLETED)
  - pytest.ini and pyproject.toml already exist
  - backend/tests/ directory structure in place

- ✅ **Story 1.2:** Python Backend Scaffolding (COMPLETED)
  - backend/main.py with FastAPI app
  - backend/tests/test_main.py with 9 basic tests
  - Health check endpoint to test

- ✅ **Story 1.5:** CI/CD Pipeline with GitHub Actions (COMPLETED)
  - CI workflow runs pytest with coverage reporting
  - Coverage baseline established (14.45%)

- 📦 **External Dependencies:**
  - pytest>=7.4.0 (already installed)
  - pytest-asyncio>=0.21.0 (already installed)
  - pytest-cov>=4.1.0 (already installed)

### Technical Approach

**Implementation Strategy:**

1. **Consolidate pytest configuration** (choose pytest.ini OR pyproject.toml, not both):
   ```toml
   [tool.pytest.ini_options]
   testpaths = ["backend/tests", "gui/tests", "tests"]
   python_files = ["test_*.py", "*_test.py"]
   python_functions = ["test_*"]
   addopts = """
       -v
       --tb=short
       --strict-markers
       --cov=backend
       --cov=gui
       --cov-report=html
       --cov-report=term-missing
   """
   markers = [
       "unit: Unit tests (fast, isolated)",
       "integration: Integration tests (moderate speed)",
       "e2e: End-to-end tests (slow, full system)",
       "slow: Tests that take >1s to run",
   ]
   ```

2. **Create `backend/tests/conftest.py`** with reusable fixtures:
   ```python
   import pytest
   from fastapi.testclient import TestClient
   from pathlib import Path
   import tempfile
   
   from backend.main import app
   
   @pytest.fixture
   def test_client():
       """Provide FastAPI test client for all backend tests."""
       with TestClient(app) as client:
           yield client
   
   @pytest.fixture
   def temp_data_dir():
       """Provide temporary directory for data tests."""
       with tempfile.TemporaryDirectory() as tmpdir:
           yield Path(tmpdir)
   
   @pytest.fixture
   def mock_ai_response():
       """Provide mock AI provider responses for testing."""
       return {
           "response": "Sample AI generated text",
           "confidence": 0.9,
           "provider": "mock"
       }
   
   @pytest.fixture
   def test_config_override():
       """Override config settings for testing."""
       return {
           "API_HOST": "127.0.0.1",
           "API_PORT": 8765,
           "LOG_LEVEL": "DEBUG"
       }
   ```

3. **Enhance `backend/tests/test_main.py`** with additional test cases:
   - Test for 404 on invalid endpoints (`GET /api/nonexistent`)
   - Test for OPTIONS preflight requests (CORS)
   - Test for malformed requests (if applicable)
   - Test for API documentation endpoints (`GET /docs`, `GET /redoc`)
   - Convert existing tests to use conftest fixtures

4. **Configure coverage reporting** in pyproject.toml:
   ```toml
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
       "if __name__ == .__main__.:",
       "if TYPE_CHECKING:",
       "@(abc\\.)?abstractmethod",
   ]
   ```

5. **Create test documentation** in backend/tests/README.md:
   - How to run tests (`pytest`, `pytest -v`, `pytest --cov`)
   - How to run specific tests (`pytest backend/tests/test_main.py::test_name`)
   - How to use fixtures
   - Coverage interpretation guidelines

**Key Design Decisions:**

- **Single pytest config location:** Use pyproject.toml (modern standard), remove pytest.ini to avoid duplication
- **Fixture-based testing:** All tests use conftest fixtures for consistency and reusability
- **Coverage threshold:** 70% minimum for tested modules (will increase as codebase grows)
- **Test markers:** Categorize tests by type (unit/integration/e2e) and speed (slow)
- **HTML coverage reports:** Generate HTML reports for detailed line-by-line coverage inspection
- **Branch coverage enabled:** Detect untested conditional branches (if/else statements)

---

## Acceptance Criteria

### AC1: Pytest Configuration Consolidated

**Given** the project with pytest.ini and pyproject.toml  
**When** consolidating pytest configuration  
**Then** pyproject.toml contains complete [tool.pytest.ini_options] section  
**And** pytest.ini is removed to avoid duplication  
**And** configuration includes:
- testpaths = ["backend/tests", "gui/tests", "tests"]
- python_files = ["test_*.py", "*_test.py"]
- python_functions = ["test_*"]
- addopts with -v, --tb=short, --strict-markers, --cov flags
- markers for unit, integration, e2e, slow tests

**And** running `pytest --help` shows custom markers in help text

### AC2: Reusable Test Fixtures Created

**Given** the need for shared test setup  
**When** creating backend/tests/conftest.py  
**Then** it contains pytest fixtures:

1. **test_client:** FastAPI TestClient instance
   ```python
   @pytest.fixture
   def test_client():
       with TestClient(app) as client:
           yield client
   ```

2. **temp_data_dir:** Temporary directory for file tests
   ```python
   @pytest.fixture
   def temp_data_dir():
       with tempfile.TemporaryDirectory() as tmpdir:
           yield Path(tmpdir)
   ```

3. **mock_ai_response:** Mock AI provider response
   ```python
   @pytest.fixture
   def mock_ai_response():
       return {
           "response": "Sample AI text",
           "confidence": 0.9,
           "provider": "mock"
       }
   ```

4. **test_config_override:** Config overrides for testing
   ```python
   @pytest.fixture
   def test_config_override():
       return {"API_HOST": "127.0.0.1", "API_PORT": 8765}
   ```

**And** fixtures are documented with docstrings

**And** all fixtures use proper cleanup (context managers, yield pattern)

### AC3: Enhanced Test Coverage for Backend

**Given** the existing 9 tests in backend/tests/test_main.py  
**When** enhancing the test suite  
**Then** backend/tests/test_main.py contains additional tests:

1. **test_invalid_endpoint_404:** Verify GET /api/nonexistent returns 404
2. **test_invalid_endpoint_json_error:** Verify 404 response is JSON with error details
3. **test_cors_preflight_options:** Verify OPTIONS requests for CORS preflight
4. **test_api_docs_accessible:** Verify GET /docs returns 200 (Swagger UI)
5. **test_api_redoc_accessible:** Verify GET /redoc returns 200 (ReDoc)

**And** existing tests are refactored to use test_client fixture from conftest:
```python
def test_health_check_success(test_client):
    """Test health check endpoint returns 200 OK."""
    response = test_client.get("/api/status")
    assert response.status_code == 200
```

**And** all tests pass with `pytest backend/tests/test_main.py -v`

**And** test output shows 14+ passing tests (9 existing + 5 new)

### AC4: Coverage Reporting Configured

**Given** pytest-cov installed and configured  
**When** running tests with coverage  
**Then** pyproject.toml contains [tool.coverage.run] section:
- source = ["backend", "gui"]
- omit = ["*/tests/*", "*/test_*.py", "*/__init__.py", "*/conftest.py"]
- branch = true (branch coverage enabled)

**And** pyproject.toml contains [tool.coverage.report] section:
- precision = 2
- show_missing = true
- exclude_lines for pragma comments and special methods

**And** running `pytest --cov --cov-report=html` generates:
- htmlcov/ directory with detailed coverage report
- htmlcov/index.html accessible in browser

**And** running `pytest --cov --cov-report=term` displays:
- Module-by-module coverage percentages
- Overall coverage summary
- Missing lines highlighted (with --cov-report=term-missing)

**Example Output:**
```
---------- coverage: platform windows, python 3.11.x -----------
Name                      Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------
backend\__init__.py           0      0      0      0   100%
backend\main.py              45      3      8      1    91%   23, 67-68
backend\config\settings.py   15      0      2      0   100%
---------------------------------------------------------------------
TOTAL                        60      3     10      1    93%
```

### AC5: Coverage Threshold Achieved

**Given** the enhanced test suite  
**When** running full test suite with coverage  
**Then** backend/main.py shows >70% coverage  
**And** backend/config/settings.py shows >70% coverage  
**And** overall backend coverage shows >70%  
**And** uncovered lines are identified in report:
- Lines that are difficult to test (e.g., if __name__ == "__main__")
- Lines excluded via pragma comments
- Lines covered in integration tests (not unit tests)

**And** coverage report saved to htmlcov/ for detailed inspection

**And** CI workflow (from Story 1.5) reports coverage on every push

### AC6: Test Documentation Created

**Given** the complete testing infrastructure  
**When** creating test documentation  
**Then** backend/tests/README.md exists with sections:

1. **Running Tests:**
   ```bash
   # Run all backend tests
   pytest backend/tests/ -v
   
   # Run with coverage
   pytest backend/tests/ --cov --cov-report=html
   
   # Run specific test
   pytest backend/tests/test_main.py::test_health_check_success
   
   # Run tests by marker
   pytest -m unit
   ```

2. **Using Fixtures:**
   - How to use test_client fixture
   - How to create custom fixtures
   - Fixture scope (function, class, module, session)

3. **Coverage Interpretation:**
   - How to read coverage report
   - What's a good coverage target (70%+ for tested modules)
   - When to add pragma: no cover comments

4. **Writing New Tests:**
   - Test naming conventions (test_*, Test*)
   - File organization (test_*.py)
   - Using markers (@pytest.mark.unit)
   - Async test patterns (pytest-asyncio)

**And** documentation includes examples and best practices

### AC7: Test Infrastructure Validated End-to-End

**Given** the complete testing infrastructure  
**When** validating end-to-end functionality  
**Then** running `pytest` from project root:
- Discovers all tests in backend/tests/, gui/tests/, tests/
- Executes 14+ tests successfully
- Generates coverage report
- Completes in <5 seconds (fast unit tests)

**And** running `pytest -v` shows verbose output with:
- Individual test names and status (PASSED/FAILED)
- Test execution time per test
- Final summary with test count

**And** running `pytest -m unit` runs only unit tests:
- Excludes integration and e2e tests
- Faster execution for quick validation

**And** running `pytest --cov --cov-report=html` generates:
- HTML coverage report in htmlcov/
- Can open htmlcov/index.html in browser

**And** CI workflow (Story 1.5) automatically runs pytest on every push

---

## Tasks / Subtasks

### Task 1: Consolidate Pytest Configuration (AC1)

- [x] Review existing pytest.ini and pyproject.toml configurations
- [ ] Choose pyproject.toml as single source of truth (modern standard)
- [ ] Ensure pyproject.toml [tool.pytest.ini_options] has complete config
- [ ] Verify markers defined: unit, integration, e2e, slow
- [ ] Remove pytest.ini to avoid duplication
- [ ] Test with `pytest --help` to verify markers show up
- [ ] Test with `pytest --markers` to list all markers
- [ ] Commit configuration changes

### Task 2: Create Reusable Test Fixtures (AC2)

- [ ] Create backend/tests/conftest.py if not exists
- [ ] Implement test_client fixture with FastAPI TestClient
- [ ] Implement temp_data_dir fixture with tempfile.TemporaryDirectory
- [ ] Implement mock_ai_response fixture with sample AI response dict
- [ ] Implement test_config_override fixture with test config
- [ ] Add docstrings to all fixtures explaining purpose and usage
- [ ] Verify fixtures use proper cleanup (yield, context managers)
- [ ] Test fixtures work with simple test case
- [ ] Commit conftest.py

### Task 3: Enhance Test Coverage for Backend (AC3)

- [ ] Add test_invalid_endpoint_404 to test_main.py
- [ ] Add test_invalid_endpoint_json_error to test_main.py
- [ ] Add test_cors_preflight_options to test_main.py (if CORS supports OPTIONS)
- [ ] Add test_api_docs_accessible (GET /docs) to test_main.py
- [ ] Add test_api_redoc_accessible (GET /redoc) to test_main.py
- [ ] Refactor existing tests to use test_client fixture from conftest
- [ ] Add @pytest.mark.unit decorator to all unit tests
- [ ] Run `pytest backend/tests/test_main.py -v` to verify all tests pass
- [ ] Verify 14+ tests passing
- [ ] Commit enhanced test_main.py

### Task 4: Configure Coverage Reporting (AC4)

- [ ] Verify [tool.coverage.run] exists in pyproject.toml
- [ ] Verify source = ["backend", "gui"] configured
- [ ] Verify omit patterns for tests and __init__.py files
- [ ] Verify branch = true for branch coverage
- [ ] Verify [tool.coverage.report] exists in pyproject.toml
- [ ] Verify precision = 2 and show_missing = true
- [ ] Verify exclude_lines for pragma comments
- [ ] Run `pytest --cov --cov-report=html`
- [ ] Verify htmlcov/ directory generated
- [ ] Open htmlcov/index.html in browser to inspect coverage
- [ ] Run `pytest --cov --cov-report=term-missing`
- [ ] Verify terminal coverage output shows module percentages
- [ ] Commit coverage configuration changes (if any)

### Task 5: Achieve Coverage Threshold (AC5)

- [ ] Run full test suite with coverage: `pytest --cov --cov-report=term-missing`
- [ ] Verify backend/main.py >70% coverage
- [ ] Verify backend/config/settings.py >70% coverage
- [ ] Identify uncovered lines in coverage report
- [ ] Add tests for uncovered lines if reasonable (not __main__ blocks)
- [ ] Add `# pragma: no cover` comments for untestable lines
- [ ] Re-run coverage to verify threshold met
- [ ] Document any intentionally uncovered code in Dev Notes
- [ ] Save final coverage report to htmlcov/
- [ ] Verify CI workflow reports coverage

### Task 6: Create Test Documentation (AC6)

- [ ] Create backend/tests/README.md
- [ ] Add "Running Tests" section with pytest commands
- [ ] Add "Using Fixtures" section with fixture examples
- [ ] Add "Coverage Interpretation" section with coverage targets
- [ ] Add "Writing New Tests" section with conventions
- [ ] Include examples for each section
- [ ] Add links to pytest documentation
- [ ] Add troubleshooting section for common issues
- [ ] Review documentation for clarity and completeness
- [ ] Commit test documentation

### Task 7: Validate End-to-End (AC7)

- [ ] Run `pytest` from project root
- [ ] Verify all tests discovered and executed
- [ ] Verify 14+ tests passing
- [ ] Verify coverage report generated
- [ ] Verify execution completes in <5 seconds
- [ ] Run `pytest -v` to verify verbose output
- [ ] Run `pytest -m unit` to verify marker filtering
- [ ] Run `pytest --cov --cov-report=html` to generate HTML report
- [ ] Open htmlcov/index.html to verify detailed coverage
- [ ] Push changes and verify CI workflow runs tests
- [ ] Verify CI workflow reports coverage
- [ ] Mark story complete

---

## Dev Notes

### Architecture Alignment

**From Architecture Document (Section 7: Testing Strategy):**
- Unit tests with pytest and pytest-asyncio ✓
- Code coverage target: >80% (starting with >70% for MVP) ✓
- Coverage reporting with pytest-cov ✓
- Test organization: backend/tests/, gui/tests/, tests/integration/ ✓

**From Architecture Document (Section 7.5: Code Quality):**
- Testing is mandatory for all new features ✓
- pytest for all Python testing ✓
- pytest-asyncio for async FastAPI endpoints ✓

### Project Structure Notes

**Files to Create:**
```
backend/tests/conftest.py       # Pytest fixtures (NEW)
backend/tests/README.md         # Test documentation (NEW)
```

**Files to Modify:**
```
backend/tests/test_main.py      # Add 5 new tests, refactor to use fixtures
pyproject.toml                  # Verify/enhance coverage configuration
pytest.ini                      # Remove to avoid duplication with pyproject.toml
```

**No Conflicts:** Testing infrastructure files are independent, no conflicts with existing code.

### Learnings from Previous Story (Story 1.5)

**From Story 1.5 (CI/CD Pipeline) - Status: done**

**CI/CD Context:**
- pytest runs in CI with --cov=backend --cov=gui --cov-report=xml
- Coverage uploaded to codecov (optional, continue-on-error: true)
- All 3 jobs (test-backend, lint-backend, test-extension) must pass

**Current Coverage Baseline:**
- Story 1.5 established 14.45% coverage baseline with 9 tests
- Story 1.6 aims to increase to >70% for tested modules
- Coverage improvement demonstrates testing infrastructure value

**CI Integration:**
- Tests run automatically on every push/PR
- Coverage reports generated in CI
- Story 1.6 ensures tests are maintainable and reusable via fixtures

**Technical Debt from Story 1.5:**
- Coverage 14.45% below 70% target → Story 1.6 addresses this
- No pytest fixtures → Story 1.6 adds conftest.py
- No test documentation → Story 1.6 adds backend/tests/README.md

**Implications for Story 1.6:**
- Build on existing 9 tests in test_main.py
- Refactor tests to use fixtures (cleaner, more maintainable)
- Add error case tests (404, malformed requests)
- Document testing patterns for future stories

[Source: docs/sprint-artifacts/stories/story-1-5-ci-cd-pipeline-github-actions.md#Dev-Agent-Record]

### Testing Strategy

**From Architecture Document (Section 7: Testing Strategy):**
- Unit tests: 70%+ coverage for tested modules
- Integration tests: Epic 6+ (backend ↔ GUI, extension ↔ backend)
- E2E tests: Out of scope for Epic 1

**Current State (Story 1.6):**
- 9 existing unit tests in backend/tests/test_main.py (Story 1.2)
- Tests cover health check endpoint, CORS headers, root endpoint
- No fixtures yet (tests use TestClient(app) directly)
- Coverage 14.45% overall (Story 1.5 baseline)

**Story 1.6 Additions:**
- conftest.py with 4 reusable fixtures
- 5 new tests for error cases and API docs endpoints
- Consolidated pytest configuration
- Coverage reporting configuration
- Test documentation for future developers

**Future Enhancements (Out of Scope):**
- Integration tests with real AI providers (Epic 3)
- GUI tests with PyQt5 (Epic 6)
- Extension tests with browser automation (Epic 5)
- Performance tests (Epic 7)

### Pytest Fixtures Explained

**What are fixtures?**
- Reusable test setup/teardown code
- Defined in conftest.py (automatically discovered)
- Injected into tests via function parameters
- Support cleanup via yield pattern

**Example Usage:**
```python
# Without fixture (test_main.py currently):
def test_health_check():
    client = TestClient(app)
    response = client.get("/api/status")
    assert response.status_code == 200

# With fixture (after Story 1.6):
def test_health_check(test_client):  # test_client auto-injected
    response = test_client.get("/api/status")
    assert response.status_code == 200
```

**Benefits:**
- DRY (Don't Repeat Yourself) - setup code written once
- Cleaner test code - focus on test logic, not setup
- Consistent setup - all tests use same client configuration
- Easy mocking - fixtures can provide mock data/services

### Coverage Targets

**Module Coverage Targets:**
- backend/main.py: >70% (100% ideal for API endpoints)
- backend/config/settings.py: >80% (configuration critical)
- Future modules: >70% for new code

**Excluded from Coverage:**
- __init__.py files (usually empty)
- Test files themselves (test_*.py)
- Fixture files (conftest.py)
- Lines with `# pragma: no cover` comment

**Coverage Interpretation:**
- 70-80%: Good baseline for tested modules
- 80-90%: Excellent coverage
- 90-100%: Great, but diminishing returns (test the edge cases that matter)
- <70%: Add tests for critical paths

**Pragmatic Approach:**
- Focus on testing critical business logic
- Test error handling and edge cases
- Don't obsess over 100% (some code is hard/impossible to test)
- Use `# pragma: no cover` for untestable code (__main__ blocks, defensive programming)

### Security Considerations

**Testing Security:**
- No secrets in test code (use environment variables or fixtures)
- Mock external services (don't call real AI providers in tests)
- Temporary directories auto-cleaned up after tests
- Test data should not contain real user information

**Best Practices:**
- Use `tempfile.TemporaryDirectory()` for file tests
- Use mocks/fixtures for AI provider responses
- Isolate tests (no shared state between tests)
- Run tests in isolated environment (CI/local venv)

### Performance Considerations

**Test Execution Speed:**
- Unit tests should be fast (<100ms each)
- Total test suite <5 seconds for Epic 1
- Use markers to separate slow tests: @pytest.mark.slow
- Run fast tests frequently, slow tests in CI

**Optimization Strategies:**
- Use in-memory TestClient (no network I/O)
- Mock external services (no real API calls)
- Parallel execution with pytest-xdist (future)

### Future Enhancements (Out of Scope)

- ❌ Integration tests with database (Epic 2)
- ❌ Integration tests with AI providers (Epic 3)
- ❌ GUI tests with PyQt5 (Epic 6)
- ❌ Extension tests with browser automation (Epic 5)
- ❌ Performance/load tests (Epic 7)
- ❌ Security tests (Epic 7)
- ❌ Mutation testing for test quality (Future)

### References

- **Architecture Document:** `docs/architecture.md#Section-7-Testing-Strategy`
- **Epic 1 Specification:** `docs/epics.md#Epic-1-Story-1.6`
- **Previous Story:** `docs/sprint-artifacts/stories/story-1-5-ci-cd-pipeline-github-actions.md`
- **Story 1.2 Tests:** `backend/tests/test_main.py`
- **Pytest Documentation:** https://docs.pytest.org/
- **pytest-cov Documentation:** https://pytest-cov.readthedocs.io/

---

## Change Log

- **2025-11-29:** Story 1.6 drafted by SM Agent. Testing infrastructure completion with pytest fixtures, enhanced coverage, and test documentation. Prerequisites: Stories 1.1, 1.2, 1.5 complete. Ready for story context creation.

---

## Status

**Current Status:** Drafted  
**Previous Status:** Backlog  
**Date Updated:** 2025-11-29

---

## Context Reference

**Technical Context:** `docs/sprint-artifacts/stories/story-1-6-testing-infrastructure-first-unit-tests-CONTEXT.md` (to be created)
