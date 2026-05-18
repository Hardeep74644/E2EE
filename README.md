<!-- Purpose: Primary project documentation and requirements traceability hub (FR-DOC-01, NFR-DOC-01) -->
# Secure End-to-End Encrypted Messaging System (Matrix Protocol)

This repository contains a professional capstone implementation for an INFO 4190/4290 integration project focused on secure messaging with end-to-end encryption. The platform integrates a Synapse homeserver, Element-compatible Matrix APIs, an operational admin dashboard, and verification scripts/tests for RBAC, forward secrecy indicators, and performance requirements. Rather than building custom cryptography, the project emphasizes secure protocol integration, reproducible infrastructure, and auditable validation artifacts.

## Team

Group 7:
- Mankaran Pal Singh — Lead/Architect
- Hardeep Singh — Systems Engineer
- Vishavdeep Singh — Testing/UI
- Gurjinder Singh — Project Manager

## Architecture overview

The system uses Synapse as the Matrix homeserver, nginx as reverse proxy ingress, and PostgreSQL (or SQLite in local dev) for persistence. End-user clients interact through Matrix Client APIs, while a dedicated React admin dashboard consumes Synapse Admin APIs with token-scoped RBAC protections. E2EE key lifecycle operations are validated through scripted checks and pytest integration tests. See `/home/runner/work/E2EE/E2EE/docs/architecture.md` for full DFD and cryptographic flow detail.

## Quick start

1. **Prerequisites**
   ```bash
   docker --version
   docker compose version
   python3 --version
   node --version
   npm --version
   ```
2. **Clone**
   ```bash
   git clone https://github.com/Hardeep74644/E2EE.git
   cd E2EE
   ```
3. **Configure `.env`**
   ```bash
   cp .env.example .env
   # edit .env and set ADMIN_TOKEN, USER_TOKEN, POSTGRES_PASSWORD
   ```
4. **Start infrastructure**
   ```bash
   docker compose --env-file .env up -d
   ```
5. **Connect Element**
   ```text
   Homeserver URL: http://localhost:8008
   ```
6. **Run tests**
   ```bash
   python3 -m pip install -r requirements-test.txt
   pytest tests/ -v
   ```

## Repository structure

```text
secure-e2ee-messaging/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── pyproject.toml
├── requirements-test.txt
├── infra/
│   ├── homeserver.yaml
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── README.md
├── admin-dashboard/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── auth/adminGuard.js
│       ├── api/synapseClient.js
│       └── components/
│           ├── Dashboard.jsx
│           ├── UserTable.jsx
│           ├── AuditLog.jsx
│           └── ServerHealth.jsx
├── scripts/
│   ├── register_user.py
│   ├── verify_ciphertext.sh
│   ├── db_inspect.py
│   └── benchmark_latency.py
├── tests/
│   ├── conftest.py
│   ├── test_rbac.py
│   ├── test_forward_secrecy.py
│   ├── test_otk_replenishment.py
│   └── test_performance.py
└── docs/
    ├── architecture.md
    ├── threat_model.md
    ├── forward_secrecy_manual_test.md
    └── benchmark_results/.gitkeep
```

## Running the test suite

Install dependencies and run pytest:

```bash
python3 -m pip install -r requirements-test.txt
pytest tests/ -v
```

Environment variables:

| Variable | Required | Purpose |
|---|---|---|
| `SYNAPSE_BASE_URL` | Yes | Base URL of Synapse API |
| `ADMIN_TOKEN` | For admin/perf tests | Admin API authentication |
| `USER_TOKEN` | For user/perf tests | Client API authentication |
| `TEST_USER_ID` | For key tests | Target Matrix user ID |
| `POSTGRES_URL` | Optional | DB inspection against PostgreSQL |
| `SYNAPSE_SQLITE_PATH` | Optional | DB inspection against SQLite |

## Security verification

Run traffic plaintext heuristic check:

```bash
SYNAPSE_BASE_URL=http://localhost:8008 bash scripts/verify_ciphertext.sh
```

Run database plaintext leakage check:

```bash
python3 scripts/db_inspect.py --db-path /path/to/homeserver.db
# OR
python3 scripts/db_inspect.py --postgres-url "$POSTGRES_URL"
```

## Requirements traceability

| Requirement | Description | Implemented/Tested In |
|---|---|---|
| FR-ADMIN-01 | Admin dashboard and protected routes | `admin-dashboard/src/App.jsx`, `admin-dashboard/src/auth/adminGuard.js` |
| FR-ADMIN-02 | User management suspend/unsuspend | `admin-dashboard/src/components/UserTable.jsx` |
| FR-ADMIN-03 | Audit visibility | `admin-dashboard/src/components/AuditLog.jsx` |
| FR-INFRA-01 | Synapse + PostgreSQL + nginx stack | `infra/docker-compose.yml`, `infra/homeserver.yaml`, `infra/nginx.conf` |
| FR-E2EE-01 | Registration + key upload workflow | `scripts/register_user.py` |
| FR-E2EE-02 | Ciphertext transport verification | `scripts/verify_ciphertext.sh` |
| FR-E2EE-03 | DB plaintext leakage inspection | `scripts/db_inspect.py`, `tests/test_forward_secrecy.py` |
| FR-RBAC-01 | Non-admin denial to admin APIs | `tests/test_rbac.py`, `admin-dashboard/src/auth/adminGuard.js` |
| NFR-P1 | p95 latency ≤ 500ms | `scripts/benchmark_latency.py`, `tests/test_performance.py` |
| NFR-P2 | Repeatable performance regression checks | `tests/test_performance.py` |

## References

1. Signal Protocol Overview — https://signal.org/docs/
2. Matrix Specification — https://spec.matrix.org/
3. Synapse Documentation — https://matrix-org.github.io/synapse/latest/
4. Olm/Megolm Security Review Materials — https://gitlab.matrix.org/matrix-org/olm
