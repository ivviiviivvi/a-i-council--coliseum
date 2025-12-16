"""
API Dependencies

Provides dependency injection for API endpoints.
"""

from typing import Optional
from backend.ai_agents.orchestrator import SystemOrchestrator
from backend.voting.gamification import GamificationSystem
from backend.voting.leaderboard import LeaderboardSystem

_orchestrator: Optional[SystemOrchestrator] = None
_gamification_system: Optional[GamificationSystem] = None
_leaderboard_system: Optional[LeaderboardSystem] = None

def get_orchestrator() -> SystemOrchestrator:
    """
    Get the global SystemOrchestrator instance.
    Initializes it if not already initialized.
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SystemOrchestrator()
    return _orchestrator

def get_gamification_system() -> GamificationSystem:
    """
    Get the global GamificationSystem instance.
    Initializes it if not already initialized.
    """
    global _gamification_system
    if _gamification_system is None:
        _gamification_system = GamificationSystem()
    return _gamification_system

def get_leaderboard_system() -> LeaderboardSystem:
    """
    Get the global LeaderboardSystem instance.
    Initializes it if not already initialized.
    """
    global _leaderboard_system
    if _leaderboard_system is None:
        gamification = get_gamification_system()
        _leaderboard_system = LeaderboardSystem(gamification)
    return _leaderboard_system
