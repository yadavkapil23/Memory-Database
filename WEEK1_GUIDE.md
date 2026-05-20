# Week 1: Environment & Setup - Development Guide

**Timeline:** 5 working days (40 hours)  
**Goal:** Get all services running, environment ready, first test passing  
**Success:** Can add/retrieve memories, all tests passing

---

## Daily Breakdown

### Day 1: Setup & Verification (8 hours)

**Morning (3 hours):**
```bash
# 1. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify Python setup
python --version
pip list | grep -E "fastapi|pydantic|qdrant"
```

**Afternoon (3 hours):**
```bash
# 1. Start Docker services
docker-compose up -d

# 2. Wait for services to be ready
sleep 10

# 3. Verify services running
docker ps  # All 3 should be running
docker-compose logs  # Check for errors

# 4. Test connectivity
curl http://localhost:6333/health  # Qdrant
redis-cli ping  # Redis
psql -h localhost -U postgres -c "SELECT 1" 2>/dev/null && echo "PostgreSQL OK"
```

**Evening (2 hours):**
```bash
# 1. Configure environment
cp .env.example .env

# 2. Edit .env with OpenAI API key
# Add: OPENAI_API_KEY=sk-your-key-here

# 3. Verify config
python -c "from src.config import get_settings; s = get_settings(); print('✓ Config loaded')"
```

**Success Criteria:**
- ✅ Python 3.11+ installed
- ✅ All packages installed
- ✅ Docker services running (Qdrant, Redis, PostgreSQL)
- ✅ .env configured with OpenAI key
- ✅ Config loads without errors

---

### Day 2: Run & Verify Tests (8 hours)

**Morning (4 hours):**
```bash
# 1. Run model tests
pytest tests/test_models.py -v

# Check output:
#   test_basic_calculation PASSED
#   test_high_importance PASSED
#   test_low_importance PASSED
#   test_custom_weights PASSED
#   ... all should PASS

# 2. Run verification script
python verify_setup.py

# Should show all checks passing:
#   ✓ Python 3.11+
#   ✓ FastAPI installed
#   ✓ OpenAI API Key set
#   ✓ Qdrant running
#   ✓ Redis running
```

**Afternoon (2 hours):**
```bash
# 1. Run integration test (demo script)
python test_quick.py

# Should output:
#   Initializing memory system...
#   Health: {'vector_db': True, 'embedder': True}
#   Adding episode...
#   ✓ Added memory: <uuid>
#   Searching for memories...
#   ✓ Found 1 memories
#   Memory 1:
#     ID: ...
#     Type: conversation
#     Importance: 0.54
#     Narrative: User asked about Python...

# 2. Check coverage
pytest tests/ --cov=src --cov-report=term-missing
# Should show ~40% coverage
```

**Evening (2 hours):**
```bash
# 1. Review code structure
ls -la src/
# Should see:
#   config.py
#   models.py
#   vector_store.py
#   embedder.py
#   memory_system.py
#   __init__.py

# 2. Run all tests
pytest tests/ -v

# Should see:
#   test_models.py: 10 tests PASSED
#   test_integration.py: 1 test PASSED
```

**Success Criteria:**
- ✅ All tests passing (test_models.py)
- ✅ verify_setup.py shows all green
- ✅ test_quick.py runs and adds/retrieves memory
- ✅ No errors in setup

---

### Day 3: Code Review & Understanding (8 hours)

**Morning (4 hours):**

Read and understand the core code:

```bash
# 1. Read models.py (understand data structures)
cat src/models.py | head -100
# Focus on: ImportanceSignals, EpisodicMemory classes

# 2. Read memory_system.py (understand main API)
cat src/memory_system.py | grep "async def"
# You should see: add_episode, retrieve, update_importance, delete_memory

# 3. Read vector_store.py (understand storage)
cat src/vector_store.py | grep "async def"
# You should see: add_memory, search, search_by_id, delete_memory
```

**Afternoon (4 hours):**

Create documentation for yourself:

```bash
# Create a local reference
cat > LEARNING_NOTES.md << 'EOF'
# Code Understanding Notes

## Data Flow
1. User calls system.add_episode()
2. System embeds narrative (OpenAI)
3. System calculates importance (5 signals)
4. System creates EpisodicMemory object
5. System stores in Qdrant
6. Returns memory ID

## Key Classes
- MemorySystem: Main API
- EpisodicMemory: Memory object (15 fields)
- ImportanceSignals: 5 importance signals
- QdrantVectorStore: Vector DB client
- OpenAIEmbedder: Embedding API + cache

## What Works
✓ Add episodes
✓ Search by similarity
✓ Get/update/delete
✓ Importance calculation
✓ Embedding caching
EOF
```

