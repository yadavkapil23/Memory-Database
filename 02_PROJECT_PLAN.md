# Episodic AI Memory System - Project Plan

**Timeline:** 24 weeks (6 months)  
**Status:** Planning Phase  
**Last Updated:** May 20, 2026

---

## PROJECT OVERVIEW

This document breaks down the episodic memory system project into actionable phases, with specific deliverables, milestones, and success criteria for each.

---

## PHASE 1: Core Infrastructure (Weeks 1-4)

**Objective:** Build the foundational components for working and episodic memory layers.

### Deliverables
- Vector database (Qdrant) up and running
- Core data structures defined
- Embedding pipeline functional
- Basic CRUD operations for episodic memory
- Unit tests (>80% coverage)

### Week 1: Environment & Setup
**Tasks:**
- [ ] Set up project repository structure
- [ ] Configure Qdrant instance (local or cloud)
- [ ] Set up PostgreSQL/SQLite for metadata
- [ ] Create virtual environment and dependency management
- [ ] Set up CI/CD pipeline (GitHub Actions basic)
- [ ] Document development environment setup

**Deliverable:** Working dev environment, reproducible setup

### Week 2: Data Structures & Schemas
**Tasks:**
- [ ] Define Pydantic models for:
  - WorkingMemory
  - EpisodicMemory
  - MemoryMetadata
- [ ] Create database migrations
- [ ] Design Qdrant collection schema
- [ ] Document data model
- [ ] Create example data fixtures

**Deliverable:** Type-safe data models, database ready

### Week 3: Embedding Pipeline
**Tasks:**
- [ ] Integrate OpenAI Embeddings API
- [ ] Create embedding cache layer (Redis)
- [ ] Build batch embedding processor
- [ ] Implement error handling & retries
- [ ] Create embedding benchmarks
- [ ] Document costs & usage

**Deliverable:** Fast, cached embedding pipeline

### Week 4: Basic Operations & Testing
**Tasks:**
- [ ] Implement `add_episode()` operation
- [ ] Implement `search_by_similarity()` operation
- [ ] Implement `retrieve_temporal_range()` operation
- [ ] Write comprehensive unit tests
- [ ] Create integration tests
- [ ] Performance benchmarks

**Deliverable:** Working episodic memory system with search

### Success Criteria
- ✅ Can add 100 episodes in <5 seconds
- ✅ Can search 100 episodes in <100ms
- ✅ All tests passing (>80% coverage)
- ✅ No critical bugs found in manual testing

---

## PHASE 2: Importance Scoring (Weeks 5-8)

**Objective:** Implement sophisticated importance calculation with all five signals.

### Deliverables
- Five importance signals implemented
- Scoring formula calibrated
- Importance update mechanisms
- Evaluation framework for signal quality
- Documentation with examples

### Week 5: Signal Implementation
**Tasks:**
- [ ] **Novelty Signal**
  - Embedding distance calculation
  - Clustering algorithm (find nearest neighbors)
  - Normalize to 0-1 range
  - Tests with known similar/different episodes

- [ ] **Task Success Signal**
  - Define success criteria
  - Create rating mechanism
  - Build feedback collection API
  - Tests with synthetic task data

**Deliverable:** Novelty and Task Success signals working

### Week 6: Access & User Signals
**Tasks:**
- [ ] **Retrieval Frequency Signal**
  - Implement access tracking
  - Calculate normalized frequency
  - Implement access counter updates
  
- [ ] **User Signal**
  - Create user rating mechanism
  - Build API for explicit ratings
  - Handle missing ratings gracefully
  
- [ ] **Emotional Salience Signal**
  - Integrate sentiment analysis (Hugging Face)
  - Extract sentiment from narrative
  - Normalize polarity to salience

**Deliverable:** All five signals independently working

### Week 7: Formula Integration & Calibration
**Tasks:**
- [ ] Combine all signals with weights:
  ```
  0.20 * Novelty + 0.30 * Task_Success + 0.25 * Retrieval_Frequency + 
  0.15 * User_Signal + 0.10 * Emotional_Salience
  ```
- [ ] Create importance update pipeline
- [ ] Build signal weight calibration framework
- [ ] Test with synthetic data (100+ scenarios)
- [ ] Manual review and adjustment

**Deliverable:** Calibrated importance scoring

### Week 8: Evaluation & Benchmarking
**Tasks:**
- [ ] Define evaluation metrics:
  - Signal correlation
  - Formula stability
  - Edge case handling
