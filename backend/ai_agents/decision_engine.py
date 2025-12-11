"""
Decision Engine Module

Provides decision-making capabilities for AI agents including
voting, consensus building, and weighted decision mechanisms.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class DecisionType(str, Enum):
    """Types of decisions the engine can make"""
    BINARY = "binary"  # Yes/No
    MULTIPLE_CHOICE = "multiple_choice"
    RANKED = "ranked"
    WEIGHTED = "weighted"
    CONSENSUS = "consensus"


class Vote(BaseModel):
    """Individual vote from an agent"""
    vote_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    decision_id: str
    choice: Any
    weight: float = 1.0
    reasoning: Optional[str] = None
    confidence: float = 1.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Decision(BaseModel):
    """A decision to be made by the agents"""
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    decision_type: DecisionType
    options: List[Any]
    required_votes: int = 1
    votes: List[Vote] = Field(default_factory=list)
    deadline: Optional[datetime] = None
    result: Optional[Any] = None
    is_finalized: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DecisionEngine:
    """
    Decision-making engine for AI agents.
    Handles voting, consensus building, and decision aggregation.
    """
    
    def __init__(self):
        self.decisions: Dict[str, Decision] = {}
        self.voting_strategies = {
            DecisionType.BINARY: self._binary_decision,
            DecisionType.MULTIPLE_CHOICE: self._multiple_choice_decision,
            DecisionType.RANKED: self._ranked_decision,
            DecisionType.WEIGHTED: self._weighted_decision,
            DecisionType.CONSENSUS: self._consensus_decision,
        }
    
    def create_decision(
        self,
        title: str,
        description: str,
        decision_type: DecisionType,
        options: List[Any],
        required_votes: int = 1,
        deadline: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Decision:
        """Create a new decision"""
        decision = Decision(
            title=title,
            description=description,
            decision_type=decision_type,
            options=options,
            required_votes=required_votes,
            deadline=deadline,
            metadata=metadata or {}
        )
        self.decisions[decision.decision_id] = decision
        return decision
    
    def cast_vote(
        self,
        decision_id: str,
        agent_id: str,
        choice: Any,
        weight: float = 1.0,
        reasoning: Optional[str] = None,
        confidence: float = 1.0
    ) -> Vote:
        """Cast a vote for a decision"""
        if decision_id not in self.decisions:
            raise ValueError(f"Decision {decision_id} not found")
        
        decision = self.decisions[decision_id]
        
        if decision.is_finalized:
            raise ValueError(f"Decision {decision_id} is already finalized")
        
        # Check if agent already voted
        existing_vote = next(
            (v for v in decision.votes if v.agent_id == agent_id),
            None
        )
        
        if existing_vote:
            raise ValueError(f"Agent {agent_id} has already voted")
        
        vote = Vote(
            agent_id=agent_id,
            decision_id=decision_id,
            choice=choice,
            weight=weight,
            reasoning=reasoning,
            confidence=confidence
        )
        
        decision.votes.append(vote)
        
        # Check if we can finalize
        if len(decision.votes) >= decision.required_votes:
            self.finalize_decision(decision_id)
        
        return vote
    
    def finalize_decision(self, decision_id: str) -> Any:
        """Finalize a decision and calculate the result"""
        if decision_id not in self.decisions:
            raise ValueError(f"Decision {decision_id} not found")
        
        decision = self.decisions[decision_id]
        
        if decision.is_finalized:
            return decision.result
        
        # Calculate result based on decision type
        strategy = self.voting_strategies.get(decision.decision_type)
        if strategy:
            decision.result = strategy(decision)
        
        decision.is_finalized = True
        return decision.result
    
    def _binary_decision(self, decision: Decision) -> bool:
        """Calculate binary decision result (majority wins)"""
        yes_votes = sum(
            v.weight for v in decision.votes 
            if v.choice in [True, "yes", "Yes", 1]
        )
        no_votes = sum(
            v.weight for v in decision.votes 
            if v.choice in [False, "no", "No", 0]
        )
        return yes_votes > no_votes
    
    def _multiple_choice_decision(self, decision: Decision) -> Any:
        """Calculate multiple choice decision (plurality wins)"""
        choice_weights: Dict[Any, float] = {}
        
        for vote in decision.votes:
            if vote.choice not in choice_weights:
                choice_weights[vote.choice] = 0
            choice_weights[vote.choice] += vote.weight
        
        if not choice_weights:
            return None
        
        return max(choice_weights.items(), key=lambda x: x[1])[0]
    
    def _ranked_decision(self, decision: Decision) -> List[Any]:
        """Calculate ranked decision using ranked-choice voting"""
        # Simplified implementation - returns options sorted by total weight
        choice_weights: Dict[Any, float] = {}
        
        for vote in decision.votes:
            if isinstance(vote.choice, list):
                # Ranked list
                for idx, choice in enumerate(vote.choice):
                    if choice not in choice_weights:
                        choice_weights[choice] = 0
                    # Higher rank = more weight
                    choice_weights[choice] += vote.weight * (len(vote.choice) - idx)
        
        sorted_choices = sorted(
            choice_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [choice for choice, _ in sorted_choices]
    
    def _weighted_decision(self, decision: Decision) -> Dict[Any, float]:
        """Calculate weighted decision (returns all options with weights)"""
        choice_weights: Dict[Any, float] = {}
        
        for vote in decision.votes:
            if vote.choice not in choice_weights:
                choice_weights[vote.choice] = 0
            choice_weights[vote.choice] += vote.weight * vote.confidence
        
        # Normalize weights
        total = sum(choice_weights.values())
        if total > 0:
            choice_weights = {
                choice: weight / total 
                for choice, weight in choice_weights.items()
            }
        
        return choice_weights
    
    def _consensus_decision(self, decision: Decision) -> Optional[Any]:
        """Calculate consensus decision (requires agreement threshold)"""
        threshold = decision.metadata.get("consensus_threshold", 0.8)
        
        choice_weights: Dict[Any, float] = {}
        total_weight = sum(v.weight for v in decision.votes)
        
        for vote in decision.votes:
            if vote.choice not in choice_weights:
                choice_weights[vote.choice] = 0
            choice_weights[vote.choice] += vote.weight
        
        if not choice_weights:
            return None
        
        # Check if any choice meets consensus threshold
        for choice, weight in choice_weights.items():
            if weight / total_weight >= threshold:
                return choice
        
        return None  # No consensus reached
    
    def get_decision(self, decision_id: str) -> Optional[Decision]:
        """Get a decision by ID"""
        return self.decisions.get(decision_id)
    
    def get_active_decisions(self) -> List[Decision]:
        """Get all active (non-finalized) decisions"""
        return [
            d for d in self.decisions.values()
            if not d.is_finalized
        ]
