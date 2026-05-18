"""Purpose: Validate RBAC enforcement for non-admin tokens on admin routes (FR-RBAC-01, NFR-SEC-01)."""

from __future__ import annotations

import pytest
import requests


@pytest.mark.parametrize(
    "path",
    ["/_synapse/admin/v1/server_version", "/_synapse/admin/v2/users?limit=5"],
)
def test_user_token_cannot_access_admin_routes(
    synapse_base_url: str,
    user_token: str,
    http_session: requests.Session,
    path: str,
) -> None:
    """Ensure user-scoped token gets denied for Synapse admin endpoints."""
    if not user_token:
        pytest.skip("USER_TOKEN is not set")

    response = http_session.get(
        f"{synapse_base_url.rstrip('/')}{path}",
        headers={"Authorization": f"Bearer {user_token}"},
        timeout=10,
    )
    assert response.status_code in {401, 403}
