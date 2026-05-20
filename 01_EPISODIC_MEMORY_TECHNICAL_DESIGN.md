# Episodic AI Memory System: Technical Design

**Project Status:** Design Phase  
**Last Updated:** May 20, 2026  
**Author:** Master (parth.garggkota@gmail.com)

---

## 1. EXECUTIVE SUMMARY

This document outlines the complete technical architecture for an episodic AI memory system that improves upon traditional RAG (Retrieval Augmented Generation) approaches. The system implements a three-tier memory hierarchy with importance-weighted consolidation, temporal decay, and associative retrieval mechanisms.

**Key Innovation:** Rather than storing all information equally, the system uses an importance score to determine what gets remembered verbatim, what gets compressed into narrative summaries, and what gets consolidated into semantic patterns.

---

## 2. PROBLEM STATEMENT

### Current RAG Limitations
- **No forgetting:** Every retrieved chunk is treated equally, causing noise
- **No learning:** No consolidation of knowledge across conversations
- **No association:** Memories aren't linked by meaning or temporal proximity
- **No reconstruction:** Can't rebuild coherent narratives from fragments
- **Scale issues:** Context window fills with irrelevant historical data

### Our Solution
A hierarchical memory system that:
1. Preserves important episodic details in working memory
2. Compresses less critical events into semantic summaries
3. Extracts timeless facts and patterns into semantic memory
4. Implements forgetting curves so unimportant data naturally decays
5. Uses multi-modal retrieval (similarity, temporal, associative)

---

## 3. ARCHITECTURE OVERVIEW

### 3.1 Three-Layer Memory Model

```
┌─────────────────────────────────────────────────────────┐
│              WORKING MEMORY (Current)                    │
│  • Active conversation context                           │
│  • Retrieved memories + task state                       │
│  • Max tokens: 128K (context window limit)               │
│  • Persistence: Session only                             │
└─────────────────────────────────────────────────────────┘
                           ↓ Consolidation
┌─────────────────────────────────────────────────────────┐
│          EPISODIC MEMORY (Specific Events)               │
│  • Event: Vector DB (Qdrant/Weaviate)                   │
│  • Each entry: {                                         │
│      timestamp, compressed_narrative,                    │
│      embedding, importance_score,                        │
│      metadata (agents, domains, entities)                │
│    }                                                      │
│  • TTL-based decay: importance determines lifespan      │
│  • Retrieval: Semantic + temporal similarity             │
└─────────────────────────────────────────────────────────┘
                           ↓ Abstraction
┌─────────────────────────────────────────────────────────┐
│         SEMANTIC MEMORY (Timeless Patterns)              │
│  • Facts: Knowledge graph or triple store                │
│  • Patterns: Extracted rules and heuristics              │
│  • Preferences: User/task patterns                       │
│  • Storage: Graph DB (Neo4j) or PostgreSQL JSON          │
│  • Persistence: Permanent (until explicitly removed)     │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

```
1. INPUT: New event/conversation turn
   ↓
2. SCORING: Calculate importance score for new information
   ↓
3. STORAGE: Place in appropriate layer(s)
   ├─ High importance (>0.7) → Working + Episodic
   ├─ Medium (0.4-0.7) → Episodic only (compressed)
   └─ Low (<0.4) → Semantic patterns only
   ↓
4. CONSOLIDATION: Async background process
   ├─ Merge similar episodic memories
   ├─ Extract semantic patterns
   └─ Apply forgetting curve decay
   ↓
5. RETRIEVAL: Query-time aggregation
   ├─ Fetch from working memory
   ├─ Search episodic by similarity + recency
   ├─ Query semantic for general knowledge
   └─ Return ranked, deduplicated results
```

---

## 4. DETAILED COMPONENT DESIGN

### 4.1 Working Memory Layer

**Purpose:** Current context window for active reasoning

**Data Structure:**
```python
WorkingMemory:
  - active_turn: str  # Current user query
  - retrieved_memories: List[Memory]  # Top-K from episodic/semantic
  - task_state: Dict[str, Any]  # Task-specific context
  - agent_state: Dict[str, Any]  # Agent goals, plans
  - token_count: int  # Current usage
  - created_at: datetime
  - expires_at: datetime  # Auto-clear after session
