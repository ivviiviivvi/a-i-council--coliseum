"""
Achievements API Router

API endpoints for achievements and gamification.
"""

from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel

from backend.voting.achievements import AchievementSystem
from backend.api.dependencies import get_achievement_system

router = APIRouter()


class AchievementResponse(BaseModel):
    """Achievement response model"""
    achievement_id: str
    name: str
    description: str
    tier: str
    points: int
    completed: bool = False


@router.get("/", response_model=List[AchievementResponse])
async def list_achievements(
    achievement_system: AchievementSystem = Depends(get_achievement_system)
):
    """List all achievements"""
    achievements = achievement_system.achievements.values()
    return [
        AchievementResponse(
            achievement_id=a.achievement_id,
            name=a.name,
            description=a.description,
            tier=a.tier.value,
            points=a.points,
            completed=False
        )
        for a in achievements
    ]


@router.get("/user/{user_id}", response_model=List[AchievementResponse])
async def get_user_achievements(
    user_id: str,
    achievement_system: AchievementSystem = Depends(get_achievement_system)
):
    """Get user's achievements"""
    user_achievements = achievement_system.get_user_achievements(user_id)
    user_achievement_map = {ua.achievement_id: ua for ua in user_achievements}

    response = []
    for achievement in achievement_system.achievements.values():
        ua = user_achievement_map.get(achievement.achievement_id)
        completed = ua.completed if ua else False

        response.append(AchievementResponse(
            achievement_id=achievement.achievement_id,
            name=achievement.name,
            description=achievement.description,
            tier=achievement.tier.value,
            points=achievement.points,
            completed=completed
        ))

    return response


@router.get("/user/{user_id}/stats")
async def get_achievement_stats(
    user_id: str,
    achievement_system: AchievementSystem = Depends(get_achievement_system)
):
    """Get user's achievement statistics"""
    return achievement_system.get_completion_stats(user_id)
