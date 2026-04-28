# Requirements Report — KPU INFO 4190 Group 7

## Functional Requirements

### Client Module (FR-C)

| ID | Requirement |
|---|---|
| FR-C1.1 | The system SHALL provide user registration (admin-initiated only) |
| FR-C1.2 | The system SHALL authenticate users with password-based login |
| FR-C1.3 | The system SHALL allow users to create rooms (1-to-1 and group) |
| FR-C2.1 | The system SHALL encrypt all room messages using Megolm (group E2EE) |
| FR-C2.2 | The system SHALL encrypt all 1-to-1 messages using Olm (pairwise E2EE) |
| FR-C2.3 | The system SHALL perform X3DH key agreement before the first Olm session |
| FR-C3.1 | The system SHALL display delivery receipts |
| FR-C3.2 | The system SHALL support file/image attachments (up to 50MB) |
| FR-C4.1 | The system SHALL provide device cross-signing via Safety Number verification |

### Server Module (FR-S)

| ID | Requirement |
|---|---|
| FR-S1.1 | The system SHALL reject all registration attempts not initiated by an admin |
| FR-S1.2 | The system SHALL store only encrypted message events (m.room.encrypted) in PostgreSQL |
| FR-S2.1 | The system SHALL distribute Olm prekey bundles to requesting clients |
| FR-S2.2 | The system SHALL replenish one-time prekeys (OTKs) when below threshold |
| FR-S3.1 | The system SHALL support Synapse key backup (encrypted client-side) |

### Admin Module (FR-A)

| ID | Requirement |
|---|---|
| FR-A1.1 | The system SHALL provide an admin API for user management (internal network only) |
| FR-A1.2 | The system SHALL block Admin API access from all external (non-Docker) requests |
| FR-A2.1 | The system SHALL expose server health metrics at /_matrix/client/versions |
| FR-A2.2 | The system SHALL log all auth events (login attempts, failures) to file |

## Non-Functional Requirements

| ID | Category | Requirement | Target Metric |
|---|---|---|---|
| NFR-P1 | Performance | p95 message delivery latency (same-server) | < 500ms |
| NFR-P2 | Performance | Olm encrypt/decrypt time per message | < 100ms |
| NFR-S1 | Security | All external traffic encrypted | TLS 1.3 only |
| NFR-S2 | Security | Password hashing | bcrypt rounds ≥ 12 |
| NFR-S3 | Security | Session tokens | Macaroon-based, server-side revocable |
| NFR-R1 | Reliability | System uptime target | ≥ 99.5% (Docker restart policies) |
| NFR-EC1 | Encryption | Algorithms | Olm (X3DH + Double Ratchet), Megolm (AES-256-GCM + HMAC-SHA256) |
| NFR-EC2 | Encryption | Forward secrecy | Every message uses a new Megolm ratchet step |

## System Architecture — Data Flow Diagram (Level 0)

```
                    ┌─────────────────┐
                    │   EXTERNAL USER  │
                    │  (Alice / Bob)   │
                    └────────┬────────┘
                             │ HTTPS (port 443)
                             ▼
                    ┌─────────────────┐
                    │   E2EE MESSAGING │
                    │     PLATFORM     │
                    │   (this system)  │
                    └─────────────────┘
```

## Data Flow Diagram (Level 1)

```
Alice's Browser          Nginx               Synapse              PostgreSQL
(libolm E2EE)       (TLS Termination)    (Homeserver)          (Database)
     │                    │                   │                      │
     │─── HTTPS login ───►│                   │                      │
     │                    │── proxy login ───►│                      │
     │                    │                   │── store session ────►│
     │◄── access token ───│◄── token ─────────│                      │
     │                    │                   │                      │
     │── encrypt msg ─────────────────────►(E2EE in browser)         │
     │── PUT /send ───────►│                  │                      │
     │                    │── proxy PUT ─────►│                      │
     │                    │                   │── store ciphertext ─►│
     │                    │                   │                      │
Bob's Browser                                 │                      │
     │── GET /sync ───────►│                  │                      │
     │                    │── proxy GET ─────►│                      │
     │                    │                   │◄── fetch events ─────│
     │◄── ciphertext ─────│◄── events ────────│                      │
     │── decrypt (libolm)                                            │
     │   (plaintext only in Bob's browser)
```

## Entity Relationship Diagram (simplified)

```
User ──────< Device (1:N)
  │              │
  │              └── DeviceKey (Curve25519 identity, Ed25519 signing, OTKs)
  │
  └───< RoomMember >── Room
                         │
                         └──< EncryptedEvent (m.room.encrypted)
                                  │
                                  └── MegolmSession (in-session key per sender device)
```