```

**Characteristics:**
- Max capacity: 128K tokens (tunable, depends on model context window)
- Access pattern: Direct, no latency
- Retrieval mechanism: In-memory search + filtering
- Lifetime: Single session (ephemeral)

**Operations:**
1. `add_context(memory, priority)` - Add retrieved memory
2. `get_available_tokens()` - Check remaining capacity
3. `search_local(query, top_k)` - Fast in-memory search
4. `clear()` - Session cleanup

---

### 4.2 Episodic Memory Layer

**Purpose:** Store specific events as compressed narratives with embeddings

**Vector DB Choice Rationale:**
- Qdrant: Fast, good for embeddings + metadata filtering
- Weaviate: Better semantic search, built-in vectorization
- **Recommendation:** Qdrant for initial implementation

**Data Structure:**
```python
EpisodicMemory:
  id: UUID
  timestamp: datetime  # When did this happen
  event_type: str  # "conversation", "error", "milestone", "interaction"
  compressed_narrative: str  # 100-300 word summary
  embedding: Vector[1536]  # Text embedding (e.g., OpenAI)
  
  # Importance tracking
  importance_score: float  # 0.0 to 1.0 (calculated)
  last_accessed: datetime
  access_count: int  # How many times retrieved
  retrieval_recency: datetime  # Last successful retrieval
  
  # Metadata for filtering
  agents_involved: List[str]
  domains: List[str]  # Knowledge domains
  entities: List[str]  # Named entities
  keywords: List[str]  # Extracted key concepts
  
  # Temporal tracking
  created_at: datetime
  consolidated_at: Optional[datetime]  # When it was created/compressed
  decayed_strength: float  # Current memory strength (0-1)
  scheduled_deletion: Optional[datetime]  # When it will be deleted
  
  # Relationships
  related_memory_ids: List[UUID]  # Similar memories
  parent_session_id: UUID  # What conversation generated this
```

**Importance Score Formula:**
```
Importance = 0.20 * Novelty 
           + 0.30 * Task_Success 
           + 0.25 * Retrieval_Frequency 
           + 0.15 * User_Signal 
           + 0.10 * Emotional_Salience
```

Where:
- **Novelty (0-1):** How different from existing memories (via embedding distance)
- **Task_Success (0-1):** Did this memory help complete a task? (binary/weighted)
- **Retrieval_Frequency (0-1):** How often has it been accessed? (normalized)
- **User_Signal (0-1):** Explicit user rating or importance marker
- **Emotional_Salience (0-1):** Does it contain high-emotion language? (sentiment)

**Operations:**
```python
# Writing
add_episode(narrative: str, event_type: str, metadata: Dict) → UUID
batch_add_episodes(episodes: List[Episode]) → List[UUID]
update_importance(id: UUID, new_score: float)
consolidate_similar(threshold: float = 0.85)  # Merge very similar memories

# Reading
search_by_similarity(query: str, top_k: int = 5) → List[EpisodicMemory]
search_temporal(start_date: datetime, end_date: datetime) → List[EpisodicMemory]
search_by_entity(entity: str) → List[EpisodicMemory]
search_by_domain(domain: str) → List[EpisodicMemory]
get_memory(id: UUID) → EpisodicMemory

# Decay
apply_forgetting_curve(memory: EpisodicMemory) → float  # Returns new strength
delete_expired_memories()  # Cleanup old, low-importance entries
```

**Forgetting Curve Implementation:**

```
Memory Strength S(t) = e^(-λt / Stability)

Where:
  t = time elapsed since last access
  λ = decay constant (higher = faster forgetting)
  Stability = importance_score (higher stability = slower decay)

