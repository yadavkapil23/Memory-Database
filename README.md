# Episodic AI Memory System

A hierarchical memory architecture for AI agents that stores important events, forgets unimportant ones, learns patterns, and retrieves relevant memories efficiently.

**Status:** Design & Planning Phase (Ready for Phase 1 Implementation)  
**Timeline:** 24 weeks (6 months) to production-ready  
**Author:** Master (parth.garggkota@gmail.com)

---
## Quick Overview

This project solves a fundamental problem with current AI memory: **traditional RAG (Retrieval Augmented Generation) treats all information equally**. Our system uses importance scoring to determine:

- **What to keep verbatim** (important conversations)
- **What to compress** (less critical events)
- **What to abstract** (timeless patterns)
- **What to forget** (unimportant details)

The result is an AI that learns, remembers appropriately, and retrieves efficiently.

---

## Core Innovation

**Three-layer memory hierarchy with importance-weighted consolidation:**

```
Working Memory (Current Context)
    ↓ [Consolidation Job]
Episodic Memory (Specific Events) + Forgetting Curve
    ↓ [Pattern Extraction]
Semantic Memory (Timeless Patterns)
```

Each layer serves a purpose:
- **Working:** Fast access to current context
- **Episodic:** Remember important past events
- **Semantic:** Extract and remember general principles

---

## Project Documentation

This project includes four main design documents:

### 1. **Technical Design** (`01_EPISODIC_MEMORY_TECHNICAL_DESIGN.md`)
Complete technical specification covering:
- Architecture and data structures
- Importance scoring formula
- Consolidation and pattern extraction
- Forgetting curve algorithm
- Retrieval mechanisms
- Implementation phases

**Read this when:** You need to understand the complete system design

### 2. **Project Plan** (`02_PROJECT_PLAN.md`)
6-month implementation roadmap:
- 6 phases with specific deliverables
- Week-by-week breakdown
- Success criteria for each phase
- Risk management and decision log

**Read this when:** You want to understand the timeline and milestones

### 3. **Quick Start Guide** (`03_QUICK_START_GUIDE.md`)
Everything needed to begin Phase 1:
- Setup instructions
- Core data models
- First working code
- Testing strategy
- Success metrics

**Read this when:** You're ready to start implementation

### 4. **Architecture Reference** (`04_ARCHITECTURE_REFERENCE.md`)
Quick lookup guide:
- System diagrams
- Data flow examples
- Performance expectations
- Technology stack

**Read this when:** You need to quickly reference a specific design detail

---

## Key Metrics

### Importance Scoring
```
Importance = 0.20 × Novelty
           + 0.30 × Task_Success
           + 0.25 × Retrieval_Frequency
           + 0.15 × User_Signal
           + 0.10 × Emotional_Salience
```

### Forgetting Curve
```
Strength(t) = e^(-λt / Stability)
```
Where memories decay at different rates based on importance.

### Performance Targets
- **Add episode:** <500ms
- **Search:** <100ms
- **Consolidation:** <15 minutes
- **Storage per memory:** ~10KB
- **Query latency:** <100ms for top-5 results

---

## Implementation Phases

| Phase | Duration | Focus | Deliverable |
|-------|----------|-------|-------------|
| **1: Core Infrastructure** | Weeks 1-4 | Working + episodic memory | Add/search episodes |
| **2: Importance Scoring** | Weeks 5-8 | All 5 signals + calibration | Validated scoring |
| **3: Semantic Memory** | Weeks 9-12 | Facts, patterns, preferences | Consolidation pipeline |
| **4: Forgetting & Decay** | Weeks 13-16 | TTL, deletion, cleanup | Automated decay |
| **5: Advanced Retrieval** | Weeks 17-20 | Multi-modal search, ranking | Production retrieval |
| **6: Integration & Testing** | Weeks 21-24 | Full integration, docs | Production-ready |

---

## Technology Stack

**Storage:**
- Qdrant (vector database for episodic memories)
- PostgreSQL (metadata and timestamps)
- Neo4j or PostgreSQL JSON (semantic facts)
- Redis (embeddings cache, working memory)

**Processing:**
- OpenAI Embeddings API (text-embedding-3-large)
- Claude API (pattern extraction, compression)
- Python 3.11+ with FastAPI

**Infrastructure:**
- Docker for services
- Celery for async jobs
- GitHub Actions for CI/CD

---

## Getting Started

### Prerequisites
- Python 3.11+
- OpenAI API key
- Docker (for Qdrant, Redis, PostgreSQL)
- ~50GB disk space
- 8GB+ RAM

### Quick Start
```bash
# 1. Read the Quick Start Guide
cat 03_QUICK_START_GUIDE.md

# 2. Set up environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start services
docker run -p 6333:6333 qdrant/qdrant
docker run -p 6379:6379 redis:latest

# 5. Run first test
pytest tests/test_integration.py -v
```

