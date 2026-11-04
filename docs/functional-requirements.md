## 1. How to read this register

Each requirement has an identifier, a priority from the project scope, an owning team, a testable statement, and acceptance criteria. **Core** requirements are required for the defence. **Add-on** requirements strengthen the thesis if the core is stable. **Stretch** requirements are attempted only after the core and add-ons are demonstrably working.

The register is deliberately narrow: only web applications and SSH servers are protected. Kubernetes, databases, email security, AI-agent governance, SWG, CASB, DLP, remote browser isolation, and firewall-as-a-service are out of scope and must not appear in the implementation.

## 2. Core requirements

| ID | Requirement | Priority | Owner | Acceptance criteria |
|---|---|---|---|---|
| FR-01 | **Passkey enrollment.** A user can register a FIDO2 credential with user verification. The credential is bound to the user and the enrolled device. | Core | Security & Hardware, Frontend | Enrollment completes in the lab; duplicate credentials are rejected; no private key leaves the authenticator; an audit event is written. |
| FR-02 | **Passkey login.** The login portal completes a WebAuthn ceremony and the server verifies challenge, origin, RP ID, user-verification flag, and signature counter. | Core | Frontend, Backend & AI | Valid assertion creates a session; replayed or expired challenges fail; counter regression is denied and the credential is revoked; p95 login ≤ 3 s. |
| FR-03 | **Login portal and session cookie.** The portal shows device status, access requests, and the current session. The session cookie is HttpOnly, Secure, and SameSite=Lax. | Core | Frontend | Idle timeout is 15 minutes; absolute lifetime is 8 hours; logout invalidates the server-side session; the cookie is never readable by JavaScript. |
| FR-04 | **Device posture agent.** A background agent reports OS version, disk-encryption state, root/jailbreak state, and a signed timestamp. | Core | Frontend | Reports arrive within 60 s of a change; tampering is detectable; the report contains no file contents or browsing data. |
| FR-05 | **Device enrollment and revocation.** An administrator enrolls a device; a user binds it to their account; revocation immediately invalidates its trust. | Core | Frontend, Backend & AI | A revoked device cannot authorize; revocation cascades to sessions; re-enrollment creates a new device identity. |
| FR-06 | **Web reverse proxy as PEP.** Every HTTP request to a protected app is authorized by the Policy Engine or validated against a short-lived session decision. Direct access to protected apps is blocked. | Core | Networking | No bypass path from the lab network; p95 proxy overhead ≤ 50 ms; a kill closes in-flight traffic within 2 s. |
| FR-07 | **Policy Engine decision API.** A single `/authorize` endpoint evaluates hard gates, risk, policy, and trust band, and returns decision, reasons, obligations, and audit correlation. | Core | Backend & AI | Same input yields the same decision; explicit deny overrides allow; p95 ≤ 80 ms at 500 concurrent sessions; every response has an audit ID. |
| FR-08 | **Policy authoring and versioning.** Administrators can draft, validate, publish, and roll back policies. Published versions are immutable. | Core | Backend & AI, Frontend | Publishing is atomic; decisions record policy ID and version; rollback restores the prior version; every change is audited. |
| FR-09 | **Rule-based risk scoring.** The scorer implements the signal catalog, category caps, 0–100 clamp, and four trust bands. | Core | Backend & AI | Each signal has a unit test; score is reproducible from the stored signal list; hard gates cannot be outvoted by arithmetic. |
| FR-10 | **Continuous session evaluation.** Live sessions are re-scored on a 60-second heartbeat and on posture, policy, device, or anomaly events. | Core | Backend & AI | A score change reaches the enforcement points within 2 s; step-up and kill transitions are recorded; missed heartbeats are handled. |
| FR-11 | **Policy Administrator.** The administrator opens sessions, closes them, revokes SSH certificates, and performs an idempotent kill. | Core | Backend & AI, Networking | Kill returns the same result on retry; proxy and SSH paths are both closed; an admin alert and audit event are emitted. |
| FR-12 | **SSH Certificate Authority.** The CA issues certificates valid for one host and about 30 minutes, bound to a principal, source address, and key. The CA private key stays in an HSM or equivalent. | Core | Security & Hardware | Certificate fails after 30 minutes, from a different source address, or for a different host; the CA key is never exported; issuance is audited. |
| FR-13 | **SSH helper CLI.** `ssh myserver` obtains a certificate, optionally sends the SPA knock, invokes the system SSH client, and removes ephemeral keys. | Core | Networking | No static keys in `authorized_keys`; p95 certificate acquisition ≤ 300 ms; failures print an actionable reason code. |
| FR-14 | **Hash-chained audit log and verifier.** Every decision and lifecycle event is appended to a SHA-256 chain; a verifier detects edits, deletions, or reordering. | Core | Security & Hardware | A tamper test is detected at the exact sequence number; sequence numbers are gap-free; the application role has no UPDATE or DELETE grant. |
| FR-15 | **Admin dashboard.** Administrators can manage policies, devices, live sessions, the approval queue, and the kill switch. | Core | Frontend | Kill is one click plus confirmation; live state refreshes within 2 s; role-based access prevents viewers from killing sessions. |
| FR-16 | **Live latency dashboard.** Per-check timings for passkey, risk, policy, proxy, and SSH issuance are visible with p50/p95. | Core | Frontend, Networking | Data is at most 5 s old; each request has a trace ID; the dashboard distinguishes decision time from network time. |
| FR-17 | **SecureVault.** Users can store and share team credentials; access is policy-checked and audited. | Core | Frontend, Backend & AI | Secrets are encrypted with AES-256-GCM; shares have an expiry and recipient; plaintext is never written to logs; no permanent SSH keys are stored. |
| FR-18 | **Audit retention and export.** Audit events can be exported as JSONL and retained for the lab period. | Core | Security & Hardware | Export verifies the chain before writing; exported records preserve sequence and hashes; retention is documented. |
| FR-19 | **API security baseline.** Every API uses authenticated sessions or bearer tokens, rate limits, idempotency keys for mutations, and a consistent error envelope. | Core | Backend & AI | 401/403/429 responses are correct; replay of a mutation with the same key is safe; OpenAPI lint passes in CI. |

