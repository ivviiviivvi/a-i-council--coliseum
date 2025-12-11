"""
AI Agent Framework - Base Module

This module provides the core abstractions for AI agents in the council system.
Agents can debate, vote, and participate in decision-making processes.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class AgentRole(str, Enum):
    """Roles an agent can take in the council"""
    MODERATOR = "moderator"
    DEBATER = "debater"
    ANALYST = "analyst"
    FACT_CHECKER = "fact_checker"
    SUMMARIZER = "summarizer"
    VOTER = "voter"
    OBSERVER = "observer"


class AgentState(BaseModel):
    """Current state of an agent"""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: AgentRole
    is_active: bool = True
    current_topic: Optional[str] = None
    memory: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)


class Message(BaseModel):
    """Message format for agent communication"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_id: Optional[str] = None  # None for broadcast
    content: str
    message_type: str = "text"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in the system.
    
    Each agent must implement core methods for:
    - Processing messages
    - Making decisions
    - Generating responses
    - Managing state
    """
    
    def __init__(self, role: AgentRole, config: Optional[Dict[str, Any]] = None):
        self.state = AgentState(role=role)
        self.config = config or {}
        self.message_history: List[Message] = []
    
    @abstractmethod
    async def process_message(self, message: Message) -> Optional[Message]:
        """
        Process incoming message and optionally return a response
        
        Args:
            message: Incoming message to process
            
        Returns:
            Optional response message
        """
        pass
    
    @abstractmethod
    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a decision based on current context
        
        Args:
            context: Decision context including relevant information
            
        Returns:
            Decision with reasoning and metadata
        """
        pass
    
    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response using the agent's AI model
        
        Args:
            prompt: Input prompt
            context: Additional context for generation
            
        Returns:
            Generated response text
        """
        pass
    
    def update_state(self, **kwargs) -> None:
        """Update agent state with new values"""
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
        self.state.last_active = datetime.utcnow()
    
    def add_to_memory(self, key: str, value: Any) -> None:
        """Add information to agent's memory"""
        self.state.memory[key] = value
    
    def get_from_memory(self, key: str) -> Optional[Any]:
        """Retrieve information from agent's memory"""
        return self.state.memory.get(key)
    
    def clear_memory(self) -> None:
        """Clear agent's memory"""
        self.state.memory.clear()
    
    async def activate(self) -> None:
        """Activate the agent"""
        self.update_state(is_active=True)
    
    async def deactivate(self) -> None:
        """Deactivate the agent"""
        self.update_state(is_active=False)
