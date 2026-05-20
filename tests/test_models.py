"""Tests for data models."""

import pytest
from datetime import datetime
from uuid import uuid4

from src.models import (
    ImportanceSignals,
    EpisodicMemory,
    WorkingMemory,
)


class TestImportanceSignals:
    """Test importance signal calculation."""

    def test_basic_calculation(self):
        """Test basic importance score calculation."""
        signals = ImportanceSignals(
            novelty=0.5,
            task_success=1.0,
            retrieval_frequency=0.0,
            user_signal=0.8,
            emotional_salience=0.2,
        )

        score = signals.calculate_importance()

        # Manual calculation:
        # 0.20 * 0.5 + 0.30 * 1.0 + 0.25 * 0.0 + 0.15 * 0.8 + 0.10 * 0.2
        # = 0.1 + 0.3 + 0 + 0.12 + 0.02 = 0.54
        assert abs(score - 0.54) < 0.001

    def test_high_importance(self):
        """Test high importance scenario."""
        signals = ImportanceSignals(
            novelty=1.0,
            task_success=1.0,
            retrieval_frequency=1.0,
            user_signal=1.0,
            emotional_salience=1.0,
        )

        score = signals.calculate_importance()
        assert score == 1.0

    def test_low_importance(self):
        """Test low importance scenario."""
        signals = ImportanceSignals(
            novelty=0.0,
            task_success=0.0,
            retrieval_frequency=0.0,
            user_signal=0.0,
            emotional_salience=0.0,
        )

        score = signals.calculate_importance()
        assert score == 0.0

    def test_custom_weights(self):
        """Test custom importance weights."""
        signals = ImportanceSignals(
            novelty=0.5,
            task_success=0.5,
            retrieval_frequency=0.5,
            user_signal=0.5,
            emotional_salience=0.5,
        )

        # All signals at 0.5, default weights sum to 1.0
        score = signals.calculate_importance()
        assert score == 0.5

        # Custom weights: only task_success matters
        custom_weights = {
            "novelty": 0.0,
            "task_success": 1.0,
            "retrieval_frequency": 0.0,
            "user_signal": 0.0,
            "emotional_salience": 0.0,
        }
        score = signals.calculate_importance(weights=custom_weights)
        assert score == 0.5


class TestEpisodicMemory:
    """Test episodic memory model."""

    def test_create_memory(self):
        """Test creating a memory."""
        session_id = uuid4()
        now = datetime.utcnow()

        memory = EpisodicMemory(
            timestamp=now,
            event_type="conversation",
            compressed_narrative="Test narrative",
            embedding=[0.1, 0.2, 0.3],
            importance_score=0.75,
            last_accessed=now,
            access_count=0,
            created_at=now,
            parent_session_id=session_id,
        )

        assert memory.event_type == "conversation"
        assert memory.importance_score == 0.75
        assert memory.access_count == 0
        assert memory.parent_session_id == session_id

    def test_memory_with_metadata(self):
        """Test memory with rich metadata."""
        session_id = uuid4()
        now = datetime.utcnow()

        memory = EpisodicMemory(
            timestamp=now,
            event_type="conversation",
            compressed_narrative="User asked about Python loops.",
            embedding=[0.1, 0.2, 0.3],
            importance_score=0.8,
            last_accessed=now,
            access_count=1,
            retrieval_frequency=0.3,
            agents_involved=["Claude"],
            domains=["Python", "Programming"],
            entities=["User", "Python", "loops"],
            keywords=["loop", "iteration", "performance"],
            created_at=now,
            parent_session_id=session_id,
        )

        assert "Python" in memory.domains
        assert "loop" in memory.keywords
        assert memory.retrieval_frequency == 0.3


class TestWorkingMemory:
    """Test working memory model."""

    def test_create_working_memory(self):
        """Test creating working memory."""
        now = datetime.utcnow()
        later = now + pytest.approx(timedelta(hours=1))

        working = WorkingMemory(
            active_turn="What is Python?",
            token_count=150,
            created_at=now,
            expires_at=later,
        )

        assert working.active_turn == "What is Python?"
        assert working.token_count == 150
        assert len(working.retrieved_memories) == 0

    def test_working_memory_with_context(self):
        """Test working memory with task context."""
        now = datetime.utcnow()
        later = now + pytest.approx(timedelta(hours=1))

        working = WorkingMemory(
            active_turn="Debug this function",
            task_state={"function": "calculate_sum", "error": "IndexError"},
            agent_state={"mode": "debugging", "depth": 0},
            token_count=500,
            created_at=now,
            expires_at=later,
        )

        assert working.task_state["function"] == "calculate_sum"
        assert working.agent_state["mode"] == "debugging"


# Import timedelta for test
from datetime import timedelta


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
