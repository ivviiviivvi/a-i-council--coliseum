import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.api.dependencies import get_solana_manager
from backend.blockchain.solana_contracts import SolanaContractManager

# Mock the dependency
mock_manager = AsyncMock(spec=SolanaContractManager)

def override_get_solana_manager():
    return mock_manager

app.dependency_overrides[get_solana_manager] = override_get_solana_manager

client = TestClient(app)

@pytest.mark.asyncio
async def test_stake_tokens():
    # Setup mock
    mock_manager.stake_tokens.return_value = True

    payload = {
        "user_address": "solana_addr_123",
        "amount": 100.0,
        "lock_period_days": 30
    }

    response = client.post("/api/blockchain/stake", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "status": "staked",
        "amount": 100.0,
        "lock_period_days": 30
    }

    # Verify manager was called correctly
    mock_manager.stake_tokens.assert_called_once_with(
        "solana_addr_123",
        100.0,
        30
    )

@pytest.mark.asyncio
async def test_stake_tokens_failure():
    # Setup mock to fail
    mock_manager.stake_tokens.return_value = False

    payload = {
        "user_address": "solana_addr_123",
        "amount": 100.0
    }

    response = client.post("/api/blockchain/stake", json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "Staking failed"}

@pytest.mark.asyncio
async def test_get_balance():
    mock_manager.get_wallet_balance.return_value = 500.0

    response = client.get("/api/blockchain/balance/solana_addr_123")

    assert response.status_code == 200
    assert response.json() == {
        "address": "solana_addr_123",
        "balance": 500.0
    }

    mock_manager.get_wallet_balance.assert_called_once_with("solana_addr_123")
