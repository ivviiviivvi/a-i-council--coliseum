import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from backend.blockchain.solana_contracts import SolanaContractManager
from solders.pubkey import Pubkey
from solders.keypair import Keypair

@pytest.fixture
def mock_solana_client():
    with patch("backend.blockchain.solana_contracts.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value = mock_client
        yield mock_client

@pytest.fixture
def manager(mock_solana_client):
    # Use a dummy program ID (must be valid base58)
    program_id = "11111111111111111111111111111111"
    return SolanaContractManager("http://localhost:8899", program_id)

@pytest.mark.asyncio
async def test_initialize_council_program_success(manager, mock_solana_client):
    # Mock is_connected
    mock_solana_client.is_connected.return_value = True

    # Mock get_account_info response
    mock_resp = MagicMock()
    mock_resp.value = MagicMock()
    mock_resp.value.executable = True
    mock_solana_client.get_account_info.return_value = mock_resp

    result = await manager.initialize_council_program()
    assert result is True
    mock_solana_client.is_connected.assert_called_once()
    mock_solana_client.get_account_info.assert_called_once()

@pytest.mark.asyncio
async def test_initialize_council_program_not_connected(manager, mock_solana_client):
    mock_solana_client.is_connected.return_value = False
    result = await manager.initialize_council_program()
    assert result is False

@pytest.mark.asyncio
async def test_initialize_council_program_not_found(manager, mock_solana_client):
    mock_solana_client.is_connected.return_value = True
    mock_resp = MagicMock()
    mock_resp.value = None
    mock_solana_client.get_account_info.return_value = mock_resp

    result = await manager.initialize_council_program()
    assert result is False

@pytest.mark.asyncio
async def test_initialize_council_program_not_executable(manager, mock_solana_client):
    mock_solana_client.is_connected.return_value = True
    mock_resp = MagicMock()
    mock_resp.value = MagicMock()
    mock_resp.value.executable = False
    mock_solana_client.get_account_info.return_value = mock_resp

    result = await manager.initialize_council_program()
    assert result is False

@pytest.mark.asyncio
async def test_create_council_account_pda(manager):
    # Test that create_council_account generates a PDA-like address string
    # when program_id is valid
    council_id = "test_council"
    address = await manager.create_council_account(council_id, 5)

    # Check that address is not the simple fallback format if program_id was valid
    # (Though in our mock manager, program_id is valid)
    assert address != f"council_{council_id}"
    # Verify it looks like a pubkey (base58 chars)
    # We can check by trying to parse it
    try:
        Pubkey.from_string(address)
    except ValueError:
        pytest.fail("Generated address is not a valid Pubkey string")
