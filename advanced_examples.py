#!/usr/bin/env python3
"""
Advanced Examples - Real-world usage patterns for the memory system.
Run: python advanced_examples.py
"""

import asyncio
import sys
import os
from uuid import uuid4
from datetime import datetime, timedelta
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.memory_system import MemorySystem
from src.models import ImportanceSignals
from src.utils import (
    MemoryStats,
    print_memory_summary,
    calculate_importance_tier,
    get_memory_lifespan_estimate,
)


class AdvancedExamples:
    """Demonstrate advanced memory system usage."""

    def __init__(self):
        """Initialize."""
        self.system = MemorySystem()
        self.session_id = uuid4()

    async def example_1_learning_session(self):
        """Example 1: Simulate a learning session with multiple memories."""
        print("\n" + "="*70)
        print("  EXAMPLE 1: Learning Session")
        print("="*70)
        print("\nScenario: User learns about machine learning")

        topics = [
            {
                "title": "Linear Regression",
                "narrative": "Linear regression is a fundamental ML algorithm that models the relationship between input features and a continuous target variable using a linear function. It minimizes the sum of squared residuals.",
                "novelty": 0.6,
                "success": 1.0,
            },
            {
                "title": "Logistic Regression",
                "narrative": "Despite its name, logistic regression is used for binary classification. It applies a sigmoid function to linear predictions to output probabilities between 0 and 1.",
                "novelty": 0.7,
                "success": 1.0,
            },
            {
                "title": "Decision Trees",
                "narrative": "Decision trees recursively split data on features to create a tree-like model for classification or regression. They're interpretable but prone to overfitting.",
                "novelty": 0.8,
                "success": 1.0,
            },
            {
                "title": "Neural Networks",
                "narrative": "Neural networks are composed of interconnected layers of neurons that learn hierarchical representations. Deep networks with multiple layers can learn complex patterns.",
                "novelty": 0.9,
                "success": 1.0,
            },
        ]

        memories_added = []

        for topic in topics:
            memory_id = await self.system.add_episode(
                narrative=topic["narrative"],
                event_type="learning",
                importance_signals=ImportanceSignals(
                    novelty=topic["novelty"],
                    task_success=topic["success"],
                    retrieval_frequency=0.0,
                    user_signal=0.85,
                    emotional_salience=0.3,
                ),
                metadata={
                    "domains": ["Machine Learning"],
                    "keywords": [topic["title"].lower()],
                },
                session_id=self.session_id,
            )

            memories_added.append(memory_id)
            print(f"  ✓ Learned: {topic['title']}")

        print(f"\n  Added {len(memories_added)} memories")

        # Test retrieval
        await asyncio.sleep(0.5)
        results = await self.system.retrieve(
            query="What machine learning algorithms should I know?",
            top_k=5,
        )

        print(f"  Retrieved {len(results)} relevant memories")
        if results:
            print(f"\n  Top result: {results[0].keywords}")

    async def example_2_importance_hierarchy(self):
        """Example 2: Demonstrate importance tier hierarchy."""
        print("\n" + "="*70)
        print("  EXAMPLE 2: Importance Tier Hierarchy")
        print("="*70)

        scenarios = [
            {
                "description": "Critical Bug Fix (Production Down)",
                "novelty": 1.0,
                "task_success": 1.0,
                "user_signal": 1.0,
            },
            {
                "description": "Important Feature (Requested by User)",
                "novelty": 0.7,
                "task_success": 0.9,
                "user_signal": 0.9,
            },
            {
                "description": "Useful Information (Reference)",
                "novelty": 0.5,
                "task_success": 0.6,
                "user_signal": 0.6,
            },
            {
                "description": "Casual Conversation (Random Thought)",
                "novelty": 0.2,
                "task_success": 0.2,
                "user_signal": 0.3,
            },
        ]

        print("\nAdding memories with different importance levels:")

        for scenario in scenarios:
            memory_id = await self.system.add_episode(
                narrative=scenario["description"],
                event_type="conversation",
                importance_signals=ImportanceSignals(
                    novelty=scenario["novelty"],
                    task_success=scenario["task_success"],
                    retrieval_frequency=0.0,
                    user_signal=scenario["user_signal"],
                    emotional_salience=0.2,
                ),
                session_id=self.session_id,
            )

            importance = (
                0.20 * scenario["novelty"]
                + 0.30 * scenario["task_success"]
                + 0.25 * 0.0
                + 0.15 * scenario["user_signal"]
                + 0.10 * 0.2
            )

            tier = calculate_importance_tier(importance)
            lifespan = get_memory_lifespan_estimate(importance)

            print(f"\n  {scenario['description']}")
            print(f"    Importance: {importance:.2f} ({tier})")
            print(f"    Est. lifespan: {lifespan.days} days")

    async def example_3_semantic_search(self):
        """Example 3: Semantic search across different topics."""
        print("\n" + "="*70)
        print("  EXAMPLE 3: Semantic Search Across Topics")
        print("="*70)

        # Add diverse memories
        diverse_memories = [
            {
                "text": "Python uses indentation to define code blocks, making it highly readable.",
                "domain": "Python",
            },
            {
                "text": "JavaScript is single-threaded but uses callbacks and promises for async operations.",
                "domain": "JavaScript",
            },
            {
                "text": "SQL SELECT statements retrieve data from databases using WHERE clauses for filtering.",
                "domain": "Databases",
            },
            {
                "text": "Docker containers package applications and dependencies for consistent deployment.",
                "domain": "DevOps",
            },
            {
                "text": "REST APIs use HTTP methods (GET, POST, PUT, DELETE) for resource operations.",
                "domain": "Web Services",
            },
        ]

        print("\nAdding diverse memories...")
        for mem in diverse_memories:
            await self.system.add_episode(
                narrative=mem["text"],
                event_type="technical",
                importance_signals=ImportanceSignals(
                    novelty=0.6,
                    task_success=1.0,
                    retrieval_frequency=0.0,
                    user_signal=0.8,
                    emotional_salience=0.2,
                ),
                metadata={"domains": [mem["domain"]]},
                session_id=self.session_id,
            )

        await asyncio.sleep(0.5)

        # Test semantic search
        queries = [
            "How do I write clean code?",
            "What asynchronous patterns exist?",
            "How do I manage deployments?",
            "What are API best practices?",
        ]

        print("\nPerforming semantic searches:")
        for query in queries:
            results = await self.system.retrieve(query, top_k=2)
            print(f"\n  Query: '{query}'")
            if results:
                print(f"  Found: {results[0].domains}")
            else:
                print("  No results")

    async def example_4_batch_operations(self):
        """Example 4: Demonstrate batch operations."""
        print("\n" + "="*70)
        print("  EXAMPLE 4: Batch Operations")
        print("="*70)

        # Create 20 test memories as batch
        episodes = [
            {
                "narrative": f"Test memory {i}: Learning topic {i}.",
                "event_type": "learning",
                "importance_signals": ImportanceSignals(
                    novelty=0.5 + (i % 5) * 0.1,
                    task_success=1.0,
                    retrieval_frequency=0.0,
                    user_signal=0.8,
                    emotional_salience=0.2,
                ),
                "metadata": {"domains": [f"Topic{i % 3}"], "keywords": [f"test{i}"]},
            }
            for i in range(20)
        ]

        print(f"\nAdding {len(episodes)} memories in batch...")

        import time

        start = time.time()
        memory_ids = await self.system.add_episodes_batch(
            episodes, self.session_id
        )
        elapsed = time.time() - start

        print(f"  ✓ Added {len(memory_ids)} memories in {elapsed:.2f}s")
        print(f"  ✓ Average: {elapsed/len(memory_ids)*1000:.0f}ms per memory")

    async def example_5_performance_analysis(self):
        """Example 5: Analyze system performance."""
        print("\n" + "="*70)
        print("  EXAMPLE 5: Performance Analysis")
        print("="*70)

        import time

        stats = await self.system.get_stats()

        print(f"\nSystem Statistics:")
        print(f"  Total memories: {stats.total_memories}")
        print(f"  Average importance: {stats.avg_importance:.2f}")
        print(f"  High importance: {stats.high_importance_count}")
        print(f"  Medium importance: {stats.medium_importance_count}")
        print(f"  Low importance: {stats.low_importance_count}")
        print(f"  Storage: {stats.storage_used_mb:.1f} MB")

        # Measure search performance
        print(f"\nSearch Performance (10 searches):")
        start = time.time()
        for i in range(10):
            await self.system.retrieve(f"query {i}", top_k=5)
        elapsed = time.time() - start

        print(f"  Time: {elapsed:.3f}s")
        print(f"  Average: {elapsed/10*1000:.1f}ms per search")

    async def example_6_update_workflow(self):
        """Example 6: Update and refine memories."""
        print("\n" + "="*70)
        print("  EXAMPLE 6: Update Workflow")
        print("="*70)

        # Add initial memory
        print("\nAdding initial memory...")
        memory_id = await self.system.add_episode(
            narrative="Initial understanding of the topic.",
            event_type="learning",
            importance_signals=ImportanceSignals(
                novelty=0.3,
                task_success=0.5,
                retrieval_frequency=0.0,
                user_signal=0.4,
                emotional_salience=0.1,
            ),
            session_id=self.session_id,
        )

        initial_mem = await self.system.retrieve_by_id(memory_id)
        if initial_mem:
            initial_importance = initial_mem.importance_score
            print(f"  Initial importance: {initial_importance:.2f}")

        # Update based on new information
        print("\nUpdating based on user confirmation...")
        await self.system.update_importance(
            memory_id,
            new_signals={
                "task_success": 1.0,  # User confirmed it worked
                "user_signal": 0.95,  # User gave positive feedback
            },
        )

        updated_mem = await self.system.retrieve_by_id(memory_id)
        if updated_mem:
            updated_importance = updated_mem.importance_score
            print(f"  Updated importance: {updated_importance:.2f}")
            print(
                f"  Improvement: {(updated_importance - initial_importance):.2f}"
            )

    async def run_all(self):
        """Run all examples."""
        print("\n")
        print("╔" + "="*68 + "╗")
        print("║" + " "*68 + "║")
        print(
            "║"
            + "  Advanced Examples - Real-World Usage Patterns".center(68)
            + "║"
        )
        print("║" + " "*68 + "║")
        print("╚" + "="*68 + "╝")

        try:
            await self.example_1_learning_session()
            await self.example_2_importance_hierarchy()
            await self.example_3_semantic_search()
            await self.example_4_batch_operations()
            await self.example_5_performance_analysis()
            await self.example_6_update_workflow()

            print("\n" + "="*70)
            print("  ✓ All examples completed successfully!")
            print("="*70)
            print("\nNext Steps:")
            print("  1. Try the CLI: python cli.py")
            print("  2. Run tests: pytest tests/ -v")
            print("  3. Read guide: EXECUTE_PHASE1.md")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback

            traceback.print_exc()


async def main():
    """Main entry point."""
    examples = AdvancedExamples()
    await examples.run_all()


if __name__ == "__main__":
    asyncio.run(main())
