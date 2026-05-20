#!/usr/bin/env python3
"""
Interactive CLI for testing the episodic memory system.
Run: python cli.py
"""

import asyncio
import sys
import os
from typing import Optional
from uuid import uuid4
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.memory_system import MemorySystem
from src.models import ImportanceSignals
from src.utils import (
    MemoryStats,
    print_memory_summary,
    truncate_text,
    calculate_importance_tier,
)


class MemoryCLI:
    """Interactive CLI for memory system."""

    def __init__(self):
        """Initialize CLI."""
        self.system = MemorySystem()
        self.session_id = uuid4()
        self.memories_added = 0

    async def add_memory(self) -> bool:
        """Add a new memory interactively."""
        print("\n" + "="*60)
        print("ADD MEMORY")
        print("="*60)

        try:
            # Get narrative
            print("\nEnter memory narrative (what happened?):")
            narrative = input("> ").strip()

            if not narrative:
                print("✗ Narrative cannot be empty")
                return False

            # Get event type
            print("\nEvent type (conversation/error/milestone/interaction)?")
            event_type = input("> ").strip().lower()

            if event_type not in [
                "conversation",
                "error",
                "milestone",
                "interaction",
            ]:
                event_type = "conversation"
                print(f"Using default: {event_type}")

            # Get importance signals
            print("\nRate these signals (0.0 to 1.0):")

            def get_signal(name: str, default: float = 0.5) -> float:
                while True:
                    try:
                        val = float(input(f"  {name} [{default}]: ") or default)
                        if 0.0 <= val <= 1.0:
                            return val
                        print("  ✗ Must be 0.0 to 1.0")
                    except ValueError:
                        print("  ✗ Invalid number")

            novelty = get_signal("Novelty (new idea?)", 0.5)
            task_success = get_signal("Task Success (did it work?)", 1.0)
            retrieval_freq = get_signal("Retrieval Frequency (accessed often?)", 0.0)
            user_signal = get_signal("User Signal (explicit rating?)", 0.8)
            emotional = get_signal("Emotional Salience (memorable?)", 0.2)

            # Get metadata
            print("\nMetadata (domains, entities, keywords):")
            domains_str = input("  Domains (comma-separated) [Python]: ").strip()
            domains = (
                [d.strip() for d in domains_str.split(",")]
                if domains_str
                else ["Python"]
            )

            keywords_str = input("  Keywords (comma-separated) []: ").strip()
            keywords = (
                [k.strip() for k in keywords_str.split(",")]
                if keywords_str
                else []
            )

            # Add memory
            print("\nAdding memory...", end=" ", flush=True)

            memory_id = await self.system.add_episode(
                narrative=narrative,
                event_type=event_type,
                importance_signals=ImportanceSignals(
                    novelty=novelty,
                    task_success=task_success,
                    retrieval_frequency=retrieval_freq,
                    user_signal=user_signal,
                    emotional_salience=emotional,
                ),
                metadata={
                    "domains": domains,
                    "keywords": keywords,
                },
                session_id=self.session_id,
            )

            self.memories_added += 1

            importance = (
                0.20 * novelty
                + 0.30 * task_success
                + 0.25 * retrieval_freq
                + 0.15 * user_signal
                + 0.10 * emotional
            )
            tier = calculate_importance_tier(importance)

            print(f"✓\n")
            print(f"Memory ID: {memory_id}")
            print(f"Importance: {importance:.2f} ({tier})")
            print(f"Stored in: Qdrant Vector DB")

            return True

        except KeyboardInterrupt:
            print("\n✗ Cancelled")
            return False
        except Exception as e:
            print(f"\n✗ Error: {e}")
            return False

    async def search_memories(self) -> bool:
        """Search for memories."""
        print("\n" + "="*60)
        print("SEARCH MEMORIES")
        print("="*60)

        try:
            print("\nEnter search query:")
            query = input("> ").strip()

            if not query:
                print("✗ Query cannot be empty")
                return False

            print(f"\nSearching for: '{query}'...", end=" ", flush=True)

            results = await self.system.retrieve(query=query, top_k=5)

            print(f"✓ ({len(results)} found)\n")

            if results:
                for i, memory in enumerate(results, 1):
                    print(f"\nResult {i}:")
                    print(print_memory_summary(memory))
            else:
                print("No memories found. Try adding some first!")

            return True

        except KeyboardInterrupt:
            print("\n✗ Cancelled")
            return False
        except Exception as e:
            print(f"\n✗ Error: {e}")
            return False

    async def show_stats(self) -> bool:
        """Show system statistics."""
        print("\n" + "="*60)
        print("SYSTEM STATISTICS")
        print("="*60)

        try:
            stats = await self.system.get_stats()

            print(f"\nTotal Memories: {stats.total_memories}")
            print(f"High Importance (>0.7): {stats.high_importance_count}")
            print(f"Medium (0.4-0.7): {stats.medium_importance_count}")
            print(f"Low (<0.4): {stats.low_importance_count}")
            print(f"Average Importance: {stats.avg_importance:.2f}")
            print(f"Embeddings Cached: {stats.total_embeddings_cached}")
            print(f"Storage Used: {stats.storage_used_mb:.1f} MB")

            print(f"\nMemories Added (This Session): {self.memories_added}")
            print(f"Session ID: {self.session_id}")

            return True

        except Exception as e:
            print(f"\n✗ Error: {e}")
            return False

    async def health_check(self) -> bool:
        """Check system health."""
        print("\n" + "="*60)
        print("SYSTEM HEALTH CHECK")
        print("="*60)

        try:
            health = await self.system.health_check()

            print("\nComponents:")
            for component, status in health.items():
                symbol = "✓" if status else "✗"
                print(f"  {symbol} {component.replace('_', ' ').title()}")

            all_ok = all(health.values())
            if all_ok:
                print("\n✓ All systems operational!")
            else:
                print("\n✗ Some components down. Check SETUP.md")

            return all_ok

        except Exception as e:
            print(f"\n✗ Error: {e}")
            return False

    async def interactive_loop(self) -> None:
        """Run interactive command loop."""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*58 + "║")
        print(
            "║"
            + "  Episodic AI Memory System - Interactive CLI".center(58)
            + "║"
        )
        print("║" + " "*58 + "║")
        print("╚" + "="*58 + "╝")

        # Initial health check
        await self.health_check()

        while True:
            print("\n" + "-"*60)
            print("COMMANDS:")
            print("  1. add    - Add a new memory")
            print("  2. search - Search for memories")
            print("  3. stats  - Show statistics")
            print("  4. health - Check system health")
            print("  5. help   - Show help")
            print("  6. quit   - Exit")
            print("-"*60)

            cmd = input("\nCommand > ").strip().lower()

            if cmd in ["1", "add"]:
                await self.add_memory()

            elif cmd in ["2", "search"]:
                await self.search_memories()

            elif cmd in ["3", "stats"]:
                await self.show_stats()

            elif cmd in ["4", "health"]:
                await self.health_check()

            elif cmd in ["5", "help"]:
                self.show_help()

            elif cmd in ["6", "quit", "exit"]:
                print("\n✓ Goodbye!")
                break

            else:
                print("✗ Unknown command. Type 'help' for commands.")

    def show_help(self) -> None:
        """Show help information."""
        print("\n" + "="*60)
        print("HELP")
        print("="*60)

        help_text = """
COMMANDS:
  add      Add a new memory to the system
  search   Search for memories by query
  stats    View system statistics
  health   Check if services are running
  help     Show this help message
  quit     Exit the CLI

WORKFLOW:
  1. Use 'add' to store memories (conversations, events, etc.)
  2. Use 'search' to find relevant memories
  3. Use 'stats' to see what's stored
  4. Use 'health' if something isn't working

IMPORTANCE SIGNALS (0.0-1.0):
  Novelty: How new/unique is this idea?
  Task Success: Did it help complete a task?
  Retrieval Frequency: How often is it accessed?
  User Signal: Did the user explicitly rate it?
  Emotional Salience: How memorable is it?

IMPORTANCE TIERS:
  HIGH (≥0.7): Keep long-term, high priority
  MEDIUM (0.4-0.7): Store compressed, medium priority
  LOW (<0.4): Extract patterns only, fade quickly

TIPS:
  • Start by adding a few test memories
  • Search using natural language queries
  • Check stats to see what's working
  • Use health check if services are slow

MORE INFO:
  → See SETUP.md for installation issues
  → See WEEK1_GUIDE.md for next steps
  → See 01_EPISODIC_MEMORY_TECHNICAL_DESIGN.md for details
        """

        print(help_text)

    async def run(self) -> None:
        """Run the CLI."""
        try:
            await self.interactive_loop()
        except KeyboardInterrupt:
            print("\n\n✓ Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n✗ Fatal error: {e}")
            sys.exit(1)


async def main():
    """Main entry point."""
    cli = MemoryCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
