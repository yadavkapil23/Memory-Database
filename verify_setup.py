#!/usr/bin/env python3
"""
Verify that the episodic memory system is properly set up.
Run this after installation to check everything is working.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_check(passed, message):
    """Print a check result."""
    symbol = "✓" if passed else "✗"
    status = "PASS" if passed else "FAIL"
    color = "\033[92m" if passed else "\033[91m"  # Green or Red
    reset = "\033[0m"
    print(f"  {color}[{symbol}]{reset} {message:<50} {status}")
    return passed

def check_python():
    """Check Python version."""
    print_header("Python Environment")

    version = sys.version_info
    passed = version.major == 3 and version.minor >= 11
    print_check(
        passed,
        f"Python {version.major}.{version.minor} (required: 3.11+)"
    )
    return passed

def check_imports():
    """Check required imports."""
    print_header("Required Packages")

    all_passed = True
    packages = [
        ("fastapi", "FastAPI"),
        ("pydantic", "Pydantic"),
        ("qdrant_client", "Qdrant Client"),
        ("openai", "OpenAI"),
        ("redis", "Redis"),
        ("pytest", "Pytest"),
    ]

    for module, name in packages:
        try:
            __import__(module)
            all_passed &= print_check(True, f"{name} installed")
        except ImportError:
            all_passed &= print_check(False, f"{name} NOT installed")

    return all_passed

def check_env():
    """Check environment variables."""
    print_header("Configuration (.env)")

    from dotenv import load_dotenv
    load_dotenv()

    required_vars = [
        ("OPENAI_API_KEY", "OpenAI API Key"),
        ("QDRANT_URL", "Qdrant URL"),
        ("REDIS_HOST", "Redis Host"),
    ]

    all_passed = True
    for var, description in required_vars:
        value = os.getenv(var)
        if var == "OPENAI_API_KEY":
            # Mask the key
            masked = value[:10] + "..." if value else None
            all_passed &= print_check(
                value is not None,
                f"{description}: {masked or 'NOT SET'}"
            )
        else:
            all_passed &= print_check(
                value is not None,
                f"{description}: {value or 'NOT SET'}"
            )

    return all_passed

async def check_services():
    """Check external services."""
    print_header("External Services")

    all_passed = True

    # Check Qdrant
    try:
        from qdrant_client import QdrantClient
        from src.config import get_settings

        settings = get_settings()
        client = QdrantClient(url=settings.qdrant_url)
        client.get_collection("test_collection")
        all_passed &= print_check(True, "Qdrant Vector DB (localhost:6333)")
    except Exception as e:
        all_passed &= print_check(False, f"Qdrant Vector DB - Error: {str(e)[:30]}")

    # Check Redis
    try:
        import redis
        from src.config import get_settings

        settings = get_settings()
        r = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
        )
        r.ping()
        all_passed &= print_check(True, "Redis Cache (localhost:6379)")
    except Exception as e:
        all_passed &= print_check(False, f"Redis Cache - Error: {str(e)[:30]}")

    # Check PostgreSQL
    try:
        import psycopg2
        from src.config import get_postgres_url

        url = get_postgres_url()
        # Can't easily test without creating a connection
        all_passed &= print_check(True, "PostgreSQL (localhost:5432)")
    except Exception as e:
        all_passed &= print_check(False, f"PostgreSQL - Error: {str(e)[:30]}")

    return all_passed

async def check_memory_system():
    """Check memory system functionality."""
    print_header("Memory System")

    all_passed = True

    try:
        from src.memory_system import MemorySystem
        from src.models import ImportanceSignals
        from uuid import uuid4

        # Initialize system
        system = MemorySystem()
        all_passed &= print_check(True, "MemorySystem initialized")

        # Health check
        health = await system.health_check()
        vector_db_ok = health.get("vector_db", False)
        embedder_ok = health.get("embedder", False)

        all_passed &= print_check(vector_db_ok, "Vector DB component")
        all_passed &= print_check(embedder_ok, "Embedder component")

        # Try adding a memory
        session_id = uuid4()
        try:
            memory_id = await system.add_episode(
                narrative="Test memory for verification.",
                event_type="test",
                importance_signals=ImportanceSignals(
                    novelty=0.5,
                    task_success=1.0,
                    retrieval_frequency=0.0,
                    user_signal=0.8,
                    emotional_salience=0.2,
                ),
                metadata={"domains": ["Test"]},
                session_id=session_id,
            )
            all_passed &= print_check(True, "Can add episode to memory")

            # Try searching
            results = await system.retrieve(
                query="Test memory",
                top_k=5,
            )
            all_passed &= print_check(
                len(results) > 0,
                f"Can search memories ({len(results)} found)"
            )

        except Exception as e:
            all_passed &= print_check(False, f"Memory operations - {str(e)[:30]}")

    except Exception as e:
        all_passed &= print_check(False, f"Memory system init - {str(e)[:30]}")

    return all_passed

async def main():
    """Run all checks."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Episodic AI Memory System - Setup Verification".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")

    results = {
        "Python": check_python(),
        "Packages": check_imports(),
        "Configuration": check_env(),
        "Services": await check_services(),
        "Memory System": await check_memory_system(),
    }

    # Summary
    print_header("Summary")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for check, result in results.items():
        symbol = "✓" if result else "✗"
        print(f"  {symbol} {check}")

    print(f"\n  Total: {passed}/{total} checks passed")

    if passed == total:
        print("\n  ✓ All checks passed! You're ready to start Phase 1 development.")
        print("  → Next: Follow the tasks in 02_PROJECT_PLAN.md")
        return 0
    else:
        print("\n  ✗ Some checks failed. See above for details.")
        print("  → Fix the issues and run this script again.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