Retrieval Threshold = 0.05 (memories below this are candidates for deletion)
```

Specific decay rates by importance:
- High importance (>0.7): λ = 0.1 (decays slowly)
- Medium (0.4-0.7): λ = 0.5 (moderate decay)
- Low (<0.4): λ = 1.5 (rapid decay, quickly deleted)

---

### 4.3 Semantic Memory Layer

**Purpose:** Store timeless facts, patterns, and preferences

**Components:**

#### 4.3.1 Fact Store
```python
SemanticFact:
  id: UUID
  subject: str  # Entity or concept
  predicate: str  # Relationship type
  object: str  # Target entity or value
  confidence: float  # 0.0 to 1.0
  source: str  # Which episodic memory generated this
  first_observed: datetime
  last_confirmed: datetime
  examples: List[str]  # Concrete examples supporting this fact
```

Storage: Neo4j property graph or PostgreSQL JSON

Example facts:
- `User { prefers_communication: "concise" }`
- `Task { required_research: "Google Docs API" }`
- `Pattern { user_error: "forgets file paths" → solution: "use_absolute_paths" }`

#### 4.3.2 User Preferences
```python
UserPreference:
  domain: str  # Communication style, work preferences
  preference_key: str
  preference_value: Any
  confidence: float
  extracted_from: List[UUID]  # Which episodic memories
```

Examples:
- `communication_style: "concise"` (confidence: 0.9)
- `prefers_code_format: "minimal_comments"` (confidence: 0.7)
- `error_sensitivity: "high"` (confidence: 0.85)

#### 4.3.3 Pattern Library
```python
LearnedPattern:
  pattern_id: UUID
  condition: str  # "When X happens"
  outcome: str  # "Then Y results"
  action: str  # "Recommended response"
  success_rate: float  # % of times this worked
  observed_count: int  # How many times seen
  contexts: List[str]  # Domains where it applies
```

Examples:
- Condition: "User asks about undefined variable"
  Outcome: "Stack trace shown"
  Action: "Provide variable definition or import statement"
  Success rate: 95%

**Operations:**
```python
# Facts
add_fact(subject: str, predicate: str, obj: str, confidence: float)
query_fact(subject: str, predicate: str) → List[SemanticFact]
update_fact_confidence(fact_id: UUID, new_confidence: float)
consolidate_facts(facts: List[SemanticFact]) → SemanticFact  # Merge similar

# Preferences
extract_preferences(episode: EpisodicMemory) → List[UserPreference]
get_user_preferences(domain: str) → List[UserPreference]
update_preference_confidence(preference_id: UUID, new_confidence: float)

# Patterns
extract_patterns(episodes: List[EpisodicMemory]) → List[LearnedPattern]
query_patterns(condition: str) → List[LearnedPattern]
update_pattern_success_rate(pattern_id: UUID, success: bool)
```

---

## 5. CONSOLIDATION PROCESS

**Purpose:** Move information between layers, compress narratives, extract patterns

**Trigger:** Asynchronous background job (hourly or after N new memories)

### 5.1 Compression Algorithm

**Input:** Raw episode (original full text)  
**Output:** Compressed narrative (100-300 words) + key entities/concepts

```python
def compress_episode(episode_text: str, importance: float) -> str:
    """
    Compress episode using importance-weighted summarization.
    
    High importance (>0.7):
      - Keep 80% of details
      - 250-300 word summary
      - Full entity preservation
    
    Medium (0.4-0.7):
      - Keep 50% of details
      - 150-200 word summary
      - Key entities only
    
    Low (<0.4):
      - Extract only patterns
      - Don't store narrative
      - Only semantic abstraction
    """
```

### 5.2 Pattern Extraction

**From:** Groups of similar episodic memories  
**To:** Semantic memory patterns, user preferences

```python
def extract_patterns(similar_episodes: List[EpisodicMemory]):
    """
    Look for repeated patterns across similar memories:
    
    1. Condition extraction
       - What triggered this outcome?
       - Extract common preconditions
    
    2. Outcome identification
       - What consistently happened?
       - Extract common results
    
    3. Solution patterns
       - What actions helped?
       - Extract effective strategies
    
    4. Preference mining
       - What user preferences appear?
       - Extract and consolidate
    """
