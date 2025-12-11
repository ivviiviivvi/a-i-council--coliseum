"""
Event Storage Module

Stores and retrieves events from database.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .processing import ProcessedEvent


class EventStorage:
    """
    Event storage and retrieval system
    """
    
    def __init__(self):
        # In-memory storage for now, will be replaced with database
        self.events: Dict[str, ProcessedEvent] = {}
        self.category_index: Dict[str, List[str]] = {}
        self.source_index: Dict[str, List[str]] = {}
        self.tag_index: Dict[str, List[str]] = {}
    
    async def store_event(self, event: ProcessedEvent) -> bool:
        """
        Store a processed event
        
        Args:
            event: Event to store
            
        Returns:
            True if successful
        """
        try:
            self.events[event.event_id] = event
            
            # Update indexes
            if event.category:
                if event.category not in self.category_index:
                    self.category_index[event.category] = []
                self.category_index[event.category].append(event.event_id)
            
            source_key = event.source.value
            if source_key not in self.source_index:
                self.source_index[source_key] = []
            self.source_index[source_key].append(event.event_id)
            
            if event.tags:
                for tag in event.tags:
                    if tag not in self.tag_index:
                        self.tag_index[tag] = []
                    self.tag_index[tag].append(event.event_id)
            
            return True
        except Exception as e:
            print(f"Error storing event: {e}")
            return False
    
    async def get_event(self, event_id: str) -> Optional[ProcessedEvent]:
        """Retrieve an event by ID"""
        return self.events.get(event_id)
    
    async def get_events_by_category(
        self,
        category: str,
        limit: int = 10
    ) -> List[ProcessedEvent]:
        """Get events by category"""
        event_ids = self.category_index.get(category, [])
        events = [self.events[eid] for eid in event_ids if eid in self.events]
        return sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    async def get_events_by_source(
        self,
        source: str,
        limit: int = 10
    ) -> List[ProcessedEvent]:
        """Get events by source"""
        event_ids = self.source_index.get(source, [])
        events = [self.events[eid] for eid in event_ids if eid in self.events]
        return sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    async def get_events_by_tag(
        self,
        tag: str,
        limit: int = 10
    ) -> List[ProcessedEvent]:
        """Get events by tag"""
        event_ids = self.tag_index.get(tag, [])
        events = [self.events[eid] for eid in event_ids if eid in self.events]
        return sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    async def get_recent_events(
        self,
        limit: int = 10,
        hours: int = 24
    ) -> List[ProcessedEvent]:
        """Get recent events within time window"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = [
            e for e in self.events.values()
            if e.timestamp > cutoff
        ]
        return sorted(recent, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    async def search_events(
        self,
        query: str,
        limit: int = 10
    ) -> List[ProcessedEvent]:
        """Search events by text query"""
        query_lower = query.lower()
        matching = []
        
        for event in self.events.values():
            text = f"{event.title} {event.description}".lower()
            if query_lower in text:
                matching.append(event)
        
        return sorted(matching, key=lambda e: e.timestamp, reverse=True)[:limit]
    
    async def delete_old_events(self, days: int = 30) -> int:
        """Delete events older than specified days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        old_event_ids = [
            event_id for event_id, event in self.events.items()
            if event.timestamp < cutoff
        ]
        
        for event_id in old_event_ids:
            del self.events[event_id]
        
        # Clean indexes (simplified)
        for category in self.category_index:
            self.category_index[category] = [
                eid for eid in self.category_index[category]
                if eid in self.events
            ]
        
        return len(old_event_ids)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return {
            "total_events": len(self.events),
            "categories": len(self.category_index),
            "sources": len(self.source_index),
            "tags": len(self.tag_index)
        }
