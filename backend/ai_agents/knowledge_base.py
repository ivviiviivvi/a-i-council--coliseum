"""
Knowledge Base Module

Provides structured knowledge storage and retrieval for AI agents.
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import uuid
import re
from collections import defaultdict


class KnowledgeEntry:
    """Single entry in the knowledge base"""
    
    def __init__(self, content: str, category: str, metadata: Optional[Dict] = None):
        self.entry_id = str(uuid.uuid4())
        self.content = content
        self.category = category
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.access_count = 0


class KnowledgeBase:
    """
    Knowledge base system for storing and retrieving information
    """
    
    def __init__(self):
        self.entries: Dict[str, KnowledgeEntry] = {}
        self.categories: Dict[str, List[str]] = {}
        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization: lowercase and split by non-alphanumeric"""
        return re.findall(r'\w+', text.lower())

    def add_entry(self, content: str, category: str, 
                  metadata: Optional[Dict] = None) -> KnowledgeEntry:
        """Add a new knowledge entry"""
        entry = KnowledgeEntry(content, category, metadata)
        self.entries[entry.entry_id] = entry
        
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(entry.entry_id)
        
        # Index content
        tokens = self._tokenize(content)
        for token in set(tokens): # Use set to avoid adding same ID multiple times for one document
            self.inverted_index[token].add(entry.entry_id)

        return entry
    
    def get_entry(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Retrieve a knowledge entry by ID"""
        entry = self.entries.get(entry_id)
        if entry:
            entry.access_count += 1
        return entry
    
    def search_by_category(self, category: str) -> List[KnowledgeEntry]:
        """Search entries by category"""
        entry_ids = self.categories.get(category, [])
        return [self.entries[eid] for eid in entry_ids if eid in self.entries]
    
    def search_by_content(self, query: str) -> List[KnowledgeEntry]:
        """Search entries by content using inverted index"""
        tokens = self._tokenize(query)
        if not tokens:
            return []

        # Start with the set of documents containing the first token
        result_ids = self.inverted_index.get(tokens[0], set())

        # Intersect with sets for subsequent tokens (AND logic)
        for token in tokens[1:]:
            result_ids = result_ids.intersection(self.inverted_index.get(token, set()))
            if not result_ids: # Optimization: if intersection is empty, we can stop
                break

        return [self.entries[eid] for eid in result_ids if eid in self.entries]
    
    def get_recent_entries(self, limit: int = 10) -> List[KnowledgeEntry]:
        """Get most recent entries"""
        sorted_entries = sorted(
            self.entries.values(),
            key=lambda e: e.created_at,
            reverse=True
        )
        return sorted_entries[:limit]
    
    def get_popular_entries(self, limit: int = 10) -> List[KnowledgeEntry]:
        """Get most accessed entries"""
        sorted_entries = sorted(
            self.entries.values(),
            key=lambda e: e.access_count,
            reverse=True
        )
        return sorted_entries[:limit]