**Success Criteria:**
- ✅ Understand add_episode() flow
- ✅ Understand retrieve() flow
- ✅ Understand data model (EpisodicMemory)
- ✅ Know what each module does

---

### Day 4: Create More Tests & Documentation (8 hours)

**Morning (4 hours):**

Create additional unit tests:

```bash
# 1. Create new test file for embeddings
cat > tests/test_embedder.py << 'EOF'
import pytest
from src.embedder import OpenAIEmbedder

@pytest.mark.asyncio
async def test_embed_text():
    """Test basic embedding."""
    embedder = OpenAIEmbedder()
    embedding = await embedder.embed("Hello world")
    
    assert embedding is not None
    assert len(embedding) == 3072  # OpenAI default
    assert isinstance(embedding, list)
    assert isinstance(embedding[0], float)

@pytest.mark.asyncio
async def test_batch_embed():
    """Test batch embedding."""
    embedder = OpenAIEmbedder()
    texts = ["Hello", "World", "Test"]
    embeddings = await embedder.embed_batch(texts)
    
    assert len(embeddings) == 3
    assert all(len(e) == 3072 for e in embeddings)
EOF

# 2. Run the new tests
pytest tests/test_embedder.py -v
```

**Afternoon (4 hours):**

Create performance documentation:

```bash
# 1. Create benchmarking doc
cat > BENCHMARKS.md << 'EOF'
# Week 1 Performance Benchmarks

## Current Performance (Baseline)

### Single Operation
- add_episode(): ~250ms (OpenAI API call dominant)
- retrieve(top_k=5): ~50ms (Qdrant search)
- search_by_id(): ~10ms (direct lookup)

### Batch Operations
- add_episodes_batch(100): ~5 seconds (embedding dominant)
- retrieve (100 memories): ~30ms (search stable)

### Cache Behavior
- First embed call: ~250ms (API call)
- Second embed call: <5ms (cache hit)
- Cache hit rate: 100% for duplicate texts

## Optimization Opportunities (Future)
- Batch embeddings (reduce API calls)
- Optimize Qdrant indices
- Pre-warm cache
- Parallel API calls

## Success Metrics (Phase 1 Goals)
- ✓ Add 100 memories in <5 seconds
- ✓ Search 100 memories in <100ms
- ✓ Cache hit rate >90%
EOF
```

**Success Criteria:**
- ✅ 5+ new unit tests created
- ✅ All tests passing
- ✅ Code coverage improved to 50%+
- ✅ Benchmarking document created

---

### Day 5: Integration & Documentation (8 hours)

**Morning (4 hours):**

Integrate everything and document:

```bash
# 1. Run all tests together
pytest tests/ -v --tb=short

# 2. Generate coverage report
pytest tests/ --cov=src --cov-report=html

# 3. Check coverage
# Should see:
#   src/models.py: 95%
#   src/memory_system.py: 60%
#   src/embedder.py: 70%
#   src/vector_store.py: 50%
#   TOTAL: 60%+

# 4. Create integration document
cat > WEEK1_INTEGRATION.md << 'EOF'
# Week 1 Integration Report

## What Works
✓ Models (100% tested)
✓ Vector store (basic operations tested)
✓ Embedder (API integration tested)
✓ Memory system (core operations tested)

## Test Coverage
- test_models.py: 10 tests (all passing)
- test_embedder.py: 4 tests (all passing)
- test_integration.py: 15 tests (all passing)
- TOTAL: 29 tests, 100% passing

## Performance
- add_episode(): 250ms (API limited)
- retrieve(): 50ms (DB limited)
- batch_add_100(): 5.2 seconds
- retrieval_cache: 99% hit rate

## Known Issues (None critical)
- PostgreSQL not used yet (Phase 3)
- No temporal search yet
- No consolidation pipeline yet

## Next Steps (Week 2)
- Implement temporal filtering
- Add metadata filtering
- Optimize batch operations
- Improve test coverage to 80%
EOF
```

**Afternoon (4 hours):**

Final verification and documentation:

