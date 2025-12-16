"""
Blockchain API Router

API endpoints for blockchain integration.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any

from backend.blockchain.solana_contracts import SolanaContractManager
from backend.api.dependencies import get_solana_manager

router = APIRouter()


class StakeRequest(BaseModel):
    """Request to stake tokens"""
    user_address: str
    amount: float
    lock_period_days: int = 0


class TransferRequest(BaseModel):
    """Request to transfer tokens"""
    from_address: str
    to_address: str
    amount: float


@router.get("/balance/{address}")
async def get_balance(
    address: str,
    manager: SolanaContractManager = Depends(get_solana_manager)
):
    """Get token balance for address"""
    balance = await manager.get_wallet_balance(address)
    return {"address": address, "balance": balance}


@router.post("/stake")
async def stake_tokens(
    request: StakeRequest,
    manager: SolanaContractManager = Depends(get_solana_manager)
):
    """Stake tokens"""
    success = await manager.stake_tokens(
        request.user_address,
        request.amount,
        request.lock_period_days
    )

    if not success:
        raise HTTPException(status_code=400, detail="Staking failed")

    return {
        "status": "staked",
        "amount": request.amount,
        "lock_period_days": request.lock_period_days
    }


@router.post("/unstake/{position_id}")
async def unstake_tokens(
    position_id: str,
    manager: SolanaContractManager = Depends(get_solana_manager)
):
    """
    Unstake tokens by position ID.

    Note: Currently a placeholder wrapper. In a full implementation,
    this would look up the position details (amount, user) using the position_id
    and then call manager.unstake_tokens(user, amount).
    """
    # TODO: Implement position lookup and unstake logic
    return {"status": "unstaked", "position_id": position_id}


@router.get("/staking/positions")
async def get_staking_positions(
    user_address: str,
    manager: SolanaContractManager = Depends(get_solana_manager)
):
    """Get user's staking positions"""
    positions = await manager.get_staking_positions(user_address)
    return positions


@router.post("/transfer")
async def transfer_tokens(
    request: TransferRequest,
    manager: SolanaContractManager = Depends(get_solana_manager)
):
    """
    Transfer tokens between addresses.

    Note: This is currently a placeholder as the SolanaContractManager
    does not expose a direct transfer method.
    """
    # TODO: Implement token transfer logic via manager
    return {"status": "transferred", "amount": request.amount}


@router.get("/rewards/pending")
async def get_pending_rewards(
    user_address: str,
    manager: SolanaContractManager = Depends(get_solana_manager)
):
    """Get pending rewards"""
    # TODO: Implement pending rewards check via manager
    return {"pending_rewards": 0.0}


@router.post("/rewards/claim")
async def claim_rewards(
    user_address: str,
    manager: SolanaContractManager = Depends(get_solana_manager)
):
    """Claim pending rewards"""
    # Attempt to distribute rewards (placeholder usage)
    success = await manager.distribute_rewards({user_address: 0.0})
    return {"status": "claimed", "amount": 0.0}
