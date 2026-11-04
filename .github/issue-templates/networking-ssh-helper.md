## Context
Implement the SSH helper CLI: a wrapper that sends SPA knock packets and gets short-lived SSH certificates from the CA before connecting. Users type `ssh myserver` as usual; the helper handles cert acquisition transparently.

## Requirements
- SSH helper CLI wrapper
- Sends SPA knock packet to open SSH path
- Requests short-lived SSH certificate from CA
- Transparent to user: `ssh myserver` works as usual
- No permanent SSH keys stored on disk
- Certificate automatically used for SSH connection

## Acceptance Criteria
- [ ] `ssh myserver` works with helper installed
- [ ] SPA knock sent before SSH connection
- [ ] Short-lived cert requested from CA
- [ ] No permanent SSH keys on client
- [ ] SSH connection succeeds with short-lived cert

## References
- `docs/functional-requirements.md` — FR-07
- `docs/flow-ssh-certificate.html` — SSH certificate issuance flow
- Team: Networking | Priority: Core
