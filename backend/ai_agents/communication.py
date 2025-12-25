"""
Agent Communication Protocol Module

Handles message routing, broadcasting, and agent-to-agent communication.
"""

from typing import List, Dict, Optional, Callable
from asyncio import Queue
import asyncio
from datetime import datetime

from .base_agent import BaseAgent, Message, AgentRole


class AgentCommunicationProtocol:
    """
    Manages communication between agents in the council system.
    Supports direct messaging, broadcasting, and topic-based routing.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: Queue = Queue()
        self.topic_subscribers: Dict[str, List[str]] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.is_running = False
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the communication system"""
        self.agents[agent.state.agent_id] = agent
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the communication system"""
        if agent_id in self.agents:
            del self.agents[agent_id]
        
        # Remove from topic subscriptions
        for topic in self.topic_subscribers:
            if agent_id in self.topic_subscribers[topic]:
                self.topic_subscribers[topic].remove(agent_id)
    
    def subscribe_to_topic(self, agent_id: str, topic: str) -> None:
        """Subscribe an agent to a topic"""
        if topic not in self.topic_subscribers:
            self.topic_subscribers[topic] = []
        if agent_id not in self.topic_subscribers[topic]:
            self.topic_subscribers[topic].append(agent_id)
    
    def unsubscribe_from_topic(self, agent_id: str, topic: str) -> None:
        """Unsubscribe an agent from a topic"""
        if topic in self.topic_subscribers:
            if agent_id in self.topic_subscribers[topic]:
                self.topic_subscribers[topic].remove(agent_id)
    
    async def send_message(self, message: Message) -> None:
        """Queue a message for delivery"""
        await self.message_queue.put(message)
    
    async def broadcast_message(self, sender_id: str, content: str, 
                               topic: Optional[str] = None) -> None:
        """
        Broadcast a message to all agents or to subscribers of a topic
        
        Args:
            sender_id: ID of the sending agent
            content: Message content
            topic: Optional topic to broadcast to specific subscribers
        """
        message = Message(
            sender_id=sender_id,
            recipient_id=None,
            content=content,
            metadata={"topic": topic} if topic else {}
        )
        
        if topic and topic in self.topic_subscribers:
            # Send to topic subscribers
            for agent_id in self.topic_subscribers[topic]:
                if agent_id != sender_id and agent_id in self.agents:
                    targeted_message = message.model_copy()
                    targeted_message.recipient_id = agent_id
                    await self.message_queue.put(targeted_message)
        else:
            # Broadcast to all agents
            await self.message_queue.put(message)
    
    async def send_direct_message(self, sender_id: str, recipient_id: str, 
                                 content: str) -> None:
        """
        Send a direct message to a specific agent
        
        Args:
            sender_id: ID of the sending agent
            recipient_id: ID of the recipient agent
            content: Message content
        """
        message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content
        )
        await self.message_queue.put(message)
    
    async def process_messages(self) -> None:
        """Process messages from the queue and deliver to agents"""
        while self.is_running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                
                # Deliver message
                if message.recipient_id:
                    # Direct message
                    if message.recipient_id in self.agents:
                        agent = self.agents[message.recipient_id]
                        if agent.state.is_active:
                            response = await agent.process_message(message)
                            if response:
                                await self.message_queue.put(response)
                else:
                    # Broadcast message
                    tasks = []
                    for agent_id, agent in self.agents.items():
                        if agent_id != message.sender_id and agent.state.is_active:
                            tasks.append(agent.process_message(message))

                    if tasks:
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        for result in results:
                            if isinstance(result, Exception):
                                print(f"Error processing broadcast message: {result}")
                            elif result:
                                await self.message_queue.put(result)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing message: {e}")
    
    async def start(self) -> None:
        """Start the communication protocol"""
        self.is_running = True
        await self.process_messages()
    
    async def stop(self) -> None:
        """Stop the communication protocol"""
        self.is_running = False
    
    def get_active_agents(self, role: Optional[AgentRole] = None) -> List[BaseAgent]:
        """
        Get list of active agents, optionally filtered by role
        
        Args:
            role: Optional role filter
            
        Returns:
            List of active agents
        """
        agents = [
            agent for agent in self.agents.values() 
            if agent.state.is_active
        ]
        
        if role:
            agents = [agent for agent in agents if agent.state.role == role]
        
        return agents
