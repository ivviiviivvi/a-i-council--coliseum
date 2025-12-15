"""
Event Processing Module

Processes events through various transformations and enrichments.
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import re

from .ingestion import NormalizedEvent


class ProcessedEvent(NormalizedEvent):
    """Event after processing with enrichments"""
    sentiment: Optional[Dict[str, float]] = None
    entities: Optional[List[Dict[str, Any]]] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    priority_score: Optional[float] = None
    processing_timestamp: datetime = None
    
    def __init__(self, **data):
        super().__init__(**data)
        self.processing_timestamp = datetime.utcnow()


class EventProcessor:
    """
    Processes events with enrichments and transformations
    """
    
    def __init__(self):
        self.processors: List[Callable] = []
        self.enrichers: Dict[str, Callable] = {}

        # Register default enrichers
        self.add_enricher("sentiment", self.enrich_sentiment)
        self.add_enricher("entities", self.enrich_entities)
        self.add_enricher("summary", self.enrich_summary)
        self.add_enricher("keywords", self.enrich_keywords)
    
    def add_processor(self, processor: Callable) -> None:
        """Add a processing function"""
        self.processors.append(processor)
    
    def add_enricher(self, name: str, enricher: Callable) -> None:
        """Add an enrichment function"""
        self.enrichers[name] = enricher
    
    async def process_event(
        self,
        event: NormalizedEvent,
        enrichments: Optional[List[str]] = None
    ) -> ProcessedEvent:
        """
        Process event through pipeline
        
        Args:
            event: Event to process
            enrichments: Optional list of enrichments to apply
            
        Returns:
            Processed event
        """
        # Convert to ProcessedEvent
        processed = ProcessedEvent(**event.model_dump())
        
        # Apply processors
        for processor in self.processors:
            try:
                processed = await processor(processed)
            except Exception as e:
                print(f"Error in processor: {e}")
        
        # Apply enrichments
        if enrichments:
            for enrichment_name in enrichments:
                if enrichment_name in self.enrichers:
                    try:
                        enricher = self.enrichers[enrichment_name]
                        processed = await enricher(processed)
                    except Exception as e:
                        print(f"Error in enrichment {enrichment_name}: {e}")
        
        return processed
    
    async def batch_process(
        self,
        events: List[NormalizedEvent],
        enrichments: Optional[List[str]] = None
    ) -> List[ProcessedEvent]:
        """Process multiple events"""
        processed_events = []
        for event in events:
            processed = await self.process_event(event, enrichments)
            processed_events.append(processed)
        return processed_events
    
    async def enrich_sentiment(self, event: ProcessedEvent) -> ProcessedEvent:
        """Add sentiment analysis enrichment"""
        text = f"{event.title} {event.description}".lower()

        positive_words = ["good", "great", "excellent", "positive", "success", "growth", "win", "benefit"]
        negative_words = ["bad", "poor", "negative", "failure", "decline", "loss", "risk", "crisis", "warn"]

        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)

        total = pos_count + neg_count + 1  # Avoid division by zero

        event.sentiment = {
            "positive": pos_count / total,
            "negative": neg_count / total,
            "neutral": 1.0 - ((pos_count + neg_count) / total)
        }
        return event
    
    async def enrich_entities(self, event: ProcessedEvent) -> ProcessedEvent:
        """Add entity extraction enrichment"""
        text = f"{event.title} {event.description}"

        # Simple heuristic: look for capitalized words that are not at start of sentence
        # This is a very basic approximation
        entities = []
        words = text.split()
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word and clean_word[0].isupper() and i > 0:
                # Check if previous word ended with punctuation
                prev_word = words[i-1]
                if not prev_word.endswith('.'):
                    entities.append({"text": clean_word, "type": "unknown"})

        # Remove duplicates
        unique_entities = []
        seen = set()
        for e in entities:
            if e["text"] not in seen:
                unique_entities.append(e)
                seen.add(e["text"])

        event.entities = unique_entities
        return event
    
    async def enrich_summary(self, event: ProcessedEvent) -> ProcessedEvent:
        """Add summary enrichment"""
        if event.description:
            # Simple summary: First sentence
            sentences = re.split(r'(?<=[.!?]) +', event.description)
            event.summary = sentences[0] if sentences else event.description[:100]
            if len(event.summary) > 200:
                event.summary = event.summary[:197] + "..."
        else:
            event.summary = event.title
        return event
    
    async def enrich_keywords(self, event: ProcessedEvent) -> ProcessedEvent:
        """Add keyword extraction enrichment"""
        text = f"{event.title} {event.description}".lower()
        words = re.findall(r'\b\w+\b', text)

        stop_words = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "with", "is", "are", "was", "were", "and", "or", "but"}

        word_freq = {}
        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top 10 keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        event.keywords = [word for word, _ in sorted_words[:10]]
        return event
