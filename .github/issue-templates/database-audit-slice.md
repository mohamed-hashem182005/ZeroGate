## Context
Implement the PostgreSQL physical schema for the audit slice: hash-chained audit events table with correlation IDs and tamper-evident chaining.

## Requirements
- Audit events table (event ID, timestamp, correlation ID, event type, actor, target, decision, score, prev_hash, curr_hash)
- Append-only constraints (no updates, no deletes)
- Hash-chaining logic (curr_hash = SHA256(prev_hash + event_data))
- Index on correlation ID and timestamp for fast lookups
- Partitioning strategy (if applicable for long-term storage)

## Acceptance Criteria
- [ ] Audit events table implemented with append-only constraints
- [ ] Hash-chaining logic verified
- [ ] Indexes on correlation ID and timestamp
- [ ] Verifier query/function to validate chain integrity

## References
- `docs/database-schema.html` — Physical PostgreSQL slices
- `docs/functional-requirements.md` — FR-08
- Team: Database (cross-team) | Priority: Core
