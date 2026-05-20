#!/usr/bin/env python3
"""
Comprehensive Phase 1 validation test.
Run this after setup to verify everything works.

Usage: python test_phase1.py
"""

import asyncio
import sys
import time
from datetime import datetime
from uuid import uuid4

from src.memory_system import MemorySystem
from src.models import ImportanceSignals


class TestRunner:
    """Run comprehensive Phase 1 tests."""

    def __init__(self):
        """Initialize test runner."""
        self.system = MemorySystem()
        self.session_id = uuid4()
        self.passed = 0
        self.failed = 0
        self.start_time = time.time()

    def print_header(self, text: str) -> None:
        """Print formatted header."""
        print("\n" + "="*70)
        print(f"  {text}")
        print("="*70)

    def print_test(self, name: str, result: bool, details: str = "") -> None:
        """Print test result."""
        symbol = "✓" if result else "✗"
        status = "PASS" if result else "FAIL"
        color = "\033[92m" if result else "\033[91m"  # Green or Red
        reset = "\033[0m"

        if result:
            self.passed += 1
        else:
            self.failed += 1

        print(f"  {color}[{symbol}]{reset} {name:<50} {status}")

        if details:
            print(f"      {details}")

    async def test_health_check(self) -> None:
        """Test system health check."""
        self.print_header("Health Check")

        try:
            health = await self.system.health_check()

            vector_db = health.get("vector_db", False)
            embedder = health.get("embedder", False)

            self.print_test("Vector DB online", vector_db)
            self.print_test("Embedder online", embedder)

        except Exception as e:
            self.print_test("Health check", False, str(e))

    async def test_add_single_memory(self) -> None:
        """Test adding a single memory."""
        self.print_header("Add Single Memory")

        try:
            memory_id = await self.system.add_episode(
                narrative="Python is a great programming language.",
                event_type="conversation",
                importance_signals=ImportanceSignals(
                    novelty=0.6,
                    task_success=1.0,
                    retrieval_frequency=0.0,
                    user_signal=0.9,
                    emotional_salience=0.2,
                ),
                metadata={"domains": ["Python"], "keywords": ["programming"]},
                session_id=self.session_id,
            )

            self.print_test(
                "Add memory",
                memory_id is not None,
                f"ID: {memory_id}",
            )

            # Store for later tests
            self.test_memory_id = memory_id

        except Exception as e:
            self.print_test("Add memory", False, str(e))

    async def test_search_memory(self) -> None:
        """Test searching for memories."""
        self.print_header("Search Memories")

        try:
            # Give DB time to index
            await asyncio.sleep(0.5)

            results = await self.system.retrieve(
                query="Python programming language",
                top_k=5,
            )

            self.print_test(
                "Search memories",
                len(results) > 0,
                f"Found {len(results)} memories",
            )

            if results:
                first = results[0]
                self.print_test(
                    "Result has content",
                    len(first.compressed_narrative) > 0,
                    f"Narrative: {first.compressed_narrative[:50]}...",
                )

                self.print_test(
                    "Result has importance",
                    0.0 <= first.importance_score <= 1.0,
                    f"Score: {first.importance_score:.2f}",
                )

        except Exception as e:
            self.print_test("Search memories", False, str(e))

    async def test_batch_add(self) -> None:
        """Test batch adding memories."""
        self.print_header("Batch Add Memories")

        try:
            episodes = [
                {
                    "narrative": f"Test memory {i}.",
                    "event_type": "conversation",
                    "importance_signals": ImportanceSignals(
                        novelty=0.5,
                        task_success=1.0,
                        retrieval_frequency=0.0,
                        user_signal=0.8,
                        emotional_salience=0.1,
                    ),
                    "metadata": {"domains": ["Test"]},
                }
                for i in range(5)
            ]

            start = time.time()
            memory_ids = await self.system.add_episodes_batch(
                episodes,
                self.session_id,
            )
            elapsed = time.time() - start

            self.print_test(
                "Batch add 5 memories",
                len(memory_ids) == 5,
                f"Time: {elapsed:.2f}s",
            )

            self.print_test(
                "All unique IDs",
                len(set(memory_ids)) == 5,
                "No duplicates",
            )

        except Exception as e:
            self.print_test("Batch add", False, str(e))

    async def test_importance_scoring(self) -> None:
        """Test importance scoring."""
        self.print_header("Importance Scoring")

        try:
            # High importance
            high_id = await self.system.add_episode(
                narrative="Critical insight!",
                event_type="conversation",
                importance_signals=ImportanceSignals(
                    novelty=1.0,
                    task_success=1.0,
                    retrieval_frequency=0.5,
                    user_signal=1.0,
                    emotional_salience=0.8,
                ),
                session_id=self.session_id,
            )

            # Low importance
            low_id = await self.system.add_episode(
                narrative="Random thought.",
                event_type="conversation",
                importance_signals=ImportanceSignals(
                    novelty=0.0,
                    task_success=0.0,
                    retrieval_frequency=0.0,
                    user_signal=0.0,
                    emotional_salience=0.0,
                ),
                session_id=self.session_id,
            )

            high_mem = await self.system.retrieve_by_id(high_id)
            low_mem = await self.system.retrieve_by_id(low_id)

            high_score = high_mem.importance_score if high_mem else 0
            low_score = low_mem.importance_score if low_mem else 0

            self.print_test(
                "High importance memory",
                high_mem is not None,
                f"Score: {high_score:.2f}",
            )

            self.print_test(
                "Low importance memory",
                low_mem is not None,
                f"Score: {low_score:.2f}",
            )

            self.print_test(
                "Correct scoring",
                high_score > low_score,
                f"High > Low: {high_score:.2f} > {low_score:.2f}",
            )

        except Exception as e:
            self.print_test("Importance scoring", False, str(e))

    async def test_stats(self) -> None:
        """Test getting statistics."""
        self.print_header("System Statistics")

        try:
            stats = await self.system.get_stats()

            self.print_test(
                "Get stats",
                stats is not None,
                f"Total: {stats.total_memories}",
            )

            self.print_test(
                "Stat values valid",
                stats.total_memories >= 0
                and 0 <= stats.avg_importance <= 1.0,
                f"Avg: {stats.avg_importance:.2f}",
            )

        except Exception as e:
            self.print_test("Get stats", False, str(e))

    async def test_embedding_cache(self) -> None:
        """Test embedding caching."""
        self.print_header("Embedding Cache")

        try:
            # First call (uncached)
            start1 = time.time()
            await self.system.add_episode(
                narrative="This is a test for caching.",
                event_type="test",
                importance_signals=ImportanceSignals(0.5, 1.0, 0, 0.8, 0.1),
                session_id=self.session_id,
            )
            time1 = time.time() - start1

            # Second call (should be cached)
            start2 = time.time()
            await self.system.add_episode(
                narrative="This is a test for caching.",  # Exact same
                event_type="test",
                importance_signals=ImportanceSignals(0.5, 1.0, 0, 0.8, 0.1),
                session_id=self.session_id,
            )
            time2 = time.time() - start2

            cache_speedup = time1 / time2 if time2 > 0 else 0

            self.print_test(
                "Cache speedup detected",
                cache_speedup > 1.5,
                f"First: {time1:.3f}s, Second: {time2:.3f}s ({cache_speedup:.1f}x faster)",
            )

        except Exception as e:
            self.print_test("Embedding cache", False, str(e))

    async def test_performance(self) -> None:
        """Test performance benchmarks."""
        self.print_header("Performance Benchmarks")

        try:
            # Single add performance
            start = time.time()
            for i in range(5):
                await self.system.add_episode(
                    narrative=f"Performance test {i}.",
                    event_type="test",
                    importance_signals=ImportanceSignals(0.5, 1.0, 0, 0.8, 0.1),
                    session_id=self.session_id,
                )
            elapsed = time.time() - start
            avg_time = elapsed / 5

            self.print_test(
                "Single add speed",
                avg_time < 1.0,  # Should be <1s including API overhead
                f"Avg: {avg_time:.3f}s",
            )

            # Search performance
            await asyncio.sleep(0.5)  # Give DB time to index

            start = time.time()
            for i in range(5):
                await self.system.retrieve(
                    query=f"test {i}",
                    top_k=5,
                )
            elapsed = time.time() - start
            avg_time = elapsed / 5

            self.print_test(
                "Search speed",
                avg_time < 0.2,  # Should be <200ms
                f"Avg: {avg_time*1000:.1f}ms",
            )

        except Exception as e:
            self.print_test("Performance", False, str(e))

    async def run_all_tests(self) -> None:
        """Run all tests."""
        print("\n")
        print("╔" + "="*68 + "╗")
        print("║" + " "*68 + "║")
        print(
            "║"
            + "  Episodic Memory System - Phase 1 Validation Tests".center(68)
            + "║"
        )
        print("║" + " "*68 + "║")
        print("╚" + "="*68 + "╝")

        # Run tests
        await self.test_health_check()
        await self.test_add_single_memory()
        await self.test_search_memory()
        await self.test_batch_add()
        await self.test_importance_scoring()
        await self.test_stats()
        await self.test_embedding_cache()
        await self.test_performance()

        # Summary
        self.print_header("Test Summary")

        total = self.passed + self.failed
        elapsed = time.time() - self.start_time

        print(f"\n  Passed: {self.passed}/{total}")
        print(f"  Failed: {self.failed}/{total}")
        print(f"  Time: {elapsed:.1f}s")

        if self.failed == 0:
            print("\n  ✓ ALL TESTS PASSED! Phase 1 ready for development.")
            print("  → Next: Follow WEEK1_GUIDE.md")
            return 0
        else:
            print(
                f"\n  ✗ {self.failed} test(s) failed. Check errors above."
            )
            print("  → Fix issues and run again")
            return 1


async def main():
    """Main entry point."""
    runner = TestRunner()
    exit_code = await runner.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
