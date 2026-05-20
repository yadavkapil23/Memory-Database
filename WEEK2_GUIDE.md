# 📚 Week 2 Detailed Execution Guide

**Feature Expansion & Vector Store Optimization**

*40 hours of focused development*

---

## 🎯 Week 2 Objective

Expand the vector store, implement temporal retrieval, add metadata filtering, and achieve 70%+ test coverage.

**Success Criteria:**
- ✓ Temporal retrieval working
- ✓ Advanced filtering implemented
- ✓ 50+ new tests written
- ✓ Test coverage 70%+
- ✓ Batch operations optimized
- ✓ No regressions from Week 1

---

## Day 6: Temporal Retrieval System

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Design temporal queries**
- Read: `01_EPISODIC_MEMORY_TECHNICAL_DESIGN.md` section on temporal retrieval
- Understand: Time-window searches, relative queries, decay functions
- Plan: Implementation approach for three query types:
  - Absolute time range: "memories between 2024-01-01 and 2024-01-31"
  - Relative range: "memories from last 7 days"
  - Around time: "memories from around Jan 15, ±3 days"

**Task 2: Implement temporal filters in vector_store.py**
- Add method: `search_by_time_range(start_date, end_date, top_k=10)`
- Add method: `search_recent(days=7, top_k=10)`
- Add method: `search_around_date(target_date, days_window=3, top_k=10)`
- Use Qdrant payload filters for timestamp comparisons
- All methods should support metadata filtering

**Quick Check:**
```bash
# Verify imports work
python -c "from src.vector_store import VectorStore; print('✓ Imports OK')"
```

### Afternoon (4 hours)

**Task 3: Write temporal retrieval tests**
- Create: `tests/test_temporal_retrieval.py` (300 lines)
- Test cases:
  - Add memories with specific timestamps (5 test cases)
  - Search by absolute date range (4 test cases)
  - Search by relative range (4 test cases)
  - Search around date with tolerance (3 test cases)
  - Edge cases (start==end, future dates, empty results) (4 test cases)
- Total: 20 new temporal tests

**Task 4: Integration tests**
- Update `tests/test_integration.py` to add temporal scenarios
- Test combining temporal search + importance filtering
- Test combining temporal search + keyword filtering
- Verify performance with 100+ memories

**Run This:**
```bash
pytest tests/test_temporal_retrieval.py -v
# Expected: 20 tests passing
```

**Progress:**
- ✓ Temporal retrieval: **IMPLEMENTED**
- ✓ Tests: **20 PASSING**
- ✓ Coverage increased: **+5%**

---

## Day 7: Advanced Metadata Filtering

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Design filter system**
- Read: `04_ARCHITECTURE_REFERENCE.md` metadata section
- Plan: Three filter types
  - Single-field filters: `domains=["Python"]`
  - Multi-field filters: `domains=["Python", "AI"], importance_tier="HIGH"`
  - Nested filters: `(domains INCLUDES "Python" OR keywords INCLUDES "async") AND importance >= 0.7`

**Task 2: Implement metadata filtering**
- Add method: `search_with_filters(query, filters, top_k=10)`
- Filters parameter format:
  ```python
  filters = {
    "domains": ["Python", "ML"],  # Match any domain
    "keywords": ["async"],         # Match any keyword
    "importance_min": 0.5,         # Importance threshold
    "event_type": "learning"       # Exact match
  }
  ```
- Support combining with temporal searches
- Support combining with importance searches

**Task 3: Implement ranking by filters**
- Boost results matching multiple filters
- Rank by relevance score + filter match score
- Document ranking formula in code comments

**Quick Check:**
```bash
python -c "from src.vector_store import VectorStore; v = VectorStore(); print('✓ Filter API OK')"
```

### Afternoon (4 hours)

**Task 4: Write filtering tests**
- Create: `tests/test_metadata_filtering.py` (400 lines)
- Test cases:
  - Single-field filters (5 tests)
  - Multi-field filters (5 tests)
  - Filter combinations (5 tests)
  - Filters + temporal search (4 tests)
  - Filters + importance search (4 tests)
  - Edge cases (empty results, invalid filters) (3 tests)
- Total: 26 new filtering tests

**Task 5: Update main API**
- Add to `src/memory_system.py`:
  - `retrieve_with_filters(query, filters, top_k=10)`
  - `retrieve_temporal(query, start_date, end_date, top_k=10)`
  - `retrieve_combined(query, filters, temporal_range, top_k=10)`