- [ ] Create evaluation dataset (100+ labeled examples)
- [ ] Run benchmarks and analysis
- [ ] Document results and insights
- [ ] Optimize any underperforming signals

**Deliverable:** Validated importance scoring system

### Success Criteria
- ✅ Each signal tested individually
- ✅ Formula produces 0.0-1.0 scores
- ✅ Important memories consistently score >0.6
- ✅ Edge cases handled gracefully

---

## PHASE 3: Semantic Memory & Consolidation (Weeks 9-12)

**Objective:** Extract and store semantic knowledge from episodic memories.

### Deliverables
- Fact extraction working
- Pattern recognition engine
- Semantic memory storage (Neo4j or PostgreSQL)
- Consolidation pipeline functional
- Preference extraction system

### Week 9: Semantic Memory Storage Design
**Tasks:**
- [ ] Choose storage backend (Neo4j vs PostgreSQL JSON)
- [ ] Design semantic fact schema
- [ ] Design pattern schema
- [ ] Design preference schema
- [ ] Create database models
- [ ] Build CRUD operations

**Deliverable:** Semantic memory storage ready

### Week 10: Fact & Preference Extraction
**Tasks:**
- [ ] Build fact extractor (LLM-based)
  - Input: EpisodicMemory narrative
  - Output: List[SemanticFact]
  - Example: "User prefers Python" → Fact(subject="User", predicate="prefers_language", object="Python")

- [ ] Build preference extractor
  - Input: Episode + context
  - Output: List[UserPreference]
  - Example: "communication_style: concise"

- [ ] Create extraction prompt templates
- [ ] Test extraction accuracy
- [ ] Build confidence scoring

**Deliverable:** Working fact & preference extraction

### Week 11: Pattern Recognition & Extraction
**Tasks:**
- [ ] Build pattern detection algorithm
  - Identify recurring conditions
  - Identify consistent outcomes
  - Calculate success rates

- [ ] Implement pattern extraction pipeline
  - Input: Cluster of similar episodic memories
  - Output: List[LearnedPattern]
  
- [ ] Create pattern consolidation logic
  - Merge similar patterns
  - Update success rates
  - Manage pattern lifetime

**Deliverable:** Pattern extraction and consolidation working

### Week 12: Consolidation Pipeline
**Tasks:**
- [ ] Build full consolidation workflow:
  1. Batch collection (episodic memories from past 24h)
  2. Grouping (semantic similarity)
  3. Compression (narrative summarization)
  4. Extraction (facts, preferences, patterns)
  5. Storage (update semantic memory)

- [ ] Implement as scheduled job (Celery task)
- [ ] Add comprehensive logging
- [ ] Build monitoring/alerting
- [ ] Create manual trigger option
- [ ] Write tests for entire pipeline

**Deliverable:** Automated consolidation running hourly

### Success Criteria
- ✅ Can extract facts with >85% accuracy (manual eval)
- ✅ Patterns extracted have >70% success rate
- ✅ Consolidation completes in <30 minutes
- ✅ No data loss during consolidation

---

## PHASE 4: Forgetting & Decay (Weeks 13-16)

**Objective:** Implement temporal decay and intelligent deletion.

### Deliverables
- Forgetting curve algorithm
- TTL management system
- Prioritized deletion strategy
- Cleanup scheduler
- Monitoring and metrics

### Week 13: Forgetting Curve Implementation
**Tasks:**
- [ ] Implement exponential decay formula:
  ```
  S(t) = e^(-λt / Importance)
  ```
  Where λ varies by importance tier

- [ ] Define decay constants:
  - High importance (>0.7): λ = 0.1
  - Medium (0.4-0.7): λ = 0.5
  - Low (<0.4): λ = 1.5

- [ ] Build memory strength calculator
- [ ] Create decay predictor (estimate remaining lifespan)
- [ ] Write tests with synthetic timelines

**Deliverable:** Forgetting curve fully implemented

### Week 14: TTL & Scheduling
**Tasks:**
- [ ] Calculate and store TTL for each memory
  - `deletion_time = created_at + time_until_threshold`
  
- [ ] Build TTL update logic
  - Update when importance changes
  - Update when memory is accessed
  
- [ ] Create priority queue for deletion
- [ ] Implement soft deletion (mark as deleted, keep data)
- [ ] Test TTL accuracy

