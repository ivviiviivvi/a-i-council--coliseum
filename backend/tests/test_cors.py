import pytest
from fastapi.testclient import TestClient
from backend.main import app
import os

client = TestClient(app)

def test_cors_security_enforcement():
    """
    Verifies that the new configuration blocks unauthorized origins.
    This test is expected to PASS after the fix is applied.
    """

    headers = {
        "Origin": "http://evil.com",
        "Access-Control-Request-Method": "GET"
    }
    response = client.options("/", headers=headers)

    # If fixed, it should NOT return the allow-origin header for evil.com
    # Starlette with restrictive allowed_origins returns 400 Bad Request
    # for preflight requests from disallowed origins, OR just omits the headers.

    # We check that the response does NOT contain the Access-Control-Allow-Origin header matching the request.
    if "access-control-allow-origin" in response.headers:
         assert response.headers["access-control-allow-origin"] != "http://evil.com"
    else:
         # This is also valid behavior (just ignoring it)
         pass

def test_cors_allowed_origin():
    """
    Verifies that the allowed origin (localhost:3000) is still accepted.
    """
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "GET"
    }
    response = client.options("/", headers=headers)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
