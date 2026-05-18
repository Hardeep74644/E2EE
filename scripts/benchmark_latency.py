#!/usr/bin/env python3
"""Purpose: Benchmark Matrix/Synapse endpoint latency against NFR-P1 thresholds (NFR-P1, NFR-P2)."""

from __future__ import annotations

import argparse
import statistics
import time
from dataclasses import dataclass
from typing import Any

import requests

NFR_P1_P95_MS = 500.0


@dataclass
class EndpointSpec:
    """Defines endpoint benchmark metadata and auth requirements."""

    name: str
    method: str
    path: str
    token_type: str
    payload: dict[str, Any] | None = None


@dataclass
class BenchmarkResult:
    """Holds aggregated latency statistics for an endpoint."""

    name: str
    avg_ms: float
    p50_ms: float
    p95_ms: float
    passed: bool


def parse_args() -> argparse.Namespace:
    """Parse CLI inputs for benchmark execution."""
    parser = argparse.ArgumentParser(description="Measure Matrix/Synapse endpoint latency.")
    parser.add_argument("--url", required=True, help="Base URL, e.g. http://localhost:8008")
    parser.add_argument("--admin-token", required=True, help="Synapse admin bearer token")
    parser.add_argument("--user-token", required=True, help="Matrix user bearer token")
    parser.add_argument("--samples", type=int, default=20, help="Samples per endpoint (default: 20)")
    return parser.parse_args()


def percentile(values: list[float], percent: float) -> float:
    """Compute percentile using nearest-rank style interpolation."""
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((percent / 100) * (len(ordered) - 1))))
    return ordered[index]


def benchmark_endpoint(base_url: str, samples: int, spec: EndpointSpec, admin_token: str, user_token: str) -> BenchmarkResult:
    """Run repeated requests for one endpoint and calculate aggregate latency."""
    latencies: list[float] = []
    token = admin_token if spec.token_type == "admin" else user_token
    for _ in range(samples):
        start = time.perf_counter()
        response = requests.request(
            spec.method,
            f"{base_url.rstrip('/')}{spec.path}",
            headers={"Authorization": f"Bearer {token}"},
            json=spec.payload,
            timeout=20,
        )
        response.raise_for_status()
        latencies.append((time.perf_counter() - start) * 1000)

    avg_ms = statistics.fmean(latencies)
    p50_ms = percentile(latencies, 50)
    p95_ms = percentile(latencies, 95)
    return BenchmarkResult(spec.name, avg_ms, p50_ms, p95_ms, p95_ms <= NFR_P1_P95_MS)


def print_results(results: list[BenchmarkResult]) -> None:
    """Render benchmark results as an ASCII table."""
    print("+--------------------------------------------+----------+----------+----------+--------+")
    print("| Endpoint                                   | Avg (ms) | P50 (ms) | P95 (ms) | NFR-P1 |")
    print("+--------------------------------------------+----------+----------+----------+--------+")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(
            f"| {result.name:<42} | {result.avg_ms:>8.2f} | {result.p50_ms:>8.2f} | {result.p95_ms:>8.2f} | {status:<6} |"
        )
    print("+--------------------------------------------+----------+----------+----------+--------+")


def main() -> int:
    """Execute benchmark suite and return failing status when thresholds are exceeded."""
    args = parse_args()
    endpoints = [
        EndpointSpec("GET /_synapse/admin/v1/server_version", "GET", "/_synapse/admin/v1/server_version", "admin"),
        EndpointSpec("GET /_matrix/client/v3/account/whoami", "GET", "/_matrix/client/v3/account/whoami", "user"),
        EndpointSpec("POST /_matrix/client/v3/keys/query", "POST", "/_matrix/client/v3/keys/query", "user", payload={"device_keys": {}}),
        EndpointSpec("GET /_synapse/admin/v2/users", "GET", "/_synapse/admin/v2/users", "admin"),
    ]
    results = [benchmark_endpoint(args.url, args.samples, endpoint, args.admin_token, args.user_token) for endpoint in endpoints]
    print_results(results)
    return 1 if any(not result.passed for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
