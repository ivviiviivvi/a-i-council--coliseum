from fastapi.testclient import TestClient
from backend.main import app
import pytest
import os
from unittest.mock import patch

client = TestClient(app)

def test_cors_configuration_secure():
    """
    Verify that the configuration rejects untrusted origins.
    Note: The app is initialized with default CORS_ORIGINS="http://localhost:3000"
    """
    # Test allowed origin
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

    # Test disallowed origin
    response = client.options(
        "/",
        headers={
            "Origin": "http://evil-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    # If the origin is not allowed, CORSMiddleware does not add CORS headers.
    # The request then proceeds to the application.
    # Since there is no OPTIONS handler for "/", FastAPI returns 405 Method Not Allowed.
    # Use assert response.status_code != 200 or check headers.
    # In some setups/versions, it might return 400 if the preflight request is deemed invalid by the middleware (though standard behavior is fallthrough).
    # The important part is that we don't give the "Go Ahead" signal (Access-Control-Allow-Origin).

    if response.status_code == 200:
        assert "access-control-allow-origin" not in response.headers
    else:
        # If it returns error (400/405), that's also a secure outcome as the browser will reject it.
        assert True
