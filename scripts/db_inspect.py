#!/usr/bin/env python3
"""Purpose: Inspect Synapse DB message events for plaintext leakage indicators (FR-E2EE-03, NFR-SEC-02)."""

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from typing import Iterable

import psycopg2
from psycopg2.extensions import connection as PgConnection

QUERY = "SELECT event_id, type, content FROM events WHERE type='m.room.message'"


@dataclass
class MessageRow:
    """Represents a room message row pulled from Synapse storage."""

    event_id: str
    event_type: str
    content: str


def parse_args() -> argparse.Namespace:
    """Parse CLI args for SQLite or PostgreSQL source selection."""
    parser = argparse.ArgumentParser(description="Inspect message events for plaintext content leaks.")
    parser.add_argument("--db-path", help="Path to Synapse SQLite database")
    parser.add_argument("--postgres-url", help="PostgreSQL URL, e.g. postgresql://user:pass@host:5432/db")
    args = parser.parse_args()
    if bool(args.db_path) == bool(args.postgres_url):
        parser.error("Provide exactly one of --db-path or --postgres-url")
    return args


def fetch_rows_sqlite(db_path: str) -> list[MessageRow]:
    """Fetch room message rows from SQLite backend."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(QUERY)
        return [MessageRow(event_id=row[0], event_type=row[1], content=row[2] or "") for row in cursor.fetchall()]
    finally:
        conn.close()


def fetch_rows_postgres(postgres_url: str) -> list[MessageRow]:
    """Fetch room message rows from PostgreSQL backend."""
    conn: PgConnection = psycopg2.connect(postgres_url)
    try:
        with conn.cursor() as cursor:
            cursor.execute(QUERY)
            rows = cursor.fetchall()
        return [MessageRow(event_id=row[0], event_type=row[1], content=row[2] or "") for row in rows]
    finally:
        conn.close()


def normalize_content(raw_content: str) -> str:
    """Normalize JSON or text content into comparable lowercase string."""
    try:
        parsed = json.loads(raw_content)
        return json.dumps(parsed, separators=(",", ":")).lower()
    except (TypeError, json.JSONDecodeError):
        return str(raw_content).lower()


def detect_plaintext_leaks(rows: Iterable[MessageRow]) -> list[MessageRow]:
    """Find message events that contain body fields without ciphertext fields."""
    leaks: list[MessageRow] = []
    for row in rows:
        content = normalize_content(row.content)
        if '"body"' in content and '"ciphertext"' not in content:
            leaks.append(row)
    return leaks


def print_report(total: int, leaks: list[MessageRow]) -> None:
    """Print inspection summary table and verdict."""
    verdict = "PASS" if not leaks else "FAIL"
    print("+------------------------+----------------+")
    print("| Metric                 | Value          |")
    print("+------------------------+----------------+")
    print(f"| Total events checked   | {total:<14} |")
    print(f"| Plaintext leaks found  | {len(leaks):<14} |")
    print(f"| Verdict                | {verdict:<14} |")
    print("+------------------------+----------------+")
    if leaks:
        print("Potential plaintext events:")
        for row in leaks:
            print(f"- {row.event_id}")


def main() -> int:
    """Execute database inspection and return process status code."""
    args = parse_args()
    rows = fetch_rows_sqlite(args.db_path) if args.db_path else fetch_rows_postgres(args.postgres_url)
    leaks = detect_plaintext_leaks(rows)
    print_report(len(rows), leaks)
    return 1 if leaks else 0


if __name__ == "__main__":
    raise SystemExit(main())
