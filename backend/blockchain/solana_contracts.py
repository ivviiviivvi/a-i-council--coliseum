"""
Solana Contract Manager

Manages interactions with Solana smart contracts.
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair


class SolanaAccount(BaseModel):
    """Solana account information"""
    address: str
    balance: float
    owner: str
    is_initialized: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SolanaContractManager:
    """
    Manager for Solana smart contract interactions
    Handles council selection, staking, and reward contracts
    """
    
    def __init__(self, rpc_url: str, program_id: str):
        self.rpc_url = rpc_url
        self.client = AsyncClient(rpc_url)
        self.accounts: Dict[str, SolanaAccount] = {}

        try:
            self.program_id = Pubkey.from_string(program_id)
        except ValueError:
            logging.error(f"Invalid program ID: {program_id}")
            self.program_id = None

        self.payer: Optional[Keypair] = None
        private_key = os.getenv("SOLANA_PRIVATE_KEY")
        if private_key:
            try:
                if private_key.startswith("["):
                    # Load from JSON array
                    key_bytes = json.loads(private_key)
                    self.payer = Keypair.from_bytes(bytes(key_bytes))
                else:
                    # Load from base58 string
                    self.payer = Keypair.from_base58_string(private_key)
            except Exception as e:
                logging.error(f"Failed to load SOLANA_PRIVATE_KEY: {e}")

    async def initialize_council_program(self) -> bool:
        """
        Initialize the council selection program.
        Verifies connection to the cluster and that the program exists on-chain.
        """
        if not self.program_id:
            logging.error("Program ID is not set or valid.")
            return False

        try:
            # Check connection
            if not await self.client.is_connected():
                logging.error("Failed to connect to Solana cluster.")
                return False

            # Check if program exists
            resp = await self.client.get_account_info(self.program_id)

            if not resp.value:
                logging.error(f"Program {self.program_id} not found on chain.")
                return False

            if not resp.value.executable:
                logging.error(f"Account {self.program_id} is not executable.")
                return False

            # Check payer balance if payer is set
            if self.payer:
                balance_resp = await self.client.get_balance(self.payer.pubkey())
                balance = balance_resp.value
                logging.info(f"Payer {self.payer.pubkey()} balance: {balance} lamports")
                if balance == 0:
                    logging.warning("Payer account has 0 SOL.")

            logging.info(f"Council program {self.program_id} initialized and verified.")
            return True

        except Exception as e:
            logging.error(f"Error initializing council program: {e}")
            return False
    
    async def close(self):
        """Close the RPC client connection"""
        await self.client.close()

    async def create_council_account(
        self,
        council_id: str,
        num_seats: int
    ) -> str:
        """
        Create a new council account
        
        Args:
            council_id: Unique council identifier
            num_seats: Number of council seats
            
        Returns:
            Account address
        """
        # In a real implementation, this would derive a PDA and initialize it on chain.
        # For now, we simulate the address generation using Pubkey logic if possible,
        # or fall back to the string based approach but make it look like a Pubkey.

        if self.program_id:
            # Simulate PDA derivation (seeds would be council_id)
            try:
                # This is just a simulation of address generation
                seeds = [council_id.encode()]
                pda, bump = Pubkey.find_program_address(seeds, self.program_id)
                account_address = str(pda)
            except Exception:
                account_address = f"council_{council_id}"
        else:
            account_address = f"council_{council_id}"

        account = SolanaAccount(
            address=account_address,
            balance=0.0,
            owner=str(self.program_id) if self.program_id else "unknown",
            is_initialized=True
        )
        self.accounts[account_address] = account
        return account_address
    
    async def get_council_members(self, council_id: str) -> List[str]:
        """Get current council members"""
        # Placeholder - would read from Solana account
        return []
    
    async def update_council_members(
        self,
        council_id: str,
        members: List[str]
    ) -> bool:
        """
        Update council member list
        
        Args:
            council_id: Council identifier
            members: List of member addresses
            
        Returns:
            True if successful
        """
        # Placeholder for actual Solana transaction
        return True
    
    async def stake_tokens(
        self,
        user_address: str,
        amount: float
    ) -> bool:
        """
        Stake tokens for governance
        
        Args:
            user_address: User's Solana address
            amount: Amount to stake
            
        Returns:
            True if successful
        """
        # Placeholder for actual staking transaction
        return True
    
    async def unstake_tokens(
        self,
        user_address: str,
        amount: float
    ) -> bool:
        """
        Unstake tokens
        
        Args:
            user_address: User's Solana address
            amount: Amount to unstake
            
        Returns:
            True if successful
        """
        # Placeholder for actual unstaking transaction
        return True
    
    async def get_stake_balance(self, user_address: str) -> float:
        """Get user's staked token balance"""
        # Placeholder - would read from Solana account
        return 0.0
    
    async def distribute_rewards(
        self,
        recipients: Dict[str, float]
    ) -> bool:
        """
        Distribute rewards to multiple recipients
        
        Args:
            recipients: Dict of address -> amount
            
        Returns:
            True if successful
        """
        # Placeholder for actual reward distribution transaction
        return True
    
    def get_program_accounts(self) -> List[SolanaAccount]:
        """Get all program accounts"""
        return list(self.accounts.values())
