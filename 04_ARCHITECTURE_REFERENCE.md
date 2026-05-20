# Episodic AI Memory System - Architecture Reference

**Quick lookup for system design, data flows, and component interactions.**

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT / USER                              │
└────────────────────┬────────────────────────────────────────────┘
                     │ New Event (narrative, metadata)
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MEMORY SYSTEM API                             │
│  • add_episode(narrative, event_type, metadata)                 │
│  • retrieve(query, filters)                                      │
│  • update_importance(id, signals)                               │
│  • consolidate()                                                │
└────────┬────────────────────────────────────────────────────────┘
         │
    ┌────┴────────────────────────────────────────────────┐
    ↓                                                      ↓
┌─────────────────────┐                    ┌──────────────────────┐
│  EMBEDDING PIPELINE  │                    │  IMPORTANCE SCORING  │
│                      │                    │                      │
│ 1. Text input        │                    │ 1. Calculate signals │
│ 2. OpenAI API call   │                    │ 2. Combine weights   │
│ 3. Cache result      │                    │ 3. Score 0.0-1.0    │
│ 4. Return vector     │                    │                      │
└──────────┬───────────┘                    └──────────┬───────────┘
           │                                           │
           └───────────────┬──────────────────────────┘
                           ↓
                ┌──────────────────────┐
                │  WORKING MEMORY      │
                │  (Session Context)   │
                │                      │
                │ • Current query      │
                │ • Retrieved memories │
                │ • Task state         │
                │ • Agent state        │
                │                      │
                │ Max: 128K tokens     │
                │ TTL: Session         │
                └──────────┬───────────┘
                           │
            ┌──────────────┼──────────────┐
            ↓              ↓              ↓
    ┌──────────────┐ ┌───────────────┐ ┌────────────────┐
    │ EPISODIC     │ │   SEMANTIC    │ │    CACHE       │
    │ MEMORY       │ │   MEMORY      │ │   (Redis)      │
    │              │ │               │ │                │
    │ • Vector DB  │ │ • Facts       │ │ • Embeddings   │
    │   (Qdrant)   │ │ • Patterns    │ │ • Hot memories │
    │ • Compress   │ │ • Preferences │ │ • Scores       │
    │   narrative  │ │               │ │                │
    │ • Embedding  │ │ • Neo4j or    │ │                │
    │ • Decay (TTL)│ │   PostgreSQL  │ │                │
    │              │ │               │ │                │
    │ Lifespan:    │ │ Lifespan:     │ │ Lifespan:      │
    │ Days-Months  │ │ Permanent     │ │ Hours-Days     │
    └──────────┬───┘ └───────┬───────┘ └────────────────┘
               │             │
               └─────┬───────┘
                     ↓
    ┌────────────────────────────────┐
    │    CONSOLIDATION PIPELINE      │
    │    (Async Background Job)      │
    │                                │
    │ 1. Collect recent episodic     │
    │ 2. Group by similarity         │
    │ 3. Compress narratives         │
    │ 4. Extract facts & patterns    │
    │ 5. Update semantic memory      │
    │ 6. Apply forgetting curve      │
    │ 7. Delete expired memories     │
    │                                │
    │ Frequency: Hourly/Daily        │
    └────────────────────────────────┘
```

---

## Data Flow: Adding a New Episode

```
User/Agent Action
    │
    ├─ Narrative: "User fixed Python IndexError using slicing"
    ├─ Event Type: "conversation"
    ├─ Metadata: {domains: ["Python"], entities: ["IndexError"]}
    │
    ↓
Step 1: Calculate Importance Scores
    │
    ├─ Novelty: Compare embedding to existing memories
    │   └─ Result: 0.7 (somewhat novel)
    │
    ├─ Task Success: Did user confirm it worked?
    │   └─ Result: 1.0 (yes, confirmed)
    │
    ├─ Retrieval Frequency: How often accessed? (first time)
    │   └─ Result: 0.0 (new)
    │
    ├─ User Signal: Did user rate it?
    │   └─ Result: 0.9 (user said "very helpful")
    │
    └─ Emotional Salience: Sentiment analysis
        └─ Result: 0.4 (neutral tone)
    
    ↓
    Final Importance = 0.20*0.7 + 0.30*1.0 + 0.25*0.0 + 0.15*0.9 + 0.10*0.4
                     = 0.14 + 0.30 + 0.0 + 0.135 + 0.04
                     = 0.615 (MEDIUM-HIGH)
    
