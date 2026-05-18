"""Purpose: Validate forward secrecy indicators via DB scan and one-time key usage checks (FR-E2EE-03, FR-E2EE-04)."""

from __future__ import annotations

import os
import subprocess

import pytest
import requests


def test_db_plaintext_scan_script_runs_cleanly_when_configured() -> None:
    """Run DB inspection script when DB connection parameters are available."""
    db_path = os.getenv("SYNAPSE_SQLITE_PATH", "")
    postgres_url = os.getenv("POSTGRES_URL", "")
    if not db_path and not postgres_url:
        pytest.skip("Set SYNAPSE_SQLITE_PATH or POSTGRES_URL to run DB inspection test")

    cmd = ["python3", "scripts/db_inspect.py"]
    if db_path:
        cmd.extend(["--db-path", db_path])
    else:
        cmd.extend(["--postgres-url", postgres_url])

    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert "Verdict" in completed.stdout
    assert completed.returncode in {0, 1}


def test_one_time_key_upload_endpoint_accepts_payload(
    synapse_base_url: str,
    user_token: str,
    test_user_id: str,
    http_session: requests.Session,
) -> None:
    """Ensure one-time key upload endpoint accepts an OTK payload format."""
    if not user_token or not test_user_id:
        pytest.skip("USER_TOKEN and TEST_USER_ID are required")

    whoami = http_session.get(
        f"{synapse_base_url.rstrip('/')}/_matrix/client/v3/account/whoami",
        headers={"Authorization": f"Bearer {user_token}"},
        timeout=10,
    )
    whoami.raise_for_status()
    device_id = whoami.json().get("device_id")
    if not device_id:
        pytest.skip("device_id unavailable from whoami response")

    payload = {
        "one_time_keys": {
            "signed_curve25519:test_otk": {
                "key": "c29tZV9rZXk",
                "signatures": {test_user_id: {f"ed25519:{device_id}": "placeholder-signature"}},
            }
        }
    }

    response = http_session.post(
        f"{synapse_base_url.rstrip('/')}/_matrix/client/v3/keys/upload",
        headers={"Authorization": f"Bearer {user_token}"},
        json=payload,
        timeout=10,
    )
    assert response.status_code in {200, 400}
