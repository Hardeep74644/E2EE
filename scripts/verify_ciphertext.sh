#!/usr/bin/env bash
# Purpose: Capture Synapse traffic and verify ciphertext-only transport heuristically (FR-E2EE-02, NFR-SEC-02)

set -euo pipefail

if ! command -v tcpdump >/dev/null 2>&1; then
  echo "FAIL: tcpdump is required" >&2
  exit 1
fi

if ! command -v tshark >/dev/null 2>&1 && ! command -v strings >/dev/null 2>&1; then
  echo "FAIL: tshark or strings is required" >&2
  exit 1
fi

if [[ -z "${SYNAPSE_BASE_URL:-}" ]]; then
  echo "FAIL: SYNAPSE_BASE_URL is not set" >&2
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${REPO_ROOT}/docs/benchmark_results"
mkdir -p "${LOG_DIR}"
LOG_FILE="${LOG_DIR}/ciphertext_verify_$(date +%Y%m%d).log"
TMP_CAPTURE="$(mktemp)"

PORT="8008"

echo "[$(date -Iseconds)] Starting 30s capture on port ${PORT}" | tee -a "${LOG_FILE}"
if ! timeout 30 tcpdump -A -s 0 -ni any "tcp port ${PORT}" >"${TMP_CAPTURE}" 2>>"${LOG_FILE}"; then
  echo "[$(date -Iseconds)] WARN: tcpdump timeout or non-zero exit during bounded capture" | tee -a "${LOG_FILE}"
fi

if command -v tshark >/dev/null 2>&1; then
  MATCHES="$(tshark -r "${TMP_CAPTURE}" -V | strings | grep -Ei "\\b(the|and|hello|message|body)\\b" || true)"
else
  MATCHES="$(strings "${TMP_CAPTURE}" | grep -Ei "\\b(the|and|hello|message|body)\\b" || true)"
fi
PACKET_COUNT="$(grep -c "IP " "${TMP_CAPTURE}" || true)"

if [[ -n "${MATCHES}" ]]; then
  echo "FAIL: plaintext heuristic matched potential cleartext" | tee -a "${LOG_FILE}"
  echo "${MATCHES}" | tee -a "${LOG_FILE}"
  rm -f "${TMP_CAPTURE}"
  exit 1
fi

echo "PASS: no plaintext heuristic matches detected (packets=${PACKET_COUNT})" | tee -a "${LOG_FILE}"
rm -f "${TMP_CAPTURE}"
exit 0
