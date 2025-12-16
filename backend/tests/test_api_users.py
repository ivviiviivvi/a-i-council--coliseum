import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.api.dependencies import get_gamification_system, get_leaderboard_system
from backend.voting.gamification import GamificationSystem, UserProgress
from backend.voting.leaderboard import LeaderboardSystem, LeaderboardType

client = TestClient(app)

# Fixture to mock the gamification system with some data
@pytest.fixture
def mock_systems():
    gamification_system = GamificationSystem()
    # Add some users
    gamification_system.add_points("user1", 110, "test") # Should be silver (>= 100)
    gamification_system.record_vote("user1")

    gamification_system.add_points("user2", 50, "test")

    leaderboard_system = LeaderboardSystem(gamification_system)
    # Generate leaderboards so they are cached/available
    leaderboard_system.generate_leaderboard(LeaderboardType.POINTS)

    return gamification_system, leaderboard_system

@pytest.fixture
def override_dependencies(mock_systems):
    gamification_system, leaderboard_system = mock_systems
    app.dependency_overrides[get_gamification_system] = lambda: gamification_system
    app.dependency_overrides[get_leaderboard_system] = lambda: leaderboard_system
    yield
    app.dependency_overrides = {}

def test_get_user_profile(override_dependencies):
    response = client.get("/api/users/user1/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user1"
    # 110 initial + 10 for vote = 120
    assert data["points"] == 120
    assert data["votes_cast"] == 1
    assert data["tier"] == "silver"

def test_get_user_stats(override_dependencies):
    response = client.get("/api/users/user1/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user1"
    assert "tier_benefits" in data
    assert "next_tier_progress" in data
    # 110 initial + 10 for vote = 120
    assert data["experience"] == 120

def test_get_leaderboard(override_dependencies):
    response = client.get("/api/users/leaderboard/points")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # user1 has 120, user2 has 50
    assert data[0]["user_id"] == "user1"
    assert data[0]["rank"] == 1
    assert data[1]["user_id"] == "user2"
    assert data[1]["rank"] == 2

def test_get_leaderboard_invalid_type(override_dependencies):
    response = client.get("/api/users/leaderboard/invalid_type")
    assert response.status_code == 400

def test_get_user_rank(override_dependencies):
    response = client.get("/api/users/user1/rank?leaderboard_type=points")
    assert response.status_code == 200
    data = response.json()
    assert data["rank"] == 1
    assert data["total_users"] == 2
    assert data["value"] == 120.0

def test_get_user_rank_unknown_user(override_dependencies):
    response = client.get("/api/users/unknown_user/rank?leaderboard_type=points")
    assert response.status_code == 200
    data = response.json()
    assert data["rank"] == 0
    assert data["total_users"] == 2
