# memory/semantic_memory/knowledge_graph.py

from typing import Dict, List, Set, Tuple, Any, Optional
import json
import time
from pathlib import Path
from collections import defaultdict


class Triple:
    """Represents a knowledge triple (subject, predicate, object)"""

    def __init__(self, subject: str, predicate: str, object_: Any,
                 confidence: float = 1.0, source: str = "", timestamp: float = None):
        self.subject = subject
        self.predicate = predicate
        self.object = object_
        self.confidence = confidence
        self.source = source
        self.timestamp = timestamp or time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'subject': self.subject,
            'predicate': self.predicate,
            'object': self.object,
            'confidence': self.confidence,
            'source': self.source,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Triple':
        return cls(
            subject=data['subject'],
            predicate=data['predicate'],
            object_=data['object'],
            confidence=data.get('confidence', 1.0),
            source=data.get('source', ''),
            timestamp=data.get('timestamp', time.time())
        )

    def __repr__(self) -> str:
        return f"Triple({self.subject}, {self.predicate}, {self.object})"


class KnowledgeGraph:
    """In-memory knowledge graph for semantic memory"""

    def __init__(self, storage_path: str = "memory/semantic"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.triples_file = self.storage_path / "triples.jsonl"

        # In-memory storage
        self._triples: List[Triple] = []
        self._subject_index: Dict[str, Set[int]] = defaultdict(set)
        self._predicate_index: Dict[str, Set[int]] = defaultdict(set)
        self._object_index: Dict[str, Set[int]] = defaultdict(set)

        # Load existing data
        self._load_triples()

    def add_triple(self, subject: str, predicate: str, object_: Any,
                   confidence: float = 1.0, source: str = "") -> bool:
        """Add a new triple to the knowledge graph"""

        # Check if triple already exists
        existing = self.find_triples(subject, predicate, object_)
        if existing:
            # Update confidence if higher
            if confidence > existing[0].confidence:
                existing[0].confidence = confidence
                existing[0].timestamp = time.time()
                self._persist_triples()
            return False

        # Create new triple
        triple = Triple(subject, predicate, object_, confidence, source)
        triple_idx = len(self._triples)

        self._triples.append(triple)

        # Update indices
        self._subject_index[subject].add(triple_idx)
        self._predicate_index[predicate].add(triple_idx)

        # Handle object indexing (objects can be complex types)
        obj_key = self._normalize_object(object_)
        self._object_index[obj_key].add(triple_idx)

        # Persist to disk
        self._persist_triple(triple)

        return True

    def remove_triple(self, subject: str, predicate: str, object_: Any) -> bool:
        """Remove a triple from the knowledge graph"""

        triples = self.find_triples(subject, predicate, object_)
        if not triples:
            return False

        # Remove the first matching triple
        triple = triples[0]
        try:
            idx = self._triples.index(triple)
        except ValueError:
            return False

        # Remove from storage
        self._triples.pop(idx)

        # Update indices (rebuild them for simplicity)
        self._rebuild_indices()

        # Rewrite triples file
        self._rewrite_triples_file()

        return True

    def find_triples(self, subject: Optional[str] = None, predicate: Optional[str] = None,
                    object_: Optional[Any] = None) -> List[Triple]:
        """Find triples matching the given pattern"""

        candidates = set(range(len(self._triples)))

        # Filter by subject
        if subject is not None:
            candidates &= self._subject_index.get(subject, set())

        # Filter by predicate
        if predicate is not None:
            candidates &= self._predicate_index.get(predicate, set())

        # Filter by object
        if object_ is not None:
            obj_key = self._normalize_object(object_)
            candidates &= self._object_index.get(obj_key, set())

        # Return matching triples
        return [self._triples[i] for i in sorted(candidates)]

    def query(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Execute a simple query on the knowledge graph"""

        # Very basic query parsing - in production you'd want a proper query language
        results = []

        if query.startswith("FIND") or query.startswith("find"):
            # Simple pattern matching: find subject predicate object
            parts = query.split()
            if len(parts) >= 4:
                subject = parts[1] if parts[1] != "?" else None
                predicate = parts[2] if parts[2] != "?" else None
                object_ = parts[3] if parts[3] != "?" else None

                triples = self.find_triples(subject, predicate, object_)

                for triple in triples[:limit]:
                    results.append({
                        'subject': triple.subject,
                        'predicate': triple.predicate,
                        'object': triple.object,
                        'confidence': triple.confidence,
                        'source': triple.source
                    })

        elif query.startswith("WHAT") or query.startswith("what"):
            # Natural language queries
            query_lower = query.lower()

            if "is" in query_lower or "are" in query_lower:
                # Find relationships
                triples = self.find_triples(predicate="is_a")
                results = [{
                    'subject': t.subject,
                    'relation': 'is a',
                    'object': t.object,
                    'confidence': t.confidence
                } for t in triples[:limit]]

            elif "can" in query_lower or "able" in query_lower:
                # Find capabilities
                triples = self.find_triples(predicate="can_do")
                results = [{
                    'subject': t.subject,
                    'capability': t.object,
                    'confidence': t.confidence
                } for t in triples[:limit]]

        return results

    def get_related_concepts(self, concept: str, depth: int = 2) -> Dict[str, Any]:
        """Get concepts related to the given concept"""

        visited = set()
        related = defaultdict(list)

        def traverse(current_concept: str, current_depth: int):
            if current_depth > depth or current_concept in visited:
                return

            visited.add(current_concept)

            # Find all triples involving this concept
            subject_triples = self.find_triples(subject=current_concept)
            object_triples = self.find_triples(object_=current_concept)

            for triple in subject_triples + object_triples:
                if triple.subject == current_concept:
                    related[triple.predicate].append({
                        'concept': triple.object,
                        'direction': 'outgoing',
                        'confidence': triple.confidence
                    })
                    if current_depth < depth:
                        traverse(str(triple.object), current_depth + 1)
                elif triple.object == current_concept:
                    related[triple.predicate].append({
                        'concept': triple.subject,
                        'direction': 'incoming',
                        'confidence': triple.confidence
                    })
                    if current_depth < depth:
                        traverse(triple.subject, current_depth + 1)

        traverse(concept, 0)

        return {
            'concept': concept,
            'relations': dict(related),
            'total_relations': sum(len(rels) for rels in related.values())
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""

        if not self._triples:
            return {
                'total_triples': 0,
                'unique_subjects': 0,
                'unique_predicates': 0,
                'unique_objects': 0,
                'avg_confidence': 0.0
            }

        subjects = set()
        predicates = set()
        objects = set()
        confidences = []

        for triple in self._triples:
            subjects.add(triple.subject)
            predicates.add(triple.predicate)
            objects.add(self._normalize_object(triple.object))
            confidences.append(triple.confidence)

        return {
            'total_triples': len(self._triples),
            'unique_subjects': len(subjects),
            'unique_predicates': len(predicates),
            'unique_objects': len(objects),
            'avg_confidence': sum(confidences) / len(confidences)
        }

    def _normalize_object(self, obj: Any) -> str:
        """Normalize object for indexing"""
        if isinstance(obj, (str, int, float, bool)):
            return str(obj)
        elif isinstance(obj, (list, tuple)):
            return f"list_{len(obj)}"
        elif isinstance(obj, dict):
            return f"dict_{len(obj)}"
        else:
            return f"object_{type(obj).__name__}"

    def _rebuild_indices(self):
        """Rebuild all indices after changes"""
        self._subject_index.clear()
        self._predicate_index.clear()
        self._object_index.clear()

        for idx, triple in enumerate(self._triples):
            self._subject_index[triple.subject].add(idx)
            self._predicate_index[triple.predicate].add(idx)
            obj_key = self._normalize_object(triple.object)
            self._object_index[obj_key].add(idx)

    def _persist_triple(self, triple: Triple):
        """Persist a single triple to disk"""
        try:
            with open(self.triples_file, 'a', encoding='utf-8') as f:
                json.dump(triple.to_dict(), f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            print(f"Failed to persist triple: {e}")

    def _persist_triples(self):
        """Persist all triples to disk"""
        try:
            # Write to temporary file first
            temp_file = self.triples_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                for triple in self._triples:
                    json.dump(triple.to_dict(), f, ensure_ascii=False)
                    f.write('\n')

            # Atomic move
            temp_file.replace(self.triples_file)

        except Exception as e:
            print(f"Failed to persist triples: {e}")

    def _rewrite_triples_file(self):
        """Rewrite the entire triples file"""
        self._persist_triples()

    def _load_triples(self):
        """Load triples from disk"""
        try:
            if self.triples_file.exists():
                with open(self.triples_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                data = json.loads(line)
                                triple = Triple.from_dict(data)
                                self._triples.append(triple)
                            except json.JSONDecodeError:
                                continue  # Skip corrupted lines

                # Build indices
                self._rebuild_indices()

        except Exception as e:
            print(f"Failed to load triples: {e}")
            self._triples = []

    def clear_all(self):
        """Clear all knowledge (for testing)"""
        self._triples.clear()
        self._subject_index.clear()
        self._predicate_index.clear()
        self._object_index.clear()

        try:
            if self.triples_file.exists():
                self.triples_file.unlink()
        except Exception as e:
            print(f"Failed to clear knowledge: {e}")