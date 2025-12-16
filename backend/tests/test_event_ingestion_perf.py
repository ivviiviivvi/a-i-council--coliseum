import pytest
import time
from datetime import datetime
from backend.event_pipeline.ingestion import EventIngestionSystem, EventSource, NormalizedEvent, RawEvent

def test_get_recent_events_performance():
    system = EventIngestionSystem()

    # Generate 100,000 events
    n_events = 100000
    print(f"\nGenerating {n_events} events...")

    # We manually populate normalized_events to simulate a filled system
    for i in range(n_events):
        event = NormalizedEvent(
            event_id=f"id_{i}",
            source=EventSource.API,
            title=f"Event {i}",
            description="Test description",
            timestamp=datetime.fromtimestamp(1600000000 + i)
        )
        system.normalized_events.append(event)

    # Measure performance of get_recent_events
    start_time = time.time()
    results = system.get_recent_events(limit=10)
    end_time = time.time()

    duration = end_time - start_time
    print(f"Time taken for get_recent_events (limit=10): {duration:.6f} seconds")

    assert len(results) == 10
    assert results[0].title == f"Event {n_events-1}"

    # Verify correctness (descending order)
    for i in range(len(results) - 1):
        assert results[i].timestamp >= results[i+1].timestamp
