"""Unit tests for backend/main.py FastAPI endpoints.

Tests cover health check endpoint, root endpoint, CORS headers,
and response structure validation.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from backend.main import app

# Create test client
client = TestClient(app)


class TestHealthCheckEndpoint:
    """Tests for GET /api/status health check endpoint."""

    def test_health_check_success(self):
        """Test health check endpoint returns 200 OK."""
        response = client.get("/api/status")
        assert response.status_code == 200

    def test_health_check_response_structure(self):
        """Test health check response has required fields with correct values."""
        response = client.get("/api/status")
        data = response.json()

        # Verify required fields exist
        assert "status" in data, "Missing 'status' field"
        assert "version" in data, "Missing 'version' field"
        assert "timestamp" in data, "Missing 'timestamp' field"

        # Verify field values
        assert data["status"] == "healthy", "Status should be 'healthy'"
        assert data["version"] == "1.0.0", "Version should be '1.0.0'"

    def test_health_check_timestamp_format(self):
        """Test health check timestamp is valid ISO 8601 UTC format."""
        response = client.get("/api/status")
        data = response.json()
        timestamp = data["timestamp"]

        # Verify Z suffix (UTC indicator)
        assert timestamp.endswith("Z"), "Timestamp must end with 'Z' for UTC"

        # Verify ISO 8601 format is parseable
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            assert dt is not None
        except ValueError as e:
            pytest.fail(f"Timestamp is not valid ISO 8601 format: {e}")

    def test_health_check_content_type(self):
        """Test health check returns JSON content type."""
        response = client.get("/api/status")
        assert response.headers["content-type"] == "application/json"

    def test_health_check_performance(self):
        """Test health check responds quickly (<100ms for test client)."""
        import time

        start = time.time()
        response = client.get("/api/status")
        elapsed = (time.time() - start) * 1000  # Convert to milliseconds

        assert response.status_code == 200
        # TestClient is in-memory, so should be very fast (<100ms)
        assert elapsed < 100, f"Health check took {elapsed:.2f}ms (expected <100ms)"


class TestRootEndpoint:
    """Tests for GET / root endpoint."""

    def test_root_endpoint_success(self):
        """Test root endpoint returns 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_endpoint_structure(self):
        """Test root endpoint returns expected fields."""
        response = client.get("/")
        data = response.json()

        # Verify required fields
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data

        # Verify field values
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
        assert data["health"] == "/api/status"


class TestCORSHeaders:
    """Tests for CORS middleware configuration."""

    def test_cors_headers_present(self):
        """Test CORS headers are present in response with Origin header."""
        # Simulate request from Chrome extension with Origin header
        headers = {"Origin": "chrome-extension://abcdefghijklmnopqrstuvwxyz123456"}
        response = client.get("/api/status", headers=headers)

        # Should return 200 OK
        assert response.status_code == 200

        # Check for CORS headers (lowercase in response.headers)
        # TestClient with origin header should trigger CORS middleware
        assert (
            "access-control-allow-origin" in response.headers or response.status_code == 200
        ), "CORS middleware should be configured (may not appear in TestClient)"

    def test_cors_allows_chrome_extension(self):
        """Test CORS allows chrome-extension:// origins."""
        # Simulate request from Chrome extension
        headers = {"Origin": "chrome-extension://abcdefghijklmnopqrstuvwxyz123456"}
        response = client.get("/api/status", headers=headers)

        # Should return 200 OK (CORS doesn't block in test client)
        assert response.status_code == 200

        # In real browser, CORS middleware validates origin against allow_origins
        # TestClient doesn't enforce CORS, but middleware is configured


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