**Deliverable:** TTL system working with updates

### Week 15: Cleanup & Optimization
**Tasks:**
- [ ] Build cleanup job:
  1. Find all memories past TTL
  2. Sort by importance (delete low-importance first)
  3. Archive to cold storage (optional)
  4. Delete from vector DB
  5. Cleanup metadata

- [ ] Implement soft delete + hard delete
- [ ] Add recovery mechanism (7-day grace period)
- [ ] Create cleanup monitoring
- [ ] Test with large dataset cleanup

**Deliverable:** Automated cleanup running daily

### Week 16: Validation & Monitoring
**Tasks:**
- [ ] Build metrics:
  - Deletion rate (memories/day)
  - Retention by importance tier
  - Estimated storage capacity
  
- [ ] Create monitoring dashboard
- [ ] Test edge cases:
  - Rapid access (should prevent deletion)
  - Importance changes (should update TTL)
  - Duplicate memories (should merge)
  
- [ ] Document cleanup behavior

**Deliverable:** Decay system fully validated

### Success Criteria
- ✅ Low-importance memories deleted within predicted timeframe
- ✅ No high-importance memories deleted prematurely
- ✅ Cleanup completes in <10 minutes daily
- ✅ Recovery works correctly

---

## PHASE 5: Advanced Retrieval (Weeks 17-20)

**Objective:** Implement multi-modal retrieval with sophisticated ranking.

### Deliverables
- Four retrieval strategies working
- Ranking algorithm implemented
- Deduplication engine
- Performance optimization
- Retrieval API

### Week 17: Retrieval Strategies Implementation
**Tasks:**
- [ ] **Semantic Similarity Retrieval**
  - Embed query
  - Vector similarity search
  - Recency weighting
  - Filter by importance threshold

- [ ] **Temporal Retrieval**
  - Date range filtering
  - Recency ordering
  - Time proximity scoring

**Deliverable:** Two retrieval modes working

### Week 18: Advanced Retrieval
**Tasks:**
- [ ] **Associative Retrieval**
  - Graph traversal of related_memory_ids
  - Depth-limited exploration
  - Relevance scoring for chains
  
- [ ] **Semantic Knowledge Retrieval**
  - Query structured facts
  - Pattern matching
  - Preference lookups

**Deliverable:** All four retrieval modes implemented

### Week 19: Ranking & Deduplication
**Tasks:**
- [ ] Implement ranking formula:
  ```
  0.35 * Semantic_Relevance +
  0.25 * Importance_Score +
  0.20 * Recency_Weight +
  0.15 * Access_Frequency +
  0.05 * Emotional_Resonance
  ```

- [ ] Build deduplication:
  - Cluster results by similarity
  - Merge information from multiple sources
  - Preserve source information
  
- [ ] Optimize query performance
  - Index optimization
  - Query planning
  - Caching strategies

**Deliverable:** Optimized retrieval with ranking

### Week 20: Integration & Testing
**Tasks:**
- [ ] Create unified `retrieve()` interface
- [ ] Build mode selection logic
- [ ] Integration tests (cross-layer retrieval)
- [ ] Performance benchmarks:
  - Single query latency
  - Batch query throughput
  - Peak load handling

- [ ] Documentation with examples

**Deliverable:** Production-ready retrieval system

### Success Criteria
- ✅ Retrieval latency <100ms for top-5
- ✅ Relevance: >80% of results relevant (manual eval)
- ✅ Deduplication: <10% duplicate information
- ✅ Handles 1000+ memories without slowdown

---

## PHASE 6: Integration & Testing (Weeks 21-24)

**Objective:** Full system integration, testing, and documentation.

### Deliverables
- Agent integration layer
- End-to-end test suite
- Performance benchmarks
- Complete documentation
- Example use cases
- Production readiness checklist

### Week 21: Agent Integration
**Tasks:**
- [ ] Design agent integration API
  - How does agent store new events?
  - How does agent retrieve context?
  - How does agent give importance signals?

- [ ] Build integration layer
- [ ] Create example agent implementation
- [ ] Write integration tests

**Deliverable:** Agent integration layer working

### Week 22: End-to-End Testing
**Tasks:**
- [ ] Create comprehensive test scenarios:
  1. Long conversation (50+ turns)
  2. Multiple agents
  3. Cross-domain queries
  4. Time-based retrieval
  5. Preference learning

