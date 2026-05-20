# Phase 1 Setup Guide

Complete guide to get the episodic memory system running locally.

## Prerequisites

- Python 3.11+
- Docker (for Qdrant, Redis, PostgreSQL)
- OpenAI API key
- ~50GB disk space
- 8GB+ RAM

---

## Step 1: Get OpenAI API Key

1. Go to https://platform.openai.com/api/keys
2. Create a new secret key
3. Copy it somewhere safe (you'll need it)

---

## Step 2: Start Docker Services

### Quick Start (All services)

```bash
# Start all services using docker
docker-compose up -d
```

If you don't have docker-compose.yml yet, create it:

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
    environment:
      - QDRANT_API_KEY=${QDRANT_API_KEY:-}

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_storage:/data

  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: memory_system
    volumes:
      - postgres_storage:/var/lib/postgresql/data

volumes:
  qdrant_storage:
  redis_storage:
  postgres_storage:
EOF
```

Then start:
```bash
docker-compose up -d
```

### Or Start Services Individually

```bash
# Start Qdrant
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest

# Start Redis
docker run -d --name redis -p 6379:6379 redis:latest

# Start PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=memory_system \
  -p 5432:5432 \
  postgres:15
```

### Verify Services Are Running

```bash
# Check Qdrant
curl http://localhost:6333/health

# Check Redis
redis-cli ping

# Check PostgreSQL
psql -h localhost -U postgres -c "SELECT 1"
```

---

## Step 3: Set Up Python Environment

```bash
# Navigate to project directory
cd Memory_Project

# Create virtual environment
python3.11 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.11+
```

---

## Step 4: Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list | grep -E "fastapi|pydantic|qdrant|openai"
```

---

## Step 5: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings
# Open in your editor and add your OpenAI API key
# nano .env    (or use your preferred editor)
```

**Important:** In `.env`, set:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

---

## Step 6: Verify Setup

```bash
# Run the health check script
python -c "
from src.memory_system import MemorySystem
import asyncio

async def check():
    system = MemorySystem()
    health = await system.health_check()
    print('Health Check:')
    for component, status in health.items():
        print(f'  {component}: {'✓' if status else '✗'}')

asyncio.run(check())
"
```

Expected output:
```
Health Check:
  vector_db: ✓
  embedder: ✓
```

---

## Step 7: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_models.py -v

# Run with output
pytest tests/ -v -s
```

Expected: All tests passing ✓

---

## Step 8: Try a Simple Example

Create `test_quick.py`:

```python
import asyncio
from uuid import uuid4
from datetime import datetime
from src.memory_system import MemorySystem
from src.models import ImportanceSignals

async def main():
    print("Initializing memory system...")
    system = MemorySystem()
    
    # Check health
    health = await system.health_check()
    print(f"Health: {health}")
    
    # Add an episode
    print("\nAdding episode...")
    session_id = uuid4()
    
    memory_id = await system.add_episode(
        narrative="User asked about Python for loops. I explained range(), enumerate(), and list comprehensions.",
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
            "domains": ["Python", "Education"],
            "entities": ["User", "Python", "loops"],
            "keywords": ["for loop", "range", "enumerate"],
        },
        session_id=session_id,
    )
    
    print(f"✓ Added memory: {memory_id}")
    
    # Search for it
    print("\nSearching for memories...")
    results = await system.retrieve(
        query="How do Python for loops work?",
        top_k=5,
    )
    
    if results:
        print(f"✓ Found {len(results)} memories")
        for i, memory in enumerate(results, 1):
            print(f"\n  Memory {i}:")
            print(f"    ID: {memory.id}")
            print(f"    Type: {memory.event_type}")
            print(f"    Importance: {memory.importance_score:.2f}")
            print(f"    Narrative: {memory.compressed_narrative[:100]}...")
    else:
        print("✗ No memories found")
    
    # Get stats
    print("\nSystem stats...")
    stats = await system.get_stats()
    print(f"✓ Total memories: {stats.total_memories}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python test_quick.py
```

---

## Common Issues & Solutions

### Issue: "Connection refused" (Qdrant)
```
Solution:
1. Verify Docker is running: docker ps
2. Check Qdrant: curl http://localhost:6333/health
3. Restart Qdrant: docker restart qdrant
```

### Issue: "OPENAI_API_KEY not found"
```
Solution:
1. Check .env file exists: cat .env
2. Verify key is set: grep OPENAI_API_KEY .env
3. Make sure it's not empty
```

### Issue: "Module not found" error
```
Solution:
1. Check virtual environment is activated: which python
2. Reinstall: pip install -r requirements.txt
3. Verify: pip list | grep package-name
```

### Issue: Tests fail with "connection error"
```
Solution:
1. Make sure all Docker services are running
2. Wait 5 seconds for services to fully start
3. Check: docker ps (all containers should be up)
```

### Issue: "OpenAI API error"
```
Solution:
1. Verify API key is correct
2. Check you have credits: https://platform.openai.com/account/billing/overview
3. Try embedding a short text manually
```

---

## File Structure After Setup

```
Memory_Project/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── vector_store.py
│   ├── embedder.py
│   └── memory_system.py
├── tests/
│   ├── __init__.py
│   └── test_models.py
├── .env
├── .env.example
├── requirements.txt
├── pytest.ini
├── docker-compose.yml
├── README.md
├── SETUP.md
└── test_quick.py
```

---

## Running the System

### Mode 1: Development (Manual Testing)
```bash
# Use the test_quick.py script
python test_quick.py
```

### Mode 2: Running Tests
```bash
# Run all tests
pytest tests/ -v

# Watch mode (auto-rerun on file changes)
pip install pytest-watch
ptw tests/
```

### Mode 3: API Server (Later, Phase 5)
```bash
# Not ready yet, but eventually:
uvicorn api:app --reload
```

---

## Next Steps

1. ✅ Environment is set up
2. ✅ Services are running
3. ✅ Tests are passing
4. **Now:** Start Phase 1 implementation
   - Expand vector store operations
   - Add batch processing
   - Optimize retrieval
   - Write more tests

---

## Useful Commands

```bash
# Check all services running
docker ps

# View logs
docker logs qdrant      # Qdrant logs
docker logs redis       # Redis logs
docker logs postgres    # PostgreSQL logs

# Stop services
docker-compose down

# Remove all containers (careful!)
docker-compose down -v

# Install dev tools
pip install black isort flake8 mypy

# Format code
black src/ tests/

# Check code quality
flake8 src/ tests/

# Type checking
mypy src/

# View embeddings cache
redis-cli
> KEYS embedding:*
> GET embedding:abc123

# Connect to PostgreSQL
psql -h localhost -U postgres -d memory_system
```

---

## Reference

- **Qdrant Docs:** https://qdrant.tech/documentation/
- **OpenAI Embeddings:** https://platform.openai.com/docs/guides/embeddings/
- **Redis Docs:** https://redis.io/documentation/
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

**Status:** Phase 1 setup complete!  
**Next:** Begin implementing core memory operations.

Go back to Phase 1 tasks and start implementing:
- [ ] Expand vector store operations
- [ ] Add temporal retrieval
- [ ] Optimize batch operations
- [ ] Write comprehensive tests
