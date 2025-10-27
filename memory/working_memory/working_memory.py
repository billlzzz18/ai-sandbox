# memory/working_memory/working_memory.py

import time
import heapq
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading


class MemoryItemPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MemoryItem:
    """An item in working memory"""

    data: Any
    priority: MemoryItemPriority = MemoryItemPriority.MEDIUM
    importance: float = 1.0  # 0.0 to 1.0
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    decay_factor: float = 0.95  # How fast importance decays
    tags: List[str] = field(default_factory=list)

    @property
    def activation_level(self) -> float:
        """Calculate activation level based on recency, frequency, and importance"""
        time_since_access = time.time() - self.last_accessed
        time_factor = max(0.1, 1.0 / (1.0 + time_since_access / 3600))  # Decay over hours
        frequency_factor = min(2.0, 1.0 + self.access_count * 0.1)
        return self.importance * time_factor * frequency_factor

    def access(self):
        """Mark item as accessed"""
        self.access_count += 1
        self.last_accessed = time.time()

    def decay_importance(self):
        """Decay importance over time"""
        time_since_creation = time.time() - self.timestamp
        hours_elapsed = time_since_creation / 3600
        self.importance *= (self.decay_factor ** hours_elapsed)
        self.importance = max(0.1, self.importance)  # Minimum importance


class WorkingMemory:
    """Working memory with limited capacity and decay"""

    def __init__(self, max_items: int = 20, decay_interval: float = 300):  # 5 minutes
        self.max_items = max_items
        self.items: List[MemoryItem] = []
        self.lock = threading.Lock()

        # Start decay timer
        self.decay_timer = None
        if decay_interval > 0:
            self._start_decay_timer(decay_interval)

    def add_item(self, data: Any, priority: MemoryItemPriority = MemoryItemPriority.MEDIUM,
                importance: float = 1.0, tags: List[str] = None) -> MemoryItem:
        """Add an item to working memory"""

        with self.lock:
            item = MemoryItem(
                data=data,
                priority=priority,
                importance=max(0.1, min(1.0, importance)),  # Clamp to 0.1-1.0
                tags=tags or []
            )

            self.items.append(item)

            # Maintain capacity
            if len(self.items) > self.max_items:
                self._evict_items()

            return item

    def get_item(self, index: int) -> Optional[MemoryItem]:
        """Get item by index and mark as accessed"""
        with self.lock:
            if 0 <= index < len(self.items):
                item = self.items[index]
                item.access()
                return item
        return None

    def find_items(self, predicate: callable = None, tags: List[str] = None,
                  min_importance: float = 0.0, limit: int = 10) -> List[MemoryItem]:
        """Find items matching criteria"""

        with self.lock:
            candidates = self.items.copy()

            # Filter by tags
            if tags:
                candidates = [item for item in candidates if any(tag in item.tags for tag in tags)]

            # Filter by predicate
            if predicate:
                candidates = [item for item in candidates if predicate(item)]

            # Filter by importance
            candidates = [item for item in candidates if item.importance >= min_importance]

            # Sort by activation level (highest first)
            candidates.sort(key=lambda x: x.activation_level, reverse=True)

            # Mark accessed and return
            result = candidates[:limit]
            for item in result:
                item.access()

            return result

    def update_item(self, index: int, **updates) -> bool:
        """Update an existing item"""

        with self.lock:
            if 0 <= index < len(self.items):
                item = self.items[index]

                for key, value in updates.items():
                    if hasattr(item, key):
                        setattr(item, key, value)

                item.access()
                return True

        return False

    def remove_item(self, index: int) -> bool:
        """Remove an item from working memory"""

        with self.lock:
            if 0 <= index < len(self.items):
                self.items.pop(index)
                return True

        return False

    def clear(self):
        """Clear all items"""
        with self.lock:
            self.items.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Get working memory statistics"""

        with self.lock:
            if not self.items:
                return {
                    'total_items': 0,
                    'avg_importance': 0.0,
                    'avg_activation': 0.0,
                    'total_accesses': 0,
                    'priority_distribution': {},
                    'tag_distribution': {}
                }

            total_importance = sum(item.importance for item in self.items)
            total_activation = sum(item.activation_level for item in self.items)
            total_accesses = sum(item.access_count for item in self.items)

            # Priority distribution
            priority_dist = {}
            for priority in MemoryItemPriority:
                count = len([item for item in self.items if item.priority == priority])
                if count > 0:
                    priority_dist[priority.name] = count

            # Tag distribution
            tag_dist = {}
            for item in self.items:
                for tag in item.tags:
                    tag_dist[tag] = tag_dist.get(tag, 0) + 1

            return {
                'total_items': len(self.items),
                'capacity': self.max_items,
                'utilization': len(self.items) / self.max_items,
                'avg_importance': total_importance / len(self.items),
                'avg_activation': total_activation / len(self.items),
                'total_accesses': total_accesses,
                'priority_distribution': priority_dist,
                'tag_distribution': tag_dist
            }

    def get_most_important(self, limit: int = 5) -> List[MemoryItem]:
        """Get most important items"""
        with self.lock:
            sorted_items = sorted(self.items, key=lambda x: x.importance, reverse=True)
            result = sorted_items[:limit]
            for item in result:
                item.access()
            return result

    def get_recent_items(self, limit: int = 5) -> List[MemoryItem]:
        """Get most recently accessed items"""
        with self.lock:
            sorted_items = sorted(self.items, key=lambda x: x.last_accessed, reverse=True)
            result = sorted_items[:limit]
            for item in result:
                item.access()
            return result

    def get_items_by_tags(self, tags: List[str], limit: int = 10) -> List[MemoryItem]:
        """Get items that have any of the specified tags"""
        return self.find_items(tags=tags, limit=limit)

    def search_content(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """Search for items containing the query string"""
        def content_matches(item):
            if isinstance(item.data, str):
                return query.lower() in item.data.lower()
            elif isinstance(item.data, dict):
                # Search in dict values
                return any(query.lower() in str(value).lower()
                          for value in item.data.values())
            return False

        return self.find_items(predicate=content_matches, limit=limit)

    def _evict_items(self):
        """Evict items when capacity is exceeded"""
        # Sort by activation level (lowest first for eviction)
        self.items.sort(key=lambda x: x.activation_level)

        # Remove lowest activation items until we're at capacity
        while len(self.items) > self.max_items:
            evicted = self.items.pop(0)
            # Could log eviction here if needed

    def _decay_items(self):
        """Apply decay to all items"""
        with self.lock:
            for item in self.items:
                item.decay_importance()

            # Re-sort after decay (important items bubble up)
            self.items.sort(key=lambda x: x.activation_level, reverse=True)

    def _start_decay_timer(self, interval: float):
        """Start the decay timer"""
        def decay_worker():
            while True:
                time.sleep(interval)
                self._decay_items()

        self.decay_timer = threading.Thread(target=decay_worker, daemon=True)
        self.decay_timer.start()

    def __len__(self) -> int:
        """Get number of items"""
        return len(self.items)

    def __getitem__(self, index: int) -> MemoryItem:
        """Get item by index"""
        return self.get_item(index)

    def __iter__(self):
        """Iterate over items"""
        return iter(self.items)