Step 2: Create Embedding
    │
    └─ Call OpenAI API with narrative
       └─ Get 1536-dim vector
       └─ Cache in Redis
    
Step 3: Store in Episodic Memory
    │
    ├─ Save to Qdrant:
    │   ├─ embedding vector
    │   ├─ compressed_narrative
    │   ├─ importance_score: 0.615
    │   ├─ timestamp: now
    │   ├─ metadata (domains, entities, etc.)
    │   └─ other fields
    │
    └─ Store metadata in PostgreSQL
        ├─ ID, timestamp, importance
        ├─ Access history
        └─ TTL calculation
    
Step 4: Add to Working Memory
    │
    └─ Include in current context for agent
        (if importance > 0.7, stays in active memory)
    
Step 5: Schedule for Later Consolidation
    │
    └─ Mark for processing in next consolidation cycle
        ├─ Extract patterns
        ├─ Update preferences
        └─ Create semantic facts
```

---

## Data Flow: Retrieving Memories

```
User/Agent Query: "How do I handle Python index errors?"
    │
    ↓
Step 1: Embed Query
    └─ OpenAI API → 1536-dim vector
    └─ Cache result
    
Step 2: Search Episodic Memory (Similarity)
    │
    ├─ Qdrant vector similarity search
    │   └─ Find top 10 most similar
    │
    ├─ Score each by relevance + recency
    │   └─ score = similarity * recency_weight
    │
    └─ Filter by importance threshold
        └─ Keep only score > 0.4
    
Step 3: Search Semantic Memory (Patterns)
    │
    ├─ Query fact store (Neo4j/PostgreSQL)
    │   └─ Find patterns about "IndexError"
    │
    ├─ Find learned patterns
    │   ├─ Condition: "User encounters IndexError"
    │   ├─ Outcome: "Slicing or enumerate() works"
    │   └─ Success rate: 90%
    │
    └─ Extract user preferences
        └─ "User prefers concise explanations"
    
Step 4: Query Working Memory
    │
    ├─ Search current context
    │   └─ Any recent discussions about this?
    │
    └─ Return highly relevant current items
    
Step 5: Merge & Rank Results
    │
    ├─ Combine from all three layers
    │
    ├─ Calculate final score for each
    │   └─ Semantic_Relevance (0.35) +
    │      Importance_Score (0.25) +
    │      Recency_Weight (0.20) +
    │      Access_Frequency (0.15) +
    │      Emotional_Resonance (0.05)
    │
    ├─ Deduplicate (remove near-duplicates)
    │
    └─ Return top 5 ranked results
    
Step 6: Update Access Tracking
    │
    ├─ Increment access_count
    ├─ Update last_accessed timestamp
    └─ Optionally boost importance slightly
        (frequently accessed memories are important)
```

---

## Data Structure Details

### EpisodicMemory Entry

```python
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    
    # Core content
    "timestamp": "2026-05-20T14:30:00Z",
    "event_type": "conversation",
    "compressed_narrative": "User asked about handling Python IndexError. 
                             Explained slicing and enumerate() approaches. 
                             User confirmed solution worked.",
    "embedding": [0.123, -0.456, 0.789, ...],  # 1536 dimensions
    
    # Importance tracking
    "importance_score": 0.615,
    "last_accessed": "2026-05-20T14:30:00Z",
    "access_count": 1,
    "retrieval_frequency": 0.2,  # (1 / estimated_future_accesses)
    
    # Metadata for filtering
    "agents_involved": ["Claude", "User"],
    "domains": ["Python", "Error Handling"],
    "entities": ["IndexError", "slicing", "enumerate"],
    "keywords": ["index", "bounds", "array", "fix"],
    
    # Lifecycle
    "created_at": "2026-05-20T14:30:00Z",
    "consolidated_at": null,  # Not yet compressed
    "decayed_strength": 1.0,  # Memory strength (0-1)
    "scheduled_deletion": "2026-06-03T14:30:00Z",
        # Will delete on this date if not accessed
    
    # Relationships
    "related_memory_ids": [
        "550e8400-e29b-41d4-a716-446655440001",  # Similar memories
        "550e8400-e29b-41d4-a716-446655440002"
    ],
    "parent_session_id": "session-2026-05-20-morning"
}
```

### SemanticFact Entry

```python
{
    "id": "fact-001",
    "subject": "Python",
    "predicate": "causes_error",
    "object": "IndexError",
    "confidence": 0.95,
    
    "source_memories": [
        "550e8400-e29b-41d4-a716-446655440000",
        "550e8400-e29b-41d4-a716-446655440001"
    ],
    
    "first_observed": "2026-05-15T10:00:00Z",
    "last_confirmed": "2026-05-20T14:30:00Z",
    "observation_count": 5,
    
    "examples": [
        "list[10] when list has 5 items",
        "accessing dict key that doesn't exist",
        "nested list indexing errors"
    ]
}
```

### LearnedPattern Entry

```python
{
    "pattern_id": "pattern-001",
    
    "condition": "User encounters Python IndexError",
    "outcome": "Suggest slicing or enumerate()",
    "action": "Explain bounds checking + provide code example",
    
    "success_rate": 0.92,  # 92% of times this pattern helped
    "observed_count": 13,  # Seen 13 times
    
    "contexts": ["Python", "Array/List Access", "Error Handling"],
    "difficulty_level": "Beginner",
    
    "related_patterns": [
        "pattern-002",  # Off-by-one errors
        "pattern-003"   # Loop bounds
    ],
    
    "created_from_memories": [
        "550e8400-e29b-41d4-a716-446655440000",
        "550e8400-e29b-41d4-a716-446655440001",
        ...
    ]
}
```

---

## Importance Score Formula Breakdown

```
Importance = (0.20 × Novelty) + (0.30 × Task_Success) + (0.25 × Retrieval_Frequency) 
           + (0.15 × User_Signal) + (0.10 × Emotional_Salience)

