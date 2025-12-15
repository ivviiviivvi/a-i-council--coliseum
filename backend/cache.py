"""
Redis Cache Module

Handles Redis connections and caching operations.
"""

import os
import json
from typing import Optional, Any, Union
import redis.asyncio as redis

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisCache:
    """
    Redis cache manager
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
            cls._instance.redis = None
        return cls._instance

    async def initialize(self):
        """Initialize Redis connection"""
        if not self.redis:
            try:
                self.redis = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
                await self.redis.ping()
                print("✅ Redis connected successfully")
            except Exception as e:
                print(f"⚠️ Redis connection failed: {e}")
                self.redis = None

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
        try:
            value = await self.redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 3600
    ) -> bool:
        """Set value in cache"""
        if not self.redis:
            return False
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await self.redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis:
            return False
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False

# Global instance
cache = RedisCache()

async def get_cache() -> RedisCache:
    """Dependency for getting cache instance"""
    if not cache.redis:
        await cache.initialize()
    return cache
