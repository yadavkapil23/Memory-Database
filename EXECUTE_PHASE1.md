# 🚀 EXECUTE PHASE 1 - Your Development Guide

**Timeline:** This Week (40 hours)  
**Goal:** Build working Phase 1 system  
**Success:** All tests passing, CLI working, ready for Phase 2

---

## What's Ready for You

### Code & Tools Just Created
- ✅ **src/utils.py** - Utility functions (async helpers, timers, stats)
- ✅ **cli.py** - Interactive memory system CLI
- ✅ **test_phase1.py** - Comprehensive validation tests

### What You Can Do Now
```
Your memory system now supports:
  ✓ Add memories (single or batch)
  ✓ Search by semantic similarity
  ✓ Get/retrieve specific memories
  ✓ Update importance scores
  ✓ Delete memories
  ✓ Calculate statistics
  ✓ Performance monitoring
  ✓ Health checks
  ✓ Interactive CLI
```

---

## Step 1: Verify Everything Works (30 minutes)

### Setup (10 minutes)
```bash
# Navigate to project
cd Memory_Project

# Activate Python venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install requirements (if not done)
pip install -r requirements.txt
```

### Start Services (5 minutes)
```bash
# In another terminal:
docker-compose up -d

# Verify running:
docker ps  # Should see 3 containers
```

### Run Tests (15 minutes)
```bash
# Run comprehensive Phase 1 validation
python test_phase1.py

# Expected output:
#   ✓ Health Check (2 tests)
#   ✓ Add Single Memory
#   ✓ Search Memories
#   ✓ Batch Add (2 tests)
#   ✓ Importance Scoring (3 tests)
#   ✓ Statistics
#   ✓ Caching
#   ✓ Performance
#   
#   Result: X/X passed
```

**If all pass:** ✓ You're ready! Move to Step 2

**If some fail:** Check SETUP.md Troubleshooting

---

## Step 2: Interactive Demo (15 minutes)

Try the CLI tool:

```bash
# Run interactive CLI
python cli.py

# You'll see:
# Welcome screen
# Health check
# Interactive menu
```

### Try These Commands:

**1. Add a memory**
```
Command > add

Enter narrative: "I learned that Python lists are ordered collections."
Event type: conversation
Novelty: 0.7
Task Success: 1.0
Retrieval Frequency: 0.0
User Signal: 0.9
Emotional Salience: 0.2
Domains: Python, Education
Keywords: list, ordered

Result: Memory added with importance 0.62
```

**2. Search for it**
```
Command > search

Query: "Are Python lists ordered?"

Result: Found 1 memory
  [HIGH] May 20, 2:30 PM
  Score: 0.62
  Text: I learned that Python lists are ordered...
  Accessed: 1x
```

**3. Check stats**
```
Command > stats

Total Memories: 1
Average Importance: 0.62
Memories Added (Session): 1
```

**4. Exit**
```
Command > quit

Result: Goodbye!
```

---

## Step 3: Understand the Code (2 hours)

Read these in order:

### 1. Core System Flow (30 min)
```bash
# Open and read:
cat src/memory_system.py

# Focus on:
#   - add_episode() method
#   - retrieve() method
#   - update_importance() method
#   - Key logic and error handling
```

### 2. Data Models (30 min)
```bash
# Open and read:
cat src/models.py

# Understand:
#   - ImportanceSignals (5 signals)
#   - EpisodicMemory (15 fields)
#   - What each field means
```

### 3. Vector Store (30 min)
```bash
# Open and read:
cat src/vector_store.py

# Understand:
#   - How memories are stored in Qdrant
#   - How search works
#   - Batch operations
```

### 4. Utility Functions (30 min)
```bash
# Open and read:
cat src/utils.py

# See available helpers:
#   - Async timers and retries
#   - Memory statistics
#   - Importance tier calculation
```

---

## Step 4: Run Tests & Expand (8 hours)

### Create More Tests

**4.1 Test temporal retrieval (1 hour)**
```bash
# Create tests/test_temporal.py
# Write tests for:
#   - Search by date range
#   - Sort by timestamp
#   - Recency weighting

# Run: pytest tests/test_temporal.py -v
```

