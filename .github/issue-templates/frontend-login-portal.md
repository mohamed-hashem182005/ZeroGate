## Context
Implement the login portal with WebAuthn passkey enrollment and authentication. Users must be able to register FIDO2 credentials with user verification and complete login ceremonies.

## Requirements
- Passkey enrollment UI: register a FIDO2 credential with user verification
- Passkey login UI: complete WebAuthn ceremony
- Server verifies challenge, origin, RP ID, user-verification flag, and signature counter
- Display device status, access requests, and current session
- Session cookie: HttpOnly, Secure, SameSite=Lax; idle timeout 15 min; absolute lifetime 8 hours
- Cookie never readable by JavaScript
- Logout invalidates server-side session

## Acceptance Criteria
- [ ] Enrollment completes in lab; duplicate credentials rejected
- [ ] No private key leaves authenticator; audit event written on enrollment
- [ ] Valid assertion creates session; replayed or expired challenges fail
- [ ] Counter regression denied and credential revoked
- [ ] p95 login ≤ 3 seconds
- [ ] Idle timeout (15 min) and absolute lifetime (8 hours) enforced

## References
- `docs/flow-passkey.html` — Passkey login sequence
- `docs/functional-requirements.md` — FR-01, FR-02, FR-03
- Team: Frontend | Priority: Core