Range: 0.0 to 1.0

Decision Thresholds:
  ≥ 0.7 = HIGH     → Keep indefinitely, high priority retrieval
  0.4-0.7 = MEDIUM → Store compressed, medium priority
  < 0.4 = LOW      → Extract patterns only, low retrieval priority
```

### Signal Definitions

| Signal | Calculation | Example |
|--------|-------------|---------|
| **Novelty** | Embedding distance from nearest similar memory / max_distance | 0.8 = Pretty different from what we've seen |
| **Task_Success** | Did task complete? Explicit user feedback? | 1.0 = Yes, confirmed worked; 0.0 = Failed |
| **Retrieval_Frequency** | access_count / (total_access_count_all_memories + 1) | 0.3 = Retrieved 30% as much as average |
| **User_Signal** | Explicit rating or importance marker | 0.9 = User marked "very helpful" |
| **Emotional_Salience** | Sentiment analysis polarity | 0.4 = Neutral; 0.8 = Very positive; 0.1 = Negative |

---

## Forgetting Curve Formula

```
Memory_Strength(t) = e^(-λt / Stability)

Where:
  t = days elapsed since last access
  λ = decay constant (higher = faster forgetting)
  Stability = importance_score (higher importance = slower decay)

Decay Constants by Importance Tier:
  High (> 0.7):    λ = 0.1   → Slow decay, keeps for months
  Medium (0.4-0.7): λ = 0.5   → Medium decay, keeps for weeks
  Low (< 0.4):      λ = 1.5   → Fast decay, gone in days

Deletion Threshold: Memory_Strength < 0.05

Example:
  Importance = 0.75
  Stability = 0.75
  λ = 0.1
  
  Day 1:  S = e^(-0.1*1/0.75) = 0.87 (Still strong)
  Day 10: S = e^(-0.1*10/0.75) = 0.26 (Weakening)
  Day 21: S = e^(-0.1*21/0.75) = 0.06 (Approach deletion threshold)
  Day 22: S = e^(-0.1*22/0.75) = 0.05 (DELETE)
```

---

## Consolidation Process Timeline

```
Daily Consolidation (1 AM):

01:00:00 START
├─ Batch Collection
│  ├─ Gather episodic memories from past 24h
│  ├─ Filter importance > 0.3
│  └─ Group 50-100 memories per batch
│
├─ Compression (2-5 min)
│  ├─ Summarize each narrative
│  ├─ Preserve key entities
│  └─ Update compressed_narrative field
│
├─ Pattern Extraction (3-8 min)
│  ├─ Identify recurring conditions
│  ├─ Extract outcomes and actions
│  └─ Create LearnedPattern entries
│
├─ Preference Mining (2-4 min)
│  ├─ Look for user preference signals
│  ├─ Update confidence scores
│  └─ Merge conflicting preferences
│
├─ Decay Application (1-2 min)
│  ├─ Apply forgetting curve to all episodic
│  ├─ Mark below-threshold for deletion
│  └─ Recalculate TTLs
│
├─ Cleanup (1-3 min)
│  ├─ Delete expired memories
│  ├─ Vacuum indices
│  └─ Optimize database
│
└─ 01:15:00 COMPLETE
   └─ Log: "Consolidated 2000 memories, extracted 50 patterns"
