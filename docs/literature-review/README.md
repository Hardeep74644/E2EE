# Literature Review — Existing E2EE Messaging Solutions
## KPU INFO 4190 Group 7

> Full academic document: see `Literature_Review_Group7.docx` (submitted to KPU)

---

## Summary of Findings

This literature review surveyed five major E2EE messaging platforms to identify architectural gaps that justify building a custom self-hosted solution.

### Platforms Reviewed

| Platform | Encryption | Self-Hostable | Open Source | Metadata Privacy |
|---|---|---|---|---|
| Signal | Olm/Double Ratchet | ❌ | ✅ Server | ✅ High |
| Telegram (secret chats) | MTProto 2.0 | ❌ | ❌ | ❌ Low |
| WhatsApp | Signal Protocol | ❌ | ❌ | ❌ Very Low |
| Wire | Proteus (Double Ratchet) | ✅ Enterprise | ✅ | ✅ Medium |
| Matrix/Synapse | Olm + Megolm | ✅ Free | ✅ | ✅ Medium |

### Four Critical Gaps Identified

1. **Centralization Trap**: Signal, WhatsApp, and Telegram all require the corporation's servers to function. Even if the cryptography is sound, the infrastructure dependency violates sovereignty.

2. **Metadata Leakage**: WhatsApp shares metadata (who talks to whom, when, how often) with Meta. Telegram logs IP addresses, device info, and contact graphs.

3. **Auditability Gap**: Telegram (non-secret chats) uses server-side encryption; the MTProto 2.0 protocol was found to have multiple vulnerabilities in Albrecht et al. (2022). Closed-source servers cannot be independently audited.

4. **No Free Self-Hosting**: Wire Enterprise requires paid licensing for self-hosted deployment. Matrix/Synapse is the only platform that is simultaneously open-source, freely self-hostable, E2EE by default, and audited.

### Conclusion

**Matrix/Synapse with Element Web** uniquely satisfies all requirements: open protocol (Matrix v1.7), audited cryptography (NCC Group 2016, Marlinspike & Perrin 2016), free self-hosting, and E2EE enforced client-side via libolm — meaning even a compromised server cannot decrypt messages.

---

## Key References

- Albrecht, M. R., Mareková, L., Paterson, K. G., & Stepanovs, I. (2022). Four attacks and a proof for Telegram. *2022 IEEE Symposium on Security and Privacy*, 385–403. https://doi.org/10.1109/SP46214.2022.9833564

- Marlinspike, M., & Perrin, T. (2016). *The Double Ratchet Algorithm*. Signal Foundation. https://signal.org/docs/specifications/doubleratchet/

- NCC Group. (2016). *Cryptographic review of the Olm and Megolm cryptographic ratchets*. https://www.nccgroup.com/media/5bspr3ie/_ncc_group_olm_cryptogrpahic_review_2016_11_01-1.pdf

- Cohn-Gordon, K., Cremers, C., Dowling, B., Garratt, L., & Stebila, D. (2020). A formal security analysis of the Signal messaging protocol. *Journal of Cryptology, 33*(4), 1914–1983. https://doi.org/10.1007/s00145-020-09360-1

---
*Reference corrections applied April 17, 2026:*
- *Albrecht et al. corrected from inaccurate ePrint attribution to peer-reviewed IEEE S&P 2022 paper*
- *NCC Group URL updated to canonical nccgroup.com link (not matrix.org-hosted copy)*

