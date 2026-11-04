## Context
Integrate the custom FIDO2 passkey hardware: fingerprint matching on-device, secure chip signs login challenges, private key never leaves chip.

## Requirements
- Custom FIDO2 hardware key integration
- Fingerprint matched on the key (not sent to server)
- Secure chip signs login challenge
- Private key never leaves the chip
- Duplicate credential rejection
- Audit event written on enrollment
- Counter regression detection and credential revocation

## Acceptance Criteria
- [ ] Enrollment completes in lab with custom hardware
- [ ] Duplicate credentials rejected
- [ ] Private key never leaves authenticator
- [ ] Fingerprint never reaches server
- [ ] Audit event written on enrollment
- [ ] Counter regression triggers revocation

## References
- `docs/functional-requirements.md` — FR-01, FR-02
- `docs/flow-passkey.html` — Passkey login sequence
- Team: Security & Hardware | Priority: Core
