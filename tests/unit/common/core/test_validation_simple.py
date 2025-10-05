"""Simple unit tests for validation - testing in complete isolation."""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException, UploadFile

from common.core.validation import (
    ValidationErrorDetail,
    ValidationErrorResponse,
    APIError,
)


class TestValidationErrorDetail:
    """Test ValidationErrorDetail model in isolation."""

    def test_validation_error_detail_creation(self):
        """Test creating a validation error detail."""
        detail = ValidationErrorDetail(
            field="test_field",
            message="Test error message",
            value="test_value",
            code="test_code"
        )
        assert detail.field == "test_field"
        assert detail.message == "Test error message"
        assert detail.value == "test_value"
        assert detail.code == "test_code"

    def test_validation_error_detail_model_dump(self):
        """Test model_dump method."""
        detail = ValidationErrorDetail(
            field="test_field",
            message="Test error message",
            value="test_value",
            code="test_code"
        )
        dumped = detail.model_dump()
        assert dumped["field"] == "test_field"
        assert dumped["message"] == "Test error message"
        assert dumped["value"] == "test_value"
        assert dumped["code"] == "test_code"


class TestValidationErrorResponse:
    """Test ValidationErrorResponse class in isolation."""

    def test_validation_error_response_creation(self):
        """Test creating a validation error response."""
        detail = ValidationErrorDetail(
            field="test_field",
            message="Test error message",
            value="test_value",
            code="test_code"
        )

        response = ValidationErrorResponse(
            message="Validation failed",
            details=[detail]
        )

        # ValidationErrorResponse is an HTTPException with dict detail
        assert response.detail["message"] == "Validation failed"
        assert len(response.detail["details"]) == 1
        assert response.detail["details"][0]["field"] == "test_field"
        assert response.status_code == 422

    def test_validation_error_response_with_correlation_id(self):
        """Test ValidationErrorResponse with correlation ID."""
        detail = ValidationErrorDetail(
            field="test_field",
            message="Test error message",
            value="test_value",
            code="test_code"
        )

        response = ValidationErrorResponse(
            message="Validation failed",
            details=[detail],
            correlation_id="test-correlation",
            request_id="test-request"
        )

        assert response.detail["message"] == "Validation failed"
        assert response.detail["correlation_id"] == "test-correlation"
        assert response.detail["request_id"] == "test-request"
        assert response.status_code == 422


class TestAPIError:
    """Test APIError class in isolation."""

    def test_api_error_creation(self):
        """Test creating an API error."""
        error_response = APIError(
            error="test_error",
            message="Test error message",
            correlation_id="test-correlation-id",
            request_id="test-request-id"
        )
        assert error_response.error == "test_error"
        assert error_response.message == "Test error message"
        assert error_response.correlation_id == "test-correlation-id"
        assert error_response.request_id == "test-request-id"

    def test_api_error_model_dump(self):
        """Test model_dump method."""
        error_response = APIError(
            error="test_error",
            message="Test error message",
            correlation_id="test-correlation-id",
            request_id="test-request-id"
        )
        dumped = error_response.model_dump()
        assert dumped["error"] == "test_error"
        assert dumped["message"] == "Test error message"
        assert dumped["correlation_id"] == "test-correlation-id"
        assert dumped["request_id"] == "test-request-id"


class TestValidationErrorDetailEdgeCases:
    """Test edge cases for ValidationErrorDetail."""

    def test_validation_error_detail_with_none_values(self):
        """Test ValidationErrorDetail with None values."""
        detail = ValidationErrorDetail(
            field="test_field",
            message="Test error message",
            value=None,
            code="test_code"  # code field doesn't allow None
        )
        assert detail.field == "test_field"
        assert detail.message == "Test error message"
        assert detail.value is None
        assert detail.code == "test_code"

    def test_validation_error_detail_empty_strings(self):
        """Test ValidationErrorDetail with empty strings."""
        detail = ValidationErrorDetail(
            field="",
            message="",
            value="",
            code=""
        )
        assert detail.field == ""
        assert detail.message == ""
        assert detail.value == ""
        assert detail.code == ""


class TestAPIErrorEdgeCases:
    """Test edge cases for APIError."""

    def test_api_error_with_none_values(self):
        """Test APIError with None values."""
        error_response = APIError(
            error="test_error",
            message="Test error message",
            correlation_id=None,
            request_id=None
        )
        assert error_response.error == "test_error"
        assert error_response.message == "Test error message"
        assert error_response.correlation_id is None
        assert error_response.request_id is None

    def test_api_error_empty_strings(self):
        """Test APIError with empty strings."""
        error_response = APIError(
            error="",
            message="",
            correlation_id="",
            request_id=""
        )
        assert error_response.error == ""
        assert error_response.message == ""
        assert error_response.correlation_id == ""
        assert error_response.request_id == ""
