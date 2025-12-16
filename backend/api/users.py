"""
Users API Router

API endpoints for user management and profiles.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from backend.voting.gamification import GamificationSystem
from backend.voting.leaderboard import LeaderboardSystem, LeaderboardType
from backend.api.dependencies import get_gamification_system, get_leaderboard_system

router = APIRouter()


class UserProfileResponse(BaseModel):
    """User profile response"""
    user_id: str
    tier: str
    level: int
    points: int
    votes_cast: int
    tokens_earned: float


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    user_id: str
    value: float
    tier: str
    display_name: Optional[str] = None
    metadata: Dict[str, Any] = {}


@router.get("/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str,
    gamification_system: GamificationSystem = Depends(get_gamification_system)
):
    """Get user profile"""
    stats = gamification_system.get_user_stats(user_id)
    return UserProfileResponse(
        user_id=stats["user_id"],
        tier=stats["tier"],
        level=stats["level"],
        points=stats["points"],
        votes_cast=stats["votes_cast"],
        tokens_earned=stats["tokens_earned"]
    )


@router.get("/{user_id}/stats")
async def get_user_stats(
    user_id: str,
    gamification_system: GamificationSystem = Depends(get_gamification_system)
):
    """Get detailed user statistics"""
    return gamification_system.get_user_stats(user_id)


@router.get("/leaderboard/{leaderboard_type}", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    leaderboard_type: str,
    limit: int = 100,
    time_period: Optional[str] = Query(None, regex="^(daily|weekly|monthly|all)$"),
    leaderboard_system: LeaderboardSystem = Depends(get_leaderboard_system)
):
    """Get leaderboard"""
    try:
        lb_type = LeaderboardType(leaderboard_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid leaderboard type: {leaderboard_type}")

    entries = leaderboard_system.get_top_users(lb_type, limit, time_period)

    # Map backend LeaderboardEntry to API LeaderboardEntry
    return [
        LeaderboardEntry(
            rank=e.rank,
            user_id=e.user_id,
            value=e.value,
            tier=e.tier or "bronze",
            display_name=e.display_name,
            metadata=e.metadata
        )
        for e in entries
    ]


@router.get("/{user_id}/rank")
async def get_user_rank(
    user_id: str,
    leaderboard_type: str = "points",
    time_period: Optional[str] = Query(None, regex="^(daily|weekly|monthly|all)$"),
    leaderboard_system: LeaderboardSystem = Depends(get_leaderboard_system),
    gamification_system: GamificationSystem = Depends(get_gamification_system)
):
    """Get user's rank in leaderboard"""
    try:
        lb_type = LeaderboardType(leaderboard_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid leaderboard type: {leaderboard_type}")

    entry = leaderboard_system.get_user_rank(user_id, lb_type, time_period)
    total_users = len(gamification_system.user_progress)

    if entry:
        return {
            "rank": entry.rank,
            "total_users": total_users,
            "value": entry.value,
            "percentile": ((total_users - entry.rank) / total_users * 100) if total_users > 0 else 0
        }
    else:
        # If user not in leaderboard (e.g. no activity), return default
        return {"rank": 0, "total_users": total_users, "value": 0, "percentile": 0}
