"""
Simple In-Memory Cache
Provides caching for API responses to reduce external calls
"""

from datetime import datetime, timedelta
from threading import Lock


class CacheManager:
    """Thread-safe in-memory cache with TTL support"""

    def __init__(self):
        self._cache = {}
        self._lock = Lock()

    def get(self, key):
        """
        Retrieve value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]

            # Check if expired
            if datetime.utcnow() > entry['expires_at']:
                del self._cache[key]
                return None

            return entry['value']

    def set(self, key, value, ttl_seconds=3600):
        """
        Store value in cache with TTL

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
        """
        with self._lock:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at
            }

    def invalidate(self, key):
        """
        Remove entry from cache

        Args:
            key: Cache key to invalidate
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()

    def cleanup_expired(self):
        """Remove all expired entries"""
        with self._lock:
            now = datetime.utcnow()
            expired_keys = [
                key for key, entry in self._cache.items()
                if now > entry['expires_at']
            ]
            for key in expired_keys:
                del self._cache[key]

    def get_stats(self):
        """Get cache statistics"""
        with self._lock:
            return {
                'total_entries': len(self._cache),
                'keys': list(self._cache.keys())
            }


# Global cache instance
cache = CacheManager()
