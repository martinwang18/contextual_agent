"""
Data Models
Defines data structures for contextual items
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Location:
    """Represents a geographic location"""
    zipcode: str
    city: str
    state: str
    state_code: str
    latitude: float
    longitude: float

    def to_dict(self):
        return asdict(self)


@dataclass
class ContextualItem:
    """Represents a single contextual item (weather, news, event)"""
    title: str
    description: str
    category: str
    source: str
    timestamp: str
    score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class SearchResult:
    """Represents the complete search result"""
    status: str
    query: Dict[str, str]
    results: list
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self):
        return {
            'status': self.status,
            'query': self.query,
            'results': [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.results],
            'metadata': self.metadata or {}
        }
