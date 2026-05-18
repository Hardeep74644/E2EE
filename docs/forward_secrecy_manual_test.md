<!-- Purpose: Manual verification procedure for forward secrecy behavior in Matrix deployment (FR-E2EE-04, NFR-SEC-02) -->
# Forward secrecy manual test

1. Start the stack and verify Synapse responds:
   ```bash
   docker compose --env-file .env up -d
   curl http://localhost:8008/_matrix/client/versions
   ```
2. Register two test users and upload keys:
   ```bash
   python3 scripts/register_user.py --url http://localhost:8008 --username alice --password 'StrongPass123!'
   python3 scripts/register_user.py --url http://localhost:8008 --username bob --password 'StrongPass123!'
   ```
3. Exchange encrypted messages between both users using Element clients.
4. Run ciphertext network verification:
   ```bash
   SYNAPSE_BASE_URL=http://localhost:8008 bash scripts/verify_ciphertext.sh
   ```
5. Run DB plaintext leakage inspection:
   ```bash
   python3 scripts/db_inspect.py --db-path /path/to/homeserver.db
   ```
6. Confirm both checks report PASS and archive evidence in `docs/benchmark_results/`.
