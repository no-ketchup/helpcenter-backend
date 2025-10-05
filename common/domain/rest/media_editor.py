from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.db import get_session_dependency
from ...core.rate_limiting import (
    rate_limit_dev_editor_read,
    rate_limit_dev_editor_upload,
    rate_limit_dev_editor_write,
)
from ...services.media import MediaService
from ..dtos.media import MediaReadDTO
from .editor_guard import verify_dev_editor_key

router = APIRouter(
    prefix="/dev-editor",
    dependencies=[Depends(verify_dev_editor_key)],
    tags=["dev-editor-media"],
)

service = MediaService()


@router.post("/media/upload", response_model=MediaReadDTO)
@rate_limit_dev_editor_upload()
async def upload_media(
    request: Request,
    file: UploadFile = File(...),
    alt: Optional[str] = Form(None),
    guide_id: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session_dependency),
):
    """Upload media file to Cloudinary."""
    if not file.content_type.startswith(("image/", "video/")):
        raise HTTPException(status_code=400, detail="Only image and video files are allowed")

    return await service.upload_media(session, file, alt, guide_id)


@router.get("/media", response_model=List[MediaReadDTO])
@rate_limit_dev_editor_read()
async def list_media(request: Request, session: AsyncSession = Depends(get_session_dependency)):
    """List all media."""
    return await service.list_media(session)


@router.get("/media/{media_id}", response_model=MediaReadDTO)
@rate_limit_dev_editor_read()
async def get_media(
    request: Request, media_id: UUID, session: AsyncSession = Depends(get_session_dependency)
):
    """Get media by ID."""
    media = await service.get_media(session, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media


@router.delete("/media/{media_id}")
@rate_limit_dev_editor_write()
async def delete_media(
    request: Request, media_id: UUID, session: AsyncSession = Depends(get_session_dependency)
):
    """Delete media."""
    await service.delete_media(session, media_id)
    return {"message": "Media deleted successfully"}


@router.get("/media/{media_id}/optimized")
@rate_limit_dev_editor_read()
async def get_optimized_media(
    request: Request,
    media_id: UUID,
    width: Optional[int] = None,
    height: Optional[int] = None,
    session: AsyncSession = Depends(get_session_dependency),
):
    """Get optimized media URL."""
    media = await service.get_media(session, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    optimized_url = service.get_optimized_url(media.url, width, height)
    return {"url": optimized_url}


# Guide-Media Association Endpoints
@router.post("/guides/{guide_id}/media/{media_id}")
@rate_limit_dev_editor_write()
async def attach_media_to_guide(
    request: Request,
    guide_id: UUID,
    media_id: UUID,
    session: AsyncSession = Depends(get_session_dependency),
):
    """Attach media to a guide."""
    await service.attach_to_guide(session, media_id, guide_id)
    return {"message": "Media attached to guide successfully"}


@router.delete("/guides/{guide_id}/media/{media_id}")
@rate_limit_dev_editor_write()
async def detach_media_from_guide(
    request: Request,
    guide_id: UUID,
    media_id: UUID,
    session: AsyncSession = Depends(get_session_dependency),
):
    """Detach media from a guide."""
    await service.detach_from_guide(session, media_id, guide_id)
    return {"message": "Media detached from guide successfully"}


@router.get("/guides/{guide_id}/media", response_model=List[MediaReadDTO])
@rate_limit_dev_editor_read()
async def get_guide_media(
    request: Request, guide_id: UUID, session: AsyncSession = Depends(get_session_dependency)
):
    """Get all media attached to a guide."""
    return await service.get_guide_media(session, guide_id)
