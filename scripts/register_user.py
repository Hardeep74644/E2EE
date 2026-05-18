#!/usr/bin/env python3
"""Purpose: Register Matrix users and upload placeholder E2EE key material (FR-USER-01, FR-E2EE-01, NFR-SEC-01)."""

from __future__ import annotations

import argparse
import base64
import json
from dataclasses import dataclass
from typing import Any

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519


@dataclass
class RegistrationResult:
    """Stores relevant response fields from Matrix registration."""

    user_id: str
    device_id: str
    access_token: str


def build_registration_payload(username: str, password: str) -> dict[str, Any]:
    """Build the Matrix client registration payload."""
    return {
        "auth": {"type": "m.login.dummy"},
        "username": username,
        "password": password,
        "inhibit_login": False,
    }


def _b64(raw: bytes) -> str:
    """Encode bytes as unpadded base64 for Matrix key payloads."""
    return base64.b64encode(raw).decode("utf-8").rstrip("=")


def generate_placeholder_curve25519_bundle(user_id: str, device_id: str) -> dict[str, Any]:
    """Generate placeholder Curve25519 keys for demonstration key upload."""
    identity_key = x25519.X25519PrivateKey.generate()
    one_time_key = x25519.X25519PrivateKey.generate()

    identity_public = identity_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    one_time_public = one_time_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    identity_b64 = _b64(identity_public)
    otk_b64 = _b64(one_time_public)

    return {
        "device_keys": {
            "user_id": user_id,
            "device_id": device_id,
            "algorithms": [
                "m.olm.curve25519-aes-sha2",
                "m.megolm.v1.aes-sha2",
            ],
            "keys": {
                f"curve25519:{device_id}": identity_b64,
            },
            "signatures": {user_id: {f"ed25519:{device_id}": "placeholder-signature"}},
        },
        "one_time_keys": {
            "signed_curve25519:otk_1": {
                "key": otk_b64,
                "signatures": {user_id: {f"ed25519:{device_id}": "placeholder-signature"}},
            }
        },
    }


def register_user(base_url: str, username: str, password: str) -> RegistrationResult:
    """Register a user against the Matrix Client API."""
    endpoint = f"{base_url.rstrip('/')}/_matrix/client/v3/register"
    response = requests.post(endpoint, json=build_registration_payload(username, password), timeout=20)
    response.raise_for_status()
    payload = response.json()
    return RegistrationResult(
        user_id=payload["user_id"],
        device_id=payload["device_id"],
        access_token=payload["access_token"],
    )


def upload_keys(base_url: str, access_token: str, key_payload: dict[str, Any]) -> dict[str, Any]:
    """Upload generated key bundle to Matrix keys upload endpoint."""
    endpoint = f"{base_url.rstrip('/')}/_matrix/client/v3/keys/upload"
    response = requests.post(
        endpoint,
        headers={"Authorization": f"Bearer {access_token}"},
        json=key_payload,
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Register Matrix user and upload placeholder key bundle.")
    parser.add_argument("--url", required=True, help="Matrix homeserver base URL, e.g., http://localhost:8008")
    parser.add_argument("--username", required=True, help="Username to register")
    parser.add_argument("--password", required=True, help="Password for the new user")
    parser.add_argument("--dry-run", action="store_true", help="Print payloads without sending requests")
    return parser.parse_args()


def main() -> int:
    """Run CLI workflow for registration and key upload."""
    args = parse_args()
    registration_payload = build_registration_payload(args.username, args.password)

    if args.dry_run:
        fake_user_id = f"@{args.username}:localhost"
        fake_device_id = "DRYRUNDEVICE"
        keys_payload = generate_placeholder_curve25519_bundle(fake_user_id, fake_device_id)
        print("DRY RUN - Registration payload:")
        print(json.dumps(registration_payload, indent=2))
        print("DRY RUN - Keys upload payload:")
        print(json.dumps(keys_payload, indent=2))
        return 0

    result = register_user(args.url, args.username, args.password)
    keys_payload = generate_placeholder_curve25519_bundle(result.user_id, result.device_id)
    upload_result = upload_keys(args.url, result.access_token, keys_payload)

    print("Registration and key upload complete")
    print(f"user_id: {result.user_id}")
    print(f"device_id: {result.device_id}")
    print(f"access_token: {result.access_token}")
    print(f"keys uploaded: {json.dumps(upload_result)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
