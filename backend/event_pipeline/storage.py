"""
Event Storage Module

Stores and retrieves events from database.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload

from .processing import ProcessedEvent
from backend.database import AsyncSessionLocal
from backend.models import Event as DBEvent
from backend.event_pipeline.ingestion import EventSource

class EventStorage:
    """
    Event storage and retrieval system using SQLAlchemy
    """
    
    def __init__(self):
        # We rely on AsyncSessionLocal for DB access
        pass
    
    async def store_event(self, event: ProcessedEvent) -> bool:
        """
        Store a processed event
        
        Args:
            event: Event to store
            
        Returns:
            True if successful
        """
        async with AsyncSessionLocal() as session:
            try:
                # Check if exists
                stmt = select(DBEvent).where(DBEvent.id == event.event_id)
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    # Update
                    existing.title = event.title
                    existing.description = event.description
                    existing.processing_timestamp = event.processing_timestamp
                    existing.sentiment = event.sentiment
                    existing.entities = event.entities
                    existing.summary = event.summary
                    existing.keywords = event.keywords
                    existing.priority_score = event.priority_score
                else:
                    # Create
                    db_event = DBEvent(
                        id=event.event_id,
                        source=event.source.value,
                        title=event.title,
                        description=event.description,
                        category=event.category,
                        url=event.url,
                        content=event.content,
                        timestamp=event.timestamp,
                        processing_timestamp=event.processing_timestamp,
                        sentiment=event.sentiment,
                        entities=event.entities,
                        summary=event.summary,
                        keywords=event.keywords,
                        priority_score=event.priority_score
                    )
                    session.add(db_event)

                await session.commit()
                return True
            except Exception as e:
                print(f"Error storing event: {e}")
                await session.rollback()
                return False

    def _to_processed_event(self, db_event: DBEvent) -> ProcessedEvent:
        """Convert DB model to ProcessedEvent"""
        return ProcessedEvent(
            event_id=db_event.id,
            source=EventSource(db_event.source),
            title=db_event.title,
            description=db_event.description,
            category=db_event.category,
            url=db_event.url,
            content=db_event.content,
            timestamp=db_event.timestamp,
            sentiment=db_event.sentiment,
            entities=db_event.entities,
            summary=db_event.summary,
            keywords=db_event.keywords,
            priority_score=db_event.priority_score
        )
    
    async def get_event(self, event_id: str) -> Optional[ProcessedEvent]:
        """Retrieve an event by ID"""
        async with AsyncSessionLocal() as session:
            stmt = select(DBEvent).where(DBEvent.id == event_id)
            result = await session.execute(stmt)
            db_event = result.scalar_one_or_none()

            if db_event:
                return self._to_processed_event(db_event)
            return None
    
    async def get_events_by_category(
        self,
        category: str,
        limit: int = 10
    ) -> List[ProcessedEvent]:
        """Get events by category"""
        async with AsyncSessionLocal() as session:
            stmt = select(DBEvent).where(DBEvent.category == category)\
                .order_by(DBEvent.timestamp.desc()).limit(limit)
            result = await session.execute(stmt)
            events = result.scalars().all()
            return [self._to_processed_event(e) for e in events]
    
    async def get_events_by_source(
        self,
        source: str,
        limit: int = 10
    ) -> List[ProcessedEvent]:
        """Get events by source"""
        async with AsyncSessionLocal() as session:
            stmt = select(DBEvent).where(DBEvent.source == source)\
                .order_by(DBEvent.timestamp.desc()).limit(limit)
            result = await session.execute(stmt)
            events = result.scalars().all()
            return [self._to_processed_event(e) for e in events]
    
    async def get_recent_events(
        self,
        limit: int = 10,
        hours: int = 24
    ) -> List[ProcessedEvent]:
        """Get recent events within time window"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        async with AsyncSessionLocal() as session:
            stmt = select(DBEvent).where(DBEvent.timestamp > cutoff)\
                .order_by(DBEvent.timestamp.desc()).limit(limit)
            result = await session.execute(stmt)
            events = result.scalars().all()
            return [self._to_processed_event(e) for e in events]
    
    async def search_events(
        self,
        query: str,
        limit: int = 10
    ) -> List[ProcessedEvent]:
        """Search events by text query (simple LIKE)"""
        async with AsyncSessionLocal() as session:
            search = f"%{query}%"
            stmt = select(DBEvent).where(
                (DBEvent.title.ilike(search)) | (DBEvent.description.ilike(search))
            ).order_by(DBEvent.timestamp.desc()).limit(limit)
            result = await session.execute(stmt)
            events = result.scalars().all()
            return [self._to_processed_event(e) for e in events]
    
    async def delete_old_events(self, days: int = 30) -> int:
        """Delete events older than specified days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        async with AsyncSessionLocal() as session:
            stmt = delete(DBEvent).where(DBEvent.timestamp < cutoff)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        async with AsyncSessionLocal() as session:
            # Note: This might be slow for large tables
            count_stmt = select(DBEvent).with_only_columns(DBEvent.id)
            result = await session.execute(count_stmt)
            count = len(result.all())

            return {
                "total_events": count,
                "storage_type": "database"
            }
