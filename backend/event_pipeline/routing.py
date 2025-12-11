"""
Event Routing Module

Routes events to appropriate handlers and agents.
"""

from typing import Dict, Any, List, Callable, Optional
from enum import Enum

from .ingestion import NormalizedEvent


class RoutingRule(str, Enum):
    """Event routing rules"""
    BY_CATEGORY = "by_category"
    BY_PRIORITY = "by_priority"
    BY_SOURCE = "by_source"
    BY_TAGS = "by_tags"
    BROADCAST = "broadcast"


class EventRouter:
    """
    Routes events to appropriate destinations
    """
    
    def __init__(self):
        self.category_routes: Dict[str, List[Callable]] = {}
        self.priority_routes: Dict[str, List[Callable]] = {}
        self.source_routes: Dict[str, List[Callable]] = {}
        self.tag_routes: Dict[str, List[Callable]] = {}
        self.broadcast_handlers: List[Callable] = []
    
    def add_category_route(self, category: str, handler: Callable) -> None:
        """Add a handler for specific category"""
        if category not in self.category_routes:
            self.category_routes[category] = []
        self.category_routes[category].append(handler)
    
    def add_priority_route(self, priority_level: str, handler: Callable) -> None:
        """Add a handler for specific priority level"""
        if priority_level not in self.priority_routes:
            self.priority_routes[priority_level] = []
        self.priority_routes[priority_level].append(handler)
    
    def add_source_route(self, source: str, handler: Callable) -> None:
        """Add a handler for specific source"""
        if source not in self.source_routes:
            self.source_routes[source] = []
        self.source_routes[source].append(handler)
    
    def add_tag_route(self, tag: str, handler: Callable) -> None:
        """Add a handler for specific tag"""
        if tag not in self.tag_routes:
            self.tag_routes[tag] = []
        self.tag_routes[tag].append(handler)
    
    def add_broadcast_handler(self, handler: Callable) -> None:
        """Add a handler that receives all events"""
        self.broadcast_handlers.append(handler)
    
    async def route_event(
        self,
        event: NormalizedEvent,
        priority_score: Optional[float] = None
    ) -> int:
        """
        Route event to appropriate handlers
        
        Args:
            event: Event to route
            priority_score: Optional priority score
            
        Returns:
            Number of handlers event was routed to
        """
        handlers = set()
        
        # Category routing
        if event.category and event.category in self.category_routes:
            handlers.update(self.category_routes[event.category])
        
        # Source routing
        source_key = event.source.value
        if source_key in self.source_routes:
            handlers.update(self.source_routes[source_key])
        
        # Tag routing
        if event.tags:
            for tag in event.tags:
                if tag in self.tag_routes:
                    handlers.update(self.tag_routes[tag])
        
        # Priority routing
        if priority_score is not None:
            if priority_score > 2.0:
                handlers.update(self.priority_routes.get("high", []))
            elif priority_score > 1.0:
                handlers.update(self.priority_routes.get("medium", []))
            else:
                handlers.update(self.priority_routes.get("low", []))
        
        # Broadcast handlers
        handlers.update(self.broadcast_handlers)
        
        # Execute handlers
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
        
        return len(handlers)
    
    def get_route_stats(self) -> Dict[str, int]:
        """Get statistics about registered routes"""
        return {
            "category_routes": len(self.category_routes),
            "priority_routes": len(self.priority_routes),
            "source_routes": len(self.source_routes),
            "tag_routes": len(self.tag_routes),
            "broadcast_handlers": len(self.broadcast_handlers),
        }
