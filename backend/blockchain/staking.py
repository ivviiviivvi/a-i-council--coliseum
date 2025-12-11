"""
Staking System Module

Manages token staking for governance participation.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import uuid


class StakePosition(BaseModel):
    """A user's staking position"""
    position_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_address: str
    amount: float
    staked_at: datetime = Field(default_factory=datetime.utcnow)
    lock_period_days: int = 0
    unlocks_at: Optional[datetime] = None
    rewards_earned: float = 0.0


class StakingSystem:
    """
    Staking system for governance tokens
    """
    
    def __init__(
        self,
        min_stake: float = 100.0,
        reward_rate: float = 0.05  # 5% annual
    ):
        self.min_stake = min_stake
        self.reward_rate = reward_rate
        self.positions: Dict[str, StakePosition] = {}
        self.user_positions: Dict[str, list[str]] = {}
    
    def create_stake(
        self,
        user_address: str,
        amount: float,
        lock_period_days: int = 0
    ) -> Optional[StakePosition]:
        """
        Create a new staking position
        
        Args:
            user_address: User's address
            amount: Amount to stake
            lock_period_days: Optional lock period
            
        Returns:
            Stake position if successful
        """
        if amount < self.min_stake:
            return None
        
        position = StakePosition(
            user_address=user_address,
            amount=amount,
            lock_period_days=lock_period_days
        )
        
        if lock_period_days > 0:
            position.unlocks_at = datetime.utcnow() + timedelta(days=lock_period_days)
        
        self.positions[position.position_id] = position
        
        if user_address not in self.user_positions:
            self.user_positions[user_address] = []
        self.user_positions[user_address].append(position.position_id)
        
        return position
    
    def get_user_stakes(self, user_address: str) -> list[StakePosition]:
        """Get all staking positions for a user"""
        position_ids = self.user_positions.get(user_address, [])
        return [
            self.positions[pid]
            for pid in position_ids
            if pid in self.positions
        ]
    
    def get_total_staked(self, user_address: str) -> float:
        """Get total staked amount for a user"""
        positions = self.get_user_stakes(user_address)
        return sum(p.amount for p in positions)
    
    def can_unstake(self, position_id: str) -> bool:
        """Check if a position can be unstaked"""
        position = self.positions.get(position_id)
        if not position:
            return False
        
        if position.unlocks_at is None:
            return True
        
        return datetime.utcnow() >= position.unlocks_at
    
    def unstake(self, position_id: str) -> Optional[float]:
        """
        Unstake a position
        
        Returns:
            Amount unstaked (including rewards) if successful
        """
        if not self.can_unstake(position_id):
            return None
        
        position = self.positions.get(position_id)
        if not position:
            return None
        
        # Calculate final rewards
        self.calculate_rewards(position_id)
        
        total_amount = position.amount + position.rewards_earned
        
        # Remove position
        del self.positions[position_id]
        if position.user_address in self.user_positions:
            self.user_positions[position.user_address].remove(position_id)
        
        return total_amount
    
    def calculate_rewards(self, position_id: str) -> float:
        """
        Calculate accumulated rewards for a position
        
        Returns:
            Rewards earned
        """
        position = self.positions.get(position_id)
        if not position:
            return 0.0
        
        # Calculate time staked
        time_staked = datetime.utcnow() - position.staked_at
        years_staked = time_staked.total_seconds() / (365.25 * 24 * 3600)
        
        # Calculate rewards (compound interest)
        rewards = position.amount * (
            (1 + self.reward_rate) ** years_staked - 1
        )
        
        # Add lock bonus (10% bonus per month locked)
        if position.lock_period_days > 0:
            lock_bonus = (position.lock_period_days / 30) * 0.1
            rewards *= (1 + lock_bonus)
        
        position.rewards_earned = rewards
        return rewards
    
    def get_staking_stats(self) -> Dict[str, float]:
        """Get staking statistics"""
        total_staked = sum(p.amount for p in self.positions.values())
        total_rewards = sum(
            self.calculate_rewards(pid)
            for pid in self.positions.keys()
        )
        
        return {
            "total_staked": total_staked,
            "total_positions": len(self.positions),
            "unique_stakers": len(self.user_positions),
            "total_rewards_pending": total_rewards,
            "average_stake": total_staked / len(self.positions) if self.positions else 0
        }
