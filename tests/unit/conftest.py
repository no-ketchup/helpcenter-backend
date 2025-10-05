"""Configuration for unit tests - NO DATABASE, USE MOCKS."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock

# Set test environment for unit tests (no database needed)
os.environ["ENVIRONMENT"] = "test"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["DEV_EDITOR_KEY"] = "test-editor-key"
# No DATABASE_URL_ASYNC needed for unit tests


@pytest.fixture
def mock_session():
    """Mock database session for unit tests."""
    return AsyncMock()


@pytest.fixture
def mock_repository():
    """Mock repository for unit tests."""
    return MagicMock()


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for unit tests."""
    return MagicMock()


@pytest.fixture
def mock_limiter():
    """Mock rate limiter for unit tests."""
    return MagicMock()


@pytest.fixture
def mock_engine():
    """Mock database engine for unit tests."""
    return MagicMock()


@pytest.fixture
def mock_session_factory():
    """Mock session factory for unit tests."""
    return MagicMock()

