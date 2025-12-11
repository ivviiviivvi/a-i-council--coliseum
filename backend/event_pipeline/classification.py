"""
Event Classification Module

Classifies events into categories and topics.
"""

from typing import Dict, Any, List, Optional
from enum import Enum

from .ingestion import NormalizedEvent


class EventCategory(str, Enum):
    """Event categories"""
    POLITICS = "politics"
    ECONOMICS = "economics"
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    ENTERTAINMENT = "entertainment"
    SPORTS = "sports"
    HEALTH = "health"
    ENVIRONMENT = "environment"
    INTERNATIONAL = "international"
    BREAKING_NEWS = "breaking_news"
    OTHER = "other"


class EventClassifier:
    """
    Classifier for categorizing events
    """
    
    def __init__(self):
        self.keyword_categories: Dict[str, List[str]] = {
            "politics": ["election", "government", "policy", "president", "congress"],
            "economics": ["market", "stock", "economy", "trade", "gdp", "inflation"],
            "technology": ["ai", "software", "hardware", "tech", "digital", "cyber"],
            "science": ["research", "discovery", "study", "scientific", "space"],
            "entertainment": ["movie", "music", "celebrity", "film", "show"],
            "sports": ["game", "team", "player", "championship", "league"],
            "health": ["medical", "disease", "health", "hospital", "treatment"],
            "environment": ["climate", "environment", "pollution", "green", "ecology"],
            "international": ["global", "international", "foreign", "world"],
        }
    
    async def classify(self, event: NormalizedEvent) -> Dict[str, float]:
        """
        Classify event into categories with confidence scores
        
        Args:
            event: Event to classify
            
        Returns:
            Dict of category -> confidence score
        """
        text = f"{event.title} {event.description}".lower()
        scores: Dict[str, float] = {}
        
        for category, keywords in self.keyword_categories.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text:
                    score += 0.2
            scores[category] = min(score, 1.0)
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {cat: score / total for cat, score in scores.items()}
        
        return scores
    
    async def get_primary_category(self, event: NormalizedEvent) -> EventCategory:
        """
        Get the primary category for an event
        
        Args:
            event: Event to classify
            
        Returns:
            Primary category
        """
        scores = await self.classify(event)
        
        if not scores:
            return EventCategory.OTHER
        
        primary = max(scores.items(), key=lambda x: x[1])[0]
        
        try:
            return EventCategory(primary)
        except ValueError:
            return EventCategory.OTHER
    
    async def extract_topics(self, event: NormalizedEvent) -> List[str]:
        """
        Extract specific topics from event
        
        Args:
            event: Event to analyze
            
        Returns:
            List of topics
        """
        # Simple implementation - use existing tags plus extracted keywords
        topics = list(event.tags) if event.tags else []
        
        # Add category as topic
        category = await self.get_primary_category(event)
        if category.value not in topics:
            topics.append(category.value)
        
        return topics
    
    def is_breaking_news(self, event: NormalizedEvent) -> bool:
        """
        Determine if event is breaking news
        
        Args:
            event: Event to check
            
        Returns:
            True if breaking news
        """
        breaking_keywords = [
            "breaking", "urgent", "alert", "just in", "developing"
        ]
        
        text = f"{event.title} {event.description}".lower()
        return any(keyword in text for keyword in breaking_keywords)
