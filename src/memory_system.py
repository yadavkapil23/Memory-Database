"""Main memory system orchestrating all components."""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from src.models import (
    EpisodicMemory,
    ImportanceSignals,
    AddEpisodeRequest,
    MemoryStats,
)
from src.vector_store import QdrantVectorStore
from src.embedder import OpenAIEmbedder
from src.config import get_settings


class MemorySystem:
    """Episodic memory system for AI agents."""

    def __init__(self):
        """Initialize the memory system."""
        self.settings = get_settings()
        self.vector_store = QdrantVectorStore()
        self.embedder = OpenAIEmbedder()

    async def add_episode(
        self,
        narrative: str,
        event_type: str,
        importance_signals: ImportanceSignals,
        metadata: Optional[Dict[str, Any]] = None,
        session_id: Optional[UUID] = None,
    ) -> UUID:
        """Add a new episode to memory.

        Args:
            narrative: Text description of the event.
            event_type: Type of event (conversation, error, etc.).
            importance_signals: Signals for importance calculation.
            metadata: Additional metadata (domains, entities, etc.).
            session_id: Which session this is from.

        Returns:
            The memory ID.
        """
        if metadata is None:
            metadata = {}
        if session_id is None:
            session_id = uuid4()

        # Generate embedding
        embedding = await self.embedder.embed(narrative)

        # Calculate importance
        importance_score = importance_signals.calculate_importance()

        # Create memory object
        now = datetime.utcnow()
        memory = EpisodicMemory(
            timestamp=now,
            event_type=event_type,
            compressed_narrative=narrative,
            embedding=embedding,
            importance_score=importance_score,
            last_accessed=now,
            access_count=0,
            retrieval_frequency=0.0,
            created_at=now,
            parent_session_id=session_id,
            agents_involved=metadata.get("agents_involved", []),
            domains=metadata.get("domains", []),
            entities=metadata.get("entities", []),
            keywords=metadata.get("keywords", []),
        )

        # Store in vector DB
        memory_id = await self.vector_store.add_memory(memory)

        return memory_id

    async def add_episodes_batch(
        self,
        episodes: List[Dict[str, Any]],
        session_id: Optional[UUID] = None,
    ) -> List[UUID]:
        """Add multiple episodes efficiently.

        Each episode dict should have:
        - narrative (required)
        - event_type (optional, default "conversation")
        - importance_signals (required)
        - metadata (optional)

        Args:
            episodes: List of episode dicts.
            session_id: Which session these are from.

        Returns:
            List of memory IDs.
        """
        if session_id is None:
            session_id = uuid4()

        # Extract narratives for batch embedding
        narratives = [ep["narrative"] for ep in episodes]
        embeddings = await self.embedder.embed_batch(narratives)

        # Create memory objects
        memories = []
        now = datetime.utcnow()

        for i, episode in enumerate(episodes):
            importance_signals = episode.get("importance_signals")
            if not isinstance(importance_signals, ImportanceSignals):
                importance_signals = ImportanceSignals(**importance_signals)

            metadata = episode.get("metadata", {})

            importance_score = importance_signals.calculate_importance()

            memory = EpisodicMemory(
                timestamp=now - timedelta(seconds=i),  # Stagger timestamps
                event_type=episode.get("event_type", "conversation"),
                compressed_narrative=episode["narrative"],
                embedding=embeddings[i],
                importance_score=importance_score,
                last_accessed=now,
                access_count=0,
                retrieval_frequency=0.0,
                created_at=now - timedelta(seconds=i),
                parent_session_id=session_id,
                agents_involved=metadata.get("agents_involved", []),
                domains=metadata.get("domains", []),
                entities=metadata.get("entities", []),
                keywords=metadata.get("keywords", []),
            )
            memories.append(memory)

        # Batch store
        memory_ids = await self.vector_store.add_memories_batch(memories)

        return memory_ids

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[EpisodicMemory]:
        """Retrieve relevant memories.

        Args:
            query: Search query.
            top_k: Number of results to return.
            filters: Optional filters (min_importance, domains, days_back, etc.).

        Returns:
            List of matching memories.
        """
        # Embed query
        query_embedding = await self.embedder.embed(query)

        # Search vector DB
        results = await self.vector_store.search(
            query_embedding,
            top_k=top_k,
            filters=filters,
        )

        # Update access counts
        for memory in results:
            memory.access_count += 1
            memory.last_accessed = datetime.utcnow()

        return results

    async def retrieve_by_id(self, memory_id: UUID) -> Optional[EpisodicMemory]:
        """Retrieve a specific memory.

        Args:
            memory_id: The memory ID.

        Returns:
            The memory if found.
        """
        memory = await self.vector_store.search_by_id(memory_id)

        if memory:
            memory.access_count += 1
            memory.last_accessed = datetime.utcnow()

        return memory

    async def retrieve_temporal(
        self,
        start_date: datetime,
        end_date: datetime,
        top_k: int = 50,
    ) -> List[EpisodicMemory]:
        """Retrieve memories from a time period (simplified - needs filtering).

        Args:
            start_date: Start of time range.
            end_date: End of time range.
            top_k: Max results.

        Returns:
            Memories in the time period (not yet implemented with Qdrant filtering).
        """
        # TODO: Implement proper date filtering in Qdrant
        # For now, return empty
        return []

    async def update_importance(
        self,
        memory_id: UUID,
        new_signals: Optional[Dict[str, float]] = None,
        new_score: Optional[float] = None,
    ) -> bool:
        """Update a memory's importance.

        Args:
            memory_id: The memory to update.
            new_signals: New signal values to recalculate from.
            new_score: Or provide a new score directly.

        Returns:
            True if successful.
        """
        memory = await self.vector_store.search_by_id(memory_id)
        if not memory:
            return False

        # Update score
        if new_score is not None:
            memory.importance_score = new_score
        elif new_signals:
            signals = ImportanceSignals(**new_signals)
            memory.importance_score = signals.calculate_importance()

        # Re-store
        await self.vector_store.add_memory(memory)

        return True

    async def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory.

        Args:
            memory_id: The memory to delete.

        Returns:
            True if successful.
        """
        return await self.vector_store.delete_memory(memory_id)

    async def get_stats(self) -> MemoryStats:
        """Get memory system statistics.

        Returns:
            Statistics about the system.
        """
        total = await self.vector_store.count()

        # TODO: Get actual stats from DB
        # For now, return defaults
        return MemoryStats(
            total_memories=total,
            high_importance_count=0,
            medium_importance_count=0,
            low_importance_count=0,
            avg_importance=0.5,
            total_embeddings_cached=0,
            storage_used_mb=0.0,
        )

    async def clear_embedding_cache(self) -> None:
        """Clear the embedding cache."""
        await self.embedder.clear_cache()

    async def health_check(self) -> Dict[str, bool]:
        """Check if all components are healthy.

        Returns:
            Health status of each component.
        """
        status = {}

        # Check vector DB
        try:
            count = await self.vector_store.count()
            status["vector_db"] = True
        except Exception as e:
            status["vector_db"] = False
            print(f"Vector DB error: {e}")

        # Check embedder (can't really test without API key)
        status["embedder"] = True

        return status