- Update health check to validate filter system

**Run This:**
```bash
pytest tests/test_metadata_filtering.py -v
# Expected: 26 tests passing
```

**Progress:**
- ✓ Metadata filtering: **IMPLEMENTED**
- ✓ Tests: **26 PASSING**
- ✓ Coverage: **65%+**

---

## Day 8: Batch Operations Optimization

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Profile batch operations**
- Create: `batch_profiler.py` (200 lines)
  - Add 10 memories, measure time
  - Add 50 memories, measure time
  - Add 100 memories, measure time
  - Add 500 memories, measure time
- Record: Timing, memory usage, API calls
- Identify bottlenecks

**Task 2: Optimize batch operations**
- Current: `add_episodes_batch()` in `memory_system.py`
- Optimization 1: Parallel embedding (increase from 10 to 20)
- Optimization 2: Batch Qdrant inserts (group into 50-item chunks)
- Optimization 3: Connection pooling (reuse HTTP connections)
- Optimization 4: Caching (skip re-embedding identical text)

**Task 3: Implement optimizations**
- Update `src/embedder.py` parallel batch size
- Update `src/vector_store.py` insert chunking
- Add connection pooling to both clients
- Update caching to check for duplicate narratives

**Quick Check:**
```bash
python batch_profiler.py
# Expected: <5 seconds for 100 memories
```

### Afternoon (4 hours)

**Task 4: Write batch optimization tests**
- Create: `tests/test_batch_optimization.py` (300 lines)
- Test cases:
  - Batch add 100 memories (2 tests: timing + correctness)
  - Batch add 500 memories (2 tests)
  - Parallel embedding correctness (3 tests)
  - Connection pooling (2 tests)
  - Duplicate detection (3 tests)
  - Memory usage validation (2 tests)
- Total: 15 new batch tests

**Task 5: Performance benchmarks**
- Create: `benchmarks/batch_performance.py` (200 lines)
- Measure and record:
  - Time to add 10, 50, 100, 500 memories
  - Average per-memory latency
  - Embedding cache hit rate
  - Total API calls (cost tracking)
- Output: CSV or JSON for tracking over time

**Run This:**
```bash
pytest tests/test_batch_optimization.py -v
pytest benchmarks/batch_performance.py
# Expected: All tests passing, <5s for 100 memories
```

**Progress:**
- ✓ Batch operations: **OPTIMIZED**
- ✓ Tests: **15 PASSING**
- ✓ 100 memories: **<5 seconds**

---

## Day 9: Deletion & Cleanup Operations

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Design deletion system**
- Read: Design patterns for cascade deletion
- Plan: Three deletion modes
  - Single: Delete one memory by ID
  - Batch: Delete multiple memories
  - Query-based: Delete all memories matching criteria

**Task 2: Implement deletion**
- In `src/vector_store.py`:
  - `delete_memory(memory_id)` - Already exists, verify works
  - `delete_memories_batch(memory_ids)` - New method
  - `delete_by_query(query_filter)` - New method (e.g., delete old memories)
- In `src/memory_system.py`:
  - Add `delete_episode(memory_id)`
  - Add `delete_episodes_batch(memory_ids)`
  - Add `delete_before_date(date)` - Cleanup old memories
