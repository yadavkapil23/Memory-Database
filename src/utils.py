"""Utility functions for the memory system."""

import asyncio
import time
from typing import List, Callable, Any, TypeVar, Coroutine
from functools import wraps
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T')


def async_timer(func: Callable) -> Callable:
    """Decorator to measure async function execution time."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start
            logger.debug(f"{func.__name__} took {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
            raise
    return wrapper


def sync_timer(func: Callable) -> Callable:
    """Decorator to measure sync function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.debug(f"{func.__name__} took {elapsed:.3f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
            raise
    return wrapper


async def retry_async(
    func: Callable[..., Coroutine],
    max_retries: int = 3,
    backoff: float = 1.0,
    *args,
    **kwargs
) -> Any:
    """Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        backoff: Backoff multiplier
        *args: Arguments for function
        **kwargs: Keyword arguments for function

    Returns:
        Result of function call

    Raises:
        Exception: If all retries fail
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                wait_time = backoff ** attempt
                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}"
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"All {max_retries} attempts failed")

    raise last_exception


def calculate_importance_tier(importance_score: float) -> str:
    """Get importance tier from score.

    Args:
        importance_score: Score between 0.0 and 1.0

    Returns:
        Tier name (HIGH, MEDIUM, LOW)
    """
    if importance_score >= 0.7:
        return "HIGH"
    elif importance_score >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"


def format_timestamp(dt: datetime) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime object

    Returns:
        Formatted string (e.g., "May 20, 2:30 PM")
    """
    return dt.strftime("%b %d, %I:%M %p")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text


def estimate_tokens(text: str) -> int:
    """Rough estimate of token count (OpenAI encoding).

    Args:
        text: Text to estimate

    Returns:
        Approximate token count
    """
    # Rough approximation: ~1 token per 4 characters
    return len(text) // 4


async def batch_process(
    items: List[T],
    process_func: Callable[[T], Coroutine],
    batch_size: int = 10,
) -> List[Any]:
    """Process items in batches asynchronously.

    Args:
        items: Items to process
        process_func: Async function to apply
        batch_size: Batch size

    Returns:
        List of results
    """
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        batch_results = await asyncio.gather(
            *[process_func(item) for item in batch]
        )
        results.extend(batch_results)

    return results


def get_memory_lifespan_estimate(
    importance_score: float,
    lambda_values: dict = None,
) -> timedelta:
    """Estimate memory lifespan based on importance.

    Args:
        importance_score: Importance score (0-1)
        lambda_values: Custom decay constants

    Returns:
        Estimated lifespan as timedelta
    """
    if lambda_values is None:
        # Default decay constants
        if importance_score >= 0.7:
            lambda_val = 0.1
        elif importance_score >= 0.4:
            lambda_val = 0.5
        else:
            lambda_val = 1.5
    else:
        # Use provided values
        if importance_score >= 0.7:
            lambda_val = lambda_values.get("high", 0.1)
        elif importance_score >= 0.4:
            lambda_val = lambda_values.get("medium", 0.5)
        else:
            lambda_val = lambda_values.get("low", 1.5)

    # Estimate days until deletion threshold (0.05)
    # S(t) = e^(-λt / stability) = 0.05
    # t = -ln(0.05) * stability / λ
    import math

    days = -math.log(0.05) * importance_score / lambda_val

    return timedelta(days=days)


def print_memory_summary(memory) -> str:
    """Create a formatted summary of a memory.

    Args:
        memory: EpisodicMemory object

    Returns:
        Formatted string
    """
    tier = calculate_importance_tier(memory.importance_score)
    text = truncate_text(memory.compressed_narrative, 80)
    timestamp = format_timestamp(memory.timestamp)

    return (
        f"[{tier}] {timestamp}\n"
        f"  Score: {memory.importance_score:.2f}\n"
        f"  Text: {text}\n"
        f"  Domains: {', '.join(memory.domains) or 'None'}\n"
        f"  Accessed: {memory.access_count}x"
    )


class MemoryStats:
    """Utility class for memory statistics."""

    @staticmethod
    def calculate_avg_importance(memories: List[Any]) -> float:
        """Calculate average importance score.

        Args:
            memories: List of memories

        Returns:
            Average score
        """
        if not memories:
            return 0.0
        return sum(m.importance_score for m in memories) / len(memories)

    @staticmethod
    def count_by_tier(memories: List[Any]) -> dict:
        """Count memories by importance tier.

        Args:
            memories: List of memories

        Returns:
            Counts by tier
        """
        high = sum(1 for m in memories if m.importance_score >= 0.7)
        medium = sum(
            1 for m in memories if 0.4 <= m.importance_score < 0.7
        )
        low = sum(1 for m in memories if m.importance_score < 0.4)

        return {
            "HIGH": high,
            "MEDIUM": medium,
            "LOW": low,
            "TOTAL": len(memories),
        }

    @staticmethod
    def get_most_accessed(memories: List[Any], top_k: int = 5) -> List[Any]:
        """Get most frequently accessed memories.

        Args:
            memories: List of memories
            top_k: Number to return

        Returns:
            Top accessed memories
        """
        return sorted(
            memories,
            key=lambda m: m.access_count,
            reverse=True,
        )[:top_k]

    @staticmethod
    def get_oldest(memories: List[Any], top_k: int = 5) -> List[Any]:
        """Get oldest memories.

        Args:
            memories: List of memories
            top_k: Number to return

        Returns:
            Oldest memories
        """
        return sorted(
            memories,
            key=lambda m: m.created_at,
        )[:top_k]

    @staticmethod
    def get_newest(memories: List[Any], top_k: int = 5) -> List[Any]:
        """Get newest memories.

        Args:
            memories: List of memories
            top_k: Number to return

        Returns:
            Newest memories
        """
        return sorted(
            memories,
            key=lambda m: m.created_at,
            reverse=True,
        )[:top_k]
