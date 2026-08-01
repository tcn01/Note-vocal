import logging

import redis.asyncio as aioredis

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

redis_client: aioredis.Redis | None = None


async def init_redis():
    global redis_client
    try:
        redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await redis_client.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning("Redis unavailable — rate limiting disabled: %s", e)
        redis_client = None


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Redis disconnected")


async def get_redis() -> aioredis.Redis | None:
    return redis_client
