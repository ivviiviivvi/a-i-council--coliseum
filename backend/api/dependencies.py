"""
API Dependencies

Provides dependency injection for API endpoints.
"""

from typing import Optional
from backend.ai_agents.orchestrator import SystemOrchestrator
from backend.voting.voting_engine import VotingEngine

_orchestrator: Optional[SystemOrchestrator] = None
_voting_engine: Optional[VotingEngine] = None

def get_orchestrator() -> SystemOrchestrator:
    """
    Get the global SystemOrchestrator instance.
    Initializes it if not already initialized.
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SystemOrchestrator()
    return _orchestrator

def get_voting_engine() -> VotingEngine:
    """
    Get the global VotingEngine instance.
    Initializes it if not already initialized.
    """
    global _voting_engine
    if _voting_engine is None:
        _voting_engine = VotingEngine()
    return _voting_engine
