## Context
Implement the PostgreSQL physical schema for the access slice: policies, sessions, JIT requests, and certificates.

## Requirements
- Policies table (policy ID, version, rule definitions, published status)
- Sessions table (session ID, user ID, device ID, created at, last active, expiry, status)
- JIT requests table (request ID, user ID, target, duration, reason, status, approved by)
- Certificates table (serial number, user ID, target, issued at, expires at, revoked)
- Explicit delete semantics per design

## Acceptance Criteria
- [ ] Schema migrations created and run cleanly
- [ ] Tables for policies, sessions, JIT, certificates implemented
- [ ] Status transitions align with state machines in design docs
- [ ] Foreign keys and indexes per design

## References
- `docs/database-schema.html` — Physical PostgreSQL slices
- `docs/diagrams/05-access-schema.pdf` — Access schema diagram
- Team: Database (cross-team) | Priority: Core
