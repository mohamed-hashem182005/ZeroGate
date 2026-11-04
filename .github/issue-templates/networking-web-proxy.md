## Context
Implement the web reverse proxy as the Policy Enforcement Point (PEP). Every HTTP request to a protected app must be authorized by the Policy Engine or validated against a short-lived session decision. Direct access to protected apps must be blocked.

## Requirements
- Web reverse proxy as PEP per NIST SP 800-207
- Every HTTP request authorized by Policy Engine (`POST /v1/authorize`) or validated against short-lived session decision
- Block direct access to protected apps (no bypass path exists)
- Integration with Policy Engine for real-time authorization
- TLS termination and re-encryption to backend
- Request context forwarding (identity, device ID, session ID)

## Acceptance Criteria
- [ ] Every HTTP request to protected app passes through proxy
- [ ] No bypass path exists (direct access blocked)
- [ ] Authorization via Policy Engine or session validation works
- [ ] TLS termination and re-encryption functional
- [ ] Lab demo: happy path + denial path both enforced
- [ ] Cached authorization verification ≤ 10ms

## References
- `docs/functional-requirements.md` — FR-06
- `docs/architecture.html` — Component architecture
- Team: Networking | Priority: Core