## 3. Add-on requirements

| ID | Requirement | Priority | Owner | Acceptance criteria |
|---|---|---|---|---|
| FR-20 | **Just-in-time access requests.** A request in the 40–59 band, or one forced by policy, enters an approval queue with a 15-minute SLA and a 30-minute single-use grant. | Add-on | Backend & AI, Frontend | Requester cannot approve their own request; expired requests cannot be approved; grant is consumed once; every transition is audited. |
| FR-21 | **ML anomaly layer.** An Isolation Forest baseline produces a bounded deduction; a supervised model is considered after enough labelled incidents exist. | Add-on | Backend & AI | p95 inference ≤ 15 ms; model never overrides a hard gate; shadow mode runs before enforcement; metrics are reported. |
| FR-22 | **k-of-n Shamir recovery.** The vault secret is split into five shares; any three rebuild it, two reveal nothing. | Add-on | Security & Hardware, Frontend | Two shares fail; three succeed; shares are stored separately; rebuild is rate-limited and audited; shares rotate after use. |
| FR-23 | **Attack demo panel.** Scripted scenarios replay a stolen certificate, connect from a compromised device, attempt impossible travel, and show the block. | Add-on | Security & Hardware, Frontend | Each scenario is reproducible; the expected reason code is displayed; no production data is used; results are recorded. |
| FR-24 | **SSH session recording.** Optional command and output recording for privileged SSH sessions, encrypted at rest and access-controlled. | Add-on | Security & Hardware | Recording starts automatically for flagged resources; playback requires an approver role; retention is configurable; secrets are redacted. |
| FR-25 | **Policy what-if tester.** A draft policy can be evaluated against historical decisions without enforcing it. | Add-on | Backend & AI, Frontend | Read-only; p95 ≤ 2 s for a 30-day sample; shows deltas by decision and band; explains the matching rule. |

## 4. Stretch requirements

| ID | Requirement | Priority | Owner | Acceptance criteria |
|---|---|---|---|---|
| FR-26 | **Single Packet Auth.** A signed single packet opens the SSH port for one source IP for a few seconds. | Stretch | Networking | Scanners see a closed port; a replayed packet fails; the port closes automatically; the helper falls back cleanly. |
| FR-27 | **SPIFFE/SPIRE service identity.** Internal services receive short-lived workload identities and use mTLS instead of static service tokens. | Stretch | Networking, Backend & AI | SVIDs rotate; policy binds to the workload identity; an expired SVID fails closed. |

## 5. Non-functional requirements

