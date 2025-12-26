
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_security_headers():
    response = client.get("/health")
    assert response.status_code == 200

    # Check for X-Content-Type-Options
    assert "x-content-type-options" in response.headers
    assert response.headers["x-content-type-options"] == "nosniff"

    # Check for X-Frame-Options
    assert "x-frame-options" in response.headers
    assert response.headers["x-frame-options"] == "DENY" or response.headers["x-frame-options"] == "SAMEORIGIN"
