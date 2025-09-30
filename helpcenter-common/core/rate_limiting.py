"""
Rate limiting configuration and middleware.

Provides different rate limits for different types of endpoints:
- Public GraphQL: More lenient
- REST API: Moderate limits
- Dev Editor: Strict limits
- Health checks: Very lenient
"""

import os
from typing import Optional

import redis.asyncio as redis
from fastapi import HTTPException, Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.logging import get_logger

logger = get_logger("rate_limiting")

# Redis connection for distributed rate limiting
redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client for distributed rate limiting."""
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
    """Custom key function for rate limiting."""
    # Use IP address as primary key
    client_ip = get_remote_address(request)

    # Add user ID if available (for authenticated endpoints)
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}:{client_ip}"

    return f"ip:{client_ip}"


# Initialize rate limiter
# Disable rate limiting in test environment
if os.getenv("ENVIRONMENT") == "test":
    limiter = Limiter(
        key_func=get_limiter_key_func,
        storage_uri="memory://",
        default_limits=["10000/hour"],  # Very high limit for tests
    )
else:
    limiter = Limiter(
        key_func=get_limiter_key_func,
        storage_uri=os.getenv("REDIS_URL", "memory://"),
        default_limits=["1000/hour"],  # Default fallback limit
    )

# Rate limit configurations for different endpoint types
RATE_LIMITS = {
    # Public GraphQL endpoints - more lenient
    "graphql": {
        "queries": "100/minute",  # 100 queries per minute
        "mutations": "20/minute",  # 20 mutations per minute
    },
    # REST API endpoints - moderate limits
    "rest": {
        "read": "200/hour",  # 200 reads per hour
        "write": "50/hour",  # 50 writes per hour
        "upload": "10/hour",  # 10 uploads per hour
    },
    # Dev Editor endpoints - strict limits
    "dev_editor": {
        "read": "100/hour",  # 100 reads per hour
        "write": "20/hour",  # 20 writes per hour
        "upload": "5/hour",  # 5 uploads per hour
    },
    # Health and utility endpoints - very lenient
    "health": {
        "check": "1000/hour",  # 1000 checks per hour
    },
}


def get_rate_limit(endpoint_type: str, action: str) -> str:
    """Get rate limit for specific endpoint type and action."""
    return RATE_LIMITS.get(endpoint_type, {}).get(action, "100/hour")


# Custom rate limit exceeded handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded errors."""
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
            "retry_after": 60,  # Default to 60 seconds
            "limit": str(exc.detail),
        },
    )


# Rate limiting decorators for different endpoint types
def rate_limit_graphql_query():
    """Rate limit for GraphQL queries."""
    return limiter.limit(get_rate_limit("graphql", "queries"))


def rate_limit_graphql_mutation():
    """Rate limit for GraphQL mutations."""
    return limiter.limit(get_rate_limit("graphql", "mutations"))


def rate_limit_rest_read():
    """Rate limit for REST read operations."""
    return limiter.limit(get_rate_limit("rest", "read"))


def rate_limit_rest_write():
    """Rate limit for REST write operations."""
    return limiter.limit(get_rate_limit("rest", "write"))


def rate_limit_rest_upload():
    """Rate limit for REST upload operations."""
    return limiter.limit(get_rate_limit("rest", "upload"))


def rate_limit_dev_editor_read():
    """Rate limit for dev editor read operations."""
    return limiter.limit(get_rate_limit("dev_editor", "read"))


def rate_limit_dev_editor_write():
    """Rate limit for dev editor write operations."""
    return limiter.limit(get_rate_limit("dev_editor", "write"))


def rate_limit_dev_editor_upload():
    """Rate limit for dev editor upload operations."""
    if os.getenv("ENVIRONMENT") == "test":
        return lambda x: x  # No-op decorator for tests
    return limiter.limit(get_rate_limit("dev_editor", "upload"))


def rate_limit_health():
    """Rate limit for health check endpoints."""
    return limiter.limit(get_rate_limit("health", "check"))


# Middleware setup
def setup_rate_limiting(app):
    """Setup rate limiting middleware and handlers."""
    # Add rate limiting middleware
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    logger.info("Rate limiting middleware configured")


# Utility functions
async def get_rate_limit_status(request: Request, endpoint_type: str, action: str) -> dict:
    """Get current rate limit status for a request."""
    key = get_limiter_key_func(request)
    limit = get_rate_limit(endpoint_type, action)

    # Parse limit (e.g., "100/hour" -> count=100, period="hour")
    count, period = limit.split("/")
    count = int(count)

    # Get current usage from limiter
    current_usage = await limiter.get_window_stats(key, limit)

    return {
        "limit": limit,
        "remaining": max(0, count - current_usage.hit_count),
        "reset_time": current_usage.reset_time,
        "retry_after": current_usage.retry_after,
    }
