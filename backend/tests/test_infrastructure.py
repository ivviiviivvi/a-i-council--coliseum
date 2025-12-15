import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from backend.cache import RedisCache, get_cache
from backend.blockchain.ethereum_contracts import EthereumContractManager

# Valid Ethereum Address for testing
VALID_ADDR = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

@pytest.mark.asyncio
async def test_redis_connection_failure():
    """Test Redis behavior when connection fails (mocked)"""
    with patch("redis.asyncio.from_url") as mock_redis:
        mock_redis.side_effect = Exception("Connection refused")

        cache = RedisCache()
        # Reset singleton state for test
        cache.redis = None

        await cache.initialize()
        assert cache.redis is None

        # Should handle graceful failure
        result = await cache.get("test")
        assert result is None

        success = await cache.set("test", "value")
        assert success is False

@pytest.mark.asyncio
async def test_ethereum_contract_mock():
    """Test Ethereum contract interactions with mocks"""
    with patch("backend.blockchain.ethereum_contracts.AsyncWeb3") as MockWeb3:
        # Setup mock
        mock_w3_instance = MagicMock()
        MockWeb3.return_value = mock_w3_instance
        # Mock AsyncHTTPProvider
        MockWeb3.AsyncHTTPProvider.return_value = MagicMock()

        mock_w3_instance.is_connected = AsyncMock(return_value=True)

        # Mock eth.contract
        mock_contract = MagicMock()
        mock_w3_instance.eth.contract.return_value = mock_contract

        # Mock balance function
        mock_function = MagicMock()
        mock_contract.functions.balanceOf.return_value = mock_function
        mock_function.call = AsyncMock(return_value=1000000000000000000) # 1 ETH in Wei

        manager = EthereumContractManager(contract_address=VALID_ADDR)
        connected = await manager.initialize_contract()
        assert connected is True

        balance = await manager.get_token_balance(VALID_ADDR)
        assert balance == 1.0

@pytest.mark.asyncio
async def test_ethereum_transfer_mock():
    """Test Ethereum token transfer mock"""
    with patch("backend.blockchain.ethereum_contracts.AsyncWeb3") as MockWeb3:
        mock_w3_instance = MagicMock()
        MockWeb3.return_value = mock_w3_instance
        MockWeb3.AsyncHTTPProvider.return_value = MagicMock()

        mock_contract = MagicMock()
        mock_w3_instance.eth.contract.return_value = mock_contract

        # Mock transfer function
        mock_function = MagicMock()
        mock_contract.functions.transfer.return_value = mock_function

        # Mock build_transaction (must be awaitable)
        mock_function.build_transaction = AsyncMock(return_value={"raw": "tx"})

        # Mock other web3 calls
        mock_w3_instance.eth.get_transaction_count = AsyncMock(return_value=1)

        # Fix: gas_price must be awaitable
        future_gas = asyncio.Future()
        future_gas.set_result(20000000000)
        mock_w3_instance.eth.gas_price = future_gas

        mock_w3_instance.eth.account.from_key.return_value = MagicMock(address=VALID_ADDR)
        mock_w3_instance.eth.account.sign_transaction.return_value = MagicMock(raw_transaction=b"signed")
        mock_w3_instance.eth.send_raw_transaction = AsyncMock(return_value=b"\xab\xcd")
        mock_w3_instance.to_hex.return_value = "0xabcd"

        manager = EthereumContractManager(contract_address=VALID_ADDR)

        tx_hash = await manager.transfer_tokens(
            VALID_ADDR, VALID_ADDR, 10.0, "0xPrivateKey"
        )

        assert tx_hash == "0xabcd"
