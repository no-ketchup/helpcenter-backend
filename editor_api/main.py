"""
Help Center Editor API - Cloud Function
A dedicated service for editor operations (REST API)
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from functions_framework import http

from common.core.logger import setup_logging
from common.core.middleware import RequestLoggingMiddleware
from common.core.rate_limiting import setup_rate_limiting
from common.core.settings import ALLOWED_ORIGINS, ENVIRONMENT, LOG_LEVEL
from common.domain.rest import (
    dev_editor_router,
    guide_editor_router,
    media_editor_router,
)

setup_logging(LOG_LEVEL)

app = FastAPI(
    title="Help Center Editor API",
    description="Editor API for help center content management",
    version="1.0.0",
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

setup_rate_limiting(app)
app.include_router(dev_editor_router)
app.include_router(guide_editor_router)
app.include_router(media_editor_router)


@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "editor_api",
        "environment": ENVIRONMENT,
        "version": "1.0.0",
        "endpoints": {
            "dev-editor": "/dev-editor",
            "guide-editor": "/guide-editor",
            "media-editor": "/media-editor",
        },
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "HelpCenter Editor API",
        "version": "1.0.0",
        "description": "Editor API for help center content management",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "dev-editor": "/dev-editor",
            "guide-editor": "/guide-editor",
            "media-editor": "/media-editor",
        },
    }


# Cloud Function entry point
@http
def editor_api(request):
    """Cloud Function entry point."""
    return app(request.environ, lambda *args: None)
