# Episodic AI Memory System - Quick Start Guide

**For:** First-time setup and Phase 1 kickoff  
**Time to read:** 10 minutes

---

## What You're Building

A memory system for AI agents that remembers important events, forgets unimportant ones, learns patterns, and retrieves relevant memories efficiently.

**Key Innovation:** Uses importance scores to determine what to keep, what to compress, and what to forget.

---

## Core Concepts (One Paragraph Each)

### Working Memory
The current context window. Whatever the agent is actively thinking about. Gets cleared at the end of each session. Fast, in-memory storage. Like your desktop workspace — cluttered but immediately accessible.

### Episodic Memory  
Specific events stored as compressed narratives with embeddings. The agent remembers "last Tuesday I fixed a Python bug" or "user prefers concise explanations." Decays over time based on importance. Like your diary — important entries you reread, forgotten ones fade.

### Semantic Memory
Timeless patterns extracted from many episodes. "Users usually need variable definitions when seeing NameError" or "Python off-by-one errors happen in loops." Persists indefinitely. Like your knowledge base — general lessons learned.

### Importance Score
A 0-1 number describing how important a memory is. Calculated from: Did it help complete a task? Is it novel? Does the user rate it highly? The higher the score, the longer it survives.

### Consolidation
Background process that runs periodically. Compresses recent memories into narratives, extracts patterns into semantic memory, applies decay. Like sleeping and remembering what mattered today.

### Forgetting Curve
Math that makes memories weaker over time. High-importance memories decay slowly. Low-importance ones decay fast and get deleted. Mimics how human memory works.

---

## The 5-Minute Mental Model

```
New Event Happens
       ↓
Calculate Importance (0-1)
       ↓
   Store Where?
   ├─ Score 0.8+  → Working + Episodic
   ├─ Score 0.4-0.8 → Episodic only
   └─ Score <0.4  → Extract patterns only
       ↓
Every Day (Consolidation)
       ├─ Compress narratives
       ├─ Extract patterns → Semantic memory
       └─ Apply decay → Delete expired
       ↓
Query Comes In
       ├─ Search working memory (current context)
       ├─ Search episodic (past events)
       ├─ Query semantic (learned patterns)
       └─ Rank & return relevant
```

---

## Phase 1: What You'll Actually Build (Weeks 1-4)

**Goal:** A working system that can store and retrieve episodes.

**By end of Week 1:**
- Project folder created
- Qdrant running locally
- PostgreSQL set up
- Can run tests

**By end of Week 2:**
- Data models defined
- Database schema created
- Example data in system

**By end of Week 3:**
- Can call OpenAI embeddings
- Embeddings cached locally
- No wasted API calls

**By end of Week 4:**
- Can add an episode
- Can search by similarity
- 100+ tests passing
- Documented and working

---

## Setup Checklist (Do This First)

### Prerequisites
- [ ] Python 3.11+ installed
- [ ] OpenAI API key (for embeddings)
- [ ] ~50GB free disk space
- [ ] 8GB+ RAM available

### Local Infrastructure
```bash
# Install Qdrant (vector database)
docker run -p 6333:6333 qdrant/qdrant

# Install PostgreSQL
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql
# Windows: Download from postgresql.org

# Install Redis (caching)
docker run -p 6379:6379 redis:latest
```

### Project Setup
```bash
# Create project directory
mkdir episodic-memory && cd episodic-memory

# Create Python environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create project structure
mkdir src tests docs data
touch requirements.txt

# Initial dependencies
cat > requirements.txt << EOF
fastapi==0.104.1
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
qdrant-client==2.7.0
openai==1.3.6
redis==5.0.1
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
EOF

pip install -r requirements.txt
```

---

## File Structure (End of Phase 1)

```
episodic-memory/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── memory.py          # Pydantic data models
│   │   ├── importance.py      # Importance scoring
│   │   └── metadata.py        # Metadata structures
│   ├── storage/
│   │   ├── vector_store.py    # Qdrant operations
│   │   ├── database.py        # PostgreSQL operations
│   │   └── cache.py           # Redis caching
│   ├── embedding/
│   │   ├── embedder.py        # OpenAI embeddings
│   │   └── cache.py           # Embedding cache
│   ├── memory_system.py       # Main API
│   └── config.py              # Configuration
├── tests/
│   ├── test_models.py
│   ├── test_storage.py
│   ├── test_embedding.py
│   └── test_integration.py
├── docs/
│   └── api.md
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Core Data Models (Copy This to `src/models/memory.py`)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any

class EpisodicMemory(BaseModel):
    """A single episodic memory (event)."""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime
    event_type: str  # "conversation", "error", "milestone", "interaction"
    compressed_narrative: str  # 100-300 words
    embedding: List[float]  # Vector from OpenAI
    
    # Importance tracking
    importance_score: float = Field(ge=0.0, le=1.0)
    last_accessed: datetime
    access_count: int = 0
    
    # Metadata
    agents_involved: List[str] = []
    domains: List[str] = []
    entities: List[str] = []
    keywords: List[str] = []
    
    # Lifecycle
    created_at: datetime
    consolidated_at: Optional[datetime] = None
    decayed_strength: float = Field(ge=0.0, le=1.0, default=1.0)
    scheduled_deletion: Optional[datetime] = None
    
    # Relationships
    related_memory_ids: List[UUID] = []
    parent_session_id: UUID

class WorkingMemory(BaseModel):
    """Current context window."""
    active_turn: str
    retrieved_memories: List[EpisodicMemory] = []
    task_state: Dict[str, Any] = {}
    agent_state: Dict[str, Any] = {}
    token_count: int = 0
    created_at: datetime
    expires_at: datetime

class ImportanceSignals(BaseModel):
    """Input for importance calculation."""
    novelty: float = Field(ge=0.0, le=1.0)  # How new is this?
    task_success: float = Field(ge=0.0, le=1.0)  # Did it help?
    retrieval_frequency: float = Field(ge=0.0, le=1.0)  # How often accessed?
    user_signal: float = Field(ge=0.0, le=1.0)  # User rating?
    emotional_salience: float = Field(ge=0.0, le=1.0)  # Emotionally salient?
    
    def calculate_importance(self) -> float:
        """Calculate combined importance score."""
        return (
            0.20 * self.novelty +
            0.30 * self.task_success +
            0.25 * self.retrieval_frequency +
            0.15 * self.user_signal +
            0.10 * self.emotional_salience
        )
```

