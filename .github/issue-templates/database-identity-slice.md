## Context
Implement the PostgreSQL physical schema for the identity slice: users, credentials, and devices, with explicit delete semantics per the database schema design.

## Requirements
- Users table (UUID, username, display name, status, timestamps)
- Credentials table (credential ID, public key, sign counter, RP ID, origin, user handle)
- Devices table (device ID, user ID, status, OS version, disk encryption, root status, enrolled at)
- Foreign keys and indexes per design
- Explicit delete semantics (soft delete vs cascade)

## Acceptance Criteria
- [ ] Schema migrations created and run cleanly
- [ ] Foreign keys, unique constraints, and indexes per design
- [ ] Explicit delete semantics implemented
- [ ] Sample seed data provided for lab testing

## References
- `docs/database-schema.html` — Physical PostgreSQL slices
- `docs/diagrams/04-identity-schema.pdf` — Identity schema diagram
- Team: Database (cross-team) | Priority: Core
