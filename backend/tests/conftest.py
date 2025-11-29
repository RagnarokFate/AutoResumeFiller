"""Pytest fixtures for backend tests.

This module provides reusable test fixtures for backend unit and integration tests.
All fixtures are automatically available to all test files in backend/tests/.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Generator
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Provide FastAPI test client for all backend tests.

    Yields:
        TestClient: FastAPI test client instance with proper lifecycle management

    Example:
        def test_health_check(test_client):
            response = test_client.get("/api/status")
            assert response.status_code == 200
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture
def temp_data_dir() -> Generator[Path, None, None]:
    """Provide temporary directory for data tests.

    Creates a temporary directory that is automatically cleaned up after the test.
    Useful for testing file operations without polluting the workspace.

    Yields:
        Path: Temporary directory path (auto-cleaned after test)

    Example:
        def test_file_operations(temp_data_dir):
            test_file = temp_data_dir / "test.txt"
            test_file.write_text("content")
            assert test_file.exists()
            # Directory automatically cleaned up after test
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_ai_response() -> dict:
    """Provide mock AI provider response for testing.

    Returns a realistic mock response from an AI provider, useful for testing
    AI integration code without making actual API calls.

    Returns:
        dict: Mock AI response with response, confidence, provider fields

    Example:
        def test_ai_processing(mock_ai_response):
            assert mock_ai_response["confidence"] > 0.8
            assert mock_ai_response["provider"] == "mock"
    """
    return {
        "response": "Sample AI generated text for testing purposes",
        "confidence": 0.92,
        "provider": "mock",
        "model": "test-model-v1",
        "tokens_used": 50,
        "completion_time_ms": 120,
    }


@pytest.fixture
def test_config_override() -> dict:
    """Provide test configuration overrides.

    Returns a dictionary of configuration settings suitable for testing.
    Use this to override default configuration values in tests without
    modifying actual configuration files.

    Returns:
        dict: Configuration overrides for testing

    Example:
        def test_with_config(test_config_override):
            assert test_config_override["API_PORT"] == 8765
            assert test_config_override["LOG_LEVEL"] == "DEBUG"
    """
    return {
        "API_HOST": "127.0.0.1",
        "API_PORT": 8765,
        "LOG_LEVEL": "DEBUG",
        "CORS_ORIGINS": ["chrome-extension://*"],
        "DATA_DIR": "./test_data",
        "ENABLE_ANALYTICS": False,
    }
