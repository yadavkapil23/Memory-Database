# ⏰ Week 7 Detailed Execution Guide

**Forgetting Curves & Knowledge Graph Architecture**

*Phase 2 Continues | 40 hours of focused development*

---

## 🎯 Week 7 Objective

Implement realistic memory decay and build knowledge graph for relationships between memories.

**Success Criteria:**
- ✓ Forgetting curves implemented
- ✓ Knowledge graph working
- ✓ Relationship inference functional
- ✓ 25+ new tests passing
- ✓ Archival system operational
- ✓ Integration complete

---

## Day 31: Forgetting Curves & Memory Decay

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Design forgetting curve implementation**
- Model: Ebbinghaus exponential decay
  - Formula: `strength(t) = strength_0 * e^(-t / tau)`
  - tau (half-life) based on importance
  - Retrieval refreshes strength
  - Spaced retrieval increases strength

**Task 2: Implement decay system**
- Create: `src/forgetting.py` (350 lines)
  - `MemoryStrength` class
  - `calculate_strength(memory, time_elapsed)`
  - `refresh_strength(memory)` - Retrieval refresh
  - `estimate_lifespan(memory)` - Days until archived
  - `get_decay_factor(importance)` - Tau calculation

**Task 3: Update memory model**
- Update `src/models.py`:
  - Add `strength_score` (0-1) to EpisodicMemory
  - Add `last_refreshed` timestamp
  - Add `refresh_count` (number of retrievals)
  - Add `created_at` timestamp
  - Calculate strength in importance calculation

**Task 4: Implement decay scheduling**
- Update `src/memory_system.py`:
  - Track all retrievals
  - Recalculate strength on schedule
  - Archive low-strength, old memories
  - Keep decay history

**Quick Check:**
```bash
python -c "from src.forgetting import MemoryStrength; print('✓ Decay OK')"
```

### Afternoon (4 hours)

**Task 5: Write forgetting curve tests**
- Create: `tests/test_forgetting_curves.py` (350 lines)
- Test cases:
  - Decay calculation (3 tests)
  - Strength refreshing (3 tests)
  - Spaced repetition (2 tests)
  - Lifespan estimation (2 tests)
  - Decay factor calculation (2 tests)
  - Archival triggering (2 tests)
  - Edge cases (2 tests)
- Total: 16 new tests

**Task 6: Implement archival system**
- Move old, low-strength memories:
  - To "cold storage" (not deleted)
  - Searchable but slower
  - Can be restored
  - Helps manage storage

**Run This:**
```bash
pytest tests/test_forgetting_curves.py -v
# Expected: 16 tests passing
```

**Progress:**
- ✓ Forgetting curves: **IMPLEMENTED**
- ✓ Decay system: **WORKING**
- ✓ Archival: **FUNCTIONAL**

---

## Day 32: Knowledge Graph Structure

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Design knowledge graph**
- Nodes: Memories (episodic + semantic)
- Edge types:
  - `similar` (conceptually similar)
  - `related` (domain/keyword match)
  - `temporal` (happened around same time)
  - `causal` (if A then B)
  - `contradicts` (A conflicts with B)
  - `refines` (B refines/corrects A)
  - `parts_of` (hierarchical)
  - `user_defined` (user-created)

**Task 2: Implement graph structure**
- Create: `src/knowledge_graph.py` (400 lines)
  - `KnowledgeGraph` class
  - Node storage (memories as nodes)
  - Edge storage (relationships as edges)
  - Weighted edges (strength of relationship)
  - Directed graph (some relationships directional)

**Task 3: Implement relationship discovery**
- Auto-detect relationships:
  - Similarity: Embedding cosine similarity
  - Domain match: Shared domains/keywords
  - Temporal: Within 7 days
  - Concepts: Shared semantic concepts
  - Keywords: Keyword overlap

**Task 4: Graph database integration**
- Use Qdrant for storage:
  - Nodes as memories (already stored)
  - Edges as payload metadata
  - Or: Use Neo4j for graph operations
  - Or: In-memory NetworkX for now

