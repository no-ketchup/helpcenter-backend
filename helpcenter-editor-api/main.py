"""
Help Center Editor API - Cloud Function
A dedicated service for editor operations (REST API)
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from functions_framework import http

from helpcenter_common.core.db import get_session
from helpcenter_common.core.logging import get_correlation_id, get_logger, setup_logging
from helpcenter_common.core.middleware import RequestLoggingMiddleware
from helpcenter_common.core.rate_limiting import setup_rate_limiting
from helpcenter_common.core.settings import ALLOWED_ORIGINS, ENVIRONMENT, LOG_LEVEL
from helpcenter_common.domain.rest import dev_editor_router, guide_editor_router, media_editor_router

setup_logging(LOG_LEVEL)

# Create FastAPI app
app = FastAPI(
    title="Help Center Editor API",
    description="Editor API for help center content management",
    version="1.0.0",
)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Setup rate limiting
setup_rate_limiting(app)

# Include routers
app.include_router(dev_editor_router)
app.include_router(guide_editor_router)
app.include_router(media_editor_router)


@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint."""
    return {"status": "healthy", "service": "editor-api", "environment": ENVIRONMENT}


# Cloud Function entry point
@http
def editor_api(request):
    """Cloud Function entry point."""
    return app(request.environ, lambda *args: None)
