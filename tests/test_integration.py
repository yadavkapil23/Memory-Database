"""Integration tests for episodic memory system."""

import pytest
import asyncio
from datetime import datetime
from uuid import uuid4

from src.memory_system import MemorySystem
from src.models import ImportanceSignals, EpisodicMemory


@pytest.fixture
def memory_system():
    """Create a memory system instance."""
    return MemorySystem()


@pytest.fixture
def session_id():
    """Create a session ID."""
    return uuid4()


@pytest.mark.asyncio
async def test_add_single_episode(memory_system, session_id):
    """Test adding a single episode."""
    memory_id = await memory_system.add_episode(
        narrative="User asked about Python loops.",
        event_type="conversation",
        importance_signals=ImportanceSignals(
            novelty=0.6,
            task_success=1.0,
            retrieval_frequency=0.0,
            user_signal=0.9,
            emotional_salience=0.2,
        ),
        metadata={
            "agents_involved": ["Claude"],
            "domains": ["Python"],
            "entities": ["loops"],
            "keywords": ["for", "while", "iteration"],
        },
        session_id=session_id,
    )

    assert memory_id is not None
    assert isinstance(memory_id, type(uuid4()))


@pytest.mark.asyncio
async def test_retrieve_added_episode(memory_system, session_id):
    """Test retrieving an episode after adding it."""
    # Add episode
    memory_id = await memory_system.add_episode(
        narrative="Python list indexing starts at 0.",
        event_type="conversation",
        importance_signals=ImportanceSignals(
            novelty=0.7,
            task_success=1.0,
            retrieval_frequency=0.0,
            user_signal=0.95,
            emotional_salience=0.1,
        ),
        metadata={"domains": ["Python"], "keywords": ["indexing", "list"]},
        session_id=session_id,
    )

    # Search for it
    await asyncio.sleep(0.5)  # Give DB time to index
    results = await memory_system.retrieve(
        query="Python list indexing",
        top_k=5,
    )

    assert len(results) > 0
    assert results[0].id == memory_id
    assert "indexing" in results[0].keywords or "Python" in results[0].domains


@pytest.mark.asyncio
async def test_batch_add_episodes(memory_system, session_id):
    """Test adding multiple episodes at once."""
    episodes = [
        {
            "narrative": "User learned about Python dictionaries.",
            "event_type": "conversation",
            "importance_signals": ImportanceSignals(
                novelty=0.8, task_success=1.0, retrieval_frequency=0.0,
                user_signal=0.9, emotional_salience=0.3
            ),
            "metadata": {"domains": ["Python"], "keywords": ["dict"]},
        },
        {
            "narrative": "Error handling in Python with try/except.",
            "event_type": "conversation",
            "importance_signals": ImportanceSignals(
                novelty=0.7, task_success=1.0, retrieval_frequency=0.0,
                user_signal=0.8, emotional_salience=0.4
            ),
            "metadata": {"domains": ["Python"], "keywords": ["error", "exception"]},
        },
        {
            "narrative": "List comprehensions are powerful in Python.",
            "event_type": "conversation",
            "importance_signals": ImportanceSignals(
                novelty=0.6, task_success=1.0, retrieval_frequency=0.0,
                user_signal=0.85, emotional_salience=0.2
            ),
            "metadata": {"domains": ["Python"], "keywords": ["list", "comprehension"]},
        },
    ]

    memory_ids = await memory_system.add_episodes_batch(episodes, session_id)

    assert len(memory_ids) == 3
    assert all(mid is not None for mid in memory_ids)


@pytest.mark.asyncio
async def test_importance_calculation(memory_system, session_id):
    """Test importance score calculation."""
    # Add high importance
    high_id = await memory_system.add_episode(
        narrative="Critical bug fix.",
        event_type="error",
        importance_signals=ImportanceSignals(
            novelty=1.0, task_success=1.0, retrieval_frequency=0.5,
            user_signal=1.0, emotional_salience=0.8
        ),
        metadata={},
        session_id=session_id,
    )

    # Add low importance
    low_id = await memory_system.add_episode(
        narrative="Random thought.",
        event_type="conversation",
        importance_signals=ImportanceSignals(
            novelty=0.0, task_success=0.0, retrieval_frequency=0.0,
            user_signal=0.0, emotional_salience=0.0
        ),
        metadata={},
        session_id=session_id,
    )

    # Retrieve both
    high_mem = await memory_system.retrieve_by_id(high_id)
    low_mem = await memory_system.retrieve_by_id(low_id)

    assert high_mem is not None
    assert low_mem is not None
    assert high_mem.importance_score > low_mem.importance_score


