"""
Local JSON Caching Module for API Optimization.
Reduces redundant API calls by caching stadium data locally.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)

CACHE_DIR = "utils/cache_data"
CACHE_EXPIRY_MINUTES = 5  # Cache expires after 5 minutes


def ensure_cache_dir() -> None:
    """Create cache directory if it doesn't exist."""
    os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_path(key: str) -> str:
    """Generate cache file path for a given key."""
    return os.path.join(CACHE_DIR, f"{key}.json")


def cache_set(key: str, data: Any, expiry_minutes: int = CACHE_EXPIRY_MINUTES) -> None:
    """
    Store data in local JSON cache.

    Args:
        key: Cache key identifier.
        data: Data to cache (must be JSON-serializable).
        expiry_minutes: Cache expiry time in minutes.
    """
    ensure_cache_dir()
    cache_entry = {
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "expiry_minutes": expiry_minutes,
    }
    try:
        cache_path = get_cache_path(key)
        with open(cache_path, "w") as f:
            json.dump(cache_entry, f, indent=2)
        logger.info(f"✓ Cached '{key}' (expires in {expiry_minutes} min)")
    except Exception as e:
        logger.warning(f"✗ Failed to cache '{key}': {str(e)}")


def cache_get(key: str) -> Optional[Any]:
    """
    Retrieve data from local JSON cache if not expired.

    Args:
        key: Cache key identifier.

    Returns:
        Cached data if valid and not expired, None otherwise.
    """
    cache_path = get_cache_path(key)
    if not os.path.exists(cache_path):
        logger.debug(f"Cache miss: '{key}'")
        return None

    try:
        with open(cache_path, "r") as f:
            cache_entry = json.load(f)

        timestamp = datetime.fromisoformat(cache_entry["timestamp"])
        expiry_minutes = cache_entry.get("expiry_minutes", CACHE_EXPIRY_MINUTES)
        expiry_time = timestamp + timedelta(minutes=expiry_minutes)

        if datetime.now() < expiry_time:
            logger.info(f"✓ Cache hit: '{key}' (still valid)")
            return cache_entry["data"]
        else:
            logger.info(f"Cache expired: '{key}'")
            os.remove(cache_path)
            return None
    except Exception as e:
        logger.warning(f"✗ Failed to retrieve cache '{key}': {str(e)}")
        return None


def cache_clear_expired() -> int:
    """
    Remove all expired cache entries.

    Returns:
        Number of entries cleared.
    """
    ensure_cache_dir()
    cleared = 0
    for filename in os.listdir(CACHE_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(CACHE_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    cache_entry = json.load(f)

                timestamp = datetime.fromisoformat(cache_entry["timestamp"])
                expiry_minutes = cache_entry.get("expiry_minutes", CACHE_EXPIRY_MINUTES)
                expiry_time = timestamp + timedelta(minutes=expiry_minutes)

                if datetime.now() >= expiry_time:
                    os.remove(filepath)
                    cleared += 1
                    logger.info(f"Cleared expired cache: {filename}")
            except Exception as e:
                logger.warning(f"Error checking cache {filename}: {str(e)}")

    logger.info(f"✓ Cleared {cleared} expired cache entries")
    return cleared


def cache_clear_all() -> None:
    """Clear all cache entries."""
    ensure_cache_dir()
    for filename in os.listdir(CACHE_DIR):
        if filename.endswith(".json"):
            try:
                os.remove(os.path.join(CACHE_DIR, filename))
            except Exception as e:
                logger.warning(f"Failed to delete cache file {filename}: {str(e)}")
    logger.info("✓ All cache entries cleared")


def get_cache_stats() -> dict:
    """
    Get cache statistics.

    Returns:
        Dictionary with cache information.
    """
    ensure_cache_dir()
    entries = 0
    total_size = 0
    for filename in os.listdir(CACHE_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(CACHE_DIR, filename)
            entries += 1
            total_size += os.path.getsize(filepath)

    return {
        "entries": entries,
        "total_size_bytes": total_size,
        "cache_dir": CACHE_DIR,
    }
