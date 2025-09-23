"""
Custom middleware for request logging and correlation IDs.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger, set_correlation_id, log_request, get_correlation_id

logger = get_logger("middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests with correlation IDs."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate correlation ID
        correlation_id = set_correlation_id()
        request_id = str(uuid.uuid4())
        
        # Add correlation ID to request headers
        request.state.correlation_id = correlation_id
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Log request start
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "correlation_id": correlation_id,
                "method": request.method,
                "endpoint": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log request completion
            log_request(
                logger,
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration,
                request_id=request_id,
                user_id=getattr(request.state, 'user_id', None),
                extra={
                    "correlation_id": correlation_id,
                    "query_params": str(request.query_params),
                    "client_ip": request.client.host if request.client else None,
                }
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                exc_info=e,
                extra={
                    "request_id": request_id,
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "endpoint": request.url.path,
                    "duration": duration * 1000,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                }
            )
            
            # Re-raise the exception
            raise
