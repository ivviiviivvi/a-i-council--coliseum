"""
Solana Contract Manager

Manages interactions with Solana smart contracts.
"""

import os
import logging
import base64
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

# Solana imports
try:
    from solana.rpc.async_api import AsyncClient
    from solana.rpc.commitment import Confirmed
    from solana.rpc.types import TxOpts
    from solders.pubkey import Pubkey
    from solders.keypair import Keypair
    from solders.transaction import Transaction
    from solders.message import Message
    from solders.system_program import TransferParams, transfer
    from solders.instruction import Instruction, AccountMeta

    # SPL Token imports
    from spl.token.constants import TOKEN_PROGRAM_ID
    from spl.token.instructions import transfer as transfer_spl, TransferParams as SplTransferParams
except ImportError:
    # Fallback for environment setup or incomplete dependencies
    logging.warning("Solana/Solders dependencies not found. Blockchain features will be limited.")
    AsyncClient = None
    Pubkey = None
    Keypair = None
    Transaction = None
    TOKEN_PROGRAM_ID = None

logger = logging.getLogger(__name__)

class SolanaAccount(BaseModel):
    """Solana account information"""
    address: str
    balance: float
    owner: str
    is_initialized: bool = False


class SolanaContractManager:
    """
    Manager for Solana smart contract interactions
    Handles council selection, staking, and reward contracts
    """
    
    def __init__(self, rpc_url: str, program_id: str):
        self.rpc_url = rpc_url
        self.program_id_str = program_id
        self.accounts: Dict[str, SolanaAccount] = {}

        self.client = None
        self.payer = None
        self.program_id = None

        if AsyncClient:
            self.client = AsyncClient(rpc_url)
            try:
                self.program_id = Pubkey.from_string(program_id)
            except Exception as e:
                logger.error(f"Invalid program ID: {e}")

            # Load payer from env
            private_key = os.getenv("SOLANA_PRIVATE_KEY")
            if private_key:
                try:
                    # Assume base58 or list of ints
                    if "[" in private_key:
                        import json
                        key_bytes = bytes(json.loads(private_key))
                        self.payer = Keypair.from_bytes(key_bytes)
                    else:
                        self.payer = Keypair.from_base58_string(private_key)
                except Exception as e:
                    logger.error(f"Failed to load SOLANA_PRIVATE_KEY: {e}")
    
    async def close(self):
        """Close the RPC client connection"""
        if self.client:
            await self.client.close()

    async def initialize_council_program(self) -> bool:
        """Initialize the council selection program"""
        # Placeholder for actual Solana program initialization
        return True
    
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
        account_address = f"council_{council_id}"
        account = SolanaAccount(
            address=account_address,
            balance=0.0,
            owner=self.program_id_str,
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
        Stake tokens for governance.
        Transfers tokens from user to the program vault.
        
        Args:
            user_address: User's Solana address (must match payer if we are signing)
            amount: Amount to stake
            
        Returns:
            True if successful
        """
        if not self.client or not self.payer:
            logger.error("Solana client or payer not initialized")
            return False

        try:
            user_pubkey = Pubkey.from_string(user_address)

            # Verify if we can sign for this user
            if user_pubkey != self.payer.pubkey():
                logger.warning(f"Cannot stake for {user_address}: Backend signer is {self.payer.pubkey()}")
                # In a real app, we might return a transaction for user to sign,
                # but here we return False as we can't execute it.
                return False

            # Determine Token Mint
            # Ideally this comes from config or env. Using a placeholder or env.
            token_mint_str = os.getenv("COUNCIL_TOKEN_MINT")
            if not token_mint_str:
                logger.error("COUNCIL_TOKEN_MINT not set")
                return False
            token_mint = Pubkey.from_string(token_mint_str)

            # Derive Vault PDA (Program Derived Address)
            # Seeds: [b"staking", token_mint] or similar
            # For now, we assume a simple vault derived from program_id
            vault_pda, bump = Pubkey.find_program_address(
                [b"staking_vault", bytes(token_mint)],
                self.program_id
            )

            # Get User Token Account
            # using spl.token.get_associated_token_address
            from spl.token.instructions import get_associated_token_address
            user_ata = get_associated_token_address(user_pubkey, token_mint)
            vault_ata = get_associated_token_address(vault_pda, token_mint, True) # allow_owner_off_curve=True for PDAs

            # We might need to create vault ATA if it doesn't exist?
            # Usually the program handles it or we include create instruction.
            # For this task, we focus on the transfer (stake) instruction.

            # Convert amount to integer (assuming 9 decimals like in token_economics.py)
            amount_int = int(amount * 1_000_000_000)

            # Create Transfer Instruction (User ATA -> Vault ATA)
            # We use SPL Token Transfer
            transfer_ix = transfer_spl(
                SplTransferParams(
                    program_id=TOKEN_PROGRAM_ID,
                    source=user_ata,
                    dest=vault_ata,
                    owner=user_pubkey,
                    amount=amount_int,
                    signers=[]
                )
            )

            # Create Transaction
            recent_blockhash = await self.client.get_latest_blockhash()
            msg = Message(
                [transfer_ix],
                self.payer.pubkey()
            )
            tx = Transaction(
                from_keypairs=[self.payer],
                message=msg,
                recent_blockhash=recent_blockhash.value.blockhash
            )

            # Send Transaction
            # Note: We need to handle potential errors (like ATA not existing)
            # which would be caught by exception handler

            signature = await self.client.send_transaction(tx, opts=TxOpts(skip_preflight=False))
            logger.info(f"Staking transaction sent: {signature.value}")

            # Wait for confirmation
            await self.client.confirm_transaction(signature.value, commitment=Confirmed)
            logger.info("Staking transaction confirmed")

            return True

        except Exception as e:
            logger.error(f"Error staking tokens: {e}")
            return False
    
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
