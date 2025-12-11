"""
Reward Distribution Module

Manages reward distribution to users based on participation.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid


class RewardType(str, Enum):
    """Types of rewards"""
    VOTING = "voting"
    STAKING = "staking"
    COUNCIL_PARTICIPATION = "council_participation"
    ACHIEVEMENT = "achievement"
    REFERRAL = "referral"
    BONUS = "bonus"


class RewardClaim(BaseModel):
    """A reward claim"""
    claim_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_address: str
    reward_type: RewardType
    amount: float
    description: str
    claimed: bool = False
    claimed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class RewardDistribution:
    """
    System for distributing rewards to users
    """
    
    def __init__(self, reward_pool: float = 1_000_000):
        self.reward_pool = reward_pool
        self.claims: Dict[str, RewardClaim] = {}
        self.user_claims: Dict[str, List[str]] = {}
        self.distributed_rewards: float = 0.0
    
    def create_reward_claim(
        self,
        user_address: str,
        reward_type: RewardType,
        amount: float,
        description: str,
        expires_days: Optional[int] = None
    ) -> Optional[RewardClaim]:
        """
        Create a reward claim for a user
        
        Args:
            user_address: User's address
            reward_type: Type of reward
            amount: Reward amount
            description: Description of reward
            expires_days: Optional expiration in days
            
        Returns:
            Reward claim if successful
        """
        if amount > self.reward_pool:
            return None
        
        claim = RewardClaim(
            user_address=user_address,
            reward_type=reward_type,
            amount=amount,
            description=description
        )
        
        if expires_days:
            from datetime import timedelta
            claim.expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        self.claims[claim.claim_id] = claim
        
        if user_address not in self.user_claims:
            self.user_claims[user_address] = []
        self.user_claims[user_address].append(claim.claim_id)
        
        return claim
    
    def claim_reward(self, claim_id: str) -> Optional[float]:
        """
        Claim a reward
        
        Returns:
            Claimed amount if successful
        """
        claim = self.claims.get(claim_id)
        if not claim:
            return None
        
        if claim.claimed:
            return None
        
        # Check expiration
        if claim.expires_at and datetime.utcnow() > claim.expires_at:
            return None
        
        if claim.amount > self.reward_pool:
            return None
        
        claim.claimed = True
        claim.claimed_at = datetime.utcnow()
        self.reward_pool -= claim.amount
        self.distributed_rewards += claim.amount
        
        return claim.amount
    
    def get_user_claims(
        self,
        user_address: str,
        claimed: Optional[bool] = None
    ) -> List[RewardClaim]:
        """
        Get reward claims for a user
        
        Args:
            user_address: User's address
            claimed: Filter by claimed status (None = all)
            
        Returns:
            List of reward claims
        """
        claim_ids = self.user_claims.get(user_address, [])
        claims = [
            self.claims[cid]
            for cid in claim_ids
            if cid in self.claims
        ]
        
        if claimed is not None:
            claims = [c for c in claims if c.claimed == claimed]
        
        return claims
    
    def get_pending_rewards(self, user_address: str) -> float:
        """Get total pending (unclaimed) rewards for user"""
        claims = self.get_user_claims(user_address, claimed=False)
        return sum(c.amount for c in claims)
    
    def get_total_earned(self, user_address: str) -> float:
        """Get total rewards earned (claimed + unclaimed) for user"""
        claims = self.get_user_claims(user_address)
        return sum(c.amount for c in claims)
    
    def distribute_batch_rewards(
        self,
        rewards: Dict[str, float],
        reward_type: RewardType,
        description: str
    ) -> int:
        """
        Distribute rewards to multiple users
        
        Returns:
            Number of successful claims created
        """
        created = 0
        for user_address, amount in rewards.items():
            claim = self.create_reward_claim(
                user_address=user_address,
                reward_type=reward_type,
                amount=amount,
                description=description
            )
            if claim:
                created += 1
        
        return created
    
    def get_distribution_stats(self) -> Dict[str, float]:
        """Get reward distribution statistics"""
        total_claims = len(self.claims)
        claimed_count = sum(1 for c in self.claims.values() if c.claimed)
        
        return {
            "reward_pool_remaining": self.reward_pool,
            "total_distributed": self.distributed_rewards,
            "total_claims": total_claims,
            "claimed_count": claimed_count,
            "pending_count": total_claims - claimed_count
        }
