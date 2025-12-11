"""
Gamification System Module

Manages user progression, tiers, points, and rewards.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from .achievements import AchievementTier


class UserTier(str, Enum):
    """User tier levels (6 tiers matching achievement tiers)"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    LEGENDARY = "legendary"


class UserProgress(BaseModel):
    """User's gamification progress"""
    user_id: str
    tier: UserTier = UserTier.BRONZE
    points: int = 0
    level: int = 1
    experience: int = 0
    votes_cast: int = 0
    sessions_attended: int = 0
    tokens_earned: float = 0.0
    tokens_staked: float = 0.0
    referrals: int = 0
    streak_days: int = 0
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GamificationSystem:
    """
    Gamification system with 6-tier progression
    """
    
    def __init__(self):
        self.user_progress: Dict[str, UserProgress] = {}
        self.tier_requirements = self._initialize_tier_requirements()
        self.level_requirements = self._initialize_level_requirements()
    
    def _initialize_tier_requirements(self) -> Dict[UserTier, int]:
        """Initialize points required for each tier"""
        return {
            UserTier.BRONZE: 0,
            UserTier.SILVER: 100,
            UserTier.GOLD: 500,
            UserTier.PLATINUM: 1500,
            UserTier.DIAMOND: 5000,
            UserTier.LEGENDARY: 15000
        }
    
    def _initialize_level_requirements(self) -> List[int]:
        """Initialize experience required for each level"""
        # Experience required grows exponentially
        return [i * 100 + (i ** 2) * 10 for i in range(1, 101)]
    
    def get_or_create_user_progress(self, user_id: str) -> UserProgress:
        """Get or create user progress"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = UserProgress(user_id=user_id)
        return self.user_progress[user_id]
    
    def add_points(self, user_id: str, points: int, reason: str = "") -> UserProgress:
        """
        Add points to user and update tier/level
        
        Args:
            user_id: User ID
            points: Points to add
            reason: Reason for points
            
        Returns:
            Updated user progress
        """
        progress = self.get_or_create_user_progress(user_id)
        progress.points += points
        progress.experience += points
        progress.last_activity = datetime.utcnow()
        
        # Update tier
        new_tier = self._calculate_tier(progress.points)
        if new_tier != progress.tier:
            progress.tier = new_tier
        
        # Update level
        new_level = self._calculate_level(progress.experience)
        if new_level > progress.level:
            progress.level = new_level
        
        return progress
    
    def _calculate_tier(self, points: int) -> UserTier:
        """Calculate user tier based on points"""
        if points >= self.tier_requirements[UserTier.LEGENDARY]:
            return UserTier.LEGENDARY
        elif points >= self.tier_requirements[UserTier.DIAMOND]:
            return UserTier.DIAMOND
        elif points >= self.tier_requirements[UserTier.PLATINUM]:
            return UserTier.PLATINUM
        elif points >= self.tier_requirements[UserTier.GOLD]:
            return UserTier.GOLD
        elif points >= self.tier_requirements[UserTier.SILVER]:
            return UserTier.SILVER
        else:
            return UserTier.BRONZE
    
    def _calculate_level(self, experience: int) -> int:
        """Calculate user level based on experience"""
        level = 1
        for required_exp in self.level_requirements:
            if experience >= required_exp:
                level += 1
            else:
                break
        return level
    
    def record_vote(self, user_id: str) -> UserProgress:
        """Record a vote and award points"""
        progress = self.get_or_create_user_progress(user_id)
        progress.votes_cast += 1
        return self.add_points(user_id, 10, "vote_cast")
    
    def record_session_attendance(self, user_id: str) -> UserProgress:
        """Record session attendance and award points"""
        progress = self.get_or_create_user_progress(user_id)
        progress.sessions_attended += 1
        return self.add_points(user_id, 25, "session_attendance")
    
    def record_referral(self, user_id: str) -> UserProgress:
        """Record a referral and award points"""
        progress = self.get_or_create_user_progress(user_id)
        progress.referrals += 1
        return self.add_points(user_id, 50, "referral")
    
    def update_streak(self, user_id: str) -> UserProgress:
        """Update daily activity streak"""
        progress = self.get_or_create_user_progress(user_id)
        
        # Check if last activity was yesterday
        now = datetime.utcnow()
        last_activity_date = progress.last_activity.date()
        today = now.date()
        
        if (today - last_activity_date).days == 1:
            # Consecutive day - increment streak
            progress.streak_days += 1
            # Award bonus points for streak
            streak_bonus = min(progress.streak_days * 5, 100)  # Max 100 bonus
            self.add_points(user_id, streak_bonus, "streak_bonus")
        elif (today - last_activity_date).days > 1:
            # Streak broken
            progress.streak_days = 1
        
        progress.last_activity = now
        return progress
    
    def award_tokens(self, user_id: str, amount: float) -> UserProgress:
        """Award tokens to user"""
        progress = self.get_or_create_user_progress(user_id)
        progress.tokens_earned += amount
        return progress
    
    def update_staked_tokens(self, user_id: str, amount: float) -> UserProgress:
        """Update user's staked token amount"""
        progress = self.get_or_create_user_progress(user_id)
        progress.tokens_staked = amount
        return progress
    
    def get_tier_benefits(self, tier: UserTier) -> Dict[str, Any]:
        """Get benefits for a specific tier"""
        benefits = {
            UserTier.BRONZE: {
                "vote_weight": 1.0,
                "reward_multiplier": 1.0,
                "features": ["Basic voting", "Achievement tracking"]
            },
            UserTier.SILVER: {
                "vote_weight": 1.2,
                "reward_multiplier": 1.2,
                "features": ["Basic voting", "Achievement tracking", "Priority notifications"]
            },
            UserTier.GOLD: {
                "vote_weight": 1.5,
                "reward_multiplier": 1.5,
                "features": [
                    "Basic voting", "Achievement tracking",
                    "Priority notifications", "Custom avatar"
                ]
            },
            UserTier.PLATINUM: {
                "vote_weight": 2.0,
                "reward_multiplier": 2.0,
                "features": [
                    "Basic voting", "Achievement tracking",
                    "Priority notifications", "Custom avatar",
                    "Exclusive events"
                ]
            },
            UserTier.DIAMOND: {
                "vote_weight": 3.0,
                "reward_multiplier": 3.0,
                "features": [
                    "Basic voting", "Achievement tracking",
                    "Priority notifications", "Custom avatar",
                    "Exclusive events", "Council suggestion rights"
                ]
            },
            UserTier.LEGENDARY: {
                "vote_weight": 5.0,
                "reward_multiplier": 5.0,
                "features": [
                    "Basic voting", "Achievement tracking",
                    "Priority notifications", "Custom avatar",
                    "Exclusive events", "Council suggestion rights",
                    "VIP badge", "Direct AI interaction"
                ]
            }
        }
        return benefits.get(tier, benefits[UserTier.BRONZE])
    
    def get_next_tier_progress(self, user_id: str) -> Dict[str, Any]:
        """Get progress towards next tier"""
        progress = self.get_or_create_user_progress(user_id)
        current_tier = progress.tier
        
        tier_order = [
            UserTier.BRONZE, UserTier.SILVER, UserTier.GOLD,
            UserTier.PLATINUM, UserTier.DIAMOND, UserTier.LEGENDARY
        ]
        
        current_index = tier_order.index(current_tier)
        
        if current_index >= len(tier_order) - 1:
            return {
                "current_tier": current_tier.value,
                "next_tier": None,
                "progress_percentage": 100,
                "points_needed": 0
            }
        
        next_tier = tier_order[current_index + 1]
        current_requirement = self.tier_requirements[current_tier]
        next_requirement = self.tier_requirements[next_tier]
        
        points_needed = next_requirement - progress.points
        progress_percentage = (
            (progress.points - current_requirement) /
            (next_requirement - current_requirement) * 100
        )
        
        return {
            "current_tier": current_tier.value,
            "next_tier": next_tier.value,
            "progress_percentage": progress_percentage,
            "points_needed": points_needed
        }
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        progress = self.get_or_create_user_progress(user_id)
        
        return {
            "user_id": user_id,
            "tier": progress.tier.value,
            "level": progress.level,
            "points": progress.points,
            "experience": progress.experience,
            "votes_cast": progress.votes_cast,
            "sessions_attended": progress.sessions_attended,
            "tokens_earned": progress.tokens_earned,
            "tokens_staked": progress.tokens_staked,
            "referrals": progress.referrals,
            "streak_days": progress.streak_days,
            "tier_benefits": self.get_tier_benefits(progress.tier),
            "next_tier_progress": self.get_next_tier_progress(user_id),
            "last_activity": progress.last_activity.isoformat(),
            "member_since": progress.created_at.isoformat()
        }
