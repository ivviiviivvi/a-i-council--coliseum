
import pytest
from fastapi.testclient import TestClient
from backend.main import app
import os

client = TestClient(app)

def test_cors_configuration():
    """
    Test that CORS is correctly configured.
    """
    # Test allowed origin
    headers_allowed = {
        "Origin": "http://localhost:3000",
    }
    response_allowed = client.get("/health", headers=headers_allowed)
    assert response_allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert response_allowed.headers.get("access-control-allow-credentials") == "true"

    # Test disallowed origin
    headers_disallowed = {
        "Origin": "http://evil-site.com",
    }
    response_disallowed = client.get("/health", headers=headers_disallowed)

    # In FastAPI CORSMiddleware, if origin is not allowed, the header is omitted
    allow_origin = response_disallowed.headers.get("access-control-allow-origin")

    assert allow_origin != "http://evil-site.com"
    assert allow_origin != "*"
