# Technical Report — E2EE Messaging Platform Design
## KPU INFO 4190 Group 7

> Full academic document: see `Technical_Report_Group7.docx` (submitted to KPU)

---

## Olm Cryptographic Protocol Walkthrough

### Phase 1: Session Bootstrapping via X3DH

Before Alice can send Bob an encrypted message for the first time, she must establish a shared secret using the **Extended Triple Diffie-Hellman (X3DH)** protocol.

**Bob's prekey bundle** (uploaded to Synapse on registration):
- `IK_B` — Identity Key (Curve25519, long-term)
- `SPK_B` — Signed Prekey (Curve25519, rotated monthly, signed by IK_B)
- `OPK_B` — One-Time Prekey (Curve25519, single-use, batch uploaded)

**Alice's X3DH computation:**
```
DH1 = DH(IK_A, SPK_B)   -- Alice identity × Bob signed prekey
DH2 = DH(EK_A, IK_B)    -- Alice ephemeral × Bob identity
DH3 = DH(EK_A, SPK_B)   -- Alice ephemeral × Bob signed prekey
DH4 = DH(EK_A, OPK_B)   -- Alice ephemeral × Bob one-time prekey

shared_secret = HKDF(DH1 || DH2 || DH3 || DH4)
```

Both Alice and Bob compute the **same** shared_secret without ever transmitting it. A MITM cannot derive it without Bob's private keys.

### Phase 2: Per-Message Keys via Double Ratchet

Every message uses a **new** symmetric key derived from the Double Ratchet:

1. **Diffie-Hellman Ratchet** — Generates new DH key pairs on each reply, providing **post-compromise security** (if Alice's current key is stolen, future messages are safe after the next DH ratchet step)

2. **Symmetric Key Ratchet** — Derives per-message keys from a chain key using HKDF, providing **forward secrecy** (stealing current key gives no access to past messages)

```
chain_key[n+1] = HMAC-SHA256(chain_key[n], 0x02)
message_key[n] = HMAC-SHA256(chain_key[n], 0x01)
```

### Phase 3: Megolm for Group Messages

Group rooms use **Megolm** — a shared session key per sender per room:

- Alice generates one `MegolmSession` and shares it (Olm-encrypted) with every room member
- Each message advances the Megolm ratchet: forward secrecy per message
- Efficient: one encryption operation per message regardless of room size

---

## Six-Phase Implementation Roadmap

| Phase | Weeks | Deliverable |
|---|---|---|
| 1 | 1–2 | Requirements, DFD, Architecture Design |
| 2 | 3–4 | Docker stack setup, Synapse config, PostgreSQL integration |
| 3 | 5–6 | E2EE verification (DB inspection, packet capture, Safety Number) |
| 4 | 7–9 | Custom React frontend (Login, Registration, Chat, Admin views) |
| 5 | 10–11 | Performance testing (p95 latency target: < 500ms) |
| 6 | 12 | Security hardening review, documentation, final demo |
