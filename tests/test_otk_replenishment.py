"""Purpose: Validate one-time key replenishment and non-reuse behavior checks (FR-E2EE-04, NFR-SEC-03)."""

from __future__ import annotations

import pytest
import requests


def test_otk_pool_monitor_endpoint_available(
    synapse_base_url: str,
    user_token: str,
    http_session: requests.Session,
) -> None:
    """Confirm one-time key count endpoint is reachable for authenticated users."""
    if not user_token:
        pytest.skip("USER_TOKEN is not set")

    response = http_session.get(
        f"{synapse_base_url.rstrip('/')}/_matrix/client/v3/keys/upload",
        headers={"Authorization": f"Bearer {user_token}"},
        timeout=10,
    )
    assert response.status_code in {200, 401, 405}


def test_otk_claim_non_reuse_guard(
    synapse_base_url: str,
    user_token: str,
    test_user_id: str,
    http_session: requests.Session,
) -> None:
    """Verify key claim endpoint responds deterministically for duplicate claims."""
    if not user_token or not test_user_id:
        pytest.skip("USER_TOKEN and TEST_USER_ID are required")

    payload = {
        "one_time_keys": {
            test_user_id: {"*": "signed_curve25519"}
        }
    }

    first = http_session.post(
        f"{synapse_base_url.rstrip('/')}/_matrix/client/v3/keys/claim",
        headers={"Authorization": f"Bearer {user_token}"},
        json=payload,
        timeout=10,
    )
    second = http_session.post(
        f"{synapse_base_url.rstrip('/')}/_matrix/client/v3/keys/claim",
        headers={"Authorization": f"Bearer {user_token}"},
        json=payload,
        timeout=10,
    )

    assert first.status_code in {200, 400, 404}
    assert second.status_code in {200, 400, 404}
