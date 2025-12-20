import pytest
import time
import random
from datetime import datetime, timedelta
from backend.event_pipeline.ingestion import EventIngestionSystem, EventSource, NormalizedEvent, RawEvent

def generate_events(count: int) -> list[NormalizedEvent]:
    events = []
    base_time = datetime.utcnow()
    for i in range(count):
        # Generate timestamps somewhat randomly but roughly increasing
        timestamp = base_time - timedelta(minutes=random.randint(0, count))
        event = NormalizedEvent(
            event_id=f"evt_{i}",
            source=EventSource.API,
            title=f"Event {i}",
            description=f"Description {i}",
            timestamp=timestamp
        )
        events.append(event)
    return events

def test_get_recent_events_performance():
    system = EventIngestionSystem()

    # Generate large number of events
    N = 100000
    events = generate_events(N)

    # Shuffle to simulate out-of-order ingestion/updates if that were to happen
    # Though ingestion is usually append-only, updates or async ingestion might cause disorder.
    random.shuffle(events)

    system.normalized_events = events

    # Measure standard sort
    start_time = time.time()
    for _ in range(100):
        _ = sorted(system.normalized_events, key=lambda e: e.timestamp, reverse=True)[:10]
    baseline_duration = time.time() - start_time

    # Measure current implementation
    start_time = time.time()
    for _ in range(100):
        system.get_recent_events(limit=10)
    current_duration = time.time() - start_time

    print(f"\nBaseline (direct sort) duration: {baseline_duration:.4f}s")
    print(f"Current implementation duration: {current_duration:.4f}s")

    # Assert correctness of current implementation before changing it
    recent = system.get_recent_events(limit=10)
    assert len(recent) == 10
    # Check if sorted desc
    for i in range(len(recent) - 1):
        assert recent[i].timestamp >= recent[i+1].timestamp

if __name__ == "__main__":
    test_get_recent_events_performance()