- [ ] Stress testing:
  - 100K+ memories
  - Concurrent access
  - Large batch operations

- [ ] Edge case testing:
  - Empty memory system
  - Conflicting data
  - Rapid changes

- [ ] Bug fixes from testing

**Deliverable:** All tests passing, system stable

### Week 23: Benchmarking & Optimization
**Tasks:**
- [ ] Comprehensive benchmarks:
  - Storage efficiency (raw KB vs compressed)
  - Compression ratio by importance
  - Consolidation throughput
  - Retrieval latency distribution
  - Memory footprint

- [ ] Performance optimization:
  - Index tuning
  - Query optimization
  - Caching improvements
  - Async pipeline improvements

- [ ] Create benchmark reports

**Deliverable:** Performance validated and optimized

### Week 24: Documentation & Launch
**Tasks:**
- [ ] Complete API documentation
- [ ] Write usage guide
- [ ] Create example notebooks
- [ ] Document deployment process
- [ ] Create architecture diagrams
- [ ] Write troubleshooting guide
- [ ] Create change log

- [ ] Final review and sign-off
- [ ] Create "readiness for production" checklist

**Deliverable:** Full documentation, ready to deploy

### Success Criteria
- ✅ All tests passing
- ✅ Performance meets targets
- ✅ Zero critical bugs
- ✅ Documentation complete
- ✅ Team trained on system

---

## MILESTONES & CHECKPOINTS

| Week | Milestone | Success Criteria |
|------|-----------|-----------------|
| 4 | Phase 1 Complete | Can add/search 100 episodes with <100ms latency |
| 8 | Importance Scoring | All signals validated, formula calibrated |
| 12 | Semantic Memory | Consolidation pipeline running, facts extracted |
| 16 | Forgetting System | TTL accurate, cleanup working |
| 20 | Retrieval System | <100ms queries, ranked results |
| 24 | Production Ready | Documented, tested, deployable |

---

## RESOURCE REQUIREMENTS

### Infrastructure
- Development Machine: 8+ GB RAM, 100GB disk
- Qdrant Instance: 50GB+ for 100K+ memories
- PostgreSQL: 20GB+ for metadata
- Redis: 5GB+ for caching
- Hosting: Cloud VM or local server

### Services/APIs
- OpenAI API: ~$200/month (embeddings)
- Qdrant Cloud (optional): ~$50/month
- Neo4j (if used): ~$50/month

### Time Investment
- Solo developer: 24 weeks (6 months)
- Team of 2: 12 weeks (3 months)
- Team of 3+: 8 weeks (2 months)

---

## RISK MANAGEMENT

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Embedding API costs balloon | Medium | High | Implement caching, monitor usage, use local model if needed |
| Vector DB performance issues | Low | High | Partitioning strategy, indexing tuning, load testing early |
| LLM extraction quality poor | Medium | Medium | Build eval framework, human validation, refine prompts |
| Importance signal gaming | Low | Medium | Diverse signals, regular calibration, monitoring |
| Data privacy concerns | Low | High | Encryption at rest, selective retention, audit logs |
| Consolidation bugs lose data | Low | Critical | Backup before consolidation, soft delete, recovery mechanism |

---

## DECISION LOG

### Decision 1: Vector DB Choice
**Options:** Qdrant, Weaviate, Pinecone, Milvus  
**Selected:** Qdrant  
**Rationale:**
- Good performance for embeddings + metadata filtering
- Self-hosted option available (cost control)
- Strong community support
- Balanced features and ease of use

### Decision 2: Semantic Storage Backend
**Options:** Neo4j, PostgreSQL JSON, TripleStore  
**To Decide:** In Phase 3 based on prototype results  
**Criteria:**
- Query flexibility
- Scale to millions of facts
- Performance for pattern matching
- Cost and complexity

### Decision 3: LLM for Extraction
**Options:** Claude, GPT-4, Open Source (Llama)  
**To Decide:** Depends on budget and accuracy requirements  
**Initial:** Use Claude API for Phase 1 (accurate), optimize in Phase 3

---

## NEXT IMMEDIATE STEPS

1. **Review this plan** with team/stakeholders
2. **Get feedback** on timeline and scope
3. **Set up development environment** (Week 1)
4. **Create GitHub project** with this as roadmap
5. **Start Phase 1: Core Infrastructure**

---

**Document Version:** 1.0  
**Status:** Ready for Execution  
**Last Updated:** May 20, 2026
