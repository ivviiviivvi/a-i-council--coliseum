"""
Event Prioritization Module

Prioritizes events based on various factors.
"""

from typing import Dict, Any
from datetime import datetime, timedelta

from .ingestion import NormalizedEvent
from .classification import EventClassifier


class EventPrioritizer:
    """
    System for prioritizing events
    """
    
    def __init__(self, classifier: EventClassifier):
        self.classifier = classifier
        self.category_weights: Dict[str, float] = {
            "breaking_news": 2.0,
            "politics": 1.5,
            "international": 1.4,
            "economics": 1.3,
            "technology": 1.2,
            "science": 1.1,
            "health": 1.1,
            "environment": 1.0,
            "sports": 0.8,
            "entertainment": 0.7,
            "other": 0.5,
        }
    
    async def calculate_priority(self, event: NormalizedEvent) -> float:
        """
        Calculate priority score for an event
        
        Args:
            event: Event to prioritize
            
        Returns:
            Priority score (higher is more important)
        """
        score = 1.0
        
        # Category weight
        category = await self.classifier.get_primary_category(event)
        score *= self.category_weights.get(category.value, 1.0)
        
        # Breaking news boost
        if self.classifier.is_breaking_news(event):
            score *= 2.0
        
        # Recency boost (events in last hour get boost)
        age = datetime.utcnow() - event.timestamp
        if age < timedelta(hours=1):
            score *= 1.5
        elif age < timedelta(hours=6):
            score *= 1.2
        
        # Content quality (longer descriptions = higher quality)
        if event.description and len(event.description) > 200:
            score *= 1.1
        
        return score
    
    async def rank_events(
        self,
        events: list[NormalizedEvent]
    ) -> list[tuple[NormalizedEvent, float]]:
        """
        Rank a list of events by priority
        
        Args:
            events: Events to rank
            
        Returns:
            List of (event, priority_score) tuples sorted by priority
        """
        scored_events = []
        for event in events:
            score = await self.calculate_priority(event)
            scored_events.append((event, score))
        
        scored_events.sort(key=lambda x: x[1], reverse=True)
        return scored_events
    
    def set_category_weight(self, category: str, weight: float) -> None:
        """
        Set priority weight for a category
        
        Args:
            category: Category name
            weight: Weight multiplier
        """
        self.category_weights[category] = weight