---

## First Code: Basic Memory System (Copy to `src/memory_system.py`)

```python
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from src.models.memory import EpisodicMemory, ImportanceSignals
from src.storage.vector_store import QdrantVectorStore
from src.embedding.embedder import OpenAIEmbedder

class MemorySystem:
    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.vector_store = QdrantVectorStore(qdrant_url)
        self.embedder = OpenAIEmbedder()
    
    async def add_episode(
        self,
        narrative: str,
        event_type: str,
        importance_signals: ImportanceSignals,
        metadata: dict,
        session_id: UUID
    ) -> UUID:
        """Add a new episode to memory."""
        
        # Create embedding
        embedding = await self.embedder.embed(narrative)
        
        # Calculate importance
        importance_score = importance_signals.calculate_importance()
        
        # Create memory object
        memory = EpisodicMemory(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            compressed_narrative=narrative,
            embedding=embedding,
            importance_score=importance_score,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            parent_session_id=session_id,
            **metadata
        )
        
        # Store in vector DB
        memory_id = await self.vector_store.add_memory(memory)
        return memory_id
    
    async def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[EpisodicMemory]:
        """Search for relevant memories."""
        
        # Embed query
        query_embedding = await self.embedder.embed(query)
        
        # Search vector DB
        results = await self.vector_store.search(query_embedding, top_k)
        
        return results
```

---

## First Test (Copy to `tests/test_integration.py`)

```python
import pytest
from uuid import uuid4
from datetime import datetime
from src.memory_system import MemorySystem
from src.models.memory import ImportanceSignals

@pytest.mark.asyncio
async def test_add_and_retrieve_episode():
    """Test basic add and retrieve flow."""
    system = MemorySystem()
    session_id = uuid4()
    
    # Add episode
    memory_id = await system.add_episode(
        narrative="User asked about Python lists. I explained indexing.",
        event_type="conversation",
        importance_signals=ImportanceSignals(
            novelty=0.5,
            task_success=1.0,
            retrieval_frequency=0.0,
            user_signal=0.8,
            emotional_salience=0.2
        ),
        metadata={
            "agents_involved": ["Claude"],
            "domains": ["Python", "Education"],
            "entities": ["User", "Python", "Lists"],
            "keywords": ["indexing", "lists"]
        },
        session_id=session_id
    )
    
    assert memory_id is not None
    
    # Search for it
    results = await system.search("How do Python lists work?", top_k=5)
    
    assert len(results) > 0
    assert results[0].id == memory_id
    assert "Python" in results[0].domains
```

---

## Key APIs to Implement (Priority Order)

**Week 1-2: Critical**
```python
async def add_episode() → UUID  # Store new memory
async def search(query) → List[Memory]  # Find memories
```

**Week 3: Important**
```python
async def search_temporal(date_range) → List[Memory]  # Time-based search
async def update_importance(id, score) → None  # Update score
def calculate_importance(signals) → float  # Score calculation
```

**Week 4: Polish**
```python
async def batch_add_episodes() → List[UUID]  # Bulk operations
async def get_memory(id) → Memory  # Retrieve by ID
def get_stats() → Dict  # System statistics
```

---

## Testing Strategy

```python
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Watch mode (auto-rerun)
pytest-watch tests/
```

**Target:** >80% code coverage by end of Phase 1

---

## Success Metrics for Phase 1

When you can answer YES to all:
- [ ] Can add 100 episodes in <5 seconds?
- [ ] Can search 100 episodes in <100ms?
- [ ] All unit tests passing?
- [ ] Code coverage >80%?
- [ ] API documented?
- [ ] Example usage notebook created?
- [ ] No critical bugs in manual testing?

If yes to all → **Phase 1 Complete!** ✅

---

## Common Pitfalls to Avoid

1. **Embedding every query is slow & expensive**
   - Solution: Cache embeddings aggressively

2. **Vector DB gets slow with 100K+ memories**
   - Solution: Use proper indexing (HNSW), batch operations

3. **Importance scoring feels arbitrary**
   - Solution: Test each signal independently, document choices

4. **Consolidation takes too long**
   - Solution: Run async, batch process, optimize compression

5. **Retrieve too many irrelevant memories**
   - Solution: Filter by importance first, then search

---

## Getting Help

**When stuck:**
1. Check the technical design doc (01_EPISODIC_MEMORY_TECHNICAL_DESIGN.md)
2. Look at the project plan (02_PROJECT_PLAN.md)
3. Search existing issues/solutions
4. Write a minimal reproducible example
5. Reach out to team

---

## Estimated Time Investment

- **Reading this guide:** 10 minutes
- **Setting up environment:** 30 minutes
- **Week 1 implementation:** 20-30 hours
- **Total Phase 1:** 80-100 hours

Adjust based on your experience level.

---

**Ready to start?** Begin with the setup checklist above, then refer to the Technical Design doc for details.

**Questions?** Check 01_EPISODIC_MEMORY_TECHNICAL_DESIGN.md sections 3-4 for architecture details.

Good luck! 🚀
