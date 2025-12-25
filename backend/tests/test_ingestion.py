
import pytest
import asyncio
from datetime import datetime, timedelta
from backend.event_pipeline.ingestion import EventIngestionSystem, EventSource, NormalizedEvent

@pytest.fixture
def ingestion_system():
    return EventIngestionSystem()

@pytest.fixture
def mock_events():
    events = []
    base_time = datetime(2023, 1, 1, 12, 0, 0)
    for i in range(10):
        events.append({
            "source": EventSource.API if i % 2 == 0 else EventSource.RSS_FEED,
            "raw_data": {"title": f"Event {i}", "description": "Test"},
            "timestamp": base_time + timedelta(minutes=i) # Increasing timestamps
        })
    return events

@pytest.mark.asyncio
async def test_get_recent_events_order_and_limit(ingestion_system, mock_events):
    # Ingest events
    for event_data in mock_events:
        # We need to manually set timestamps to ensure order for the test
        # but ingest_event uses utcnow.
        # So we will manually append to normalized_events to control the state exactly like in benchmark
        # Or better, we can modify normalized_events after ingestion if needed,
        # but let's just use ingestion and rely on sequential execution which guarantees order.
        await ingestion_system.ingest_event(
            source=event_data["source"],
            raw_data=event_data["raw_data"]
        )

    # Get recent 3 events
    recent = ingestion_system.get_recent_events(limit=3)

    assert len(recent) == 3
    # Should be reversed order of insertion (newest first)
    assert recent[0].title == "Event 9"
    assert recent[1].title == "Event 8"
    assert recent[2].title == "Event 7"

@pytest.mark.asyncio
async def test_get_recent_events_filter(ingestion_system, mock_events):
    for event_data in mock_events:
        await ingestion_system.ingest_event(
            source=event_data["source"],
            raw_data=event_data["raw_data"]
        )

    # Get recent API events (Even numbers: 0, 2, 4, 6, 8)
    # Newest API event is 8
    recent_api = ingestion_system.get_recent_events(limit=2, source=EventSource.API)

    assert len(recent_api) == 2
    assert recent_api[0].title == "Event 8"
    assert recent_api[1].title == "Event 6"
    assert recent_api[0].source == EventSource.API
    assert recent_api[1].source == EventSource.API

@pytest.mark.asyncio
async def test_get_recent_events_empty(ingestion_system):
    recent = ingestion_system.get_recent_events(limit=10)
    assert len(recent) == 0

@pytest.mark.asyncio
async def test_get_recent_events_limit_exceeds_size(ingestion_system, mock_events):
    for event_data in mock_events:
        await ingestion_system.ingest_event(
            source=event_data["source"],
            raw_data=event_data["raw_data"]
        )

    recent = ingestion_system.get_recent_events(limit=20)
    assert len(recent) == 10
    assert recent[0].title == "Event 9"
    assert recent[-1].title == "Event 0"

@pytest.mark.asyncio
async def test_get_recent_events_zero_limit(ingestion_system, mock_events):
    for event_data in mock_events:
        await ingestion_system.ingest_event(
            source=event_data["source"],
            raw_data=event_data["raw_data"]
        )

    recent = ingestion_system.get_recent_events(limit=0)
    assert len(recent) == 0

    recent_negative = ingestion_system.get_recent_events(limit=-1)
    assert len(recent_negative) == 0
