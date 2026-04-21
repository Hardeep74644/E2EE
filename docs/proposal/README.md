# Project Proposal — KPU INFO 4190 Group 7

## Project Title
Secure End-to-End Encrypted (E2EE) Messaging Web Application

## Problem Statement

Modern messaging platforms present a fundamental contradiction: they promise privacy while remaining architecturally incapable of delivering it. WhatsApp, Telegram (non-secret chats), and Discord store message metadata or plaintext on centralized servers, creating honeypots for both state surveillance and data breaches. Signal — while cryptographically sound — depends on a centralized corporate infrastructure and requires a phone number, precluding institutional or anonymous deployment.

The gap we identified: **no existing platform combines strong E2EE, full self-hosting capability, open-source auditability, and freedom from third-party infrastructure dependencies.** Institutions like universities, law firms, or healthcare providers that need private internal communications currently have no viable solution.

## Proposed Solution

A self-hosted messaging web application built on the **Matrix protocol** (IETF-standardized federated messaging standard), using:

| Component | Technology |
|---|---|
| Homeserver | Synapse (Python, Matrix reference implementation) |
| Client | Element Web (React SPA with libolm WASM E2EE) |
| Reverse Proxy | Nginx (TLS 1.3 termination) |
| Database | PostgreSQL 15 |
| Containerization | Docker Compose (ARM64-native for Apple M1) |

## Justification for Technology Choices

**Why Matrix over building from scratch?**  
The Olm/Megolm cryptographic protocol has been independently audited by NCC Group (2016) and verified against the formal Double Ratchet specification (Marlinspike & Perrin, 2016). Building our own cryptographic protocol would be academic suicide — "don't roll your own crypto" is a foundational principle of applied cryptography.

**Why self-hosted over Signal?**  
Signal's server code is open-source but the centralized Signal Foundation servers are a mandatory dependency. Self-hosting Synapse gives us full data sovereignty — no third party ever touches our message metadata.

**Why ARM64 (Apple M1)?**  
All four group members develop on Apple Silicon MacBooks. Native ARM64 Docker images prevent QEMU emulation overhead and correctly represent the production deployment environment.

## Scope and Deliverables

1. Fully functional E2EE messaging system running on Docker Compose
2. Cryptographic verification test suite (database inspection + packet capture + Safety Number)
3. Custom React frontend (custom branding, simplified UX vs. default Element Web)
4. Security hardening: TLS 1.3 only, Admin API blocked, federation disabled, registration locked

## Team Roles

| Member | Responsibility |
|---|---|
| Mankaran Pal Singh | Synapse homeserver configuration, PostgreSQL integration |
| Hardeep Singh | Security design, STRIDE threat model, E2EE verification tests |
| Vishavdeep Singh | Frontend development, Element Web integration, UI/UX |
| Gurjinder Singh | Docker/Nginx infrastructure, ARM64 optimization, CI/CD |
