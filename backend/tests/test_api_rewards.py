import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.api.dependencies import get_reward_distribution
from backend.blockchain.rewards import RewardDistribution, RewardType

client = TestClient(app)

# Fixture to provide a clean RewardDistribution instance for each test
@pytest.fixture
def reward_system():
    return RewardDistribution()

@pytest.fixture
def override_dependency(reward_system):
    app.dependency_overrides[get_reward_distribution] = lambda: reward_system
    yield
    app.dependency_overrides = {}

def test_get_pending_rewards_empty(override_dependency):
    response = client.get("/api/blockchain/rewards/pending?address=test_user_1")
    assert response.status_code == 200
    assert response.json() == {"pending_rewards": 0.0}

def test_claim_rewards_empty(override_dependency):
    response = client.post(
        "/api/blockchain/rewards/claim",
        json={"user_address": "test_user_1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "claimed"
    assert data["amount"] == 0.0
    assert data["claimed_count"] == 0

def test_claim_existing_rewards(override_dependency, reward_system):
    # Setup: Create a reward claim
    user_address = "test_user_with_rewards"
    reward_amount = 100.0
    reward_system.create_reward_claim(
        user_address=user_address,
        reward_type=RewardType.VOTING,
        amount=reward_amount,
        description="Test Reward"
    )

    # Check pending
    response = client.get(f"/api/blockchain/rewards/pending?address={user_address}")
    assert response.status_code == 200
    assert response.json() == {"pending_rewards": reward_amount}

    # Claim
    response = client.post(
        "/api/blockchain/rewards/claim",
        json={"user_address": user_address}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "claimed"
    assert data["amount"] == reward_amount
    assert data["claimed_count"] == 1

    # Check pending again (should be 0)
    response = client.get(f"/api/blockchain/rewards/pending?address={user_address}")
    assert response.status_code == 200
    assert response.json() == {"pending_rewards": 0.0}

    # Claim again (should be 0)
    response = client.post(
        "/api/blockchain/rewards/claim",
        json={"user_address": user_address}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 0.0
