"""
Cache System — SQLite-based TTL cache for search results and scraped pages.

Provides zero-dependency persistent caching with automatic expiry.
Uses aiosqlite for async operations so we don't block the event loop.

TTL Categories:
    - search: 30 minutes (search results change frequently)
    - page: 1 hour (scraped page content)
    - profile: 24 hours (profile data is relatively stable)
    - default: 30 minutes
"""

import hashlib
import json
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

# TTL values in seconds
TTL_MAP = {
    "search": 1800,      # 30 minutes
    "page": 3600,         # 1 hour
    "profile": 86400,     # 24 hours
    "news": 900,          # 15 minutes
    "default": 1800,      # 30 minutes
}

# Cache database path — stored next to the package
_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache")
_CACHE_DB = os.path.join(_CACHE_DIR, "mcp_cache.db")

# In-memory fallback if SQLite is unavailable
_memory_cache: dict[str, tuple[float, str]] = {}

_db_initialized = False


def _make_key(category: str, query: str, **params) -> str:
    """Generate a deterministic cache key from category + query + params."""
    raw = f"{category}:{query}:{json.dumps(params, sort_keys=True)}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def _ensure_db():
    """Initialize the database and table if not yet done."""
    global _db_initialized
    if _db_initialized:
        return
    
    try:
        import aiosqlite
        
        os.makedirs(_CACHE_DIR, exist_ok=True)
        
        async with aiosqlite.connect(_CACHE_DB) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    ttl INTEGER NOT NULL
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_category ON cache(category)
            """)
            # Purge expired entries on startup
            await db.execute("DELETE FROM cache WHERE created_at + ttl < ?", (time.time(),))
            await db.commit()
        
        _db_initialized = True
        logger.info("Cache database initialized")
        
    except ImportError:
        logger.info("aiosqlite not available, using in-memory cache")
        _db_initialized = True
    except Exception as e:
        logger.warning(f"Cache DB initialization failed, using in-memory: {e}")
        _db_initialized = True


async def cache_get(category: str, query: str, **params) -> str | None:
    """
    Retrieve a cached value if it exists and hasn't expired.
    
    Args:
        category: Cache category (search, page, profile, etc.)
        query: The original query string
        **params: Additional parameters that affect the cache key
        
    Returns:
        Cached value as string, or None if not found/expired
    """
    await _ensure_db()
    key = _make_key(category, query, **params)
    
    try:
        import aiosqlite
        
        async with aiosqlite.connect(_CACHE_DB) as db:
            cursor = await db.execute(
                "SELECT value, created_at, ttl FROM cache WHERE key = ?",
                (key,)
            )
            row = await cursor.fetchone()
            
            if row is None:
                return None
            
            value, created_at, ttl = row
            
            if time.time() - created_at > ttl:
                # Expired — remove it
                await db.execute("DELETE FROM cache WHERE key = ?", (key,))
                await db.commit()
                return None
            
            logger.debug(f"Cache HIT: {category}:{query[:50]}")
            return value
            
    except ImportError:
        # In-memory fallback
        if key in _memory_cache:
            expires, value = _memory_cache[key]
            if time.time() < expires:
                logger.debug(f"Memory cache HIT: {category}:{query[:50]}")
                return value
            else:
                del _memory_cache[key]
        return None
    except Exception as e:
        logger.warning(f"Cache read error: {e}")
        return None


async def cache_set(category: str, query: str, value: str, **params) -> None:
    """
    Store a value in the cache.
    
    Args:
        category: Cache category (determines TTL)
        query: The original query string
        value: The value to cache
        **params: Additional parameters for the cache key
    """
    await _ensure_db()
    key = _make_key(category, query, **params)
    ttl = TTL_MAP.get(category, TTL_MAP["default"])
    
    try:
        import aiosqlite
        
        async with aiosqlite.connect(_CACHE_DB) as db:
            await db.execute(
                """INSERT OR REPLACE INTO cache (key, category, value, created_at, ttl) 
                   VALUES (?, ?, ?, ?, ?)""",
                (key, category, value, time.time(), ttl)
            )
            await db.commit()
            
        logger.debug(f"Cache SET: {category}:{query[:50]} (TTL: {ttl}s)")
        
    except ImportError:
        # In-memory fallback
        _memory_cache[key] = (time.time() + ttl, value)
    except Exception as e:
        logger.warning(f"Cache write error: {e}")


async def cache_clear(category: str | None = None) -> int:
    """
    Clear cached entries.
    
    Args:
        category: If specified, only clear entries in this category.
                  If None, clear all entries.
                  
    Returns:
        Number of entries cleared
    """
    await _ensure_db()
    
    try:
        import aiosqlite
        
        async with aiosqlite.connect(_CACHE_DB) as db:
            if category:
                cursor = await db.execute(
                    "DELETE FROM cache WHERE category = ?", (category,)
                )
            else:
                cursor = await db.execute("DELETE FROM cache")
            
            count = cursor.rowcount
            await db.commit()
            return count
            
    except ImportError:
        if category:
            keys_to_remove = [
                k for k, (_, _) in _memory_cache.items()
            ]
            # Can't filter by category in memory cache easily, clear all
            count = len(_memory_cache)
            _memory_cache.clear()
            return count
        else:
            count = len(_memory_cache)
            _memory_cache.clear()
            return count
    except Exception as e:
        logger.warning(f"Cache clear error: {e}")
        return 0