**4.2 Test metadata filtering (1 hour)**
```bash
# Create tests/test_filtering.py
# Write tests for:
#   - Filter by domain
#   - Filter by importance tier
#   - Filter by entities

# Run: pytest tests/test_filtering.py -v
```

**4.3 Test performance (1 hour)**
```bash
# Create tests/test_performance.py
# Write tests for:
#   - Add 100 memories performance
#   - Search latency
#   - Batch operation speed

# Run: pytest tests/test_performance.py -v
```

### Implement Missing Features

**4.4 Add temporal search to vector_store.py (2 hours)**
```python
async def search_temporal(
    self,
    start_date: datetime,
    end_date: datetime,
    top_k: int = 50,
) -> List[EpisodicMemory]:
    """Search memories in date range."""
    # Implementation here
```

**4.5 Add metadata filtering (1 hour)**
```python
async def search_with_filters(
    self,
    query_embedding: List[float],
    filters: Dict[str, Any],
) -> List[EpisodicMemory]:
    """Search with domain/importance/entity filters."""
    # Implementation here
```

**4.6 Improve batch operations (1 hour)**
```python
async def add_memories_parallel(
    self,
    memories: List[EpisodicMemory],
    batch_size: int = 10,
) -> List[UUID]:
    """Add memories with parallel processing."""
    # Implementation here
```

### Run Full Test Suite
```bash
# Run all tests
pytest tests/ -v --tb=short

# Check coverage
pytest tests/ --cov=src --cov-report=html

# Expected: 50%+ coverage, all tests passing
```

---

## Step 5: Performance Optimization (4 hours)

### Profile the System
```bash
# Create a performance profiling script
cat > profile_memory_system.py << 'EOF'
import asyncio
import time
from src.memory_system import MemorySystem
from src.models import ImportanceSignals
from uuid import uuid4

async def profile():
    system = MemorySystem()
    session_id = uuid4()
    
    # Test adding 100 memories
    print("Adding 100 memories...")
    start = time.time()
    
    for i in range(100):
        await system.add_episode(
            narrative=f"Memory {i}",
            event_type="test",
            importance_signals=ImportanceSignals(
                novelty=0.5, task_success=1.0,
                retrieval_frequency=0.0, user_signal=0.8,
                emotional_salience=0.1
            ),
            session_id=session_id,
        )
    
    elapsed = time.time() - start
    print(f"Added 100 in {elapsed:.1f}s ({elapsed/100:.2f}s each)")
    
    # Test searching
    print("Searching 100 memories...")
    start = time.time()
    
    for i in range(10):
        results = await system.retrieve(
            query=f"Memory query {i}",
            top_k=5
        )
    
    elapsed = time.time() - start
    print(f"10 searches in {elapsed:.3f}s ({elapsed/10*1000:.1f}ms each)")

asyncio.run(profile())
EOF

python profile_memory_system.py
```

### Optimize Based on Results
```
If add_episode() > 500ms:
  - Check embedding cache hit rate
  - Verify batch processing
  - Profile OpenAI API latency

If retrieve() > 100ms:
  - Check Qdrant index optimization
  - Verify vector DB tuning
  - Consider caching hot queries

If memory usage grows:
  - Implement memory pooling
  - Clean up unused caches
  - Monitor Redis memory
```

---

## Step 6: Documentation & Integration (4 hours)

### Document What You Built
```bash
# Create Phase 1 summary
cat > PHASE1_SUMMARY.md << 'EOF'
# Phase 1 Summary

## What Works
- [x] Add single/batch episodes
- [x] Search by similarity
- [x] Importance scoring
- [x] Metadata handling
- [x] Caching

## Performance Metrics
- Add: XXms per memory
- Search: XXms per query
- Batch (100): XXs total

## Code Statistics
- Tests: XX passing
- Coverage: XX%
- Lines of code: XXXX

## Known Limitations
- No temporal filtering yet
- No semantic memory yet
- No consolidation yet

## Next Steps (Phase 2)
- [ ] Implement Phase 2 importance signals
- [ ] Add temporal retrieval
- [ ] Build consolidation pipeline
EOF
```

