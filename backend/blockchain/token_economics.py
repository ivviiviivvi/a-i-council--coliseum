"""
Token Economics Module

Manages token economics including supply, distribution, and incentives.
"""

from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime


class TokenConfig(BaseModel):
    """Token configuration"""
    name: str = "CouncilToken"
    symbol: str = "COUNCIL"
    decimals: int = 9
    total_supply: float = 1_000_000_000
    initial_circulation: float = 100_000_000


class TokenEconomics:
    """
    Token economics management system
    """
    
    def __init__(self, config: TokenConfig):
        self.config = config
        self.balances: Dict[str, float] = {}
        self.total_staked: float = 0.0
        self.reward_pool: float = config.total_supply * 0.3  # 30% for rewards
        self.voting_rewards: float = 0.0
        self.council_rewards: float = 0.0
    
    def get_balance(self, address: str) -> float:
        """Get token balance for address"""
        return self.balances.get(address, 0.0)
    
    def transfer(
        self,
        from_address: str,
        to_address: str,
        amount: float
    ) -> bool:
        """Transfer tokens between addresses"""
        if self.get_balance(from_address) < amount:
            return False
        
        self.balances[from_address] = self.get_balance(from_address) - amount
        self.balances[to_address] = self.get_balance(to_address) + amount
        return True
    
    def stake(self, address: str, amount: float) -> bool:
        """Stake tokens"""
        if self.get_balance(address) < amount:
            return False
        
        self.balances[address] -= amount
        self.total_staked += amount
        return True
    
    def unstake(self, address: str, amount: float) -> bool:
        """Unstake tokens"""
        if amount > self.total_staked:
            return False
        
        self.balances[address] += amount
        self.total_staked -= amount
        return True
    
    def calculate_voting_reward(
        self,
        votes_cast: int,
        total_votes: int
    ) -> float:
        """Calculate reward for voting participation"""
        if total_votes == 0:
            return 0.0
        
        base_reward = 10.0  # Base reward per vote
        participation_bonus = (votes_cast / total_votes) * 5.0
        return base_reward + participation_bonus
    
    def calculate_council_reward(
        self,
        sessions_participated: int,
        performance_score: float
    ) -> float:
        """Calculate reward for council participation"""
        base_reward = 100.0  # Base reward per session
        performance_multiplier = 1.0 + (performance_score * 0.5)
        return base_reward * sessions_participated * performance_multiplier
    
    def allocate_rewards(
        self,
        recipients: Dict[str, float]
    ) -> bool:
        """Allocate rewards from reward pool"""
        total_allocation = sum(recipients.values())
        
        if total_allocation > self.reward_pool:
            return False
        
        for address, amount in recipients.items():
            self.balances[address] = self.get_balance(address) + amount
        
        self.reward_pool -= total_allocation
        return True
    
    def get_economics_stats(self) -> Dict[str, Any]:
        """Get token economics statistics"""
        return {
            "total_supply": self.config.total_supply,
            "circulating_supply": sum(self.balances.values()),
            "total_staked": self.total_staked,
            "reward_pool": self.reward_pool,
            "unique_holders": len(self.balances)
        }
