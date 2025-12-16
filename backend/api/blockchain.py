"""
Blockchain API Router

API endpoints for blockchain integration.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Any

from backend.blockchain.rewards import RewardDistribution
from backend.api.dependencies import get_reward_distribution


router = APIRouter()


class StakeRequest(BaseModel):
    """Request to stake tokens"""
    amount: float
    lock_period_days: int = 0


class TransferRequest(BaseModel):
    """Request to transfer tokens"""
    to_address: str
    amount: float


class ClaimRewardRequest(BaseModel):
    """Request to claim rewards"""
    user_address: str


@router.get("/balance/{address}")
async def get_balance(address: str):
    """Get token balance for address"""
    # Placeholder - integrate with actual blockchain system
    return {"address": address, "balance": 0.0}


@router.post("/stake")
async def stake_tokens(request: StakeRequest):
    """Stake tokens"""
    # Placeholder - integrate with actual staking system
    return {"status": "staked", "amount": request.amount}


@router.post("/unstake/{position_id}")
async def unstake_tokens(position_id: str):
    """Unstake tokens"""
    # Placeholder - integrate with actual staking system
    return {"status": "unstaked", "position_id": position_id}


@router.get("/staking/positions")
async def get_staking_positions():
    """Get user's staking positions"""
    # Placeholder - integrate with actual staking system
    return []


@router.post("/transfer")
async def transfer_tokens(request: TransferRequest):
    """Transfer tokens"""
    # Placeholder - integrate with actual token system
    return {"status": "transferred", "amount": request.amount}


@router.get("/rewards/pending")
async def get_pending_rewards(
    address: str = Query(..., description="User wallet address"),
    rewards_system: RewardDistribution = Depends(get_reward_distribution)
):
    """Get pending rewards"""
    amount = rewards_system.get_pending_rewards(address)
    return {"pending_rewards": amount}


@router.post("/rewards/claim")
async def claim_rewards(
    request: ClaimRewardRequest,
    rewards_system: RewardDistribution = Depends(get_reward_distribution)
):
    """Claim pending rewards"""
    user_address = request.user_address

    # Get all pending claims
    pending_claims = rewards_system.get_user_claims(user_address, claimed=False)

    claimed_amount = 0.0
    claimed_ids = []

    for claim in pending_claims:
        result = rewards_system.claim_reward(claim.claim_id)
        if result is not None:
            claimed_amount += result
            claimed_ids.append(claim.claim_id)

    return {
        "status": "claimed",
        "amount": claimed_amount,
        "transaction_id": "tx_simulated_" + str(len(claimed_ids)), # Simulated transaction ID
        "claimed_count": len(claimed_ids)
    }
