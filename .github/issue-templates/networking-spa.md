## Context
Implement Single Packet Auth (SPA) for SSH path concealment. The SPA knock packet temporarily opens the SSH path; without the knock, SSH ports remain closed.

## Requirements
- SPA knock endpoint implementation
- Port knocking for SSH path concealment
- Knock packet opens SSH path temporarily (5 minute time window)
- Integration with SSH helper CLI
- Cryptographically authenticated knock packets (HMAC-SHA256)
- Failed knocks logged to audit chain

## Acceptance Criteria
- [ ] SPA knock endpoint functional
- [ ] SSH path opens only after valid knock
- [ ] Time window for SSH connection after knock (300 seconds)
- [ ] Cryptographically authenticated knocks
- [ ] Failed knocks logged

## References
- `docs/functional-requirements.md` — Single Packet Auth requirement
- Team: Networking | Priority: Add-on
