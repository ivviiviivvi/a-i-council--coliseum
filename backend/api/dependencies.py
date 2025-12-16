"""
API Dependencies

Provides dependency injection for API endpoints.
"""

from typing import Optional
from backend.ai_agents.orchestrator import SystemOrchestrator
from backend.voting.achievements import AchievementSystem

_orchestrator: Optional[SystemOrchestrator] = None
_achievement_system: Optional[AchievementSystem] = None

def get_orchestrator() -> SystemOrchestrator:
    """
    Get the global SystemOrchestrator instance.
    Initializes it if not already initialized.
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SystemOrchestrator()
    return _orchestrator

def get_achievement_system() -> AchievementSystem:
    """
    Get the global AchievementSystem instance.
    Initializes it if not already initialized.
    """
    global _achievement_system
    if _achievement_system is None:
        _achievement_system = AchievementSystem()
    return _achievement_system
