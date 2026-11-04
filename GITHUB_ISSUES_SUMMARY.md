# ZeroGate Project — GitHub Issues Summary

**Project Repository:** https://github.com/mohamed-hashem182005/ZeroGate  
**Created:** November 4, 2026  
**Total Issues:** 28 (22 Core, 4 Add-on, 0 Stretch)

---

## 📊 Issues by Team

### 🔧 Backend & AI Team (7 issues)
| # | Title | Priority | Labels |
|---|-------|----------|--------|
| #2 | Policy Engine — /v1/authorize decision endpoint | Core | `team/backend`, `priority/core` |
| #3 | Policy Administrator — session lifecycle & JIT workflow | Core | `team/backend`, `priority/core` |
| #4 | Identity & device management APIs | Core | `team/backend`, `priority/core` |
| #5 | Rule-based risk scoring engine | Core | `team/backend`, `team/ai`, `priority/core` |
| #6 | ML anomaly adjustment model | Core | `team/backend`, `team/ai`, `priority/core` |
| #7 | OpenAPI contract implementation | Core | `team/backend`, `priority/core` |
| #8 | Hash-chained audit log (backend) | Core | `team/backend`, `team/security`, `priority/core` |

**Team Members:** Mohamed Hashem, Dai Yasser, Rewan Fathy

---

### 🎨 Frontend Team (6 issues)
| # | Title | Priority | Labels |
|---|-------|----------|--------|
| #9 | Login portal — WebAuthn passkey UI | Core | `team/frontend`, `priority/core` |
| #10 | Admin dashboard | Core | `team/frontend`, `priority/core` |
| #11 | Live latency dashboard | Core | `team/frontend`, `priority/core` |
| #12 | Attack demo panel | Add-on | `team/frontend`, `priority/add-on` |
| #13 | SecureVault desktop app | Core | `team/frontend`, `priority/core` |
| #14 | Device posture agent | Core | `team/frontend`, `priority/core` |

**Team Members:** Mohamed Abdelwahed, Sara Mohamed, Malak Osama, Amna Waleed

---

### 🔐 Security & Hardware Team (5 issues)
| # | Title | Priority | Labels |
|---|-------|----------|--------|
| #15 | Custom FIDO2 passkey integration | Core | `team/security`, `priority/core` |
| #16 | SSH Certificate Authority | Core | `team/security`, `priority/core` |
| #17 | Hash-chained audit log (cryptographic) | Core | `team/security`, `priority/core` |
| #18 | k-of-n Shamir Secret Sharing recovery | Core | `team/security`, `priority/core` |
| #19 | Threat model & attack scenarios | Add-on | `team/security`, `priority/add-on` |

**Team Member:** Abdelrehman Fouad

---

### 🌐 Networking Team (4 issues)
| # | Title | Priority | Labels |
|---|-------|----------|--------|
| #20 | Web reverse proxy (PEP) | Core | `team/networking`, `priority/core` |
| #21 | SSH helper CLI | Core | `team/networking`, `priority/core` |
| #22 | Single Packet Auth (SPA) | Add-on | `team/networking`, `priority/add-on` |
| #23 | Lab environment setup | Core | `team/networking`, `priority/core` |

**Team Members:** Abdelrehman Hamdy, Mohamed Elsayed

---

### 🗄️ Database Team (3 issues - cross-team)
| # | Title | Priority | Labels |
|---|-------|----------|--------|
| #24 | PostgreSQL schema — identity slice | Core | `team/database`, `priority/core` |
| #25 | PostgreSQL schema — access slice | Core | `team/database`, `priority/core` |
| #26 | PostgreSQL schema — audit slice | Core | `team/database`, `priority/core` |

**Team Members:** Cross-team effort (all teams contribute)

---

### 🤖 AI Team (2 issues)
| # | Title | Priority | Labels |
|---|-------|----------|--------|
| #27 | Trust score ML model | Core | `team/ai`, `priority/core` |
| #28 | Model card & explainability contract | Core | `team/ai`, `priority/core` |

**Team Members:** Backend & AI team members (Mohamed Hashem, Dai Yasser, Rewan Fathy)

---

## 🎯 Key Performance Targets (Embedded in Issues)

