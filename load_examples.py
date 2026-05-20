#!/usr/bin/env python3
"""
Load example memories into the system for learning and testing.
Run: python load_examples.py
"""

import asyncio
import sys
import os
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.memory_system import MemorySystem
from src.models import ImportanceSignals


EXAMPLE_MEMORIES = [
    {
        "narrative": "Python is a versatile, high-level programming language known for its simple syntax and readability. It's widely used in data science, web development, automation, and AI. Python has a large ecosystem of libraries including NumPy, Pandas, and TensorFlow.",
        "event_type": "conversation",
        "domains": ["Python", "Programming"],
        "keywords": ["python", "language", "data-science", "web"],
        "novelty": 0.8,
        "task_success": 1.0,
        "user_signal": 0.9,
    },
    {
        "narrative": "JavaScript is essential for web development. It runs in browsers and can also run on servers with Node.js. JavaScript is dynamic, event-driven, and supports functional programming. Modern JavaScript (ES6+) has significantly improved the language.",
        "event_type": "conversation",
        "domains": ["JavaScript", "Web Development"],
        "keywords": ["javascript", "web", "nodejs", "es6"],
        "novelty": 0.7,
        "task_success": 1.0,
        "user_signal": 0.85,
    },
    {
        "narrative": "Machine learning involves training algorithms on data to make predictions or decisions. Key concepts include supervised learning (classification, regression), unsupervised learning (clustering), and reinforcement learning. Libraries like scikit-learn and TensorFlow are essential tools.",
        "event_type": "conversation",
        "domains": ["Machine Learning", "AI"],
        "keywords": ["ml", "ai", "algorithms", "training"],
        "novelty": 0.9,
        "task_success": 1.0,
        "user_signal": 0.95,
    },
    {
        "narrative": "Git is a distributed version control system that tracks changes in source code. Key commands include git clone, commit, push, pull, and branch. GitHub is a popular platform for hosting Git repositories and collaborating on projects.",
        "event_type": "conversation",
        "domains": ["Git", "DevOps"],
        "keywords": ["git", "version-control", "github"],
        "novelty": 0.6,
        "task_success": 1.0,
        "user_signal": 0.8,
    },
    {
        "narrative": "REST APIs (Representational State Transfer) use HTTP methods (GET, POST, PUT, DELETE) to perform operations on resources. RESTful design principles emphasize statelessness, uniform interfaces, and client-server separation. FastAPI is a modern Python framework for building REST APIs.",
        "event_type": "conversation",
        "domains": ["API Design", "Web Services"],
        "keywords": ["rest", "api", "http", "fastapi"],
        "novelty": 0.75,
        "task_success": 1.0,
        "user_signal": 0.88,
    },
    {
        "narrative": "Docker containers package applications and their dependencies into isolated, portable units. Containers ensure consistency across development, testing, and production environments. Docker Compose orchestrates multiple containers, while Kubernetes manages container orchestration at scale.",
        "event_type": "conversation",
        "domains": ["DevOps", "Containerization"],
        "keywords": ["docker", "containers", "kubernetes"],
        "novelty": 0.8,
        "task_success": 1.0,
        "user_signal": 0.9,
    },
    {
        "narrative": "SQL (Structured Query Language) is used to manage relational databases. Key concepts include SELECT, INSERT, UPDATE, DELETE, JOINs, and transactions. PostgreSQL is a powerful open-source relational database with JSON support and advanced features.",
        "event_type": "conversation",
        "domains": ["Databases", "SQL"],
        "keywords": ["sql", "postgresql", "databases"],
        "novelty": 0.7,
        "task_success": 1.0,
        "user_signal": 0.85,
    },
    {
        "narrative": "Testing is crucial for software quality. Unit tests verify individual functions, integration tests verify multiple components working together, and end-to-end tests verify complete workflows. Pytest is a popular Python testing framework.",
        "event_type": "conversation",
        "domains": ["Testing", "Quality Assurance"],
        "keywords": ["testing", "pytest", "quality"],
        "novelty": 0.65,
        "task_success": 1.0,
        "user_signal": 0.82,
    },
    {
        "narrative": "Asynchronous programming allows multiple operations to run concurrently without blocking. Python's asyncio library provides async/await syntax. Async is essential for building high-performance web servers and handling many concurrent connections.",
        "event_type": "conversation",
        "domains": ["Python", "Async Programming"],
        "keywords": ["async", "asyncio", "concurrency"],
        "novelty": 0.85,
        "task_success": 1.0,
        "user_signal": 0.92,
    },
    {
        "narrative": "Data structures are fundamental to efficient programming. Arrays and lists store ordered data, dictionaries map keys to values, sets store unique elements, and linked lists provide efficient insertion/deletion. Choosing the right data structure is crucial for performance.",
        "event_type": "conversation",
        "domains": ["Computer Science", "Algorithms"],
        "keywords": ["data-structures", "arrays", "algorithms"],
        "novelty": 0.5,
        "task_success": 1.0,
        "user_signal": 0.8,
    },
]


