from fastapi import Header, HTTPException, status
from app.core import settings

async def verify_dev_editor_key(x_dev_editor_key: str = Header(...)) -> None:
    """
    Guard for dev-editor endpoints.
    Requires `x-dev-editor-key` header to match the configured DEV_EDITOR_KEY.
    """
    if x_dev_editor_key != settings.DEV_EDITOR_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: invalid editor key",
        )