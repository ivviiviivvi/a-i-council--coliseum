"""
System Orchestrator Module

Manages the lifecycle of AI agents and the main event loop of the council.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import logging

from .agent import Agent, AgentRole, Message
from .communication import AgentCommunicationProtocol
from .decision_engine import DecisionEngine
from ..event_pipeline.ingestion import EventIngestionSystem
from ..voting.voting_engine import VotingEngine

logger = logging.getLogger(__name__)

class SystemOrchestrator:
    """
    The central nervous system of the AI Council.

    Responsibilities:
    - Manage agent lifecycles (spawn, kill, pause)
    - Run the main "tick" loop for continuous operation
    - Coordinate between Agents, Event Pipeline, and Voting Engine
    """

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.is_running = False
        self.tick_rate = 1.0  # Seconds between ticks
        self.loop_task: Optional[asyncio.Task] = None

        # Initialize Subsystems
        self.communication_protocol = AgentCommunicationProtocol()
        self.event_system = EventIngestionSystem()
        self.voting_engine = VotingEngine()
        self.decision_engine = DecisionEngine()

    def add_agent(self, agent: Agent) -> None:
        """Register a new agent with the system"""
        self.agents[agent.state.agent_id] = agent
        self.communication_protocol.register_agent(agent)
        logger.info(f"Agent {agent.name} ({agent.state.role}) added.")

    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the system"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            self.communication_protocol.unregister_agent(agent_id)
            del self.agents[agent_id]
            logger.info(f"Agent {agent.name} removed.")

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    async def start(self) -> None:
        """Start the orchestrator and main loop"""
        if self.is_running:
            return

        self.is_running = True

        # Start communication protocol
        asyncio.create_task(self.communication_protocol.start())

        # Start main loop
        self.loop_task = asyncio.create_task(self._main_loop())
        logger.info("System Orchestrator started.")

    async def stop(self) -> None:
        """Stop the orchestrator"""
        self.is_running = False
        if self.loop_task:
            self.loop_task.cancel()
            try:
                await self.loop_task
            except asyncio.CancelledError:
                pass

        await self.communication_protocol.stop()
        logger.info("System Orchestrator stopped.")

    async def _main_loop(self) -> None:
        """Main system loop"""
        while self.is_running:
            try:
                await self._tick()
                await asyncio.sleep(self.tick_rate)
            except Exception as e:
                logger.error(f"Error in main loop: {e}")

    async def _tick(self) -> None:
        """
        Single system tick.

        1. Process pending messages
        2. Allow agents to reflect/act based on new events
        3. Check for expired voting sessions
        """
        # 1. Communication is handled by its own loop, but we can check status

        # 2. Check for new events from pipeline (mocked for now)
        # events = self.event_system.get_recent_events(limit=5)
        # For each agent, notify if there's a new event they haven't seen?
        # This would be done via broadcasting a message to agents.

        # 3. Random background chatter or "thinking"
        # In a real system, we might pick a random agent to start a conversation
        # if silence persists for too long.
        pass

    async def broadcast_event(self, event_content: str) -> None:
        """
        Manually inject an event/message to all agents
        """
        # Create a system message
        await self.communication_protocol.broadcast_message(
            sender_id="SYSTEM",
            content=event_content
        )