| Metric | Target | Relevant Issues |
|--------|--------|-----------------|
| **Login Latency** | p95 ≤ 3 seconds | #2, #9 |
| **Authorization Decision (uncached)** | p95 ≤ 100 ms | #2 |
| **Authorization Decision (cached)** | p95 ≤ 10 ms | #20 |
| **SSH Certificate Issuance** | ≤ 2 seconds | #16 |
| **Audit Log Append** | ≤ 20 ms | #8, #17 |
| **ML Risk Inference** | ≤ 100 ms | #6, #27 |
| **Session Idle Timeout** | 15 minutes | #3, #9 |
| **Session Absolute Timeout** | 8 hours | #3, #9 |
| **SSH Certificate Validity** | 5 minutes (300 seconds) | #16, #21 |

---

## 🔒 Critical Security Requirements

### Cryptographic Standards
- **WebAuthn:** ES256 (ECDSA P-256 + SHA-256) or RS256
- **Audit Chain:** SHA-256 with RFC 8785 canonical JSON
- **SPA Knock:** HMAC-SHA256 with 5-minute time window
- **SSH CA:** ED25519 or RSA-SHA2-512
- **Shamir SSS:** k-of-n over GF(2^8)

### Hard Gates (Cannot Be Overridden)
- Unknown credential → Immediate deny
- Counter regression → Deny + revoke credential
- Device revoked → Deny
- Policy explicit deny → Deny

### Trust Score Bands
- **ALLOW:** 80–100
- **STEP_UP:** 60–79
- **APPROVAL:** 40–59
- **DENY:** 0–39

---

## 📋 Next Steps

### For Project Manager
1. **Assign Team Members:** Use GitHub's assignee feature to assign specific team members to each issue
2. **Set Milestones:** Create milestones (e.g., "Sprint 1: Core Infrastructure", "Sprint 2: Frontend & Auth")
3. **Create Project Board:** Set up a GitHub Project board with columns: Backlog, In Progress, In Review, Done
4. **Prioritize Core Issues:** Focus on Core priority issues first (22 issues) before Add-on features

### For Each Team
1. **Review Your Issues:** Each team should review their assigned issues
2. **Break Down Tasks:** For complex issues, create sub-tasks or checklists
3. **Estimate Effort:** Add time estimates to each issue
4. **Identify Dependencies:** Link related issues (e.g., Frontend #9 depends on Backend #2)

### Critical Dependencies
- **Frontend #9** (Login Portal) depends on **Backend #2** (Policy Engine) and **Backend #4** (Identity APIs)
- **Networking #20** (Web Proxy) depends on **Backend #2** (Policy Engine)
- **Networking #21** (SSH Helper) depends on **Security #16** (SSH CA)
- **Frontend #13** (SecureVault) depends on **Security #18** (Shamir Recovery) and **Security #16** (SSH CA)
- **All teams** depend on **Database #24, #25, #26** (Schema implementation)

### Quick Links
- **Repository:** https://github.com/mohamed-hashem182005/ZeroGate
- **Issues:** https://github.com/mohamed-hashem182005/ZeroGate/issues
- **Documentation:** `D:/Graduation_project/docs/`
- **Design Diagrams:** `D:/Graduation_project/docs/diagrams/`
- **OpenAPI Spec:** `D:/Graduation_project/docs/openapi.yaml`

---

## 📖 Reference Documentation

All issues reference the following core documents from your project:
- `docs/functional-requirements.md` — All FR-XX requirements with acceptance criteria
- `docs/openapi.yaml` — Complete API contract (all endpoints)
- `docs/risk-scoring-report.md` — Trust scoring model and signal catalog
- `docs/architecture.html` — Component architecture and zones
- `docs/database-schema.html` — PostgreSQL physical schema
- `docs/flow-*.html` — Sequence diagrams for key flows
- `docs/diagrams/*.pdf` — Visual architecture and data model diagrams

---

## 🎓 Defense Preparation Notes

For your graduation defense:
1. **Demonstrate Core Requirements First:** All 22 Core issues must be complete and demonstrable
2. **Prepare Lab Demo:** Issues #2, #9, #16, #20 are critical for live demonstration
3. **Explainability is Key:** Issues #5, #6, #27, #28 require clear explanations of scoring decisions
4. **Security Verification:** Be ready to demonstrate issues #15, #17 (counter regression, tamper detection)
5. **Performance Metrics:** Latency dashboard (#11) must show all targets met

---

**Project:** ZeroGate — Zero Trust Access Broker
