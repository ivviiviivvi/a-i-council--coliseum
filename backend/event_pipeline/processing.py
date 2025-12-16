"""
Event Processing Module

Processes events through various transformations and enrichments.
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

from .ingestion import NormalizedEvent
from backend.ai_agents.nlp_module import NLPProcessor


class ProcessedEvent(NormalizedEvent):
    """Event after processing with enrichments"""
    sentiment: Optional[Dict[str, float]] = None
    entities: Optional[List[Dict[str, Any]]] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    priority_score: Optional[float] = None
    processing_timestamp: Optional[datetime] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.processing_timestamp is None:
            self.processing_timestamp = datetime.utcnow()


class EventProcessor:
    """
    Processes events with enrichments and transformations
    """
    
    def __init__(self, nlp_processor: Optional[NLPProcessor] = None):
        self.processors: List[Callable] = []
        self.enrichers: Dict[str, Callable] = {}
        self.nlp = nlp_processor or NLPProcessor()
    
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
        # Integrate with NLP module
        text = f"{event.title} {event.description}"
        result = await self.nlp.analyze_sentiment(text)

        # Map NLP result (label, score) to sentiment distribution
        label = result.get("sentiment", "neutral").lower()
        score = result.get("score", 0.0)

        # Initialize distribution
        distribution = {
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 0.0
        }

        # Heuristic mapping: assign score to label, distribute remainder
        if label in distribution:
            distribution[label] = score
            remaining = 1.0 - score
            others = [k for k in distribution if k != label]
            if others:
                split = remaining / len(others)
                for k in others:
                    distribution[k] = split
        else:
            # Fallback for unknown labels
            distribution["neutral"] = 1.0

        event.sentiment = distribution
        return event
    
    async def enrich_entities(self, event: ProcessedEvent) -> ProcessedEvent:
        """Add entity extraction enrichment"""
        # Placeholder for actual entity extraction
        event.entities = []
        return event
    
    async def enrich_summary(self, event: ProcessedEvent) -> ProcessedEvent:
        """Add summary enrichment"""
        # Placeholder for actual summarization
        if event.description and len(event.description) > 100:
            event.summary = event.description[:100] + "..."
        else:
            event.summary = event.description
        return event
    
    async def enrich_keywords(self, event: ProcessedEvent) -> ProcessedEvent:
        """Add keyword extraction enrichment"""
        # Placeholder for actual keyword extraction
        text = f"{event.title} {event.description}".lower()
        words = text.split()
        # Simple word frequency
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Only longer words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top 5 keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        event.keywords = [word for word, _ in sorted_words[:5]]
        return event
