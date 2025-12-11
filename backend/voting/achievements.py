"""
Achievement System Module

Manages user achievements and progression with 13 achievements across 6 tiers.
"""

from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid


class AchievementTier(str, Enum):
    """Achievement tiers (6 tiers)"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    LEGENDARY = "legendary"


class AchievementCategory(str, Enum):
    """Achievement categories"""
    VOTING = "voting"
    PARTICIPATION = "participation"
    SOCIAL = "social"
    GOVERNANCE = "governance"
    SPECIAL = "special"


class Achievement(BaseModel):
    """Achievement definition"""
    achievement_id: str
    name: str
    description: str
    category: AchievementCategory
    tier: AchievementTier
    points: int
    icon: str
    requirement_value: int
    requirement_description: str


class UserAchievement(BaseModel):
    """User's earned achievement"""
    user_id: str
    achievement_id: str
    earned_at: datetime = Field(default_factory=datetime.utcnow)
    progress: int = 0
    completed: bool = False


class AchievementSystem:
    """
    Achievement system with 13 achievements across 6 tiers
    """
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.user_achievements: Dict[str, List[UserAchievement]] = {}
        self._initialize_achievements()
    
    def _initialize_achievements(self):
        """Initialize the 13 achievements"""
        
        achievements_data = [
            # Voting Achievements (3)
            {
                "achievement_id": "first_vote",
                "name": "First Vote",
                "description": "Cast your first vote in a council session",
                "category": AchievementCategory.VOTING,
                "tier": AchievementTier.BRONZE,
                "points": 10,
                "icon": "🗳️",
                "requirement_value": 1,
                "requirement_description": "Cast 1 vote"
            },
            {
                "achievement_id": "voting_veteran",
                "name": "Voting Veteran",
                "description": "Cast 100 votes in council sessions",
                "category": AchievementCategory.VOTING,
                "tier": AchievementTier.GOLD,
                "points": 100,
                "icon": "🎖️",
                "requirement_value": 100,
                "requirement_description": "Cast 100 votes"
            },
            {
                "achievement_id": "democratic_champion",
                "name": "Democratic Champion",
                "description": "Cast 1000 votes in council sessions",
                "category": AchievementCategory.VOTING,
                "tier": AchievementTier.LEGENDARY,
                "points": 1000,
                "icon": "👑",
                "requirement_value": 1000,
                "requirement_description": "Cast 1000 votes"
            },
            
            # Participation Achievements (3)
            {
                "achievement_id": "active_participant",
                "name": "Active Participant",
                "description": "Attend 10 live council sessions",
                "category": AchievementCategory.PARTICIPATION,
                "tier": AchievementTier.SILVER,
                "points": 50,
                "icon": "📺",
                "requirement_value": 10,
                "requirement_description": "Attend 10 sessions"
            },
            {
                "achievement_id": "dedicated_viewer",
                "name": "Dedicated Viewer",
                "description": "Watch 100 hours of council debates",
                "category": AchievementCategory.PARTICIPATION,
                "tier": AchievementTier.PLATINUM,
                "points": 200,
                "icon": "⏰",
                "requirement_value": 100,
                "requirement_description": "Watch 100 hours"
            },
            {
                "achievement_id": "council_observer",
                "name": "Council Observer",
                "description": "Attend every session for 30 consecutive days",
                "category": AchievementCategory.PARTICIPATION,
                "tier": AchievementTier.DIAMOND,
                "points": 500,
                "icon": "👁️",
                "requirement_value": 30,
                "requirement_description": "30 day streak"
            },
            
            # Social Achievements (3)
            {
                "achievement_id": "community_builder",
                "name": "Community Builder",
                "description": "Refer 5 friends to join the platform",
                "category": AchievementCategory.SOCIAL,
                "tier": AchievementTier.SILVER,
                "points": 75,
                "icon": "🤝",
                "requirement_value": 5,
                "requirement_description": "Refer 5 users"
            },
            {
                "achievement_id": "influencer",
                "name": "Influencer",
                "description": "Have your vote align with the majority 50 times",
                "category": AchievementCategory.SOCIAL,
                "tier": AchievementTier.GOLD,
                "points": 150,
                "icon": "📊",
                "requirement_value": 50,
                "requirement_description": "Align with majority 50 times"
            },
            {
                "achievement_id": "trendsetter",
                "name": "Trendsetter",
                "description": "Start a voting trend that 100 users follow",
                "category": AchievementCategory.SOCIAL,
                "tier": AchievementTier.PLATINUM,
                "points": 300,
                "icon": "🌟",
                "requirement_value": 100,
                "requirement_description": "Lead 100 followers"
            },
            
            # Governance Achievements (3)
            {
                "achievement_id": "token_holder",
                "name": "Token Holder",
                "description": "Acquire 1000 governance tokens",
                "category": AchievementCategory.GOVERNANCE,
                "tier": AchievementTier.BRONZE,
                "points": 25,
                "icon": "🪙",
                "requirement_value": 1000,
                "requirement_description": "Hold 1000 tokens"
            },
            {
                "achievement_id": "staking_master",
                "name": "Staking Master",
                "description": "Stake 10000 tokens for governance",
                "category": AchievementCategory.GOVERNANCE,
                "tier": AchievementTier.GOLD,
                "points": 250,
                "icon": "💎",
                "requirement_value": 10000,
                "requirement_description": "Stake 10000 tokens"
            },
            {
                "achievement_id": "governance_elite",
                "name": "Governance Elite",
                "description": "Participate in 50 governance decisions",
                "category": AchievementCategory.GOVERNANCE,
                "tier": AchievementTier.DIAMOND,
                "points": 400,
                "icon": "⚖️",
                "requirement_value": 50,
                "requirement_description": "50 governance votes"
            },
            
            # Special Achievement (1)
            {
                "achievement_id": "founding_member",
                "name": "Founding Member",
                "description": "Join during the first month of launch",
                "category": AchievementCategory.SPECIAL,
                "tier": AchievementTier.LEGENDARY,
                "points": 2000,
                "icon": "🏆",
                "requirement_value": 1,
                "requirement_description": "Be a founding member"
            }
        ]
        
        for data in achievements_data:
            achievement = Achievement(**data)
            self.achievements[achievement.achievement_id] = achievement
    
    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get achievement by ID"""
        return self.achievements.get(achievement_id)
    
    def get_achievements_by_tier(self, tier: AchievementTier) -> List[Achievement]:
        """Get all achievements of a specific tier"""
        return [
            a for a in self.achievements.values()
            if a.tier == tier
        ]
    
    def get_achievements_by_category(self, category: AchievementCategory) -> List[Achievement]:
        """Get all achievements in a category"""
        return [
            a for a in self.achievements.values()
            if a.category == category
        ]
    
    def track_progress(
        self,
        user_id: str,
        achievement_id: str,
        progress: int
    ) -> Optional[UserAchievement]:
        """
        Track user progress towards an achievement
        
        Args:
            user_id: User ID
            achievement_id: Achievement to track
            progress: Current progress value
            
        Returns:
            UserAchievement if tracked successfully
        """
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            return None
        
        if user_id not in self.user_achievements:
            self.user_achievements[user_id] = []
        
        # Find existing user achievement or create new
        user_achievement = next(
            (ua for ua in self.user_achievements[user_id]
             if ua.achievement_id == achievement_id),
            None
        )
        
        if not user_achievement:
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement_id,
                progress=0
            )
            self.user_achievements[user_id].append(user_achievement)
        
        user_achievement.progress = progress
        
        # Check if achievement is complete
        if progress >= achievement.requirement_value and not user_achievement.completed:
            user_achievement.completed = True
            user_achievement.earned_at = datetime.utcnow()
        
        return user_achievement
    
    def award_achievement(
        self,
        user_id: str,
        achievement_id: str
    ) -> Optional[UserAchievement]:
        """
        Directly award an achievement to a user
        
        Returns:
            UserAchievement if awarded successfully
        """
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            return None
        
        return self.track_progress(
            user_id,
            achievement_id,
            achievement.requirement_value
        )
    
    def get_user_achievements(
        self,
        user_id: str,
        completed_only: bool = False
    ) -> List[UserAchievement]:
        """Get all achievements for a user"""
        achievements = self.user_achievements.get(user_id, [])
        
        if completed_only:
            achievements = [a for a in achievements if a.completed]
        
        return achievements
    
    def get_user_points(self, user_id: str) -> int:
        """Calculate total achievement points for a user"""
        user_achievements = self.get_user_achievements(user_id, completed_only=True)
        total_points = 0
        
        for user_achievement in user_achievements:
            achievement = self.achievements.get(user_achievement.achievement_id)
            if achievement:
                total_points += achievement.points
        
        return total_points
    
    def get_completion_stats(self, user_id: str) -> Dict[str, any]:
        """Get achievement completion statistics for a user"""
        total_achievements = len(self.achievements)
        user_achievements = self.get_user_achievements(user_id)
        completed = sum(1 for ua in user_achievements if ua.completed)
        
        tier_stats = {}
        for tier in AchievementTier:
            tier_achievements = self.get_achievements_by_tier(tier)
            tier_completed = sum(
                1 for ta in tier_achievements
                for ua in user_achievements
                if ua.achievement_id == ta.achievement_id and ua.completed
            )
            tier_stats[tier.value] = {
                "total": len(tier_achievements),
                "completed": tier_completed
            }
        
        return {
            "total_achievements": total_achievements,
            "completed": completed,
            "completion_percentage": (completed / total_achievements * 100) if total_achievements > 0 else 0,
            "total_points": self.get_user_points(user_id),
            "tier_stats": tier_stats
        }