**Quick Check:**
```bash
python -c "from src.knowledge_graph import KnowledgeGraph; print('✓ Graph OK')"
```

### Afternoon (4 hours)

**Task 5: Write graph tests**
- Create: `tests/test_knowledge_graph.py` (350 lines)
- Test cases:
  - Add nodes (2 tests)
  - Add edges (3 tests)
  - Find relationships (3 tests)
  - Similarity calculation (2 tests)
  - Graph traversal (2 tests)
  - Weight management (2 tests)
  - Edge cases (2 tests)
- Total: 16 new tests

**Task 6: Implement graph algorithms**
- BFS/DFS traversal
- Shortest path (concept distance)
- Connected components (related clusters)
- Centrality measures (important memories)

**Run This:**
```bash
pytest tests/test_knowledge_graph.py -v
# Expected: 16 tests passing
```

**Progress:**
- ✓ Graph structure: **IMPLEMENTED**
- ✓ Relationships: **DISCOVERABLE**
- ✓ Algorithms: **WORKING**

---

## Day 33: Graph-Based Retrieval

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Implement associative retrieval**
- "Find memories related to this memory"
- Methods:
  - `get_related_memories(memory_id)` - Direct neighbors
  - `get_similar_concepts(memory_id)` - Concept similarity
  - `walk_graph(start, depth=2)` - Multi-hop traversal
  - `find_path(memory_id1, memory_id2)` - Connection path

**Task 2: Implement analogy-based retrieval**
- "A is to B as X is to ?"
- Use vector arithmetic:
  - embedding(B) - embedding(A) + embedding(X) = embedding(?)
  - Find closest memory to result vector
  - Supports conceptual reasoning

**Task 3: Implement discovery**
- Serendipitous recommendations:
  - Random walk on graph
  - Biased by importance
  - Avoid recently seen
  - Encourages exploration

**Quick Check:**
```bash
python -c "from src.knowledge_graph import KnowledgeGraph; print('✓ Retrieval OK')"
```

### Afternoon (4 hours)

**Task 4: Write retrieval tests**
- Create: `tests/test_graph_retrieval.py` (300 lines)
- Test cases:
  - Associative retrieval (3 tests)
  - Analogy search (3 tests)
  - Path finding (2 tests)
  - Discovery (2 tests)
  - Graph traversal limits (2 tests)
  - Performance under load (2 tests)
- Total: 14 new tests

**Task 5: Integrate with memory_system**
- Add retrieval methods:
  - `retrieve_related(memory_id)`
  - `retrieve_by_analogy(a, b, x)`
  - `discover_random(importance_min=0.0)`
- Update ranking to consider graph

**Run This:**
```bash
pytest tests/test_graph_retrieval.py -v
# Expected: 14 tests passing
```

**Progress:**
- ✓ Associative retrieval: **WORKING**
- ✓ Analogy search: **FUNCTIONAL**
- ✓ Discovery: **OPERATIONAL**

---

## Day 34: Graph Maintenance & Optimization

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Implement graph maintenance**
- Edge creation:
  - Automatic during consolidation
  - Periodic relationship update
  - User-defined relationships
  - Remove stale edges

**Task 2: Optimize graph performance**
- Caching:
  - Cache common paths
  - Pre-compute centrality
  - Cache similarity scores
- Pruning:
  - Remove weak edges (weight < 0.1)
  - Keep only top-K relationships
  - Archive old relationships

**Task 3: Implement graph analysis**
- Statistics:
  - Graph density
  - Average path length
  - Clustering coefficient
  - Most central memories

**Quick Check:**
```bash
python -c "from src.knowledge_graph import KnowledgeGraph; print('✓ Maintenance OK')"
```

### Afternoon (4 hours)

**Task 4: Write maintenance tests**
- Create: `tests/test_graph_maintenance.py` (250 lines)
- Test cases:
  - Edge lifecycle (2 tests)
  - Weight updates (2 tests)
  - Pruning (2 tests)
  - Caching (2 tests)
  - Statistics (2 tests)
  - Performance (2 tests)
