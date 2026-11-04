## Context
Implement identity and device management APIs: user enrollment, device bind/unbind, revocation, and passkey credential storage.

## Requirements
- User enrollment and device bind/unbind APIs
- Revocation immediately invalidates device trust; cascades to sessions
- Passkey credential store: public key, sign counter, RP ID, origin, user handle
- Re-enrollment creates a new device identity
- Audit event written on enrollment, bind, revoke

## Acceptance Criteria
- [ ] User enrollment API functional
- [ ] Device bind/unbind/revocation APIs functional
- [ ] Revoked device cannot authorize new requests
- [ ] Revocation cascades to active sessions
- [ ] Passkey credential store matches WebAuthn requirements

## References
- `docs/domain-model.html` — Identity and device objects
- `docs/functional-requirements.md` — FR-04, FR-05
- Team: Backend & AI | Priority: Core