```

### 5.3 Consolidation Workflow

```
1. BATCH COLLECTION
   - Gather episodic memories from last 24 hours
   - Filter by importance > 0.3
   - Group by similarity (embedding distance > 0.85)

2. COMPRESSION
   - For each group, summarize narrative
   - Preserve key entities and concepts
   - Update `compressed_narrative` field

3. PATTERN EXTRACTION
   - Identify recurring themes
   - Extract conditions → outcomes → actions
   - Create LearnedPattern entries in semantic memory

4. PREFERENCE CONSOLIDATION
   - Look for user preference signals
   - Update confidence scores
   - Merge conflicting preferences (keep higher confidence)

5. DECAY APPLICATION
   - Apply forgetting curve to all episodic memories
   - Mark memories below threshold for deletion
   - Schedule cleanup for next batch

6. CLEANUP
   - Delete expired episodic memories
   - Vacuum vector DB indices
   - Optimize semantic memory indices
```

---

## 6. RETRIEVAL SYSTEM

**Purpose:** Given a query, return most relevant memories from all three layers

### 6.1 Multi-Modal Retrieval

**Four retrieval strategies:**

#### 6.1.1 Semantic Similarity
```python
def retrieve_by_similarity(query: str, top_k: int = 5) -> List[Memory]:
    """
    Embedding-based semantic search.
    
    1. Embed query
    2. Search episodic vector DB (cosine similarity)
    3. Filter by recency weight (recent = higher score)
    4. Return top_k by combined score
    """
    
    score = similarity_score * recency_weight
    # recent_decay = e^(-days_ago / 30)
```

#### 6.1.2 Temporal Retrieval
```python
def retrieve_by_temporal_proximity(
    query: str, 
    time_window_days: int = 7
) -> List[Memory]:
    """
    Find memories near the current time.
    
    Useful for: "What happened last Tuesday?"
    - Search episodic within time window
    - Order by recency
    - Weight by relevance score
    """
```

#### 6.1.3 Associative Retrieval
```python
def retrieve_by_association(
    query: str,
    depth: int = 2
) -> List[Memory]:
    """
    Follow memory relationship chains.
    
    1. Find initial matching memories
    2. Follow related_memory_ids up to depth
    3. Return network of connected memories
    
    Useful for: Understanding broader context
    """
```

#### 6.1.4 Semantic Knowledge Queries
```python
def retrieve_semantic_knowledge(
    query: str,
    fact_type: str = "facts"  # facts | preferences | patterns
) -> List[SemanticMemory]:
    """
    Query structured semantic memory.
    
    - For facts: Graph pattern matching
    - For preferences: Confidence-weighted filtering
    - For patterns: Condition matching + ranking by success rate
    """
```

### 6.2 Retrieval Ranking Algorithm

**Score calculation per retrieved memory:**

```
Final_Rank = 0.35 * Semantic_Relevance
           + 0.25 * Importance_Score
           + 0.20 * Recency_Weight
           + 0.15 * Access_Frequency
           + 0.05 * Emotional_Resonance

Where:
  Semantic_Relevance = cosine_similarity(query_embedding, memory_embedding)
  Importance_Score = stored importance value
  Recency_Weight = e^(-days_ago / decay_constant)
  Access_Frequency = normalized access_count
  Emotional_Resonance = sentiment_polarity if applicable
```

### 6.3 Deduplication & Merging

**When multiple layers return overlapping info:**

```python
def merge_retrieved_memories(results: List[Memory]) -> List[Memory]:
    """
    Deduplicate and merge results from different layers.
    
    1. Group by semantic similarity (embed all, cluster)
    2. For each group:
       - Keep highest-ranked result
       - Note alternative perspectives in metadata
       - Preserve source layer info
    
    3. Return merged list, ranked by final score
    """
