"""Rate limiting configuration and middleware."""

import os
from typing import Optional

import redis.asyncio as redis
from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from ..core.logger import get_logger

logger = get_logger("rate_limiting")

redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    global redis_client
    if redis_client is None and os.getenv("REDIS_URL"):
        try:
            redis_client = redis.from_url(os.getenv("REDIS_URL"))
            logger.info("Redis client initialized for rate limiting")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {e}")
            logger.warning("Rate limiting will use in-memory storage")
    return redis_client


def get_limiter_key_func(request: Request) -> str:
    client_ip = get_remote_address(request)
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}:{client_ip}"
    return f"ip:{client_ip}"


if os.getenv("ENVIRONMENT") == "test":
    limiter = Limiter(
        key_func=get_limiter_key_func,
        storage_uri="memory://",
        default_limits=["10000/hour"],
    )
else:
    limiter = Limiter(
        key_func=get_limiter_key_func,
        storage_uri=os.getenv("REDIS_URL", "memory://"),
        default_limits=["1000/hour"],
    )

RATE_LIMITS = {
    "graphql": {
        "queries": "100/minute",
        "mutations": "20/minute",
    },
    "rest": {
        "read": "200/hour",
        "write": "50/hour",
        "upload": "10/hour",
    },
    "dev_editor": {
        "read": "100/hour",
        "write": "20/hour",
        "upload": "5/hour",
    },
    "health": {
        "check": "1000/hour",
    },
}


def get_rate_limit(endpoint_type: str, action: str) -> str:
    return RATE_LIMITS.get(endpoint_type, {}).get(action, "100/hour")


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(
        f"Rate limit exceeded for {get_limiter_key_func(request)}",
        extra={
            "client_ip": get_remote_address(request),
            "endpoint": request.url.path,
            "method": request.method,
            "limit": str(exc.detail),
        },
    )

    raise HTTPException(
        status_code=429,
        detail={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": 60,
            "limit": str(exc.detail),
        },
    )


def rate_limit_graphql_query():
    return limiter.limit(get_rate_limit("graphql", "queries"))


def rate_limit_graphql_mutation():
    return limiter.limit(get_rate_limit("graphql", "mutations"))


def rate_limit_rest_read():
    return limiter.limit(get_rate_limit("rest", "read"))


def rate_limit_rest_write():
    return limiter.limit(get_rate_limit("rest", "write"))


def rate_limit_rest_upload():
    return limiter.limit(get_rate_limit("rest", "upload"))


def rate_limit_dev_editor_read():
    return limiter.limit(get_rate_limit("dev_editor", "read"))


def rate_limit_dev_editor_write():
    return limiter.limit(get_rate_limit("dev_editor", "write"))


def rate_limit_dev_editor_upload():
    if os.getenv("ENVIRONMENT") == "test":
        return lambda x: x
    return limiter.limit(get_rate_limit("dev_editor", "upload"))


def rate_limit_health():
    return limiter.limit(get_rate_limit("health", "check"))


def setup_rate_limiting(app):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    logger.info("Rate limiting middleware configured")


def get_rate_limit_status(endpoint_type: str, action: str) -> dict:
    limit = get_rate_limit(endpoint_type, action)
    count, period = limit.split("/")
    count = int(count)

    return {
        "limit": limit,
        "remaining": count,
        "reset_time": None,
        "retry_after": None,
    }