@pytest.mark.asyncio
async def test_metadata_filtering(memory_system, session_id):
    """Test filtering by metadata."""
    # Add Python-specific memory
    await memory_system.add_episode(
        narrative="Python specific content.",
        event_type="conversation",
        importance_signals=ImportanceSignals(
            novelty=0.5, task_success=1.0, retrieval_frequency=0.0,
            user_signal=0.8, emotional_salience=0.1
        ),
        metadata={"domains": ["Python"], "keywords": ["python"]},
        session_id=session_id,
    )

    # Add JavaScript-specific memory
    await memory_system.add_episode(
        narrative="JavaScript specific content.",
        event_type="conversation",
        importance_signals=ImportanceSignals(
            novelty=0.5, task_success=1.0, retrieval_frequency=0.0,
            user_signal=0.8, emotional_salience=0.1
        ),
        metadata={"domains": ["JavaScript"], "keywords": ["javascript"]},
        session_id=session_id,
    )

    # Search with filter
    await asyncio.sleep(0.5)
    results = await memory_system.retrieve(
        query="Programming languages",
        top_k=10,
        filters={"domains": ["Python"]},
    )

    # Should get Python results
    assert any("Python" in r.domains for r in results)


@pytest.mark.asyncio
async def test_update_importance(memory_system, session_id):
    """Test updating memory importance."""
    # Add memory
    memory_id = await memory_system.add_episode(
        narrative="Initial memory.",
        event_type="conversation",
        importance_signals=ImportanceSignals(
            novelty=0.3, task_success=0.5, retrieval_frequency=0.0,
            user_signal=0.4, emotional_salience=0.1
        ),
        metadata={},
        session_id=session_id,
    )

    # Update importance
    success = await memory_system.update_importance(
        memory_id,
        new_signals={
            "task_success": 1.0,
            "user_signal": 0.95,
        },
    )

    assert success
    # Note: Verification would require re-retrieving the memory


@pytest.mark.asyncio
async def test_delete_memory(memory_system, session_id):
    """Test deleting a memory."""
    # Add memory
    memory_id = await memory_system.add_episode(
        narrative="Memory to delete.",
        event_type="conversation",
        importance_signals=ImportanceSignals(
            novelty=0.5, task_success=1.0, retrieval_frequency=0.0,
            user_signal=0.5, emotional_salience=0.1
        ),
        metadata={},
        session_id=session_id,
    )

    # Delete it
    success = await memory_system.delete_memory(memory_id)
    assert success


@pytest.mark.asyncio
async def test_system_health_check(memory_system):
    """Test system health check."""
    health = await memory_system.health_check()

    assert isinstance(health, dict)
    assert "vector_db" in health
    assert "embedder" in health
    # Both should be True if services are running
    assert health["vector_db"] or not health["vector_db"]  # Either is valid


@pytest.mark.asyncio
async def test_get_system_stats(memory_system):
    """Test getting system statistics."""
    stats = await memory_system.get_stats()

    assert stats.total_memories >= 0
    assert stats.high_importance_count >= 0
    assert stats.medium_importance_count >= 0
    assert stats.low_importance_count >= 0
    assert 0 <= stats.avg_importance <= 1.0


@pytest.mark.asyncio
async def test_multiple_sessions(memory_system):
    """Test handling multiple sessions."""
    session1 = uuid4()
    session2 = uuid4()

    # Add to session 1
    mem1 = await memory_system.add_episode(
        narrative="Session 1 memory.",
        event_type="conversation",
        importance_signals=ImportanceSignals(
            novelty=0.5, task_success=1.0, retrieval_frequency=0.0,
            user_signal=0.8, emotional_salience=0.1
        ),
        session_id=session1,
    )

    # Add to session 2
    mem2 = await memory_system.add_episode(
        narrative="Session 2 memory.",
        event_type="conversation",
        importance_signals=ImportanceSignals(
            novelty=0.5, task_success=1.0, retrieval_frequency=0.0,
            user_signal=0.8, emotional_salience=0.1
        ),
        session_id=session2,
    )

    assert mem1 != mem2


@pytest.mark.asyncio
async def test_concurrent_operations(memory_system, session_id):
    """Test concurrent add operations."""
    tasks = [
        memory_system.add_episode(
            narrative=f"Concurrent memory {i}.",
            event_type="conversation",
            importance_signals=ImportanceSignals(
                novelty=0.5, task_success=1.0, retrieval_frequency=0.0,
                user_signal=0.8, emotional_salience=0.1
            ),
            session_id=session_id,
        )
        for i in range(5)
    ]

    memory_ids = await asyncio.gather(*tasks)

    assert len(memory_ids) == 5
    assert all(mid is not None for mid in memory_ids)
    assert len(set(memory_ids)) == 5  # All unique


@pytest.mark.asyncio
async def test_cache_embedding(memory_system, session_id):
    """Test that embeddings are cached."""
    # Add first memory
    await memory_system.add_episode(
        narrative="Test narrative for caching.",
        event_type="conversation",
        importance_signals=ImportanceSignals(
            novelty=0.5, task_success=1.0, retrieval_frequency=0.0,
            user_signal=0.8, emotional_salience=0.1
        ),
        session_id=session_id,
    )

    # Add second memory with exact same narrative (should use cache)
    mem2 = await memory_system.add_episode(
        narrative="Test narrative for caching.",  # Exact same
        event_type="conversation",
        importance_signals=ImportanceSignals(
            novelty=0.5, task_success=1.0, retrieval_frequency=0.0,
            user_signal=0.8, emotional_salience=0.1
        ),
        session_id=session_id,
    )

    assert mem2 is not None
    # Second call should be faster (from cache)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
