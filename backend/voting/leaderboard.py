"""
Leaderboard System Module

Manages competitive leaderboards and rankings.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum

from .gamification import UserProgress
from .achievements import AchievementSystem


class LeaderboardType(str, Enum):
    """Types of leaderboards"""
    POINTS = "points"
    VOTES = "votes"
    STREAK = "streak"
    TOKENS = "tokens"
    LEVEL = "level"
    ACHIEVEMENTS = "achievements"


class LeaderboardEntry(BaseModel):
    """Entry in a leaderboard"""
    rank: int
    user_id: str
    value: float
    display_name: Optional[str] = None
    tier: Optional[str] = None
    metadata: Dict[str, Any] = {}


class LeaderboardSystem:
    """
    Leaderboard system for competitive rankings
    """
    
    def __init__(self, gamification_system, achievement_system: Optional[AchievementSystem] = None):
        self.gamification_system = gamification_system
        self.achievement_system = achievement_system
        self.leaderboards: Dict[str, List[LeaderboardEntry]] = {}
        self.last_updated: Dict[str, datetime] = {}
    
    def generate_leaderboard(
        self,
        leaderboard_type: LeaderboardType,
        limit: int = 100,
        time_period: Optional[str] = None
    ) -> List[LeaderboardEntry]:
        """
        Generate a leaderboard
        
        Args:
            leaderboard_type: Type of leaderboard
            limit: Maximum entries to return
            time_period: Optional time period filter ("daily", "weekly", "monthly", "all")
            
        Returns:
            Sorted list of leaderboard entries
        """
        entries = []
        
        for user_id, progress in self.gamification_system.user_progress.items():
            # Apply time period filter if specified
            if time_period and not self._in_time_period(progress, time_period):
                continue
            
            value = self._get_leaderboard_value(progress, leaderboard_type)
            
            entry = LeaderboardEntry(
                rank=0,  # Will be set after sorting
                user_id=user_id,
                value=value,
                tier=progress.tier.value,
                metadata={
                    "level": progress.level,
                    "votes": progress.votes_cast,
                    "streak": progress.streak_days
                }
            )
            entries.append(entry)
        
        # Sort by value descending
        entries.sort(key=lambda e: e.value, reverse=True)
        
        # Assign ranks
        for i, entry in enumerate(entries[:limit], start=1):
            entry.rank = i
        
        # Cache leaderboard
        cache_key = f"{leaderboard_type.value}_{time_period or 'all'}"
        self.leaderboards[cache_key] = entries[:limit]
        self.last_updated[cache_key] = datetime.utcnow()
        
        return entries[:limit]
    
    def _get_leaderboard_value(
        self,
        progress: UserProgress,
        leaderboard_type: LeaderboardType
    ) -> float:
        """Get the value for leaderboard sorting"""
        if leaderboard_type == LeaderboardType.POINTS:
            return float(progress.points)
        elif leaderboard_type == LeaderboardType.VOTES:
            return float(progress.votes_cast)
        elif leaderboard_type == LeaderboardType.STREAK:
            return float(progress.streak_days)
        elif leaderboard_type == LeaderboardType.TOKENS:
            return progress.tokens_earned + progress.tokens_staked
        elif leaderboard_type == LeaderboardType.LEVEL:
            return float(progress.level)
        elif leaderboard_type == LeaderboardType.ACHIEVEMENTS:
            # Get achievement count from achievement system
            if self.achievement_system:
                user_achievements = self.achievement_system.get_user_achievements(
                    progress.user_id,
                    completed_only=True
                )
                return float(len(user_achievements))
            return 0.0
        else:
            return 0.0
    
    def _in_time_period(self, progress: UserProgress, time_period: str) -> bool:
        """Check if progress is within time period"""
        now = datetime.utcnow()
        
        if time_period == "daily":
            cutoff = now - timedelta(days=1)
        elif time_period == "weekly":
            cutoff = now - timedelta(weeks=1)
        elif time_period == "monthly":
            cutoff = now - timedelta(days=30)
        else:
            return True
        
        return progress.last_activity >= cutoff
    
    def get_user_rank(
        self,
        user_id: str,
        leaderboard_type: LeaderboardType,
        time_period: Optional[str] = None
    ) -> Optional[LeaderboardEntry]:
        """
        Get user's rank in a leaderboard
        
        Args:
            user_id: User to get rank for
            leaderboard_type: Type of leaderboard
            time_period: Optional time period filter
            
        Returns:
            Leaderboard entry for user or None
        """
        cache_key = f"{leaderboard_type.value}_{time_period or 'all'}"
        
        # Generate if not cached or stale
        if (cache_key not in self.leaderboards or
            cache_key not in self.last_updated or
            datetime.utcnow() - self.last_updated[cache_key] > timedelta(minutes=5)):
            self.generate_leaderboard(leaderboard_type, limit=1000, time_period=time_period)
        
        leaderboard = self.leaderboards.get(cache_key, [])
        
        for entry in leaderboard:
            if entry.user_id == user_id:
                return entry
        
        return None
    
    def get_top_users(
        self,
        leaderboard_type: LeaderboardType,
        limit: int = 10,
        time_period: Optional[str] = None
    ) -> List[LeaderboardEntry]:
        """
        Get top users from leaderboard
        
        Args:
            leaderboard_type: Type of leaderboard
            limit: Number of top users
            time_period: Optional time period filter
            
        Returns:
            List of top leaderboard entries
        """
        return self.generate_leaderboard(leaderboard_type, limit, time_period)
    
    def get_nearby_users(
        self,
        user_id: str,
        leaderboard_type: LeaderboardType,
        range_size: int = 5
    ) -> List[LeaderboardEntry]:
        """
        Get users ranked near the specified user
        
        Args:
            user_id: Center user
            leaderboard_type: Type of leaderboard
            range_size: Number of users above and below
            
        Returns:
            List of nearby leaderboard entries
        """
        user_entry = self.get_user_rank(user_id, leaderboard_type)
        
        if not user_entry:
            return []
        
        cache_key = f"{leaderboard_type.value}_all"
        leaderboard = self.leaderboards.get(cache_key, [])
        
        user_rank = user_entry.rank
        start_rank = max(1, user_rank - range_size)
        end_rank = user_rank + range_size
        
        nearby = [
            entry for entry in leaderboard
            if start_rank <= entry.rank <= end_rank
        ]
        
        return nearby
    
    def get_tier_leaderboard(
        self,
        tier: str,
        leaderboard_type: LeaderboardType = LeaderboardType.POINTS,
        limit: int = 50
    ) -> List[LeaderboardEntry]:
        """
        Get leaderboard filtered by tier
        
        Args:
            tier: Tier to filter by
            leaderboard_type: Type of leaderboard
            limit: Maximum entries
            
        Returns:
            Leaderboard entries for the tier
        """
        all_entries = self.generate_leaderboard(leaderboard_type, limit=1000)
        
        tier_entries = [e for e in all_entries if e.tier == tier]
        
        # Re-rank within tier
        for i, entry in enumerate(tier_entries[:limit], start=1):
            entry.rank = i
        
        return tier_entries[:limit]
    
    def get_leaderboard_stats(self) -> Dict[str, Any]:
        """Get leaderboard statistics"""
        total_users = len(self.gamification_system.user_progress)
        
        return {
            "total_users": total_users,
            "cached_leaderboards": len(self.leaderboards),
            "last_update_times": {
                key: time.isoformat()
                for key, time in self.last_updated.items()
            }
        }