| ID | Requirement | Target | Verification |
|---|---|---|---|
| NFR-01 | Authorization latency | p95 ≤ 80 ms at 500 concurrent sessions | Load test with recorded traffic |
| NFR-02 | Proxy overhead | p95 ≤ 50 ms per request | Latency dashboard and benchmark |
| NFR-03 | Kill propagation | p95 ≤ 2 s from decision to proxy close | Timed attack scenario |
| NFR-04 | Availability | 99.5% in the lab | Health checks and incident log |
| NFR-05 | Cryptographic hygiene | TLS 1.3 in transit; AES-256-GCM at rest; Argon2id for vault passwords; keys in HSM/KMS | Configuration review and key-ceremony test |
| NFR-06 | Privacy | No raw biometrics, packet payloads, or file contents in logs or audit | Log inspection and schema review |
| NFR-07 | Audit integrity | SHA-256 chain; no UPDATE/DELETE grants; 1-year retention | Tamper test and database role inspection |
| NFR-08 | Scale | 500 concurrent sessions; 100 requests/s through the proxy; 50 certificates/minute | Load test |
| NFR-09 | Accessibility | WCAG 2.1 AA for the portal and dashboards | Keyboard, contrast, and screen-reader checks |
| NFR-10 | Operability | Health endpoints, structured logs, metrics, and runbooks | Game day and on-call review |
| NFR-11 | Testability | Unit, integration, and end-to-end tests; deterministic fixtures; scripted attacks | CI pipeline and coverage report |
| NFR-12 | Portability | Docker Compose lab on Linux; no cloud lock-in | Clean-machine rebuild |
| NFR-13 | Maintainability | Typed API contracts, OpenAPI contract tests, decision records | Review checklist |
| NFR-14 | Claims discipline | No FIDO certification claim; no production-deployment claim | Documentation review |

## 6. Out of scope

The following are explicitly excluded. No requirement, diagram, or API operation may imply them:

- Secure web gateway (SWG), CASB, data loss prevention (DLP), remote browser isolation, and firewall-as-a-service.
- Access to Kubernetes clusters or databases. Only web apps and SSH servers are protected.
- Email security and AI-agent governance.
- Production deployment, real company data, or real users beyond test participants.
- FIDO certification of the custom passkey.
- Multi-tenancy or hosting ZeroGate as a service for many organizations.

## 7. Ownership

| Team | Members | Owns |
|---|---|---|
| Security & Hardware | Abdelrehman Fouad | Custom passkey, SSH CA, audit chain, k-of-n recovery, threat model, attack scenarios |
| Networking | Abdelrehman Hamdy, Mohamed Elsayed | Web reverse proxy, SSH path, SSH helper CLI, Single Packet Auth, lab environment |
| Backend & AI | Mohamed Hashem, Dai Yasser, Rewan Fathy | Policy Engine, Policy Administrator, identity, APIs, JIT workflow, risk scoring and ML |
| Frontend | Mohamed Abdelwahed, Sara Mohamed, Malak Osama, Amna Waleed | Login portal, admin and latency dashboards, attack demo panel, SecureVault, posture agent |

## 8. Traceability

| Requirement group | Design artefact |
|---|---|
| FR-01–FR-05 | Passkey sequence, domain model, identity schema, device state machine |
| FR-06–FR-11 | Component diagram, policy activity, session state machine, kill sequence |
| FR-12–FR-13 | SSH certificate sequence, access schema, certificate table |
| FR-14, FR-18 | Audit chain schema, database schema page, risk report explainability contract |
| FR-15–FR-17 | Admin console component, latency dashboard, SecureVault, access schema |
| FR-19 | OpenAPI specification, API page, error envelope |
| FR-20 | JIT approval sequence, JIT state machine, JIT API |
| FR-21 | Risk scoring report, ML model card, `/risk/evaluate` |
| FR-22 | Identity schema `recovery_shares`, vault recovery API |
| FR-23 | Attack demo API, kill and SSH sequences |
| FR-24 | SSH sequence, audit schema, recording API extension |
| FR-25 | Policy what-if API, policy authoring flow |
| FR-26–FR-27 | Component diagram, SPA endpoint, service identity notes |

## 9. Definition of done

A requirement is done when:

1. The happy path and at least one failure path are demonstrated in the lab.
2. The decision and lifecycle events appear in the audit chain with a correlation ID.
3. The acceptance criteria are covered by an automated test or a scripted scenario.
4. The relevant diagram and OpenAPI operation agree with the implementation.
5. The limitation is written down if the implementation is a lab simplification.
