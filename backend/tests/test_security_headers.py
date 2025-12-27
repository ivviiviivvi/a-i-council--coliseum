import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

@pytest.mark.asyncio
async def test_security_headers_present():
    """
    Test that security headers are present in the response.
    Sentinel Check:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - Referrer-Policy: strict-origin-when-cross-origin
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")

        assert response.status_code == 200

        # Check for X-Content-Type-Options
        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"

        # Check for X-Frame-Options
        assert "x-frame-options" in response.headers
        assert response.headers["x-frame-options"] == "DENY"

        # Check for Referrer-Policy
        assert "referrer-policy" in response.headers
        assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
