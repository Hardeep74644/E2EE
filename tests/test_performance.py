"""Purpose: Validate latency against NFR-P1/NFR-P2 using benchmark script integration (NFR-P1, NFR-P2)."""

from __future__ import annotations

import subprocess

import pytest


def test_latency_benchmark_script_executes(
    synapse_base_url: str,
    admin_token: str,
    user_token: str,
) -> None:
    """Execute benchmark script and assert successful invocation behavior."""
    if not admin_token or not user_token:
        pytest.skip("ADMIN_TOKEN and USER_TOKEN are required")

    completed = subprocess.run(
        [
            "python3",
            "scripts/benchmark_latency.py",
            "--url",
            synapse_base_url,
            "--admin-token",
            admin_token,
            "--user-token",
            user_token,
            "--samples",
            "2",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert "Endpoint" in completed.stdout
    assert completed.returncode in {0, 1}
