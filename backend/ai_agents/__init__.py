"""AI Agent Framework Package"""

from .base_agent import BaseAgent, AgentRole, AgentState, Message
from .communication import AgentCommunicationProtocol
from .decision_engine import DecisionEngine
from .nlp_module import NLPProcessor
from .knowledge_base import KnowledgeBase
from .memory_manager import MemoryManager
from .coordination import CoordinationSystem

__all__ = [
    'BaseAgent',
    'AgentRole',
    'AgentState',
    'Message',
    'AgentCommunicationProtocol',
    'DecisionEngine',
    'NLPProcessor',
    'KnowledgeBase',
    'MemoryManager',
    'CoordinationSystem',
]
