## Context
Implement the hash-chained audit log: a tamper-evident cryptographic chain where every lifecycle event and decision is recorded. Any modification breaks the chain.

## Requirements
- Append-only hash-chained audit events
- Every decision and lifecycle event recorded with correlation IDs
- Tamper-evident: any modification breaks the chain
- Verifier tooling to validate chain integrity
- Export tooling for compliance and forensics
- SHA-256 canonical JSON (RFC 8785)

## Acceptance Criteria
- [ ] Audit events appended with hash chain
- [ ] Every decision and lifecycle event logged with correlation IDs
- [ ] Verifier detects tampering (modification breaks chain)
- [ ] Export tooling functional
- [ ] Lab demo: verification passes on unmodified chain, fails on tampered chain
- [ ] Chain verification of 1,000 events ≤ 500ms

## References
- `docs/functional-requirements.md` — FR-08
- Team: Security & Hardware (with Backend & AI) | Priority: Core
