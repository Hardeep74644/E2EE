# STRIDE Threat Model — KPU INFO 4190 Group 7
## E2EE Messaging Platform

### Methodology

STRIDE is a structured threat modelling framework developed at Microsoft. Each letter identifies a threat category. This analysis maps all six categories to our specific system components and documents the mitigations implemented in the design.

---

## S — Spoofing (Identity Impersonation)

**Threat:** An attacker impersonates Alice to send messages or gain access to her account.

| Attack Vector | Mitigation |
|---|---|
| Stolen credentials (password) | bcrypt_rounds: 12 hashing; login throttling (3 attempts / 15 min) |
| Session token theft | Macaroon tokens (short-lived, server-side revocable); TLS 1.3 in transit |
| MITM key substitution | Safety Number (SHA-256 of identity key pair) — out-of-band verification required |
| Fake Synapse server | Self-signed cert warning + users must trust cert explicitly |

**Residual Risk:** Low. Key substitution is possible if users skip Safety Number verification. Documented in onboarding.

---

## T — Tampering (Data Modification)

**Threat:** An attacker modifies messages in transit or in storage.

| Attack Vector | Mitigation |
|---|---|
| Message in transit modified | TLS 1.3 AEAD (AES-256-GCM) — any modification invalidates MAC |
| Ciphertext tampered in DB | Megolm uses HMAC-SHA256 message authentication — tampering detected client-side |
| homeserver.yaml modified | Docker volume mounts use `:ro` (read-only); secrets managed via environment |
| Nginx config replaced | `:ro` volume mount; container filesystem not writable |

**Residual Risk:** Very Low. Integrity protection at both transport (TLS) and application (Megolm MAC) layers.

---

## R — Repudiation (Denying Actions)

**Threat:** A user denies sending a message or performing an action.

| Attack Vector | Mitigation |
|---|---|
| "I never sent that message" | Synapse logs all event_ids with sender, timestamp, room_id in PostgreSQL |
| Admin denies account deletion | Admin API actions logged to Synapse event stream |
| No audit trail | PostgreSQL events table is append-only (no UPDATE/DELETE on message events) |

**Residual Risk:** Medium. Log integrity not cryptographically guaranteed (no write-once storage). Acceptable for academic scope.

---

## I — Information Disclosure (Privacy Breach)

**Threat:** Sensitive message content is exposed to unauthorized parties.

| Attack Vector | Mitigation |
|---|---|
| Database compromised | PostgreSQL stores only `m.room.encrypted` blobs — no plaintext. Attacker gets useless ciphertext |
| Server admin reads messages | E2EE enforced client-side via libolm — Synapse never holds decryption keys |
| Network eavesdropping | TLS 1.3 with PFS (each session uses ephemeral keys) |
| Metadata leakage (who talks to whom) | Admin API blocked externally; server is closed/private |
| Key backup compromised | Key backup encrypted with user's recovery passphrase — server cannot decrypt |

**Residual Risk:** Low for message content. Medium for metadata (who sends to whom, when) — inherent to any messaging system.

---

## D — Denial of Service (Availability Attack)

**Threat:** The system is made unavailable.

| Attack Vector | Mitigation |
|---|---|
| Login brute force (amplified load) | Nginx rate limit: 5 req/min on `/_matrix/client/v3/login` |
| General API flood | Nginx rate limit: 10 req/s with burst:20 on `/_matrix/*` |
| Large file upload exhausts disk | `client_max_body_size 55M` in Nginx; `max_upload_size: 52428800` in Synapse |
| PostgreSQL connection exhaustion | `cp_max: 10` connection pool limit in homeserver.yaml |
| Container crash loop | `restart: unless-stopped` on all Docker services |

**Residual Risk:** Medium. Sophisticated DDoS beyond scope of this deployment (no CDN or cloud-based scrubbing).

---

## E — Elevation of Privilege (Unauthorized Access Escalation)

**Threat:** A regular user gains admin or root access.

| Attack Vector | Mitigation |
|---|---|
| Exploit Synapse Admin API | Nginx blocks `/_synapse/admin/*` with `deny all` + `return 403` |
| Container escape to host | Docker user namespace isolation; no privileged containers |
| PostgreSQL direct access | Postgres not exposed on host ports — internal Docker network only |
| Read another user's messages | E2EE enforced client-side; Synapse relays ciphertexts only — server cannot read |
| Registration to bypass auth | `enable_registration: false` — no self-registration possible |

**Residual Risk:** Low. Admin API is the highest-value target; defense-in-depth via both Nginx block and internal-only network.

---

## Summary Risk Matrix

| Threat | Likelihood | Impact | Residual Risk | Status |
|---|---|---|---|---|
| Spoofing via stolen password | Medium | High | Low (bcrypt + throttle) | ✅ Mitigated |
| MITM key substitution | Low | High | Medium (requires Safety Number UX) | ⚠️ Partially mitigated |
| Message tampering | Low | High | Very Low (TLS + Megolm MAC) | ✅ Mitigated |
| Repudiation | Medium | Medium | Medium (no cryptographic log integrity) | ⚠️ Accepted |
| DB plaintext exposure | Low | Critical | Very Low (E2EE — no plaintext in DB) | ✅ Mitigated |
| DoS via login flood | High | Medium | Low (Nginx rate limiting) | ✅ Mitigated |
| Admin API exploitation | Low | Critical | Low (Nginx block + private network) | ✅ Mitigated |
| Privilege escalation | Low | High | Low (no privileged containers) | ✅ Mitigated |
