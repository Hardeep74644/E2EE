<!-- Purpose: Infrastructure setup instructions for Synapse, PostgreSQL, and nginx stack (FR-INFRA-01, NFR-OPS-01) -->
# Infrastructure setup

1. Copy environment values:
   ```bash
   cp /home/runner/work/E2EE/E2EE/.env.example /home/runner/work/E2EE/E2EE/.env
   ```
2. Edit `.env` and set `POSTGRES_PASSWORD` to a strong value.
3. Start the stack:
   ```bash
   cd /home/runner/work/E2EE/E2EE/infra
   docker compose --env-file ../.env up -d
   ```
4. Verify Synapse health endpoint:
   ```bash
   curl http://localhost:8008/_matrix/client/versions
   ```
5. For production, update `homeserver.yaml` server name and enable real TLS cert paths.
