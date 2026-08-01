import logging
import time

from fastapi import Depends, HTTPException, Request, status

from app.core.redis import get_redis

logger = logging.getLogger(__name__)


def rate_limit(max_requests: int = 5, window_seconds: int = 60):
    key_prefix = f"rl:{max_requests}:{window_seconds}"

    async def limiter(request: Request, redis=Depends(get_redis)):
        if redis is None:
            logger.debug("Redis unavailable — skipping rate limit")
            return

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - window_seconds
        key = f"{key_prefix}:{client_ip}:{request.url.path}"

        await redis.zremrangebyscore(key, 0, window_start)
        count = await redis.zcard(key)

        if count >= max_requests:
            logger.warning("Rate limit hit — %s on %s", client_ip, request.url.path)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Max {max_requests} per {window_seconds}s",
            )

        await redis.zadd(key, {str(now): now})
        await redis.expire(key, window_seconds)

    return Depends(limiter)
