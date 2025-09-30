"""
Comprehensive input validation and error handling utilities.
"""

import re
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from app.core.logging import get_logger

logger = get_logger("validation")


class ValidationErrorDetail(BaseModel):
    """Detailed validation error information."""

    field: str
    message: str
    value: Any
    code: str


class APIError(BaseModel):
    """Standardized API error response."""

    error: str
    message: str
    details: Optional[List[ValidationErrorDetail]] = None
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None


class ValidationErrorResponse(HTTPException):
    """Custom HTTP exception for validation errors."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[List[ValidationErrorDetail]] = None,
        correlation_id: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        self.details = details or []
        self.correlation_id = correlation_id
        self.request_id = request_id

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "validation_error",
                "message": message,
                "details": [detail.dict() for detail in self.details],
                "correlation_id": correlation_id,
                "request_id": request_id,
            },
        )


# Common validation patterns
class CommonValidators:
    """Common validation patterns and utilities."""

    @staticmethod
    def validate_slug(value: str) -> str:
        """Validate slug format (lowercase, alphanumeric, hyphens only)."""
        if not value:
            raise ValueError("Slug cannot be empty")

        if not re.match(r"^[a-z0-9-]+$", value):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")

        if value.startswith("-") or value.endswith("-"):
            raise ValueError("Slug cannot start or end with a hyphen")

        if "--" in value:
            raise ValueError("Slug cannot contain consecutive hyphens")

        return value

    @staticmethod
    def validate_email(value: str) -> str:
        """Validate email format."""
        if not value:
            raise ValueError("Email cannot be empty")

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, value):
            raise ValueError("Invalid email format")

        return value.lower()

    @staticmethod
    def validate_positive_int(value: int) -> int:
        """Validate positive integer."""
        if value <= 0:
            raise ValueError("Value must be positive")
        return value

    @staticmethod
    def validate_non_empty_string(value: str) -> str:
        """Validate non-empty string."""
        if not value or not value.strip():
            raise ValueError("Value cannot be empty")
        return value.strip()

    @staticmethod
    def validate_rich_text_body(value: Dict[str, Any]) -> Dict[str, Any]:
        """Validate rich text body structure."""
        if not isinstance(value, dict):
            raise ValueError("Body must be a JSON object")

        if "blocks" not in value:
            raise ValueError("Body must contain 'blocks' array")

        if not isinstance(value["blocks"], list):
            raise ValueError("Blocks must be an array")

        if not value["blocks"]:
            raise ValueError("Blocks array cannot be empty")

        # Validate each block
        for i, block in enumerate(value["blocks"]):
            if not isinstance(block, dict):
                raise ValueError(f"Block {i} must be an object")

            if "type" not in block:
                raise ValueError(f"Block {i} must have a 'type' field")

            if not isinstance(block["type"], str):
                raise ValueError(f"Block {i} type must be a string")

            # Validate specific block types
            if block["type"] == "heading":
                if "level" not in block:
                    raise ValueError(f"Heading block {i} must have a 'level' field")
                if not isinstance(block["level"], int) or block["level"] < 1 or block["level"] > 6:
                    raise ValueError(f"Heading block {i} level must be between 1 and 6")
                if "text" not in block or not block["text"]:
                    raise ValueError(f"Heading block {i} must have text content")

            elif block["type"] == "paragraph":
                if "text" not in block or not block["text"]:
                    raise ValueError(f"Paragraph block {i} must have text content")

            elif block["type"] == "list":
                if "items" not in block or not isinstance(block["items"], list):
                    raise ValueError(f"List block {i} must have an 'items' array")
                if not block["items"]:
                    raise ValueError(f"List block {i} items array cannot be empty")

        return value


def handle_validation_error(
    error: ValidationError, correlation_id: Optional[str] = None, request_id: Optional[str] = None
) -> ValidationErrorResponse:
    """Convert Pydantic ValidationError to our custom exception."""

    details = []
    for err in error.errors():
        field = ".".join(str(loc) for loc in err["loc"])
        details.append(
            ValidationErrorDetail(
                field=field, message=err["msg"], value=err.get("input"), code=err["type"]
            )
        )

    logger.warning(
        "Validation error occurred",
        extra={
            "correlation_id": correlation_id,
            "request_id": request_id,
            "validation_errors": [detail.dict() for detail in details],
        },
    )

    return ValidationErrorResponse(
        message="Input validation failed",
        details=details,
        correlation_id=correlation_id,
        request_id=request_id,
    )


def handle_business_logic_error(
    message: str,
    field: Optional[str] = None,
    correlation_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> ValidationErrorResponse:
    """Handle business logic validation errors."""

    details = []
    if field:
        details.append(
            ValidationErrorDetail(
                field=field, message=message, value=None, code="business_logic_error"
            )
        )

    logger.warning(
        "Business logic validation error",
        extra={
            "correlation_id": correlation_id,
            "request_id": request_id,
            "message": message,
            "field": field,
        },
    )

    return ValidationErrorResponse(
        message=message, details=details, correlation_id=correlation_id, request_id=request_id
    )


def sanitize_input(value: str) -> str:
    """Basic input sanitization."""
    if not isinstance(value, str):
        return value

    # Remove null bytes and control characters
    value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", value)

    # Trim whitespace
    value = value.strip()

    return value


def validate_file_upload(
    filename: str, content_type: str, max_size: int = 10 * 1024 * 1024  # 10MB
) -> None:
    """Validate file upload parameters."""

    if not filename:
        raise ValidationErrorResponse(
            message="Filename is required",
            details=[
                ValidationErrorDetail(
                    field="filename",
                    message="Filename cannot be empty",
                    value=filename,
                    code="required",
                )
            ],
        )

    # Check file extension
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
    file_ext = filename.lower().split(".")[-1] if "." in filename else ""
    if f".{file_ext}" not in allowed_extensions:
        raise ValidationErrorResponse(
            message="Invalid file type",
            details=[
                ValidationErrorDetail(
                    field="filename",
                    message=f"File type must be one of: {', '.join(allowed_extensions)}",
                    value=filename,
                    code="invalid_file_type",
                )
            ],
        )

    # Check content type
    allowed_types = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
    }
    if content_type not in allowed_types:
        raise ValidationErrorResponse(
            message="Invalid content type",
            details=[
                ValidationErrorDetail(
                    field="content_type",
                    message=f"Content type must be one of: {', '.join(allowed_types)}",
                    value=content_type,
                    code="invalid_content_type",
                )
            ],
        )


def create_error_response(
    error: Union[ValidationErrorResponse, HTTPException, Exception],
    correlation_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> JSONResponse:
    """Create standardized error response."""

    if isinstance(error, ValidationErrorResponse):
        return JSONResponse(status_code=error.status_code, content=error.detail)

    elif isinstance(error, HTTPException):
        return JSONResponse(
            status_code=error.status_code,
            content={
                "error": "http_error",
                "message": error.detail,
                "correlation_id": correlation_id,
                "request_id": request_id,
            },
        )

    else:
        logger.error(
            "Unhandled exception",
            exc_info=error,
            extra={
                "correlation_id": correlation_id,
                "request_id": request_id,
                "error_type": type(error).__name__,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_error",
                "message": "An internal error occurred",
                "correlation_id": correlation_id,
                "request_id": request_id,
            },
        )
