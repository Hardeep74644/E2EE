<!-- Purpose: STRIDE threat model and mitigation verification map for security assurance (FR-SEC-01, NFR-SEC-02) -->
# Threat model (STRIDE)

| STRIDE Category | Threat example | Mitigation | Verification method |
|---|---|---|---|
| Spoofing | Attacker reuses stolen non-admin token to access admin APIs | RBAC checks on `/_synapse/admin/*`, adminGuard token validation, token separation for admin/user contexts | `tests/test_rbac.py` ensures user tokens receive 401/403 on admin routes |
| Tampering | Malicious actor alters traffic in transit | TLS termination at nginx with strict transport and forwarded header controls; Matrix message signing and encrypted payloads | `scripts/verify_ciphertext.sh` checks capture stream for plaintext heuristics and flags anomalies |
| Repudiation | Admin denies account suspension action | Audit trail retrieval in dashboard plus Synapse admin event records | `admin-dashboard/src/components/AuditLog.jsx` and `getAuditLog()` provide inspectable action history |
| Information Disclosure | Plaintext message body appears in server database | Client-side E2EE via Olm/Megolm, database inspection for leakage indicators, upload limits | `scripts/db_inspect.py` scans for `"body"` without `"ciphertext"`; exercised by `tests/test_forward_secrecy.py` |
| Denial of Service | Excessive payloads or request floods degrade service | `max_upload_size` constraints, reverse proxy controls, resource-isolated compose stack | `infra/homeserver.yaml` + `scripts/benchmark_latency.py` monitor service responsiveness |
| Elevation of Privilege | Regular user gains admin dashboard access | `adminGuard` validates admin endpoint access and clears invalid tokens | `admin-dashboard/src/auth/adminGuard.js` and `tests/test_rbac.py` |

## Out of scope threats

1. **Physical device compromise:** If an attacker gains full device/root access, they may read currently decrypted local content. Endpoint hardening and hardware-backed key storage are out of scope for this capstone.
2. **Post-quantum attacks:** This project follows current Matrix cryptographic baselines and does not implement post-quantum migration or hybrid key exchange.