async def load_examples():
    """Load example memories into the system."""
    print("\n" + "="*70)
    print("  Loading Example Memories")
    print("="*70)

    system = MemorySystem()
    session_id = uuid4()

    loaded = 0
    failed = 0

    for i, example in enumerate(EXAMPLE_MEMORIES, 1):
        try:
            print(f"\n  [{i}/{len(EXAMPLE_MEMORIES)}] Loading: {example['domains'][0]}")

            # Calculate importance
            novelty = example.pop("novelty")
            task_success = example.pop("task_success")
            user_signal = example.pop("user_signal")

            # Extract narrative and metadata
            narrative = example.pop("narrative")
            event_type = example.pop("event_type")
            domains = example.pop("domains")
            keywords = example.pop("keywords")

            # Add memory
            memory_id = await system.add_episode(
                narrative=narrative,
                event_type=event_type,
                importance_signals=ImportanceSignals(
                    novelty=novelty,
                    task_success=task_success,
                    retrieval_frequency=0.0,
                    user_signal=user_signal,
                    emotional_salience=0.3,
                ),
                metadata={
                    "domains": domains,
                    "keywords": keywords,
                },
                session_id=session_id,
            )

            importance = (
                0.20 * novelty
                + 0.30 * task_success
                + 0.25 * 0.0
                + 0.15 * user_signal
                + 0.10 * 0.3
            )

            tier = "HIGH" if importance >= 0.7 else "MEDIUM" if importance >= 0.4 else "LOW"

            print(f"       ✓ Added (ID: {memory_id}, Importance: {importance:.2f} [{tier}])")
            loaded += 1

        except Exception as e:
            print(f"       ✗ Failed: {e}")
            failed += 1

    # Summary
    print("\n" + "="*70)
    print(f"  Summary: {loaded} loaded, {failed} failed")
    print("="*70)

    # Test search
    print("\n  Testing search on loaded memories...")
    try:
        results = await system.retrieve("Python programming language", top_k=5)
        print(f"  ✓ Search found {len(results)} relevant memories")

        if results:
            print(f"\n  Top result: {results[0].compressed_narrative[:100]}...")
            print(f"  Importance: {results[0].importance_score:.2f}")

    except Exception as e:
        print(f"  ✗ Search failed: {e}")

    # Get stats
    print("\n  System statistics:")
    try:
        stats = await system.get_stats()
        print(f"  • Total memories: {stats.total_memories}")
        print(f"  • Average importance: {stats.avg_importance:.2f}")
        print(f"  • High importance: {stats.high_importance_count}")
        print(f"  • Medium importance: {stats.medium_importance_count}")
        print(f"  • Low importance: {stats.low_importance_count}")
    except Exception as e:
        print(f"  ✗ Stats failed: {e}")

    print("\n  ✓ Examples loaded! Try searching or using the CLI.")
    print("  Run: python cli.py")


async def main():
    """Main entry point."""
    try:
        await load_examples()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
