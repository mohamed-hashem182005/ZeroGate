## Context
Implement the hash-chained audit log: an append-only, tamper-evident chain where every decision and lifecycle event is appended with correlation IDs. Audit append performance target: ≤ 20ms.

## Requirements
- Append-only hash-chained audit events table
- Every decision and lifecycle event appended with correlation IDs
- Verifier endpoint to validate chain integrity
- Export tooling for audit logs
- Tamper-evident: any modification breaks the chain
- SHA-256 hashing with canonical JSON (RFC 8785)

## Acceptance Criteria
- [ ] Audit events appended with hash chain
- [ ] Correlation IDs on every decision and lifecycle event
- [ ] Chain verifier endpoint functional
- [ ] Export tooling available
- [ ] Tamper detection verified (modification breaks chain)
- [ ] Append latency ≤ 20ms

## References
- `docs/openapi.yaml` — Audit tag
- `docs/functional-requirements.md` — FR-10
- Team: Backend & AI + Security | Priority: Core
