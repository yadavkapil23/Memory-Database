"""Embedding generation with caching using OpenAI."""

import asyncio
import hashlib
import json
from typing import List, Optional

import redis
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import get_settings


class OpenAIEmbedder:
    """Generate embeddings using OpenAI API with Redis caching."""

    def __init__(self, cache_ttl: Optional[int] = None):
        """Initialize the embedder.

        Args:
            cache_ttl: Cache time-to-live in seconds. Uses config default if None.
        """
        settings = get_settings()
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.embedding_dim = settings.embedding_dimension
        self.cache_ttl = cache_ttl or settings.embedding_cache_ttl

        self.client = AsyncOpenAI(api_key=self.api_key)

        # Initialize Redis cache
        try:
            self.cache = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
            )
            # Test connection
            self.cache.ping()
            self.cache_enabled = True
        except Exception as e:
            print(f"Warning: Redis cache unavailable: {e}")
            self.cache = None
            self.cache_enabled = False

    def _get_cache_key(self, text: str) -> str:
        """Generate a cache key from text.

        Args:
            text: The text to cache.

        Returns:
            A cache key.
        """
        hash_value = hashlib.md5(text.encode()).hexdigest()
        return f"embedding:{hash_value}"

    def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache if available.

        Args:
            text: The text.

        Returns:
            Embedding if cached, None otherwise.
        """
        if not self.cache_enabled:
            return None

        try:
            cache_key = self._get_cache_key(text)
            cached = self.cache.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            print(f"Cache retrieval error: {e}")

        return None

    def _cache_embedding(self, text: str, embedding: List[float]) -> None:
        """Cache an embedding.

        Args:
            text: The text.
            embedding: The embedding vector.
        """
        if not self.cache_enabled:
            return

        try:
            cache_key = self._get_cache_key(text)
            self.cache.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(embedding),
            )
        except Exception as e:
            print(f"Cache write error: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _call_openai(self, text: str) -> List[float]:
        """Call OpenAI API to get embedding (with retries).

        Args:
            text: The text to embed.

        Returns:
            The embedding vector.
        """
        response = await self.client.embeddings.create(
            input=text,
            model=self.model,
        )
        return response.data[0].embedding

    async def embed(self, text: str) -> List[float]:
        """Get embedding for text (with caching).

        Args:
            text: The text to embed.

        Returns:
            The embedding vector.

        Raises:
            ValueError: If embedding fails after retries.
        """
        # Check cache first
        cached = self._get_cached_embedding(text)
        if cached is not None:
            return cached

        # Call OpenAI
        try:
            embedding = await self._call_openai(text)

            # Verify dimension
            if len(embedding) != self.embedding_dim:
                print(
                    f"Warning: Expected {self.embedding_dim} dims, "
                    f"got {len(embedding)}"
                )

            # Cache it
            self._cache_embedding(text, embedding)

            return embedding

        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {e}")

    async def embed_batch(
        self, texts: List[str], batch_size: int = 10
    ) -> List[List[float]]:
        """Get embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed.
            batch_size: How many to embed in parallel.

        Returns:
            List of embedding vectors.
        """
        embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            # Try cache first for each
            batch_results = []
            remaining_texts = []
            remaining_indices = []

            for j, text in enumerate(batch):
                cached = self._get_cached_embedding(text)
                if cached is not None:
                    batch_results.append(cached)
                else:
                    remaining_texts.append(text)
                    remaining_indices.append(j)

            # Get uncached embeddings from OpenAI
            if remaining_texts:
                try:
                    response = await self.client.embeddings.create(
                        input=remaining_texts,
                        model=self.model,
                    )

                    # Match responses to original positions
                    new_results = [None] * len(batch)
                    for idx, embedding_obj in enumerate(response.data):
                        text = remaining_texts[idx]
                        embedding = embedding_obj.embedding
                        self._cache_embedding(text, embedding)
                        new_results[remaining_indices[idx]] = embedding

                    # Merge results
                    result_idx = 0
                    for j in range(len(batch)):
                        if remaining_indices and j == remaining_indices[
                            0
                        ]:
                            result_idx = remaining_indices.pop(0)
                            batch_results.append(new_results[j])
                        # This logic could be simplified

                    # Simpler approach: reconstruct
                    final_batch = []
                    uncached_idx = 0
                    for j, text in enumerate(batch):
                        cached = self._get_cached_embedding(text)
                        if cached:
                            final_batch.append(cached)
                        else:
                            final_batch.append(new_results[j])
                    batch_results = final_batch

                except Exception as e:
                    print(f"Batch embedding error: {e}")
                    # Return what we have
                    pass

            embeddings.extend(batch_results)

        return embeddings

    async def clear_cache(self) -> None:
        """Clear the embedding cache."""
        if not self.cache_enabled:
            return

        try:
            # Delete all embedding keys
            keys = self.cache.keys("embedding:*")
            if keys:
                self.cache.delete(*keys)
                print(f"Cleared {len(keys)} cached embeddings")
        except Exception as e:
            print(f"Cache clear error: {e}")

    async def get_cache_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats.
        """
        if not self.cache_enabled:
            return {"cache_enabled": False}

        try:
            keys = self.cache.keys("embedding:*")
            return {
                "cache_enabled": True,
                "cached_embeddings": len(keys),
                "cache_size_bytes": sum(
                    len(self.cache.get(k).encode())
                    for k in keys
                ),
            }
        except Exception as e:
            print(f"Stats error: {e}")
            return {"cache_enabled": False, "error": str(e)}
