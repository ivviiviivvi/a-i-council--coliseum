"""
Ethereum Contract Manager

Manages interactions with Ethereum smart contracts.
"""

import os
import json
import logging
from typing import Optional, Union

from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.contract import AsyncContract

# Configure logging
logger = logging.getLogger(__name__)

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_from", "type": "address"},
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "transferFrom",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

class EthereumContractManager:
    """
    Manager for Ethereum smart contract interactions
    Handles cross-chain functionality and Ethereum-based features
    """
    
    def __init__(self, rpc_url: str, contract_address: str):
        self.rpc_url = rpc_url
        self.contract_address = contract_address
        self.w3: Optional[AsyncWeb3] = None
        self.contract: Optional[AsyncContract] = None
        self.private_key = os.getenv("ETHEREUM_PRIVATE_KEY")
        self.account = None
        self._decimals: Optional[int] = None

        if self.private_key:
            try:
                # We need to use Account from eth_account, but web3 exposes it too
                from eth_account import Account
                self.account = Account.from_key(self.private_key)
            except Exception as e:
                logger.error(f"Failed to load private key: {e}")

    async def initialize_contract(self) -> bool:
        """Initialize contract connection"""
        try:
            self.w3 = AsyncWeb3(AsyncHTTPProvider(self.rpc_url))

            # Check connection
            if not await self.w3.is_connected():
                logger.error("Failed to connect to Ethereum node")
                return False

            # Initialize contract
            self.contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.contract_address),
                abi=ERC20_ABI
            )

            # Fetch decimals
            try:
                self._decimals = await self.contract.functions.decimals().call()
            except Exception as e:
                logger.warning(f"Could not fetch decimals, defaulting to 18: {e}")
                self._decimals = 18

            logger.info("Ethereum contract initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Ethereum contract: {e}")
            return False
    
    async def get_token_balance(self, address: str) -> float:
        """Get ERC-20 token balance"""
        if not self.contract:
            if not await self.initialize_contract():
                return 0.0

        try:
            checksum_address = self.w3.to_checksum_address(address)
            balance_wei = await self.contract.functions.balanceOf(checksum_address).call()
            return float(balance_wei) / (10 ** (self._decimals or 18))
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0.0
    
    async def transfer_tokens(
        self,
        from_address: str,
        to_address: str,
        amount: float
    ) -> str:
        """
        Transfer tokens.

        If from_address matches the configured private key, uses 'transfer'.
        If from_address is different, attempts 'transferFrom' (requires allowance).
        
        Returns:
            Transaction hash
        """
        if not self.contract:
            if not await self.initialize_contract():
                raise ConnectionError("Contract not initialized")

        if not self.account:
            raise ValueError("Private key not configured")

        try:
            to_checksum = self.w3.to_checksum_address(to_address)
            from_checksum = self.w3.to_checksum_address(from_address)
            amount_wei = int(amount * (10 ** (self._decimals or 18)))

            # Determine if we are the sender or if we are spending on behalf of someone
            if from_checksum == self.account.address:
                # Direct transfer
                func_call = self.contract.functions.transfer(to_checksum, amount_wei)
            else:
                # Transfer From (we are the spender)
                func_call = self.contract.functions.transferFrom(from_checksum, to_checksum, amount_wei)

            # Build transaction
            # We need nonce, gas price, etc.
            nonce = await self.w3.eth.get_transaction_count(self.account.address)
            gas_price = await self.w3.eth.gas_price

            # Estimate gas?
            try:
                gas_estimate = await func_call.estimate_gas({'from': self.account.address})
            except Exception:
                gas_estimate = 100000  # Fallback

            tx_data = func_call.build_transaction({
                'chainId': await self.w3.eth.chain_id,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': nonce,
            })

            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.private_key)

            # Send transaction
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            return self.w3.to_hex(tx_hash)

        except Exception as e:
            logger.error(f"Error transferring tokens: {e}")
            raise e
    
    async def approve_tokens(
        self,
        owner_address: str,
        spender_address: str,
        amount: float
    ) -> str:
        """
        Approve token spending.
        
        Note: This can only be called if we hold the keys for 'owner_address'.
        If owner_address != self.account.address, we cannot sign this.
        """
        if not self.contract:
            if not await self.initialize_contract():
                raise ConnectionError("Contract not initialized")

        if not self.account:
            raise ValueError("Private key not configured")

        owner_checksum = self.w3.to_checksum_address(owner_address)

        if owner_checksum != self.account.address:
            raise ValueError("Cannot sign approval for address other than configured account")

        try:
            spender_checksum = self.w3.to_checksum_address(spender_address)
            amount_wei = int(amount * (10 ** (self._decimals or 18)))

            func_call = self.contract.functions.approve(spender_checksum, amount_wei)

            nonce = await self.w3.eth.get_transaction_count(self.account.address)
            gas_price = await self.w3.eth.gas_price

            try:
                gas_estimate = await func_call.estimate_gas({'from': self.account.address})
            except Exception:
                gas_estimate = 100000

            tx_data = func_call.build_transaction({
                'chainId': await self.w3.eth.chain_id,
                'gas': gas_estimate,
                'gasPrice': gas_price,
                'nonce': nonce,
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx_data, self.private_key)
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            return self.w3.to_hex(tx_hash)

        except Exception as e:
            logger.error(f"Error approving tokens: {e}")
            raise e
    
    async def bridge_to_solana(
        self,
        amount: float,
        solana_address: str
    ) -> str:
        """
        Bridge tokens from Ethereum to Solana
        
        Args:
            amount: Amount to bridge
            solana_address: Destination Solana address
            
        Returns:
            Transaction hash
        """
        # Placeholder for actual bridge transaction
        # This typically involves:
        # 1. Approve bridge contract
        # 2. Call bridge/lock function on bridge contract
        return "0x" + "0" * 64