```

---

## 7. IMPLEMENTATION PHASES

### Phase 1: Core Infrastructure (Weeks 1-4)
**Goal:** Build basic working and episodic memory

- [ ] Set up vector DB (Qdrant)
- [ ] Implement basic data structures
- [ ] Create embedding pipeline (OpenAI API)
- [ ] Build simple add/search operations
- [ ] Write unit tests
- **Deliverable:** Working memory system that stores/retrieves episodes

### Phase 2: Importance Scoring (Weeks 5-8)
**Goal:** Implement sophisticated importance calculation

- [ ] Define and test each signal (novelty, task success, etc.)
- [ ] Calibrate scoring formula weights
- [ ] Build importance update mechanisms
- [ ] Create evaluation benchmarks
- **Deliverable:** System that can rank memories by importance

### Phase 3: Semantic Memory & Consolidation (Weeks 9-12)
**Goal:** Extract and store semantic patterns

- [ ] Implement fact extraction from episodes
- [ ] Build pattern recognition engine
- [ ] Create semantic memory storage (Neo4j or PostgreSQL)
- [ ] Implement consolidation pipeline
- [ ] Build preference extraction
- **Deliverable:** System that learns and abstracts patterns

### Phase 4: Forgetting & Decay (Weeks 13-16)
**Goal:** Implement temporal decay and cleanup

- [ ] Implement forgetting curve algorithm
- [ ] Build TTL management system
- [ ] Create prioritized deletion strategy
- [ ] Build cleanup scheduler
- **Deliverable:** Memory naturally forgets unimportant info

### Phase 5: Advanced Retrieval (Weeks 17-20)
**Goal:** Multi-modal retrieval with ranking

- [ ] Implement all 4 retrieval strategies
- [ ] Build ranking algorithm
- [ ] Create deduplication engine
- [ ] Optimize query performance
- **Deliverable:** System that finds most relevant memories efficiently

### Phase 6: Integration & Testing (Weeks 21-24)
**Goal:** Full system integration and evaluation

- [ ] Build agent integration layer
- [ ] Run end-to-end tests
- [ ] Benchmark performance (latency, accuracy)
- [ ] Document API
- [ ] Create example use cases
- **Deliverable:** Production-ready memory system

---

## 8. TECHNOLOGY STACK

### Storage
- **Vector DB:** Qdrant (episodic embeddings)
- **Graph DB:** Neo4j or PostgreSQL JSON (semantic facts)
- **Cache:** Redis (working memory, hot facts)

### Processing
- **Embeddings:** OpenAI API (text-embedding-3-large, 3072 dims)
- **LLM:** Claude API (text generation, pattern extraction)
- **Async Jobs:** Celery + Redis (consolidation, decay)

### Development
- **Language:** Python 3.11+
- **Framework:** FastAPI (API layer)
- **Database ORM:** SQLAlchemy + Alembic
- **Testing:** pytest, pytest-asyncio
- **Monitoring:** Prometheus + Grafana

### Infrastructure
- **Deployment:** Docker + Kubernetes (optional)
- **Logging:** ELK stack or CloudWatch
- **CI/CD:** GitHub Actions

---

## 9. API DESIGN

### 9.1 Core Interface

```python
class EpisodicMemorySystem:
    
    # Storage
    def add_episode(
        self,
        narrative: str,
        event_type: str,
        metadata: Dict[str, Any],
        agent_id: str,
        session_id: str
    ) -> UUID:
        """Add a new episode to memory."""
    
    # Retrieval
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        retrieval_modes: List[str] = ["similarity", "recency"],
        filters: Optional[Dict] = None
    ) -> List[Memory]:
        """Retrieve relevant memories."""
    
    def retrieve_working(self, top_k: int = 5) -> List[Memory]:
        """Get current working memory context."""
    
    # Importance
    def calculate_importance(
        self,
        episode_id: UUID,
        **signals: Dict[str, float]
    ) -> float:
        """Calculate importance score."""
    
    def update_importance(
        self,
        episode_id: UUID,
        new_score: float,
        signal_updates: Optional[Dict] = None
    ) -> None:
        """Update importance after learning."""
    
    # Consolidation
    def consolidate(self, hours: int = 24) -> Dict[str, int]:
        """Run consolidation pipeline."""
    
    # Admin
    def get_stats(self) -> Dict[str, Any]:
        """Memory system statistics."""
    
    def export(self, format: str = "json") -> str:
        """Export all memories."""
    
    def clear(self, older_than: Optional[datetime] = None) -> int:
        """Delete memories (with safeguards)."""