- Total: 12 new tests

**Task 5: Add graph visualization**
- Create: `graph_visualization.py` (200 lines)
  - Export to GraphML
  - Export to JSON
  - Generate adjacency matrix
  - Basic statistics report

**Run This:**
```bash
pytest tests/test_graph_maintenance.py -v
# Expected: 12 tests passing
```

**Progress:**
- ✓ Maintenance: **IMPLEMENTED**
- ✓ Optimization: **WORKING**
- ✓ Analysis: **FUNCTIONAL**

---

## Day 35: Week 7 Completion & Integration

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Full integration testing**
- End-to-end: Add memories → Build graph → Query graph
- Test scenarios:
  1. Add 50 episodic memories (mixed domains)
  2. Trigger consolidation
  3. Auto-build graph relationships
  4. Query related, analogies, discover
  5. Verify meaningful results

**Task 2: Performance testing**
- Query performance on 1000+ node graphs
- Path finding efficiency
- Analogy search speed
- Discovery performance

**Task 3: Code review**
- forgetting.py
- knowledge_graph.py
- graph_retrieval.py
- graph_maintenance.py

### Afternoon (4 hours)

**Task 4: Documentation**
- Create: `KNOWLEDGE_GRAPH.md` (500 lines)
  - Graph structure overview
  - Relationship types
  - Retrieval strategies
  - Performance characteristics
  - Use cases and examples

**Task 5: CLI enhancements**
- New commands:
  - `related [memory_id]` - Show related memories
  - `analogy [a] [b] [x]` - Analogy search
  - `discover` - Random walk discovery
  - `graph_stats` - Show graph statistics

**Run This:**
```bash
pytest tests/ --cov=src
# Expected: 260+ tests, 85%+ coverage
python cli.py related [memory_id]
python cli.py discover
```

**Progress:**
- ✓ Forgetting curves: **OPERATIONAL**
- ✓ Knowledge graph: **FUNCTIONAL**
- ✓ Retrieval: **WORKING**
- ✓ Tests: **58+ NEW**
- ✓ Week 7: **COMPLETE**

---

## 📊 Week 7 Metrics

**Code**
- New modules: 4 (forgetting, graph, retrieval, maintenance)
- Updated modules: 2 (models, memory_system)
- New lines: 1300+
- New tests: 58+

**Graph Statistics**
- Nodes: All memories (episodic + semantic)
- Edge types: 8
- Relationship discovery: Automatic
- Graph density: Moderate to high

**Performance**
- Path finding: < 100ms (for 1000 nodes)
- Analogy search: < 200ms
- Discovery: < 50ms
- Caching improves repeat queries

---

## ✅ Week 7 Completion Checklist

- [ ] Forgetting curves implemented (16 tests)
- [ ] Knowledge graph working (16 tests)
- [ ] Graph retrieval working (14 tests)
- [ ] Graph maintenance working (12 tests)
- [ ] All tests passing (58+ new)
- [ ] Performance verified
- [ ] Integration complete
- [ ] Documentation done
- [ ] CLI updated
- [ ] Ready for Week 8

**If all YES:** Week 7 Complete! ✅

---

## 🎓 What You've Built

**Forgetting System**
- Ebbinghaus decay curves
- Memory strength scoring
- Spaced repetition support
- Archival system
- Realistic memory lifetime

**Knowledge Graph**
- Relationship discovery
- Multiple edge types
- Weighted relationships
- Graph algorithms
- Performance optimization

**Advanced Retrieval**
- Associative queries
- Analogy search
- Random discovery
- Path-based reasoning
- Graph-informed ranking

---

## 🚀 Ready for Week 8?

→ Proceed to `WEEK8_GUIDE.md` (Advanced Retrieval & Phase 2 Completion)

---

**Week 7 Status:** ✅ COMPLETE  
**Tests Added:** 58+  
**Graph Nodes:** All memories  
**Relationship Types:** 8  
**Next:** Advanced Retrieval & Final Integration (Week 8)  

Knowledge networks complete! 🧠📊🚀
