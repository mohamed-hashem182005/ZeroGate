## Context
Implement all `/v1/*` operations per the OpenAPI 3.1.0 contract. Tags: Auth, Devices, Authorization, Sessions, SSH, JIT, Policies, Risk, Audit, Vault, Operations, Attack Lab.

## Requirements
- Implement all endpoints defined in `docs/openapi.yaml`
- Standard error envelope for all endpoints
- Request/response validation per schema
- Content negotiation and versioning
- Health endpoint under Operations tag

## Acceptance Criteria
- [ ] All `/v1/*` endpoints implemented per OpenAPI spec
- [ ] Standard error envelope used consistently
- [ ] Request/response validated against schemas
- [ ] `/health` endpoint returns service status
- [ ] OpenAPI spec and implementation stay in sync

## References
- `docs/openapi.yaml` — Full API contract
- Team: Backend & AI | Priority: Core