```

---

## 10. EVALUATION METRICS

**How we'll measure success:**

### 10.1 Quality Metrics
- **Relevance:** Are retrieved memories actually relevant? (manual evaluation)
- **Completeness:** Can we reconstruct past conversations from memories?
- **Redundancy:** How much duplicate information are we storing?

### 10.2 Performance Metrics
- **Retrieval latency:** <100ms for top-k queries
- **Storage efficiency:** Compression ratio (raw text → stored)
- **Memory retention:** % of important memories retained over time

### 10.3 Learning Metrics
- **Pattern extraction accuracy:** % of learned patterns that are correct
- **Preference accuracy:** How well captured user preferences match reality
- **Improvement over baseline:** vs. naive RAG retrieval

---

## 11. KNOWN CHALLENGES & SOLUTIONS

| Challenge | Risk | Mitigation |
|-----------|------|-----------|
| Embedding cost | High API bills | Batch embedding, cache embeddings, use cheaper local model |
| Vector DB scale | Slow search with 100K+ memories | Partitioning, filtering before search, HNSW indexing |
| Consolidation complexity | Errors in compression/extraction | Thorough testing, human-in-the-loop validation |
| Importance signal gaming | System learns wrong priorities | Diverse signal sources, regular calibration |
| Privacy of stored data | Memories contain sensitive info | Encryption at rest, selective retention |
| Temporal consistency | Contradictory facts over time | Versioning, confidence scores, audit trails |

---

## 12. NEXT STEPS

1. **Validate design:** Get feedback from LLM/AI practitioners
2. **Prototype Phase 1:** Build minimal working memory system
3. **Stress test:** Simulate 1000+ memories, measure performance
4. **Iterate:** Refine based on early results
5. **Scale:** Gradually increase complexity

---

## 13. APPENDICES

### A. Example Importance Score Calculation

```
Scenario: User asks Claude to fix a subtle Python bug

Raw episode:
  "User asked about IndexError. Provided minimal code snippet.
   Identified was off-by-one error. Suggested fix was correct and
   user confirmed it worked. User rated response as 'very helpful.'"

Signals:
  - Novelty: 0.6 (seen off-by-one errors before, but specific context new)
  - Task_Success: 1.0 (user confirmed it worked)
  - Retrieval_Frequency: 0.0 (first time seeing)
  - User_Signal: 1.0 (explicit "very helpful" rating)
  - Emotional_Salience: 0.3 (neutral tone)

Importance Score:
  = 0.20 * 0.6 + 0.30 * 1.0 + 0.25 * 0.0 + 0.15 * 1.0 + 0.10 * 0.3
  = 0.12 + 0.30 + 0.0 + 0.15 + 0.03
  = 0.60 (MEDIUM-HIGH importance)

Storage decision:
  - Store compressed narrative in episodic memory
  - Extract pattern: "off-by-one errors in loops → check range"
  - Add user preference: "appreciates concise bug fix explanations"
```

### B. Forgetting Curve Example

```
Memory added at t=0, importance=0.75

Day 1: S(1) = e^(-0.1*1/0.75) ≈ 0.87
Day 3: S(3) = e^(-0.1*3/0.75) ≈ 0.67
Day 7: S(7) = e^(-0.1*7/0.75) ≈ 0.36
Day 10: S(10) = e^(-0.1*10/0.75) ≈ 0.26 (approaching deletion threshold of 0.05)
Day 15: S(15) = e^(-0.1*15/0.75) ≈ 0.14
Day 21: S(21) = e^(-0.1*21/0.75) ≈ 0.06 (candidate for deletion)

If accessed on Day 5:
  - Reset decay clock
  - Boost importance slightly
  - Recalculate new deletion schedule
```

---

**Document Version:** 1.0  
**Status:** Ready for Phase 1 Planning
