"""Vector database operations using Qdrant."""

import asyncio
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    PointStruct,
    VectorParams,
    Distance,
    FieldCondition,
    MatchValue,
    Range,
)

from src.models import EpisodicMemory
from src.config import get_settings


class QdrantVectorStore:
    """Vector database client for episodic memories."""

    def __init__(self, url: str = None, collection_name: str = None):
        """Initialize Qdrant client.

        Args:
            url: Qdrant server URL. If None, uses config.
            collection_name: Collection name. If None, uses config.
        """
        settings = get_settings()
        self.url = url or settings.qdrant_url
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.embedding_dim = settings.embedding_dimension

        self.client = QdrantClient(url=self.url)
        self._ensure_collection_exists()

    def _ensure_collection_exists(self) -> None:
        """Create collection if it doesn't exist."""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            print(f"Created collection: {self.collection_name}")

    async def add_memory(self, memory: EpisodicMemory) -> UUID:
        """Add a memory to the vector database.

        Args:
            memory: The episodic memory to store.

        Returns:
            The memory ID.
        """
        # Prepare metadata (everything except the embedding)
        payload = {
            "id": str(memory.id),
            "timestamp": memory.timestamp.isoformat(),
            "event_type": memory.event_type,
            "compressed_narrative": memory.compressed_narrative,
            "importance_score": memory.importance_score,
            "last_accessed": memory.last_accessed.isoformat(),
            "access_count": memory.access_count,
            "retrieval_frequency": memory.retrieval_frequency,
            "agents_involved": memory.agents_involved,
            "domains": memory.domains,
            "entities": memory.entities,
            "keywords": memory.keywords,
            "created_at": memory.created_at.isoformat(),
            "consolidated_at": (
                memory.consolidated_at.isoformat()
                if memory.consolidated_at
                else None
            ),
            "decayed_strength": memory.decayed_strength,
            "scheduled_deletion": (
                memory.scheduled_deletion.isoformat()
                if memory.scheduled_deletion
                else None
            ),
            "related_memory_ids": [str(mid) for mid in memory.related_memory_ids],
            "parent_session_id": str(memory.parent_session_id),
        }

        # Create point
        point = PointStruct(
            id=int(memory.id.int % (2**63 - 1)),  # Qdrant requires uint64
            vector=memory.embedding,
            payload=payload,
        )

        # Add to vector DB
        await asyncio.to_thread(
            self.client.upsert,
            self.collection_name,
            points=[point],
        )

        return memory.id

    async def add_memories_batch(
        self, memories: List[EpisodicMemory]
    ) -> List[UUID]:
        """Add multiple memories efficiently.

        Args:
            memories: List of memories to store.

        Returns:
            List of memory IDs.
        """
        points = []
        ids = []

        for memory in memories:
            payload = {
                "id": str(memory.id),
                "timestamp": memory.timestamp.isoformat(),
                "event_type": memory.event_type,
                "compressed_narrative": memory.compressed_narrative,
                "importance_score": memory.importance_score,
                "last_accessed": memory.last_accessed.isoformat(),
                "access_count": memory.access_count,
                "retrieval_frequency": memory.retrieval_frequency,
                "agents_involved": memory.agents_involved,
                "domains": memory.domains,
                "entities": memory.entities,
                "keywords": memory.keywords,
                "created_at": memory.created_at.isoformat(),
                "consolidated_at": (
                    memory.consolidated_at.isoformat()
                    if memory.consolidated_at
                    else None
                ),
                "decayed_strength": memory.decayed_strength,
                "scheduled_deletion": (
                    memory.scheduled_deletion.isoformat()
                    if memory.scheduled_deletion
                    else None
                ),
                "related_memory_ids": [str(mid) for mid in memory.related_memory_ids],
                "parent_session_id": str(memory.parent_session_id),
            }

            point = PointStruct(
                id=int(memory.id.int % (2**63 - 1)),
                vector=memory.embedding,
                payload=payload,
            )
            points.append(point)
            ids.append(memory.id)

        # Batch upsert
        await asyncio.to_thread(
            self.client.upsert,
            self.collection_name,
            points=points,
        )

        return ids

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[EpisodicMemory]:
        """Search for similar memories.

        Args:
            query_embedding: Query vector.
            top_k: Number of results to return.
            filters: Optional filters (min_importance, domains, etc.).

        Returns:
            List of matching memories.
        """
        # Apply filters if provided
        query_filter = None
        if filters:
            conditions = []
            if "min_importance" in filters:
                conditions.append(
                    FieldCondition(
                        key="importance_score",
                        range=Range(
                            gte=filters["min_importance"],
                        ),
                    )
                )
            if "domains" in filters and filters["domains"]:
                conditions.append(
                    FieldCondition(
                        key="domains",
                        match=MatchValue(value=filters["domains"][0]),
                    )
                )
            # Note: Qdrant filter syntax may vary; adjust as needed
            if conditions:
                query_filter = conditions[0]  # Simplified for now

        # Search
        results = await asyncio.to_thread(
            self.client.search,
            self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=query_filter,
        )

        # Convert results to memories
        memories = []
        for result in results:
            payload = result.payload
            try:
                memory = EpisodicMemory(
                    id=UUID(payload["id"]),
                    timestamp=datetime.fromisoformat(payload["timestamp"]),
                    event_type=payload["event_type"],
                    compressed_narrative=payload["compressed_narrative"],
                    embedding=result.vector or [],
                    importance_score=payload["importance_score"],
                    last_accessed=datetime.fromisoformat(
                        payload["last_accessed"]
                    ),
                    access_count=payload["access_count"],
                    retrieval_frequency=payload.get("retrieval_frequency", 0.0),
                    agents_involved=payload.get("agents_involved", []),
                    domains=payload.get("domains", []),
                    entities=payload.get("entities", []),
                    keywords=payload.get("keywords", []),
                    created_at=datetime.fromisoformat(payload["created_at"]),
                    consolidated_at=(
                        datetime.fromisoformat(payload["consolidated_at"])
                        if payload.get("consolidated_at")
                        else None
                    ),
                    decayed_strength=payload.get("decayed_strength", 1.0),
                    scheduled_deletion=(
                        datetime.fromisoformat(payload["scheduled_deletion"])
                        if payload.get("scheduled_deletion")
                        else None
                    ),
                    related_memory_ids=[
                        UUID(mid)
                        for mid in payload.get("related_memory_ids", [])
                    ],
                    parent_session_id=UUID(payload["parent_session_id"]),
                )
                memories.append(memory)
            except Exception as e:
                print(f"Error converting result: {e}")
                continue

        return memories

    async def search_by_id(self, memory_id: UUID) -> Optional[EpisodicMemory]:
        """Retrieve a specific memory by ID.

        Args:
            memory_id: The memory ID.

        Returns:
            The memory if found, None otherwise.
        """
        point_id = int(memory_id.int % (2**63 - 1))

        try:
            points = await asyncio.to_thread(
                self.client.retrieve,
                self.collection_name,
                ids=[point_id],
            )

            if not points:
                return None

            payload = points[0].payload
            memory = EpisodicMemory(
                id=UUID(payload["id"]),
                timestamp=datetime.fromisoformat(payload["timestamp"]),
                event_type=payload["event_type"],
                compressed_narrative=payload["compressed_narrative"],
                embedding=[],
                importance_score=payload["importance_score"],
                last_accessed=datetime.fromisoformat(payload["last_accessed"]),
                access_count=payload["access_count"],
                retrieval_frequency=payload.get("retrieval_frequency", 0.0),
                agents_involved=payload.get("agents_involved", []),
                domains=payload.get("domains", []),
                entities=payload.get("entities", []),
                keywords=payload.get("keywords", []),
                created_at=datetime.fromisoformat(payload["created_at"]),
                consolidated_at=(
                    datetime.fromisoformat(payload["consolidated_at"])
                    if payload.get("consolidated_at")
                    else None
                ),
                decayed_strength=payload.get("decayed_strength", 1.0),
                scheduled_deletion=(
                    datetime.fromisoformat(payload["scheduled_deletion"])
                    if payload.get("scheduled_deletion")
                    else None
                ),
                related_memory_ids=[
                    UUID(mid) for mid in payload.get("related_memory_ids", [])
                ],
                parent_session_id=UUID(payload["parent_session_id"]),
            )
            return memory
        except Exception as e:
            print(f"Error retrieving memory: {e}")
            return None

    async def count(self) -> int:
        """Get total number of memories."""
        collection = await asyncio.to_thread(
            self.client.get_collection,
            self.collection_name,
        )
        return collection.points_count

    async def delete_memory(self, memory_id: UUID) -> bool:
        """Delete a memory by ID.

        Args:
            memory_id: The memory to delete.

        Returns:
            True if successful.
        """
        point_id = int(memory_id.int % (2**63 - 1))

        try:
            await asyncio.to_thread(
                self.client.delete,
                self.collection_name,
                points_selector=[point_id],
            )
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False
