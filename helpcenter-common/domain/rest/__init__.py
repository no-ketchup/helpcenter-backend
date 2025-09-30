"""
REST API routers for the help center application.

This module contains all REST API endpoints organized by domain:
- dev_editor: Development editor endpoints
- guide_editor: Guide management endpoints
- media_editor: Media management endpoints
- editor_guard: Authentication/authorization for editor endpoints
"""

from .dev_editor import router as dev_editor_router
from .editor_guard import verify_dev_editor_key
from .guide_editor import router as guide_editor_router
from .media_editor import router as media_editor_router

__all__ = [
    "dev_editor_router",
    "guide_editor_router",
    "media_editor_router",
    "verify_dev_editor_key",
]
