from fastapi import Header, HTTPException, Depends
from app.core import settings

async def verify_dev_editor_key(x_dev_editor_key: str = Header(None)):
    """Guard to protect dev-editor endpoints with API key"""
    if not x_dev_editor_key or x_dev_editor_key != settings.DEV_EDITOR_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: invalid editor key")