import pytest
import asyncio
from datetime import datetime
from backend.event_pipeline.ingestion import EventIngestionSystem, EventSource
from backend.event_pipeline.classification import EventClassifier
from backend.event_pipeline.prioritization import EventPrioritizer
from backend.event_pipeline.routing import EventRouter
from backend.event_pipeline.processing import EventProcessor
from backend.event_pipeline.storage import EventStorage
from backend.event_pipeline.notification import NotificationSystem

@pytest.mark.asyncio
async def test_event_pipeline_flow():
    # 1. Setup Components
    ingestion = EventIngestionSystem()
    classifier = EventClassifier()
    prioritizer = EventPrioritizer(classifier)
    router = EventRouter()
    processor = EventProcessor()
    storage = EventStorage()
    notifications = NotificationSystem()

    # 2. Ingest Event
    raw_data = {
        "title": "AI Council Elections Begin",
        "description": "The first ever AI Council elections are starting today. Voters can stake tokens to participate.",
        "category": "politics",
        "tags": ["election", "ai", "governance"],
        "url": "https://example.com/election",
        "content": "Full content of the article..."
    }

    event = await ingestion.ingest_event(
        source=EventSource.API,
        raw_data=raw_data
    )

    assert event is not None
    assert event.title == "AI Council Elections Begin"

    # 3. Classify
    scores = await classifier.classify(event)
    primary_category = await classifier.get_primary_category(event)

    assert "politics" in scores
    assert primary_category.value == "politics"

    # 4. Prioritize
    priority = await prioritizer.calculate_priority(event)
    assert priority > 0

    # 5. Route (Mock handler)
    received_events = []
    async def handler(e):
        received_events.append(e)

    router.add_category_route("politics", handler)
    routed_count = await router.route_event(event, priority)

    assert routed_count >= 1
    assert len(received_events) == 1

    # 6. Process
    # Add simple processor
    async def uppercase_title(e):
        e.title = e.title.upper()
        return e

    processor.add_processor(uppercase_title)

    processed_event = await processor.process_event(event, enrichments=["sentiment", "entities", "summary", "keywords"])

    assert processed_event.title == "AI COUNCIL ELECTIONS BEGIN"
    assert processed_event.sentiment is not None # Check if enrichment worked
    assert processed_event.summary is not None

    # 7. Store
    stored = await storage.store_event(processed_event)
    assert stored is True

    retrieved = await storage.get_event(processed_event.event_id)
    assert retrieved is not None
    assert retrieved.title == "AI COUNCIL ELECTIONS BEGIN"

    # 8. Notify
    # Subscribe user
    notifications.subscribe("user1", "politics", ["in_app"])

    notifs = await notifications.notify_event(processed_event)
    assert len(notifs) >= 1
    assert notifs[0].recipient == "user1"

if __name__ == "__main__":
    asyncio.run(test_event_pipeline_flow())
