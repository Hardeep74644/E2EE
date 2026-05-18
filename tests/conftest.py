"""Purpose: Shared pytest fixtures and environment guards for Synapse integration tests (FR-TEST-01, NFR-ROBUST-01)."""

from __future__ import annotations

import os

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def synapse_base_url() -> str:
    """Return configured Synapse base URL."""
    return os.getenv("SYNAPSE_BASE_URL", "http://localhost:8008")


@pytest.fixture(scope="session")
def admin_token() -> str:
    """Return admin token from environment."""
    return os.getenv("ADMIN_TOKEN", "")


@pytest.fixture(scope="session")
def user_token() -> str:
    """Return user token from environment."""
    return os.getenv("USER_TOKEN", "")


@pytest.fixture(scope="session")
def test_user_id() -> str:
    """Return target test user ID from environment."""
    return os.getenv("TEST_USER_ID", "")


@pytest.fixture(scope="session")
def http_session() -> requests.Session:
    """Provide reusable HTTP session for integration calls."""
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope="session")
def synapse_reachable(synapse_base_url: str, http_session: requests.Session) -> bool:
    """Check whether Synapse endpoint is reachable for integration tests."""
    try:
        response = http_session.get(f"{synapse_base_url.rstrip('/')}/_matrix/client/versions", timeout=5)
        return response.status_code < 500
    except requests.RequestException:
        return False


@pytest.fixture(autouse=True)
def skip_if_synapse_unreachable(synapse_reachable: bool) -> None:
    """Auto-skip all tests if Synapse is unavailable in the environment."""
    if not synapse_reachable:
        pytest.skip("Synapse is unreachable; skipping integration suite.")
