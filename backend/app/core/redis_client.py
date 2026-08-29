from typing import Optional, Any
import json
import redis.asyncio as aioredis
from backend.app.config import get_settings
from backend.app.core.logging import logger

settings = get_settings()

class RedisService:
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None

    async def connect(self):
        try:
            self.client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=3.0,
            )
            await self.client.ping()
            logger.info("Connected to Redis server successfully.")
        except Exception as e:
            logger.warning(f"Could not connect to Redis at {settings.REDIS_URL}: {e}. Operating in graceful fallback mode.")
            self.client = None

    async def close(self):
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[str]:
        if not self.client:
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis get error for {key}: {e}")
            return None

    async def set(self, key: str, value: str, expire: int = 3600):
        if not self.client:
            return
        try:
            await self.client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis set error for {key}: {e}")

    async def publish(self, channel: str, message: Any):
        if not self.client:
            return
        try:
            payload = json.dumps(message) if not isinstance(message, str) else message
            await self.client.publish(channel, payload)
        except Exception as e:
            logger.error(f"Redis publish error to {channel}: {e}")

    async def is_healthy(self) -> bool:
        if not self.client:
            return False
        try:
            return await self.client.ping()
        except Exception:
            return False

redis_service = RedisService()

async def get_redis() -> RedisService:
    return redis_service
