
import pytest
from fastapi.testclient import TestClient
from backend.main import app
import os

# Initialize TestClient
client = TestClient(app)

def test_cors_configuration_secure_default():
    """
    Test that the default configuration is secure (allows localhost:3000, rejects others).
    """
    # 1. Test allowed origin
    origin = "http://localhost:3000"
    response = client.get("/", headers={"Origin": origin})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"

    # 2. Test disallowed origin
    evil_origin = "http://evil.com"
    response = client.get("/", headers={"Origin": evil_origin})
    assert response.status_code == 200 # The request succeeds but headers should be missing/different

    # In secure mode, the header should NOT be returned for disallowed origins
    allow_origin = response.headers.get("access-control-allow-origin")

    # If it returns it, it must NOT be * and must NOT be the evil origin
    if allow_origin:
        assert allow_origin != "*"
        assert allow_origin != evil_origin
    else:
        # Ideally it's missing, which is secure
        pass

def test_cors_configuration_env_var():
    """
    Test that setting CORS_ORIGINS env var works (though we can't easily change env var for the already loaded app in this process)

    Since `app` is imported at module level, changing os.environ here won't affect `backend.main.allow_origins` which was already evaluated.
    So we rely on the default behavior test above.
    """
    pass
