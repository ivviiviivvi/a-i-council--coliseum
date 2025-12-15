import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.ai_agents.base_agent import AgentRole

client = TestClient(app)

def test_create_agent_success():
    # This test expects 200 now
    response = client.post("/api/agents/", json={"role": "moderator", "config": {}})
    assert response.status_code == 200
    data = response.json()
    assert "agent_id" in data
    assert data["role"] == "moderator"
    assert data["is_active"] == True

    agent_id = data["agent_id"]

    # Test Get Agent
    response = client.get(f"/api/agents/{agent_id}")
    assert response.status_code == 200
    assert response.json()["agent_id"] == agent_id

    # Test List Agents
    response = client.get("/api/agents/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # Test Deactivate
    response = client.post(f"/api/agents/{agent_id}/deactivate")
    assert response.status_code == 200

    # Verify Deactivated
    response = client.get(f"/api/agents/{agent_id}")
    assert response.json()["is_active"] == False

    # Test Activate
    response = client.post(f"/api/agents/{agent_id}/activate")
    assert response.status_code == 200

    # Verify Activated
    response = client.get(f"/api/agents/{agent_id}")
    assert response.json()["is_active"] == True

    # Test Delete
    response = client.delete(f"/api/agents/{agent_id}")
    assert response.status_code == 200

    # Verify Deleted
    response = client.get(f"/api/agents/{agent_id}")
    assert response.status_code == 404
