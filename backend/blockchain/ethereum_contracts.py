"""
Ethereum Contract Manager

Manages interactions with Ethereum smart contracts.
"""

from typing import Dict, Any, Optional
from web3 import Web3, AsyncWeb3
from web3.contract import AsyncContract
import json
import os

# Default to a local node if not set, but won't crash if unreachable for testing
ETH_RPC_URL = os.getenv("ETH_RPC_URL", "http://localhost:8545")

# ABI placeholders - in production these would be loaded from JSON files
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
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
    }
]

class EthereumContractManager:
    """
    Manager for Ethereum smart contract interactions
    Handles cross-chain functionality and Ethereum-based features
    """
    
    def __init__(self, rpc_url: str = ETH_RPC_URL, contract_address: Optional[str] = None):
        self.rpc_url = rpc_url
        self.contract_address = contract_address
        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))
    
    async def initialize_contract(self) -> bool:
        """Initialize contract connection"""
        return await self.w3.is_connected()
    
    async def get_token_balance(self, address: str, token_address: Optional[str] = None) -> float:
        """
        Get ERC-20 token balance.
        If token_address is provided, queries that token.
        Otherwise queries the default contract.
        """
        target_contract = token_address or self.contract_address
        if not target_contract:
            return 0.0

        try:
            checksum_address = Web3.to_checksum_address(target_contract)
            contract = self.w3.eth.contract(address=checksum_address, abi=ERC20_ABI)
            balance = await contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
            # Assuming 18 decimals by default for generic tokens
            return float(balance) / 10**18
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return 0.0
    
    async def transfer_tokens(
        self,
        from_address: str, # Not used in Web3 without private key, acting as 'sender' context
        to_address: str,
        amount: float,
        private_key: str  # Required for actual transaction
    ) -> str:
        """
        Transfer tokens
        
        Returns:
            Transaction hash
        """
        if not self.contract_address:
            raise ValueError("No contract address configured")

        try:
            account = self.w3.eth.account.from_key(private_key)
            checksum_contract = Web3.to_checksum_address(self.contract_address)
            contract = self.w3.eth.contract(address=checksum_contract, abi=ERC20_ABI)

            # Amount to Wei (assuming 18 decimals)
            amount_wei = int(amount * 10**18)

            # Build transaction
            tx = await contract.functions.transfer(
                Web3.to_checksum_address(to_address),
                amount_wei
            ).build_transaction({
                'from': account.address,
                'nonce': await self.w3.eth.get_transaction_count(account.address),
                'gas': 100000,
                'gasPrice': await self.w3.eth.gas_price
            })

            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            return self.w3.to_hex(tx_hash)

        except Exception as e:
            print(f"Error transferring tokens: {e}")
            return "0x"
    
    async def approve_tokens(
        self,
        owner_address: str, # Context
        spender_address: str,
        amount: float,
        private_key: str
    ) -> str:
        """
        Approve token spending
        
        Returns:
            Transaction hash
        """
        if not self.contract_address:
            raise ValueError("No contract address configured")

        try:
            account = self.w3.eth.account.from_key(private_key)
            checksum_contract = Web3.to_checksum_address(self.contract_address)
            contract = self.w3.eth.contract(address=checksum_contract, abi=ERC20_ABI)

            amount_wei = int(amount * 10**18)

            tx = await contract.functions.approve(
                Web3.to_checksum_address(spender_address),
                amount_wei
            ).build_transaction({
                'from': account.address,
                'nonce': await self.w3.eth.get_transaction_count(account.address),
                'gas': 100000,
                'gasPrice': await self.w3.eth.gas_price
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            return self.w3.to_hex(tx_hash)
        except Exception as e:
            print(f"Error approving tokens: {e}")
            return "0x"
    
    async def bridge_to_solana(
        self,
        amount: float,
        solana_address: str,
        private_key: str
    ) -> str:
        """
        Bridge tokens from Ethereum to Solana.
        This would typically involve burning/locking on Eth and minting/releasing on Solana.
        For this simplified version, we just burn/transfer to a bridge address.
        """
        # Placeholder bridge address
        BRIDGE_ADDRESS = "0x000000000000000000000000000000000000dEaD"

        return await self.transfer_tokens(
            from_address="", # Derived from private key
            to_address=BRIDGE_ADDRESS,
            amount=amount,
            private_key=private_key
        )
