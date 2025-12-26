"""
Memory Manager Module

Manages agent memory including short-term and long-term storage.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque, OrderedDict


class MemoryEntry:
    """Single memory entry"""
    
    def __init__(self, key: str, value: Any, ttl: Optional[int] = None):
        self.key = key
        self.value = value
        self.created_at = datetime.utcnow()
        self.expires_at = (
            datetime.utcnow() + timedelta(seconds=ttl) if ttl else None
        )
        self.access_count = 0
        self.last_accessed = datetime.utcnow()


class MemoryManager:
    """
    Memory management system for AI agents
    Supports short-term and long-term memory with TTL
    """
    
    def __init__(self, max_short_term: int = 100, max_long_term: int = 1000):
        self.short_term: deque = deque(maxlen=max_short_term)
        # Optimized: Use OrderedDict for O(1) LRU eviction
        self.long_term: OrderedDict[str, MemoryEntry] = OrderedDict()
        self.max_long_term = max_long_term
    
    def add_short_term(self, value: Any) -> None:
        """Add to short-term memory (FIFO queue)"""
        self.short_term.append({
            "value": value,
            "timestamp": datetime.utcnow()
        })
    
    def get_short_term(self, limit: Optional[int] = None) -> List[Any]:
        """Get recent short-term memories"""
        memories = list(self.short_term)
        if limit:
            memories = memories[-limit:]
        return [m["value"] for m in memories]
    
    def add_long_term(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Add to long-term memory with optional TTL"""
        # Optimized: O(1) insertion/update
        
        # If key exists, move to end (mark as recent) and update value
        if key in self.long_term:
            self.long_term.move_to_end(key)
            entry = self.long_term[key]
            entry.value = value
            # Update TTL if provided? Original code didn't update existing entry fields
            # except overwriting the whole entry object.
            # So we create a new entry to be safe.
            entry = MemoryEntry(key, value, ttl)
            self.long_term[key] = entry
            return

        # If full, evict LRU (O(1))
        if len(self.long_term) >= self.max_long_term:
            self.long_term.popitem(last=False)

        # Add new entry
        entry = MemoryEntry(key, value, ttl)
        self.long_term[key] = entry
    
    def get_long_term(self, key: str) -> Optional[Any]:
        """Get from long-term memory"""
        # Optimized: Lazy expiration check (O(1)) instead of full scan
        entry = self.long_term.get(key)

        if entry:
            # Check expiration
            if entry.expires_at and entry.expires_at < datetime.utcnow():
                del self.long_term[key]
                return None

            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()
            self.long_term.move_to_end(key) # Mark as recently used
            return entry.value

        return None
    
    def remove_long_term(self, key: str) -> None:
        """Remove from long-term memory"""
        if key in self.long_term:
            del self.long_term[key]
    
    def clear_short_term(self) -> None:
        """Clear short-term memory"""
        self.short_term.clear()
    
    def clear_long_term(self) -> None:
        """Clear long-term memory"""
        self.long_term.clear()
    
    def clear_all(self) -> None:
        """Clear all memory"""
        self.clear_short_term()
        self.clear_long_term()
    
    def _clean_expired(self) -> None:
        """Remove expired entries"""
        # Kept for compatibility or manual cleanup, but optimization relies on lazy expiration.
        # Still O(N), but not called on hot path anymore.
        now = datetime.utcnow()
        expired_keys = [
            key for key, entry in self.long_term.items()
            if entry.expires_at and entry.expires_at < now
        ]
        for key in expired_keys:
            del self.long_term[key]
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self.long_term:
            return
        # Optimized: O(1) eviction
        self.long_term.popitem(last=False)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "long_term_max": self.max_long_term
        }
