"""
API Dependencies

Provides dependency injection for API endpoints.
"""

from typing import Optional
from backend.ai_agents.orchestrator import SystemOrchestrator

_orchestrator: Optional[SystemOrchestrator] = None

def get_orchestrator() -> SystemOrchestrator:
    """
    Get the global SystemOrchestrator instance.
    Initializes it if not already initialized.
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SystemOrchestrator()
    return _orchestrator
