## Context
Implement session lifecycle management and Just-In-Time (JIT) access workflows per the Policy Administrator design. Sessions are created after successful passkey auth, heartbeated during use, and can be killed mid-session on risk spikes.

## Requirements
- Session create / heartbeat / kill APIs
- JIT access request → approval → grant → expiry flow
- Mid-session kill: invalidate session and SSH certificate on risk spike
- Session cookie: HttpOnly, Secure, SameSite=Lax; idle timeout 15 min; absolute lifetime 8 hours
- Revocation cascades to sessions and SSH certs

## Acceptance Criteria
- [ ] Session CRUD APIs implemented per OpenAPI
- [ ] JIT request/approve/grant/expiry workflow functional
- [ ] Mid-session kill invalidates session and SSH cert
- [ ] Revocation cascades to all active sessions for a device/user
- [ ] Idle timeout (15 min) and absolute lifetime (8 hours) enforced server-side

## References
- `docs/flow-jit-approval.html` — JIT approval flow
- `docs/flow-session-kill.html` — Session kill flow
- `docs/state-device.html` — Device state machine
- Team: Backend & AI | Priority: Core
