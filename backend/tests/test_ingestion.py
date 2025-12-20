import pytest
from datetime import datetime, timedelta
from backend.event_pipeline.ingestion import EventIngestionSystem, EventSource, NormalizedEvent

@pytest.fixture
def ingestion_system():
    return EventIngestionSystem()

def test_get_recent_events_ordering(ingestion_system):
    """Test that events are returned in correct order"""
    now = datetime.utcnow()
    events = []
    for i in range(5):
        events.append(NormalizedEvent(
            event_id=f"id_{i}",
            source=EventSource.API,
            title=f"Event {i}",
            description="test",
            timestamp=now - timedelta(minutes=i)
        ))

    # Shuffle events and set
    import random
    random.shuffle(events)
    ingestion_system.normalized_events = events

    recent = ingestion_system.get_recent_events(limit=5)

    # Should be sorted by timestamp descending (newest first)
    assert len(recent) == 5
    assert recent[0].event_id == "id_0"  # Newest
    assert recent[4].event_id == "id_4"  # Oldest

    for i in range(len(recent) - 1):
        assert recent[i].timestamp >= recent[i+1].timestamp

def test_get_recent_events_limit(ingestion_system):
    """Test that limit is respected"""
    now = datetime.utcnow()
    events = [
        NormalizedEvent(
            event_id=f"id_{i}",
            source=EventSource.API,
            title=f"Event {i}",
            description="test",
            timestamp=now - timedelta(minutes=i)
        )
        for i in range(20)
    ]

    ingestion_system.normalized_events = events

    recent = ingestion_system.get_recent_events(limit=5)
    assert len(recent) == 5
    assert recent[0].event_id == "id_0" # Newest

def test_get_recent_events_source_filter(ingestion_system):
    """Test filtering by source"""
    now = datetime.utcnow()
    e1 = NormalizedEvent(
        event_id="id_1",
        source=EventSource.API,
        title="API Event",
        description="test",
        timestamp=now
    )
    e2 = NormalizedEvent(
        event_id="id_2",
        source=EventSource.RSS_FEED,
        title="RSS Event",
        description="test",
        timestamp=now
    )

    ingestion_system.normalized_events = [e1, e2]

    recent_api = ingestion_system.get_recent_events(limit=10, source=EventSource.API)
    assert len(recent_api) == 1
    assert recent_api[0].source == EventSource.API

    recent_rss = ingestion_system.get_recent_events(limit=10, source=EventSource.RSS_FEED)
    assert len(recent_rss) == 1
    assert recent_rss[0].source == EventSource.RSS_FEED

def test_get_recent_events_empty(ingestion_system):
    """Test with empty list"""
    recent = ingestion_system.get_recent_events(limit=10)
    assert recent == []

def test_get_recent_events_limit_larger_than_size(ingestion_system):
    """Test when limit is larger than number of events"""
    now = datetime.utcnow()
    events = [
        NormalizedEvent(
            event_id=f"id_{i}",
            source=EventSource.API,
            title=f"Event {i}",
            description="test",
            timestamp=now
        )
        for i in range(5)
    ]
    ingestion_system.normalized_events = events

    recent = ingestion_system.get_recent_events(limit=10)
    assert len(recent) == 5
