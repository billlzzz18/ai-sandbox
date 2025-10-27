# memory/episodic_memory/episodic_memory.py

import json
import os
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import heapq


@dataclass
class Experience:
    """Represents a single experience/episode"""
    task: str
    success: bool
    timestamp: float
    context: Dict[str, Any]
    lessons_learned: List[str]
    performance_metrics: Dict[str, Any]
    agent_name: str
    task_type: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Experience':
        return cls(**data)


class EpisodicMemory:
    """Episodic memory for storing and retrieving task experiences"""

    def __init__(self, storage_path: str = "memory/episodic", max_entries: int = 10000):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.max_entries = max_entries
        self.index_file = self.storage_path / "index.json"
        self.entries_file = self.storage_path / "entries.jsonl"

        # In-memory cache for faster access
        self._cache: List[Experience] = []
        self._loaded = False

        # Load existing data
        self._load_index()

    def store_experience(self, experience: Experience):
        """Store a new experience"""
        # Add to cache
        self._cache.append(experience)

        # Maintain size limit (keep most recent)
        if len(self._cache) > self.max_entries:
            # Sort by timestamp (newest first) and keep top entries
            self._cache.sort(key=lambda x: x.timestamp, reverse=True)
            self._cache = self._cache[:self.max_entries]

        # Persist to disk
        self._persist_experience(experience)

        # Update index
        self._update_index()

    def retrieve_similar(self, query_task: str, limit: int = 5,
                        agent_filter: Optional[str] = None,
                        task_type_filter: Optional[str] = None) -> List[Experience]:
        """Retrieve experiences similar to the query task"""

        if not self._loaded:
            self._load_all_experiences()

        # Filter experiences
        candidates = self._cache

        if agent_filter:
            candidates = [exp for exp in candidates if exp.agent_name == agent_filter]

        if task_type_filter:
            candidates = [exp for exp in candidates if exp.task_type == task_type_filter]

        if not candidates:
            return []

        # Calculate similarity scores
        scored_experiences = []
        for exp in candidates:
            similarity = self._calculate_similarity(query_task, exp.task)
            if similarity > 0:  # Only include somewhat similar experiences
                scored_experiences.append((similarity, exp))

        # Sort by similarity and return top results
        scored_experiences.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in scored_experiences[:limit]]

    def get_recent_experiences(self, agent_name: Optional[str] = None,
                              limit: int = 10) -> List[Experience]:
        """Get most recent experiences"""

        if not self._loaded:
            self._load_all_experiences()

        candidates = self._cache

        if agent_name:
            candidates = [exp for exp in candidates if exp.agent_name == agent_name]

        # Sort by timestamp (most recent first)
        candidates.sort(key=lambda x: x.timestamp, reverse=True)

        return candidates[:limit]

    def get_successful_experiences(self, task_pattern: Optional[str] = None,
                                  limit: int = 10) -> List[Experience]:
        """Get successful experiences, optionally filtered by task pattern"""

        if not self._loaded:
            self._load_all_experiences()

        candidates = [exp for exp in self._cache if exp.success]

        if task_pattern:
            candidates = [exp for exp in candidates if task_pattern.lower() in exp.task.lower()]

        # Sort by timestamp (most recent first)
        candidates.sort(key=lambda x: x.timestamp, reverse=True)

        return candidates[:limit]

    def get_performance_stats(self, agent_name: Optional[str] = None,
                             task_type: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics"""

        if not self._loaded:
            self._load_all_experiences()

        candidates = self._cache

        if agent_name:
            candidates = [exp for exp in candidates if exp.agent_name == agent_name]

        if task_type:
            candidates = [exp for exp in candidates if exp.task_type == task_type]

        if not candidates:
            return {
                'total_experiences': 0,
                'success_rate': 0.0,
                'avg_execution_time': 0.0,
                'task_types': [],
                'recent_performance': []
            }

        total_experiences = len(candidates)
        successful_experiences = len([exp for exp in candidates if exp.success])
        success_rate = successful_experiences / total_experiences if total_experiences > 0 else 0

        # Calculate average execution time
        execution_times = []
        for exp in candidates:
            if 'execution_time' in exp.performance_metrics:
                execution_times.append(exp.performance_metrics['execution_time'])

        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0

        # Get task type distribution
        task_types = {}
        for exp in candidates:
            task_types[exp.task_type] = task_types.get(exp.task_type, 0) + 1

        # Recent performance (last 10 experiences)
        recent = sorted(candidates, key=lambda x: x.timestamp, reverse=True)[:10]
        recent_performance = [
            {
                'task': exp.task,
                'success': exp.success,
                'execution_time': exp.performance_metrics.get('execution_time', 0),
                'timestamp': exp.timestamp
            }
            for exp in recent
        ]

        return {
            'total_experiences': total_experiences,
            'success_rate': success_rate,
            'avg_execution_time': avg_execution_time,
            'task_types': task_types,
            'recent_performance': recent_performance
        }

    def _calculate_similarity(self, query: str, target: str) -> float:
        """Calculate similarity between two task descriptions"""
        # Simple similarity based on common words
        query_words = set(query.lower().split())
        target_words = set(target.lower().split())

        if not query_words or not target_words:
            return 0.0

        intersection = query_words.intersection(target_words)
        union = query_words.union(target_words)

        # Jaccard similarity
        similarity = len(intersection) / len(union) if union else 0.0

        # Boost similarity for exact matches or very similar tasks
        if query.lower() == target.lower():
            similarity = 1.0
        elif len(intersection) >= min(len(query_words), len(target_words)) * 0.8:
            similarity *= 1.2  # Boost for high overlap

        return min(similarity, 1.0)  # Cap at 1.0

    def _persist_experience(self, experience: Experience):
        """Persist experience to disk"""
        try:
            with open(self.entries_file, 'a', encoding='utf-8') as f:
                json.dump(experience.to_dict(), f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            print(f"Failed to persist experience: {e}")

    def _load_all_experiences(self):
        """Load all experiences from disk into cache"""
        if self._loaded:
            return

        try:
            if self.entries_file.exists():
                self._cache = []
                with open(self.entries_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                data = json.loads(line)
                                experience = Experience.from_dict(data)
                                self._cache.append(experience)
                            except json.JSONDecodeError:
                                continue  # Skip corrupted lines

                # Sort by timestamp (newest first)
                self._cache.sort(key=lambda x: x.timestamp, reverse=True)

            self._loaded = True

        except Exception as e:
            print(f"Failed to load experiences: {e}")
            self._cache = []

    def _load_index(self):
        """Load index file"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    # Could store metadata here in the future
        except Exception as e:
            print(f"Failed to load index: {e}")

    def _update_index(self):
        """Update index file with metadata"""
        try:
            index_data = {
                'total_entries': len(self._cache),
                'last_updated': time.time(),
                'agents': list(set(exp.agent_name for exp in self._cache)),
                'task_types': list(set(exp.task_type for exp in self._cache))
            }

            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Failed to update index: {e}")

    def cleanup_old_entries(self, max_age_days: int = 30):
        """Clean up old entries to save space"""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)

        # Filter out old entries
        original_count = len(self._cache)
        self._cache = [exp for exp in self._cache if exp.timestamp > cutoff_time]

        if len(self._cache) < original_count:
            # Rewrite the entire file with remaining entries
            self._rewrite_entries_file()
            self._update_index()

            print(f"Cleaned up {original_count - len(self._cache)} old entries")

    def _rewrite_entries_file(self):
        """Rewrite the entire entries file"""
        try:
            # Write to temporary file first
            temp_file = self.entries_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                for experience in self._cache:
                    json.dump(experience.to_dict(), f, ensure_ascii=False)
                    f.write('\n')

            # Atomic move
            temp_file.replace(self.entries_file)

        except Exception as e:
            print(f"Failed to rewrite entries file: {e}")

    def clear_all(self):
        """Clear all experiences (for testing)"""
        self._cache = []
        self._loaded = True

        try:
            if self.entries_file.exists():
                self.entries_file.unlink()
            if self.index_file.exists():
                self.index_file.unlink()
        except Exception as e:
            print(f"Failed to clear memory: {e}")