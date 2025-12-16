"""
API Dependencies

Provides dependency injection for API endpoints.
"""

from typing import Optional
from backend.ai_agents.orchestrator import SystemOrchestrator
from backend.blockchain.rewards import RewardDistribution

_orchestrator: Optional[SystemOrchestrator] = None
_reward_distribution: Optional[RewardDistribution] = None

def get_orchestrator() -> SystemOrchestrator:
    """
    Get the global SystemOrchestrator instance.
    Initializes it if not already initialized.
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SystemOrchestrator()
    return _orchestrator

def get_reward_distribution() -> RewardDistribution:
    """
    Get the global RewardDistribution instance.
    Initializes it if not already initialized.
    """
    global _reward_distribution
    if _reward_distribution is None:
        _reward_distribution = RewardDistribution()
    return _reward_distribution
