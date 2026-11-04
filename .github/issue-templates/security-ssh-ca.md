## Context
Implement the SSH Certificate Authority (CA) that issues short-lived SSH certificates (minutes, not days) to replace permanent SSH keys.

## Requirements
- SSH CA implementation (certificate issuance and revocation)
- Short-lived certificates: expiry in minutes, not days (exactly 5 minutes / 300 seconds)
- Certificate issuance API per OpenAPI SSH tag
- Revocation immediately invalidates certificates
- No permanent SSH keys stored on client devices
- Integration with SSH helper CLI and SecureVault

## Acceptance Criteria
- [ ] SSH CA issues short-lived certificates
- [ ] Certificates expire in exactly 300 seconds (5 minutes)
- [ ] Revocation immediately invalidates certificates
- [ ] No permanent SSH keys required on client
- [ ] Integration with SSH helper and SecureVault works
- [ ] Issuance latency ≤ 2 seconds

## References
- `docs/flow-ssh-certificate.html` — SSH certificate issuance flow
- `docs/functional-requirements.md` — FR-07
- Team: Security & Hardware | Priority: Core
