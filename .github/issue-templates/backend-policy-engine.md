## Context
Implement the central zero-trust decision endpoint per the NIST SP 800-207 architecture and the OpenAPI contract. Every request to a protected resource must be authorized by the Policy Engine or validated against a short-lived session decision.

## Requirements
- Implement `POST /v1/authorize` as the central policy decision endpoint
- Evaluate every request against: user passkey identity, device posture, live trust score, and published policy set
- Return an explainable decision (allow/deny) with reason codes and point deductions
- Decisions must be appended to the hash-chained audit log with correlation IDs
- Lab demo required: one happy path + one denial path, both recorded in the audit chain

## Acceptance Criteria
- [ ] `POST /v1/authorize` returns explainable allow/deny decisions
- [ ] Decisions incorporate identity, device posture, trust score, and policy
- [ ] Every decision is logged to the hash-chained audit trail
- [ ] p95 authorize latency meets latency dashboard targets
- [ ] Happy path and denial path both verified in lab demo

## References
- `docs/openapi.yaml` — Authorization tag
- `docs/policy-engine.html` — Policy Engine design
- `docs/functional-requirements.md` — FR-06 (Web reverse proxy PEP)
- Team: Backend & AI | Priority: Core
