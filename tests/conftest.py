"""Base test configuration - minimal setup for all tests."""

import os
import pytest

# Set basic test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["DEV_EDITOR_KEY"] = "test-editor-key"
