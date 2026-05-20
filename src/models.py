"""Data models for the episodic memory system."""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any


class ImportanceSignals(BaseModel):
    """Input signals for calculating importance score."""

    novelty: float = Field(ge=0.0, le=1.0, description="How novel is this? (0-1)")
    task_success: float = Field(
        ge=0.0, le=1.0, description="Did it complete a task? (0-1)"
    )
    retrieval_frequency: float = Field(
        ge=0.0, le=1.0, description="How often accessed? (0-1)"
    )
    user_signal: float = Field(
        ge=0.0, le=1.0, description="User rating? (0-1)"
    )
    emotional_salience: float = Field(
        ge=0.0, le=1.0, description="Emotionally salient? (0-1)"
    )

    def calculate_importance(
        self,
        weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """Calculate combined importance score.

        Args:
            weights: Custom weights. If None, uses defaults.

        Returns:
            Importance score between 0.0 and 1.0
        """
        if weights is None:
            weights = {
                "novelty": 0.20,
                "task_success": 0.30,
                "retrieval_frequency": 0.25,
                "user_signal": 0.15,
                "emotional_salience": 0.10,
            }

        importance = (
            weights.get("novelty", 0.20) * self.novelty
            + weights.get("task_success", 0.30) * self.task_success
            + weights.get("retrieval_frequency", 0.25) * self.retrieval_frequency
            + weights.get("user_signal", 0.15) * self.user_signal
            + weights.get("emotional_salience", 0.10) * self.emotional_salience
        )

        return min(1.0, max(0.0, importance))


class EpisodicMemory(BaseModel):
    """A single episodic memory (an event)."""

    id: UUID = Field(default_factory=uuid4, description="Unique memory ID")
    timestamp: datetime = Field(
        description="When did this event happen?"
    )
    event_type: str = Field(
        description="Type: 'conversation', 'error', 'milestone', 'interaction'"
    )
    compressed_narrative: str = Field(
        description="100-300 word summary of the event"
    )
    embedding: List[float] = Field(
        description="Vector embedding (1536 or 3072 dims)"
    )

    # Importance tracking
    importance_score: float = Field(
        ge=0.0, le=1.0, description="Importance (0-1)"
    )
    last_accessed: datetime = Field(
        description="When was this memory last retrieved?"
    )
    access_count: int = Field(ge=0, description="How many times accessed?")
    retrieval_frequency: float = Field(
        ge=0.0, le=1.0, description="Relative retrieval frequency"
    )

    # Metadata for filtering
    agents_involved: List[str] = Field(
        default=[], description="Which agents were involved?"
    )
    domains: List[str] = Field(
        default=[], description="Knowledge domains (Python, Math, etc.)"
    )
    entities: List[str] = Field(
        default=[], description="Named entities mentioned"
    )
    keywords: List[str] = Field(
        default=[], description="Key concepts"
    )

    # Lifecycle
    created_at: datetime = Field(
        description="When was this memory created?"
    )
    consolidated_at: Optional[datetime] = Field(
        default=None, description="When was it consolidated?"
    )
    decayed_strength: float = Field(
        ge=0.0, le=1.0, default=1.0,
        description="Current memory strength (0-1)"
    )
    scheduled_deletion: Optional[datetime] = Field(
        default=None, description="When should this be deleted?"
    )

    # Relationships
    related_memory_ids: List[UUID] = Field(
        default=[], description="IDs of similar memories"
    )
    parent_session_id: UUID = Field(
        description="Which session generated this memory?"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2026-05-20T14:30:00Z",
                "event_type": "conversation",
                "compressed_narrative": "User asked about Python indexing...",
                "embedding": [0.123, -0.456, 0.789],
                "importance_score": 0.65,
                "last_accessed": "2026-05-20T14:30:00Z",
                "access_count": 1,
                "agents_involved": ["Claude"],
                "domains": ["Python"],
                "created_at": "2026-05-20T14:30:00Z",
                "parent_session_id": "session-id",
            }
        }


class WorkingMemory(BaseModel):
    """Current context window for active reasoning."""

    active_turn: str = Field(
        description="The current user query or task"
    )
    retrieved_memories: List[EpisodicMemory] = Field(
        default=[], description="Top-K retrieved memories"
    )
    task_state: Dict[str, Any] = Field(
        default={}, description="Task-specific context"
    )
    agent_state: Dict[str, Any] = Field(
        default={}, description="Agent goals and state"
    )
    token_count: int = Field(
        ge=0, description="Current token usage"
    )
    created_at: datetime = Field(
        description="When was this context created?"
    )
    expires_at: datetime = Field(
        description="When does this context expire?"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "active_turn": "How do I fix IndexError in Python?",
                "retrieved_memories": [],
                "task_state": {},
                "token_count": 1500,
                "created_at": "2026-05-20T14:30:00Z",
                "expires_at": "2026-05-20T15:30:00Z",
            }
        }


class AddEpisodeRequest(BaseModel):
    """Request to add a new episode to memory."""

    narrative: str = Field(
        description="Text description of the event"
    )
    event_type: str = Field(
        default="conversation",
        description="Type of event"
    )
    importance_signals: ImportanceSignals = Field(
        description="Signals for importance calculation"
    )
    metadata: Dict[str, Any] = Field(
        default={},
        description="Additional metadata (domains, entities, etc.)"
    )
    session_id: UUID = Field(
        description="Which session is this from?"
    )


class SearchRequest(BaseModel):
    """Request to search for memories."""

    query: str = Field(
        description="Search query"
    )
    top_k: int = Field(
        default=5, ge=1, le=50,
        description="Number of results to return"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Filters (min_importance, domains, days_back, etc.)"
    )


class MemoryStats(BaseModel):
    """Statistics about the memory system."""

    total_memories: int = Field(
        description="Total episodic memories stored"
    )
    high_importance_count: int = Field(
        description="Memories with importance > 0.7"
    )
    medium_importance_count: int = Field(
        description="Memories with importance 0.4-0.7"
    )
    low_importance_count: int = Field(
        description="Memories with importance < 0.4"
    )
    avg_importance: float = Field(
        description="Average importance score"
    )
    total_embeddings_cached: int = Field(
        description="Embeddings in cache"
    )
    storage_used_mb: float = Field(
        description="Storage used in MB"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_memories": 150,
                "high_importance_count": 45,
                "medium_importance_count": 75,
                "low_importance_count": 30,
                "avg_importance": 0.52,
                "total_embeddings_cached": 150,
                "storage_used_mb": 15.3,
            }
        }
