# E2EE Messaging Platform
### KPU INFO 4190 — Integration Project I — Group 7

A self-hosted, end-to-end encrypted (E2EE) messaging web application built on the [Matrix Protocol](https://matrix.org), powered by the **Synapse** homeserver, **Element Web** client, **Nginx** reverse proxy, and **PostgreSQL** database — containerized with **Docker Compose** and developed natively on **Apple Silicon (ARM64 / M1)**.

---

## Team Members

| Name | Role |
|---|---|
| Mankaran Pal Singh | Backend & Synapse Configuration |
| Hardeep Singh | Security & STRIDE Threat Modelling |
| Vishavdeep Singh | Frontend & Element Web Integration |
| Gurjinder Singh | DevOps & Docker/Nginx Infrastructure |

---

## Architecture Overview

```
Alice's Browser ──HTTPS/TLS 1.3──► Nginx Reverse Proxy ──► Synapse Homeserver ──► PostgreSQL
    (Element Web + libolm E2EE)         (port 443)           (Matrix API)          (ciphertexts only)
Bob's Browser ───HTTPS/TLS 1.3──►       │
    (Element Web + libolm E2EE)         └──► Element Web (static SPA)
```

All message encryption/decryption happens **client-side** in the browser using [libolm](https://gitlab.matrix.org/matrix-org/olm) (WebAssembly). The Synapse server and PostgreSQL database **never see plaintext messages**.

---

## Cryptographic Design

| Protocol | Purpose |
|---|---|
| **X3DH** (Extended Triple Diffie-Hellman) | Initial session key agreement |
| **Double Ratchet** | Forward secrecy + post-compromise security per message |
| **Olm** | 1-to-1 E2EE sessions (wraps X3DH + Double Ratchet) |
| **Megolm** | Group E2EE (shared ratchet for room efficiency) |

---

## Stack

| Component | Image | Purpose |
|---|---|---|
| **Synapse** | `matrixdotorg/synapse:latest` | Matrix homeserver — auth, key distribution, relay |
| **PostgreSQL 15** | `postgres:15-alpine` | Database — stores only encrypted event blobs |
| **Nginx** | `nginx:alpine` | TLS termination, reverse proxy, Admin API blocking |
| **Element Web** | `vectorim/element-web:latest` | React SPA client with libolm E2EE |

All images use `platform: linux/arm64` for native Apple M1 performance.

---

## Quick Start (Development)

> **Prerequisites:** Docker Desktop with Apple Silicon support, `docker compose` v2+

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/e2ee-messaging-platform.git
cd e2ee-messaging-platform

# 2. Generate Synapse signing key (first-time only)
docker run --rm \
  -v "$(pwd)/config:/data" \
  --platform linux/arm64 \
  matrixdotorg/synapse:latest generate

# 3. Generate self-signed TLS cert for local dev
./scripts/generate-dev-cert.sh

# 4. Start the stack
docker compose up -d

# 5. Verify all containers are healthy
docker compose ps

# 6. Create the first admin user
docker compose exec synapse \
  register_new_matrix_user http://localhost:8008 \
  -c /data/homeserver.yaml \
  --admin -u admin -p your_secure_password

# 7. Open Element Web
open https://localhost
```

---

## Project Phase

| Phase | Status | Description |
|---|---|---|
| Phase 1 | ✅ Complete | Project Proposal |
| Phase 2 | ✅ Complete | Requirements & Architecture (DFD, ERD) |
| Phase 3 | ✅ Complete | Security Design (STRIDE threat model) |
| Phase 4 | ✅ Complete | Literature Review & Tech Report |
| Phase 5 | 🔄 In Progress | Docker Stack Setup & E2EE Verification |
| Phase 6 | ⏳ Planned | Custom React Front-End |

---

## Security Properties

- **Registration disabled** — No public sign-ups; admin-only account creation
- **Federation disabled** — Closed private deployment; no inter-server traffic
- **TLS 1.3 only** — Nginx rejects TLS 1.0/1.1/1.2
- **Admin API blocked** — `/_synapse/admin/*` returns 403 for all external requests
- **PostgreSQL stores ciphertexts only** — E2EE enforced client-side via libolm
- **bcrypt_rounds: 12** — Brute-force resistant password hashing

---

## Documentation

| Document | Location |
|---|---|
| Project Proposal | `docs/proposal/` |
| Requirements Report (with DFD) | `docs/requirements/` |
| STRIDE Threat Model | `docs/security/STRIDE.md` |
| Literature Review | `docs/literature-review/` |
| Technical Report | `docs/technical-report/` |

---

## License

Academic project — KPU INFO 4190, Spring 2026. Not for production use without security review.
