"""
Concrete Agent Implementation

This module provides the concrete implementation of the AI Agent,
integrating all core modules (Memory, Knowledge, NLP, Decision Engine).
"""

from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent, AgentRole, Message
from .memory_manager import MemoryManager
from .knowledge_base import KnowledgeBase
from .decision_engine import DecisionEngine
from .nlp_module import NLPProcessor

class Agent(BaseAgent):
    """
    Concrete implementation of an AI Agent.
    Integrates Memory, Knowledge, NLP, and Decision making capabilities.
    """

    def __init__(
        self,
        role: AgentRole,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[MemoryManager] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        decision_engine: Optional[DecisionEngine] = None,
        nlp_processor: Optional[NLPProcessor] = None
    ):
        super().__init__(role, config)
        self.memory_manager = memory_manager or MemoryManager()
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.decision_engine = decision_engine or DecisionEngine()
        self.nlp_processor = nlp_processor or NLPProcessor()

    async def process_message(self, message: Message) -> Optional[Message]:
        """
        Process incoming message, update memory, and potentially respond.
        """
        # Add to short term memory
        self.memory_manager.add_short_term(message.dict())

        # Analyze content
        sentiment = await self.nlp_processor.analyze_sentiment(message.content)
        topics = await self.nlp_processor.classify_topic(message.content)

        # Store analysis in memory
        self.add_to_memory("last_sentiment", sentiment)
        self.add_to_memory("last_topics", topics)

        # Decide if response is needed
        # Respond if addressed directly or if it's a broadcast and we are active
        should_respond = (
            message.recipient_id == self.state.agent_id or
            (message.recipient_id is None and self.state.is_active)
        )

        if should_respond:
            response_text = await self.generate_response(message.content)
            return Message(
                sender_id=self.state.agent_id,
                recipient_id=message.sender_id,
                content=response_text,
                metadata={
                    "sentiment_context": sentiment,
                    "topics": topics,
                    "responding_to": message.message_id
                }
            )
        return None

    async def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a decision using the DecisionEngine or internal logic.
        """
        decision_type = context.get("type", "internal")

        if decision_type == "vote":
            decision_id = context.get("decision_id")
            if not decision_id:
                return {"error": "No decision_id provided for vote"}

            # Logic to determine vote would go here, possibly using NLP and KnowledgeBase
            # For now, we simulate a random or default choice
            choice = context.get("default_choice", "yes")

            try:
                self.decision_engine.cast_vote(
                    decision_id=decision_id,
                    agent_id=self.state.agent_id,
                    choice=choice,
                    reasoning="Automated decision based on role configuration"
                )
                return {"status": "voted", "choice": choice}
            except ValueError as e:
                return {"error": str(e)}

        return {"status": "skipped", "reason": "Unknown decision type"}

    async def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response using NLP processor.
        """
        # Since NLPProcessor currently lacks generation, we use summarization as a proxy
        # or a simple template. In a real scenario, this would call an LLM.

        summary = await self.nlp_processor.summarize(prompt, max_length=50)

        role_prefixes = {
            AgentRole.MODERATOR: "As a moderator, I note:",
            AgentRole.DEBATER: "I argue that:",
            AgentRole.ANALYST: "Analysis shows:",
            AgentRole.FACT_CHECKER: "Fact check:",
        }

        prefix = role_prefixes.get(self.state.role, "Response:")
        return f"{prefix} {summary} (processed by {self.state.agent_id})"
