import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from backend.event_pipeline.processing import EventProcessor, ProcessedEvent
from backend.event_pipeline.ingestion import NormalizedEvent, EventSource
from backend.ai_agents.nlp_module import NLPProcessor

@pytest.mark.asyncio
async def test_enrich_sentiment_integration():
    # Mock NLPProcessor
    mock_nlp = MagicMock(spec=NLPProcessor)
    mock_nlp.analyze_sentiment = AsyncMock(return_value={
        "sentiment": "positive",
        "score": 0.9,
        "confidence": 0.95
    })

    # Initialize EventProcessor with mocked NLP
    processor = EventProcessor(nlp_processor=mock_nlp)

    # Create a dummy event
    event = ProcessedEvent(
        event_id="test_id_1",
        source=EventSource.INTERNAL,
        source_id="test_source",
        title="Test Event",
        description="This is a very positive event.",
        url="http://test.com",
        timestamp=datetime.now(),
        normalized_at=datetime.now()
    )

    # Call enrich_sentiment
    enriched_event = await processor.enrich_sentiment(event)

    # Verify NLP module was called
    mock_nlp.analyze_sentiment.assert_called_once()
    args, _ = mock_nlp.analyze_sentiment.call_args
    # It should pass the text (title + description usually, or just description)
    assert "Test Event" in args[0] or "positive event" in args[0]

    # Verify sentiment was populated in event
    assert enriched_event.sentiment is not None
    # We expect some mapping logic.
    # If we map 'positive' 0.9 to positive: 0.9, then:
    assert enriched_event.sentiment["positive"] == 0.9
    # The others should probably be present too
    assert "neutral" in enriched_event.sentiment
    assert "negative" in enriched_event.sentiment

@pytest.mark.asyncio
async def test_enrich_sentiment_default_nlp():
    # Test with default NLPProcessor (the placeholder)
    processor = EventProcessor() # Uses real NLPProcessor placeholder

    event = ProcessedEvent(
        event_id="test_id_2",
        source=EventSource.INTERNAL,
        source_id="test_source",
        title="Test Event",
        description="This is a test.",
        url="http://test.com",
        timestamp=datetime.now(),
        normalized_at=datetime.now()
    )

    enriched_event = await processor.enrich_sentiment(event)

    assert enriched_event.sentiment is not None
    # The placeholder returns "neutral", 0.5
    # So we expect neutral to be high-ish
    print(enriched_event.sentiment)
    assert enriched_event.sentiment["neutral"] > 0
