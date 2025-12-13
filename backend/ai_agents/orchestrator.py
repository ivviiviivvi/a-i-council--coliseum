"""
System Orchestrator Module

Manages the lifecycle of AI agents and coordinates system-wide activities.
"""

from typing import Dict, List, Optional
import asyncio
from .base_agent import AgentRole, Message
from .agent import Agent
from .memory_manager import MemoryManager
from .knowledge_base import KnowledgeBase
from .decision_engine import DecisionEngine

class SystemOrchestrator:
    """
    Orchestrates the AI Council system.
    Manages agents, distributes messages, and coordinates activities.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemOrchestrator, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.agents: Dict[str, Agent] = {}
        self.active = False
        self.memory_manager = MemoryManager()
        self.knowledge_base = KnowledgeBase()
        self.decision_engine = DecisionEngine()
        self._initialized = True

    def register_agent(self, agent: Agent) -> str:
        """Register a new agent with the system"""
        # Inject shared components if they are using defaults
        # Note: In a real system we might force sharing, but here we just register
        self.agents[agent.state.agent_id] = agent
        return agent.state.agent_id

    def create_agent(self, role: AgentRole, config: Optional[Dict] = None) -> Agent:
        """Create and register a new agent"""
        agent = Agent(
            role=role,
            config=config,
            knowledge_base=self.knowledge_base,
            decision_engine=self.decision_engine
            # We give them their own memory manager, but share knowledge and decisions
        )
        self.register_agent(agent)
        return agent

    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the system"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False

    async def broadcast_message(self, message: Message) -> None:
        """Broadcast a message to all active agents"""
        tasks = []
        for agent in self.agents.values():
            if agent.state.is_active:
                tasks.append(agent.process_message(message))

        # Gather responses
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process responses (if any agents replied)
        for response in responses:
            if isinstance(response, Message):
                # Handle agent response (e.g. log it, or re-broadcast if needed)
                # For now, we just print it
                print(f"Agent {response.sender_id} replied: {response.content}")

    async def start(self):
        """Start the orchestration loop"""
        self.active = True
        print("System Orchestrator started.")
        # In a real app, this might start a background loop

    async def stop(self):
        """Stop the orchestration loop"""
        self.active = False
        print("System Orchestrator stopped.")

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    def get_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """Get all agents with a specific role"""
        return [a for a in self.agents.values() if a.state.role == role]