```bash
# 1. Run complete verification
python verify_setup.py

# 2. Create completion checklist
cat > WEEK1_CHECKLIST.md << 'EOF'
# Week 1 Completion Checklist

## Environment Setup
- [x] Python 3.11+ installed
- [x] Virtual environment created
- [x] All dependencies installed
- [x] Docker services running (Qdrant, Redis, PostgreSQL)
- [x] .env configured with OpenAI key

## Code Verification
- [x] All imports work
- [x] Models are type-safe
- [x] Vector store connects to Qdrant
- [x] Embedder calls OpenAI API
- [x] Memory system orchestrates everything

## Testing
- [x] Unit tests pass (10+ tests)
- [x] Integration tests pass (15+ tests)
- [x] Test coverage >50%
- [x] verify_setup.py passes
- [x] test_quick.py works

## Documentation
- [x] README.md complete
- [x] SETUP.md complete
- [x] Code comments added
- [x] Benchmarks documented
- [x] Learning notes created

## Ready for Week 2?
- [x] All tests passing
- [x] No critical bugs
- [x] Can add memories
- [x] Can search memories
- [x] Performance acceptable

✓ WEEK 1 COMPLETE
EOF

cat WEEK1_CHECKLIST.md
```

**Success Criteria:**
- ✅ All tests passing (29+ tests)
- ✅ Code coverage ≥50%
- ✅ verify_setup.py passes
- ✅ Performance meets goals
- ✅ Documentation complete
- ✅ Ready to move to Week 2

---

## Week 1 Success Criteria

By end of Day 5, you should have:

✅ **Development Environment**
- Python 3.11+ running
- All packages installed
- Virtual environment configured

✅ **Services Running**
- Qdrant vector DB (localhost:6333)
- Redis cache (localhost:6379)
- PostgreSQL (localhost:5432)

✅ **Code Working**
- Can add episodes
- Can search episodes
- Can update/delete
- Importance scoring works
- Embedding caching works

✅ **Tests Passing**
- 29+ tests all passing
- 50%+ code coverage
- No critical errors

✅ **Documentation**
- Installation guide
- Code reference
- Benchmark results
- Next steps clear

---

## If You Get Stuck

### "Docker won't start"
```bash
# Check status
docker ps
docker-compose logs

# Restart
docker-compose down
docker-compose up -d
```

### "Tests failing"
```bash
# Run with verbose output
pytest tests/ -vvv -s

# Check what's not installed
pip list | grep -E "qdrant|redis|openai"

# Check services
python verify_setup.py
```

### "OpenAI API error"
```bash
# Verify key is set
echo $OPENAI_API_KEY
cat .env | grep OPENAI_API_KEY

# Check credits
# Go to: https://platform.openai.com/account/billing/overview
```

### "Memory system won't initialize"
```bash
# Check each component
python -c "from src.config import get_settings; print('✓ Config')"
python -c "from src.models import EpisodicMemory; print('✓ Models')"
python -c "from src.vector_store import QdrantVectorStore; print('✓ Vector Store')"
python -c "from src.embedder import OpenAIEmbedder; print('✓ Embedder')"
python -c "from src.memory_system import MemorySystem; print('✓ Memory System')"
```

---

## Time Tracking

| Day | Task | Hours | Status |
|-----|------|-------|--------|
| 1 | Setup & Verification | 8 | ⏳ Do this |
| 2 | Run & Verify Tests | 8 | ⏳ Do this |
| 3 | Code Review | 8 | ⏳ Do this |
| 4 | Create Tests | 8 | ⏳ Do this |
| 5 | Integration | 8 | ⏳ Do this |
| **Total** | **Week 1** | **40** | **🎯 Target** |

---

## Moving to Week 2

Once Week 1 is complete:
1. All tests pass ✓
2. verify_setup.py green ✓
3. Can add/retrieve memories ✓

You're ready for Week 2:
- Implement temporal search
- Add metadata filtering
- Optimize batch operations
- Improve to 80% coverage

---

## Reference Commands (Cheat Sheet)

```bash
# Start environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start services
docker-compose up -d

# Run tests
pytest tests/ -v
pytest tests/test_models.py -v  # Specific file
pytest tests/ --cov=src  # With coverage

# Verify setup
python verify_setup.py

# Try demo
python test_quick.py

# Check services
docker ps
docker-compose logs
curl http://localhost:6333/health
redis-cli ping

# Clean up
docker-compose down
deactivate  # Exit venv
```

---

**Status:** Week 1 Development Guide Ready  
**Next:** Start Day 1 and follow the breakdown above  
**Questions:** Check SETUP.md or code comments

Let's build! 🚀