- Implement soft-delete pattern (mark deleted, don't remove)

**Task 3: Add cleanup utilities**
- In `src/utils.py`:
  - `cleanup_old_memories(days_old=90)` - Delete memories older than N days
  - `cleanup_low_importance(importance_threshold=0.2)` - Delete low-value memories
  - `compute_storage_recovery(operation)` - Estimate space saved

**Quick Check:**
```bash
python -c "from src.memory_system import MemorySystem; print('✓ Deletion API OK')"
```

### Afternoon (4 hours)

**Task 4: Write deletion tests**
- Create: `tests/test_deletion.py` (250 lines)
- Test cases:
  - Delete single memory (3 tests)
  - Delete batch (3 tests)
  - Delete by query (3 tests)
  - Soft-delete verification (2 tests)
  - Cleanup old memories (3 tests)
  - Cleanup by importance (3 tests)
  - Edge cases (delete non-existent, invalid IDs) (3 tests)
- Total: 20 new deletion tests

**Task 5: Integration**
- Update `tests/test_integration.py` with deletion workflows
- Test: Add → Update → Delete → Verify gone
- Test: Batch operations → Cleanup → Verify storage
- Verify search doesn't return deleted items

**Run This:**
```bash
pytest tests/test_deletion.py -v
# Expected: 20 tests passing
```

**Progress:**
- ✓ Deletion system: **IMPLEMENTED**
- ✓ Tests: **20 PASSING**
- ✓ Cleanup utilities: **READY**

---

## Day 10: Week 2 Completion & Integration

**Time Budget:** 8 hours

### Morning (4 hours)

**Task 1: Full test suite run**
- Run all tests with coverage
- Record baseline metrics
- Fix any failures

**Run This:**
```bash
pytest tests/ -v --cov=src --cov-report=html
# Expected: 70%+ coverage, all tests passing
```

**Task 2: Code review**
- Review new code for quality:
  - Type hints complete?
  - Error handling comprehensive?
  - Documentation clear?
  - Performance acceptable?
- Make improvements

**Task 3: Documentation**
- Update `04_ARCHITECTURE_REFERENCE.md`:
  - Add temporal retrieval section
  - Add metadata filtering section
  - Add batch optimization section
  - Add deletion operations section
- Add method signatures to reference

### Afternoon (4 hours)

**Task 4: CLI updates**
- Update `cli.py` with new commands:
  - `search_temporal` - Temporal queries
  - `search_filtered` - Metadata filtering
  - `delete` - Delete memories
  - `cleanup` - Run cleanup utilities
- Test each new command interactively

**Task 5: Final validation**
- Create comprehensive test scenario
- Add 100 memories with metadata
- Test temporal search (different date ranges)
- Test metadata filtering (various combinations)
- Test batch deletion
- Test performance
- Record results

**Task 6: Week 2 Summary**
- Count new code lines
- Record test count (target: 75+ total tests)
- Verify coverage (target: 70%+)
- Document new capabilities
- List remaining work for Week 3

**Run This:**
```bash
python cli.py
# Test all new commands interactively
```

**Progress:**
- ✓ Temporal retrieval: **WORKING**
- ✓ Metadata filtering: **WORKING**
- ✓ Batch optimization: **WORKING**
- ✓ Deletion: **WORKING**
- ✓ Coverage: **70%+**
- ✓ Tests: **75+**

---

## 📊 Week 2 Metrics

Track these numbers:

**Code**
- Starting tests: 29
- New tests: 81 (20 temporal + 26 filtering + 15 batch + 20 deletion)
- Ending tests: 110+
- Starting coverage: 50%
- Ending coverage: 70%+

**Performance**
- Add 100 memories: < 5 seconds
- Search 100 memories: < 100ms
- Batch filtering: < 200ms
- Deletion: < 50ms

**Functionality**
- ✓ Temporal retrieval (3 methods)
- ✓ Metadata filtering (1 main method + ranking)
- ✓ Batch optimization (parallel, chunked, pooled)
- ✓ Deletion system (3 deletion modes + cleanup)
- ✓ CLI commands for all (4 new commands)

---

## ✅ Week 2 Completion Checklist

- [ ] Temporal retrieval implemented and tested (20 tests)
- [ ] Metadata filtering implemented and tested (26 tests)
- [ ] Batch operations optimized (15 tests)
- [ ] Deletion system implemented (20 tests)
- [ ] CLI updated with new commands
- [ ] All tests passing (110+)
- [ ] Coverage 70%+
- [ ] Performance benchmarks recorded
- [ ] Documentation updated
- [ ] Code reviewed and cleaned
- [ ] Ready for Week 3

**If all YES:** Week 2 Complete! ✅

---

## 📈 What You'll Know After Week 2

✓ Temporal query system  
✓ Advanced metadata filtering  
✓ Batch operation optimization  
✓ Deletion and cleanup strategies  
✓ Query combining (temporal + filters + importance)  
✓ Performance profiling techniques  
✓ Production-quality operations  

---

## 🎯 Ready for Week 3?

When you complete all Week 2 tasks:
1. All tests passing (110+)
2. Coverage at 70%+
3. Performance benchmarks documented
4. Code reviewed
5. CLI fully functional

→ Proceed to `WEEK3_GUIDE.md`

---

**Week 2 Status:** Ready to Execute  
**Time Commitment:** 40 hours (5 days × 8 hours)  
**Target Completion:** End of Week 2  
**Next:** WEEK3_GUIDE.md  

Let's build! 🚀