```

---

## Query Performance: Expected Latencies

| Operation | Database | Latency | Notes |
|-----------|----------|---------|-------|
| Add episode | All | <500ms | Embedding call is slowest (~250ms) |
| Search similarity | Qdrant | <50ms | 100K memories, HNSW index |
| Search temporal | PostgreSQL | <30ms | Date range query |
| Query facts | Neo4j/PostgreSQL | <20ms | Simple pattern matching |
| Retrieve top-5 | Combined | <100ms | All layers searched in parallel |
| Consolidation | All | <15min | Full pipeline on 100K memories |

---

## Scalability Considerations

### Memory Capacity

```
Assumption: Average memory 300 tokens

Monthly growth: ~1000 new memories
Yearly: ~12,000 new memories

Year 1: 12,000 memories (active)
Year 2: ~8,000 active (4,000 deleted by decay)
Year 3: ~8,000 active (stable state)
Year N: ~8,000 active (older ones forgotten)

Storage per memory: ~10 KB (narrative + metadata + embedding)
Total storage: 8,000 × 10 KB = 80 MB (reasonable for VM)
```

### Performance Scaling

```
Vector DB (Qdrant) Performance:
- 1K memories: <10ms search (trivial)
- 10K memories: <20ms search (cached)
- 100K memories: <50ms search (HNSW index required)
- 1M memories: <100ms search (partitioned indices)

If you exceed 1M memories:
  - Partition by time (old memories in archive)
  - Partition by domain (separate indices per topic)
  - Use hierarchical clustering
```

---

## Common Operations Reference

### Add Episode
```python
importance = calculate_importance(
    novelty=0.6,
    task_success=1.0,
    retrieval_frequency=0.0,
    user_signal=0.9,
    emotional_salience=0.3
)  # Result: 0.61

memory_id = await system.add_episode(
    narrative="Fixed off-by-one error using range()",
    event_type="conversation",
    importance=importance,
    metadata={
        "agents": ["Claude"],
        "domains": ["Python"],
        "entities": ["off-by-one", "range()"],
        "keywords": ["loop", "bounds"]
    }
)
```

### Retrieve Memories
```python
results = await system.retrieve(
    query="How do I fix Python loop errors?",
    top_k=5,
    retrieval_modes=["similarity", "recency"],
    filters={
        "min_importance": 0.4,
        "domains": ["Python"],
        "days_back": 30  # Last 30 days
    }
)

for memory in results:
    print(f"{memory.compressed_narrative}")
    print(f"  Importance: {memory.importance_score}")
    print(f"  Accessed {memory.access_count} times")
```

### Update Importance
```python
# After agent learns that a memory was helpful
await system.update_importance(
    memory_id=uuid,
    new_signals={
        "task_success": 1.0,  # User confirmed it worked
        "user_signal": 0.95,   # User rated it
    }
)
```

---

## Decision Tree: Where Should Data Go?

```
New Information Arrives
    │
    ├─ Calculate Importance
    │
    ├─ Importance Score?
    │
    ├─ > 0.7 (HIGH)
    │  └─ → Working Memory + Episodic (full detail)
    │     └─ Retrieve frequently, keep long
    │
    ├─ 0.4-0.7 (MEDIUM)
    │  └─ → Episodic Memory (compressed)
    │     └─ Keep as narrative, decay slowly
    │
    └─ < 0.4 (LOW)
       └─ → Extract patterns only → Semantic Memory
          └─ Don't store narrative, store only abstraction
```

---

## Technology Stack Reference

```
Vector DB:       Qdrant (cosine similarity, metadata filtering)
Graph DB:        Neo4j or PostgreSQL JSON (facts, patterns)
Cache:           Redis (embeddings, hot memories)
Embeddings:      OpenAI API (text-embedding-3-large, 3072 dims)
LLM:             Claude or GPT-4 (pattern extraction, compression)
Database:        PostgreSQL (metadata, timestamps, access logs)
Language:        Python 3.11+
Framework:       FastAPI (API layer)
Jobs:            Celery + Redis (async consolidation)
```

---

**Print this page for quick reference during implementation!**
