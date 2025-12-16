"""
API Dependencies

Provides dependency injection for API endpoints.
"""

import os
from typing import Optional
from backend.ai_agents.orchestrator import SystemOrchestrator
from backend.blockchain.solana_contracts import SolanaContractManager

_orchestrator: Optional[SystemOrchestrator] = None
_solana_manager: Optional[SolanaContractManager] = None

def get_orchestrator() -> SystemOrchestrator:
    """
    Get the global SystemOrchestrator instance.
    Initializes it if not already initialized.
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SystemOrchestrator()
    return _orchestrator

def get_solana_manager() -> SolanaContractManager:
    """
    Get the global SolanaContractManager instance.
    Initializes it if not already initialized.
    """
    global _solana_manager
    if _solana_manager is None:
        rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        program_id = os.getenv("SOLANA_PROGRAM_ID", "mock_program_id")
        _solana_manager = SolanaContractManager(rpc_url, program_id)
    return _solana_manager