See `03_QUICK_START_GUIDE.md` for detailed setup instructions.

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────┐
│         Agent / User Interface              │
└────────────────┬────────────────────────────┘
                 │
         ┌───────┴────────┐
         ↓                ↓
    ┌─────────┐      ┌──────────┐
    │Embedding│      │Importance│
    │Pipeline │      │ Scoring  │
    └────┬────┘      └────┬─────┘
         └────────┬───────┘
                  ↓
         ┌────────────────┐
         │Working Memory  │
         │ (128K tokens)  │
         └────────┬───────┘
                  │
        ┌─────────┼──────────┐
        ↓         ↓          ↓
    ┌────────┐ ┌───────┐ ┌──────┐
    │Episodic│ │Semantic│ │Cache │
    │Memory  │ │Memory  │ │Redis │
    └────┬───┘ └───┬───┘ └──────┘
         │         │
         └────┬────┘
              ↓
      ┌──────────────────┐
      │Consolidation Job │
      │  (Async)         │
      └──────────────────┘
```

---

## Key Design Decisions

### 1. Vector Database: Qdrant
- ✅ Fast semantic search
- ✅ Metadata filtering
- ✅ Self-hosted option
- ✅ HNSW indexing for scale

### 2. Importance Formula: Five Signals
- Novelty (how different?)
- Task Success (did it help?)
- Retrieval Frequency (accessed often?)
- User Signal (explicit rating?)
- Emotional Salience (memorable?)

### 3. Storage Strategy: Three Layers
- Working: Ephemeral (session)
- Episodic: Time-decaying (days-months)
- Semantic: Permanent (unless explicitly removed)

### 4. Consolidation: Async Background Job
- Runs hourly/daily
- Compresses narratives
- Extracts patterns
- Applies decay
- No impact on response time

---

## Expected Outcomes

After completing this project, you'll have:

✅ **A production-quality memory system** that AI agents can actually use  
✅ **A 50-100K memory capacity** (limited by disk, not algorithm)  
✅ **Sub-100ms retrieval latency** for most queries  
✅ **Automatic forgetting** of unimportant information  
✅ **Pattern learning** that improves agent behavior  
✅ **Complete documentation** and working code  

---

## Success Metrics

**Phase 1 Success:** Can add and retrieve 100 episodes in <100ms  
**Phase 2 Success:** Importance scoring validated with >80% accuracy  
**Phase 3 Success:** Patterns extracted with >70% relevance  
**Phase 4 Success:** Low-importance memories deleted as predicted  
**Phase 5 Success:** Retrieval latency <100ms, >80% relevant results  
**Phase 6 Success:** Production-ready, fully documented, tested  

---

## What's Next?

1. **Review the documents:**
   - Start with this README
   - Read 03_QUICK_START_GUIDE.md for implementation
   - Reference 04_ARCHITECTURE_REFERENCE.md while coding

2. **Set up environment** (following Quick Start Guide)

3. **Begin Phase 1** (Core Infrastructure)
   - Set up project structure
   - Implement basic add/search operations
   - Write comprehensive tests

4. **Iterate:** Complete each phase, then move to the next

---

## Contributing & Questions

For design questions → Check the technical design doc (`01_EPISODIC_MEMORY_TECHNICAL_DESIGN.md`)  
For implementation questions → Check the quick start guide (`03_QUICK_START_GUIDE.md`)  
For architecture questions → Check the reference guide (`04_ARCHITECTURE_REFERENCE.md`)  
For timeline questions → Check the project plan (`02_PROJECT_PLAN.md`)

---

## Document Map

```
README.md (YOU ARE HERE)
├─ 01_EPISODIC_MEMORY_TECHNICAL_DESIGN.md     [Complete spec]
├─ 02_PROJECT_PLAN.md                         [6-month roadmap]
├─ 03_QUICK_START_GUIDE.md                    [How to start coding]
└─ 04_ARCHITECTURE_REFERENCE.md               [Quick lookup]
```

---

## License

This project is designed and documented for implementation. No specific license imposed.

---

## Timeline

- **Start:** May 20, 2026
- **Phase 1 Complete:** June 17, 2026 (4 weeks)
- **Phase 6 Complete:** August 12, 2026 (24 weeks)

---

## Additional Resources

- **Embeddings:** [OpenAI Embeddings Documentation](https://platform.openai.com/docs/guides/embeddings)
- **Vector Databases:** [Qdrant Documentation](https://qdrant.tech/documentation/)
- **Pattern Extraction:** [Claude API Documentation](https://docs.anthropic.com/)
- **Forgetting Curves:** [Research on Memory Retention](https://en.wikipedia.org/wiki/Forgetting_curve)

---

**Ready to build?** Start with the Quick Start Guide and begin Phase 1! 🚀

---

**Last Updated:** May 20, 2026  
**Version:** 1.0  
**Status:** Ready for Implementation
