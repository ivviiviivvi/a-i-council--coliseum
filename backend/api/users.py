"""
Users API Router

API endpoints for user management and profiles.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.api.dependencies import get_gamification_system, get_leaderboard_system
from backend.voting.gamification import GamificationSystem
from backend.voting.leaderboard import LeaderboardSystem, LeaderboardType


router = APIRouter()


class UserProfileResponse(BaseModel):
    """User profile response"""
    user_id: str
    tier: str
    level: int
    points: int
    votes_cast: int
    tokens_earned: float


class LeaderboardEntryResponse(BaseModel):
    """Leaderboard entry response"""
    rank: int
    user_id: str
    value: float
    tier: str
    display_name: Optional[str] = None


@router.get("/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str,
    gamification_system: GamificationSystem = Depends(get_gamification_system)
):
    """Get user profile"""
    progress = gamification_system.get_or_create_user_progress(user_id)
    return UserProfileResponse(
        user_id=progress.user_id,
        tier=progress.tier.value,
        level=progress.level,
        points=progress.points,
        votes_cast=progress.votes_cast,
        tokens_earned=progress.tokens_earned
    )


@router.get("/{user_id}/stats")
async def get_user_stats(
    user_id: str,
    gamification_system: GamificationSystem = Depends(get_gamification_system)
):
    """Get detailed user statistics"""
    return gamification_system.get_user_stats(user_id)


@router.get("/leaderboard/{leaderboard_type}", response_model=List[LeaderboardEntryResponse])
async def get_leaderboard(
    leaderboard_type: str,
    limit: int = 100,
    leaderboard_system: LeaderboardSystem = Depends(get_leaderboard_system)
):
    """Get leaderboard"""
    try:
        type_enum = LeaderboardType(leaderboard_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid leaderboard type: {leaderboard_type}")

    entries = leaderboard_system.generate_leaderboard(type_enum, limit=limit)

    return [
        LeaderboardEntryResponse(
            rank=entry.rank,
            user_id=entry.user_id,
            value=entry.value,
            tier=entry.tier or "bronze",
            display_name=entry.display_name
        ) for entry in entries
    ]


@router.get("/{user_id}/rank")
async def get_user_rank(
    user_id: str,
    leaderboard_type: str = "points",
    leaderboard_system: LeaderboardSystem = Depends(get_leaderboard_system)
):
    """Get user's rank in leaderboard"""
    try:
        type_enum = LeaderboardType(leaderboard_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid leaderboard type: {leaderboard_type}")

    entry = leaderboard_system.get_user_rank(user_id, type_enum)
    stats = leaderboard_system.get_leaderboard_stats()

    if entry:
        return {
            "rank": entry.rank,
            "total_users": stats["total_users"],
            "value": entry.value,
            "tier": entry.tier
        }
    else:
        return {
            "rank": None,
            "total_users": stats["total_users"],
            "message": "User not ranked"
        }
