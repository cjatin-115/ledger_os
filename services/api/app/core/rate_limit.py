from collections.abc import Callable

from fastapi import HTTPException, Request, status
from redis.asyncio import Redis

from app.core.config import settings

_redis: Redis | None = None


def _get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


def rate_limit(scope: str, limit: int, window_seconds: int) -> Callable:
    async def dependency(request: Request) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return

        client_host = request.client.host if request.client else "unknown"
        key = f"ledgeros:rate-limit:{scope}:{client_host}"

        try:
            redis = _get_redis()
            async with redis.pipeline(transaction=True) as pipeline:
                pipeline.incr(key)
                pipeline.expire(key, window_seconds)
                results = await pipeline.execute()
            request_count = int(results[0])
        except Exception as exc:
            if settings.ENVIRONMENT == "production":
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication protection is temporarily unavailable.",
                ) from exc
            return

        if request_count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Try again later.",
                headers={"Retry-After": str(window_seconds)},
            )

    return dependency