### Run Full Verification
```bash
# 1. Run all tests
pytest tests/ -v

# 2. Run CLI
python cli.py
# Try add/search/stats

# 3. Run comprehensive validation
python test_phase1.py

# 4. Check coverage
pytest tests/ --cov=src

# Expected: 80%+ coverage, all tests passing
```

---

## Step 7: Phase 1 Completion (2 hours)

### Final Checklist

- [ ] All tests passing (pytest tests/ -v)
- [ ] CLI working (python cli.py)
- [ ] Can add 100 memories in <5 seconds
- [ ] Can search 100 memories in <100ms
- [ ] Code coverage >80%
- [ ] No critical bugs
- [ ] Documentation complete
- [ ] Performance benchmarks recorded

### Document Your Progress

```bash
cat > PHASE1_COMPLETE.md << 'EOF'
# Phase 1 Complete! ✓

## Timeline
Started: [Date]
Completed: [Date]
Total Time: [Hours]

## Tests
- Unit Tests: XX passed
- Integration Tests: XX passed
- Performance Tests: XX passed
- Coverage: XX%

## Performance
- Add single: XXms
- Add batch (100): XXs
- Search: XXms
- Batch search: XXms

## What Works
✓ Store memories with importance
✓ Search by semantic similarity
✓ Batch operations
✓ Caching (Redis)
✓ Vector DB (Qdrant)
✓ Statistics
✓ Interactive CLI

## Ready for Phase 2?
YES ✓

## Next Steps
1. Move to Phase 2
2. Implement all 5 importance signals
3. Add semantic memory storage
4. Build consolidation pipeline
EOF
```

---

## Time Breakdown (40 hours)

| Task | Hours | Status |
|------|-------|--------|
| Verify setup | 0.5 | ⏳ Do first |
| Interactive demo | 0.25 | ⏳ Quick test |
| Code review | 2 | ⏳ Understand |
| Create tests | 3 | ⏳ Expand coverage |
| Implement features | 5 | ⏳ Add functionality |
| Performance test | 2 | ⏳ Measure & optimize |
| Documentation | 2 | ⏳ Record progress |
| Integration | 2 | ⏳ Final verification |
| **TOTAL** | **~17** | **First week estimate** |

---

## Quick Reference Commands

```bash
# Activate environment
source venv/bin/activate

# Start services
docker-compose up -d

# Run tests
pytest tests/ -v
pytest tests/test_phase1.py -v

# Run CLI
python cli.py

# Run comprehensive validation
python test_phase1.py

# Check coverage
pytest tests/ --cov=src

# View logs
docker-compose logs qdrant
docker-compose logs redis

# Stop services
docker-compose down
```

---

## Success Indicators

**You've completed Phase 1 when:**

✅ Can add memories reliably  
✅ Can search and find memories  
✅ Can manage importance  
✅ All tests passing (80%+ coverage)  
✅ Performance meets targets  
✅ CLI works smoothly  
✅ No critical bugs  
✅ Documentation complete  

---

## Next Phase (Phase 2)

Once Phase 1 is complete:
1. Follow 02_PROJECT_PLAN.md Week 5-8
2. Implement full importance scoring
3. Calibrate all 5 signals
4. Create evaluation framework
5. Validate scoring accuracy

---

## Getting Help

**If you get stuck:**
- Check SETUP.md (Troubleshooting)
- Check WEEK1_GUIDE.md ("If You Get Stuck")
- Read code comments in src/*.py
- Check 01_EPISODIC_MEMORY_TECHNICAL_DESIGN.md

**If you have questions:**
- System design: Technical Design doc
- Architecture: Architecture Reference
- Code: Comments in source files
- Timeline: Project Plan

---

## You've Got This! 💪

You now have:
- ✅ Complete working foundation
- ✅ Interactive CLI tool
- ✅ Comprehensive tests
- ✅ Performance profiling
- ✅ Clear roadmap

**Start with Step 1 today. Complete Phase 1 this week. Move to Phase 2 next week.**

---

**Status:** Phase 1 Execution Guide Ready ✓  
**Next Action:** Run `python test_phase1.py`  
**Time Estimate:** 40 hours over 1 week

Let's build! 🚀
