<!-- Purpose: Document system architecture, data flows, and protocol choices for capstone review (FR-DOC-01, NFR-DOC-01) -->
# System architecture

## Overview

The Secure End-to-End Encrypted (E2EE) Messaging System is designed as an integration-first capstone implementation that combines proven Matrix components rather than inventing a custom protocol stack. The platform uses a Synapse homeserver as the protocol engine, Element-compatible Matrix clients for end users, and an operations-focused admin dashboard for governance and monitoring. This approach gives the team a professional repository with realistic deployment workflows, measurable controls, and defensible security boundaries while still leaving room for capstone-specific automation and verification.

Architecturally, the system is split into three practical zones. The client zone contains user devices that hold long-term identity keys and perform all message encryption/decryption. The application zone contains Synapse and the admin dashboard, where authenticated API requests are accepted, validated, and routed. The data zone contains SQLite (development) or PostgreSQL (production-ready) persistence for event metadata, account state, and server management records. nginx acts as the ingress reverse proxy, preserving TLS and forwarding headers required for secure edge behavior and operational visibility.

This separation supports the project’s core goals: preserve confidentiality by keeping plaintext off the server path, enforce role boundaries through explicit admin API controls, and provide reproducible evidence via scripts and tests. Rather than claiming theoretical security, the repository emphasizes executable checks that tie directly to functional and non-functional requirements.

## Level 0 DFD description

At the Level 0 data flow view, three external actors interact with the system boundary: **End User**, **Administrator**, and **Federated Matrix Peer**. End Users authenticate through Matrix client APIs and exchange room events. Their clients generate and manage E2EE key material and submit encrypted message envelopes. The Administrator interacts with protected Synapse admin endpoints (for version info, user lifecycle control, room inventory, and audit records) through the dedicated dashboard client.

Inside the boundary, Synapse is the central processing node that validates tokens, enforces policy, and persists protocol artifacts. Events and account records are written to the database backend, while media and transient runtime assets are managed under Synapse data storage paths. nginx forwards incoming HTTP traffic to Synapse and adds standard forwarding metadata needed for secure policy handling upstream. Outbound data includes API responses, health telemetry, audit events, and federation traffic to trusted Matrix peers.

## Level 1 DFD description

At Level 1, the system is decomposed into three main process chains.

**1) Account onboarding and key publishing:** A user registration process (manual client flow or `scripts/register_user.py`) sends `POST /_matrix/client/v3/register` with credentials. Synapse creates user and device records and issues an access token. The client then posts a key bundle to `/_matrix/client/v3/keys/upload`, publishing identity and one-time keys required for secure session establishment.

**2) Secure messaging flow:** Clients query peer key state and claim one-time keys through Matrix key endpoints before creating Olm sessions. Messages are encrypted on the client and submitted as room events where encrypted payload fields are transported and stored. Synapse brokers delivery and synchronization but does not need message plaintext for normal operation.

**3) Administrative governance flow:** The admin dashboard first validates privilege scope using `/_synapse/admin/v1/server_version`. If authorized, it can list users, suspend/unsuspend accounts, inspect room inventories, and view audit streams. Unauthorized tokens are rejected and cleared by the dashboard guard logic. This path supports both operational safety and auditability.

## Cryptographic protocol (X3DH + Double Ratchet)

The project adopts Matrix’s established Olm/Megolm implementation model, which follows an X3DH-style prekey-based session setup and Double Ratchet style per-message key evolution. This is essential for capstone reliability: the team avoids cryptographic reimplementation risk and relies on audited ecosystem behavior.

**X3DH-style setup:** During session bootstrap, the sender retrieves recipient key material (identity keys and signed one-time keys). Using local private inputs and recipient public prekeys, the client derives a shared secret without exposing raw keying material to the server. In Matrix deployments this behavior is executed through standard APIs and client crypto libraries.

**Double Ratchet progression:** Once a secure session exists, each message advances key state so compromise of one key does not reveal previous or future messages. In group contexts, Megolm provides scalable encrypted group session behavior. Forward secrecy expectations are operationally validated through one-time-key tests and database leakage checks in this repository.

## Data model summary

- **User**: Account principal with identity, profile metadata, and privilege state (admin/deactivated flags).
- **Device**: Per-client endpoint bound to a user, including device identifiers and key registration lifecycle.
- **PreKeyBundle**: Identity and signed one-time key material published for session initiation.
- **MessageEnvelope**: Event container carrying encrypted content and metadata for routing, ordering, and history sync.
- **AdminAuditLog**: Immutable administrative action records containing actor, operation, target, and timestamp context.

## Technology selection rationale

Selecting Matrix (Synapse + Element ecosystem) over a custom Signal-protocol implementation is a deliberate engineering tradeoff aligned with INFO 4190/4290 integration objectives. Custom secure messaging stacks require specialized cryptographic engineering, extensive formal validation, and long-term maintenance burden that exceed normal capstone timelines. Matrix provides mature specifications, interoperable APIs, existing server/client implementations, and well-known cryptographic primitives through Olm/Megolm.

This choice enables the team to focus on integration quality: infrastructure reproducibility, policy enforcement, operational observability, and automated verification artifacts. It also improves educational value because students can demonstrate real-world systems engineering—deployment, API security, requirements traceability, and performance analysis—while still delivering a meaningful E2EE platform. In short, Matrix reduces unnecessary protocol risk and increases confidence that project outcomes are robust, testable, and professionally maintainable.
