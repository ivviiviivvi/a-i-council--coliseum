"""
Ethereum Contract Manager

Manages interactions with Ethereum smart contracts.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware
from eth_account import Account

# Configure logging
logger = logging.getLogger(__name__)

# Minimal ABI for ERC20 and Bridge functionality
# Assuming the contract has standard ERC20 methods and a bridgeToSolana method
MINIMAL_ABI = [
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
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "amount", "type": "uint256"},
            {"name": "solanaAddress", "type": "string"},
        ],
        "name": "bridgeToSolana",
        "outputs": [],
        "type": "function",
    },
]

class EthereumContractManager:
    """
    Manager for Ethereum smart contract interactions
    Handles cross-chain functionality and Ethereum-based features
    """
    
    def __init__(self, rpc_url: str, contract_address: str):
        self.rpc_url = rpc_url
        self.contract_address = contract_address
        self.w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.contract = None
        self._private_key = os.getenv("ETHEREUM_PRIVATE_KEY")
        if self._private_key:
            self.account = Account.from_key(self._private_key)
        else:
            self.account = None
            logger.warning("ETHEREUM_PRIVATE_KEY not set. Transaction signing will fail.")

    async def initialize_contract(self) -> bool:
        """Initialize contract connection"""
        try:
            if not await self.w3.is_connected():
                logger.error("Failed to connect to Ethereum node")
                return False

            self.contract = self.w3.eth.contract(
                address=AsyncWeb3.to_checksum_address(self.contract_address),
                abi=MINIMAL_ABI
            )
            return True
        except Exception as e:
            logger.error(f"Error initializing contract: {str(e)}")
            return False
    
    async def get_token_balance(self, address: str) -> float:
        """Get ERC-20 token balance"""
        if not self.contract:
            await self.initialize_contract()

        try:
            checksum_address = AsyncWeb3.to_checksum_address(address)
            balance_wei = await self.contract.functions.balanceOf(checksum_address).call()
            # Assuming 18 decimals
            return float(self.w3.from_wei(balance_wei, 'ether'))
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return 0.0

    async def _send_transaction(self, function_call) -> str:
        """Helper to sign and send a transaction"""
        try:
            if not self.account:
                raise ValueError("ETHEREUM_PRIVATE_KEY environment variable not set")

            from_address = self.account.address

            # Get nonce
            nonce = await self.w3.eth.get_transaction_count(from_address)

            # Build transaction
            try:
                gas_estimate = await function_call.estimate_gas({'from': from_address})
                gas_limit = int(gas_estimate * 1.2) # buffer
            except Exception:
                gas_limit = 300000 # Fallback

            tx = await function_call.build_transaction({
                'from': from_address,
                'nonce': nonce,
                'gas': gas_limit,
                'gasPrice': await self.w3.eth.gas_price
            })

            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self._private_key)

            # Send transaction
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            return self.w3.to_hex(tx_hash)
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            raise e
    
    async def transfer_tokens(
        self,
        from_address: str,
        to_address: str,
        amount: float
    ) -> str:
        """
        Transfer tokens.
        If from_address is the managed account, use 'transfer'.
        Otherwise use 'transferFrom' (requires prior approval).
        
        Returns:
            Transaction hash
        """
        if not self.contract:
            await self.initialize_contract()

        amount_wei = self.w3.to_wei(amount, 'ether')
        to_checksum = AsyncWeb3.to_checksum_address(to_address)

        if self.account and from_address.lower() == self.account.address.lower():
            # Direct transfer from managed wallet
            return await self._send_transaction(
                self.contract.functions.transfer(to_checksum, amount_wei)
            )
        else:
            # transferFrom (requires allowance)
            from_checksum = AsyncWeb3.to_checksum_address(from_address)
            return await self._send_transaction(
                self.contract.functions.transferFrom(from_checksum, to_checksum, amount_wei)
            )
    
    async def approve_tokens(
        self,
        owner_address: str,
        spender_address: str,
        amount: float
    ) -> str:
        """
        Approve token spending.
        Note: This only works if owner_address is the managed account,
        since we need the private key to sign the approval.
        
        Returns:
            Transaction hash
        """
        if not self.contract:
            await self.initialize_contract()

        if self.account and owner_address.lower() != self.account.address.lower():
             logger.error("Cannot approve tokens for an address we don't control.")
             raise ValueError("Cannot sign for owner_address provided")

        amount_wei = self.w3.to_wei(amount, 'ether')
        spender_checksum = AsyncWeb3.to_checksum_address(spender_address)

        return await self._send_transaction(
            self.contract.functions.approve(spender_checksum, amount_wei)
        )
    
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
        if not self.contract:
            await self.initialize_contract()

        # Convert amount to Wei (assuming 18 decimals)
        amount_wei = self.w3.to_wei(amount, 'ether')

        # Call bridgeToSolana(uint256 amount, string solanaAddress)
        return await self._send_transaction(
            self.contract.functions.bridgeToSolana(amount_wei, solana_address)
        )
