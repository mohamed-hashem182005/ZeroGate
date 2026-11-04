# ZeroGate — Backend & AI Team Roadmap

## Team Responsibilities
- Policy Engine and authorization logic
- Session management and JIT workflows
- Risk scoring engine (rule-based + ML)
- Identity and device management APIs
- Complete OpenAPI implementation
- Audit log backend integration

---

## 📋 Issues Assigned to Backend Team

### Phase 1: Foundation (Week 1-2)
**Priority: CRITICAL — Other teams depend on these**

#### Issue #7: OpenAPI Contract Implementation
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 1 week  

**Tasks:**
- [ ] Set up backend framework (Node.js/Python/Java - choose one)
- [ ] Implement API skeleton for all endpoints from `docs/openapi.yaml`
- [ ] Set up request/response validation middleware
- [ ] Implement standard error envelope format
- [ ] Create `/health` endpoint
- [ ] API documentation generation (Swagger UI)
- [ ] Unit tests for validation logic

**Deliverables:**
- Working API server with all endpoint stubs
- Swagger UI accessible at `/api-docs`
- Health check returns `200 OK`

**Dependencies:**
- Database schemas (#24, #25, #26) should be ready

---

#### Issue #4: Identity & Device Management APIs
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 1 week  

**Tasks:**
- [ ] Implement user enrollment endpoint (`POST /v1/users`)
- [ ] Device bind/unbind endpoints (`POST /v1/devices/{deviceId}/bind`)
- [ ] Device revocation endpoint (`POST /v1/devices/{deviceId}/revoke`)
- [ ] Passkey credential storage (public key, sign counter, RP ID, origin)
- [ ] Cascade revocation logic (device → sessions → certs)
- [ ] Audit event generation on enrollment/bind/revoke
- [ ] Integration tests with database

**Deliverables:**
- All identity/device CRUD operations working
- Revocation cascade verified
- Audit events written to chain

**Dependencies:**
- Database #24 (Identity slice)
- Issue #7 (OpenAPI skeleton)

---

### Phase 2: Core Authorization (Week 3-4)
**Priority: CRITICAL — This is the heart of the system**

#### Issue #2: Policy Engine — /v1/authorize Decision Endpoint ⭐
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 weeks  

**Tasks:**
- [ ] Implement `POST /v1/authorize` endpoint
- [ ] Hard gate evaluation logic (before arithmetic):
  - Unknown credential → Deny
  - Counter regression → Deny + revoke
  - Device revoked → Deny
  - Policy explicit deny → Deny
- [ ] Trust score integration (call Risk Scoring service)
- [ ] Trust band mapping (ALLOW/STEP_UP/APPROVAL/DENY)
- [ ] Explainable decision response (reason codes + signals)
- [ ] Audit log integration (every decision logged)
- [ ] Performance optimization (target: p95 ≤ 100ms uncached)
- [ ] Load testing (50 concurrent requests)

**Deliverables:**
- `/v1/authorize` returns correct decisions
- Hard gates work correctly
- p95 latency ≤ 100ms (uncached)
- Lab demo: happy path + denial path both logged

**Dependencies:**
- Issue #4 (Identity APIs)
- Issue #5 (Risk Scoring) — can develop in parallel with mock scores
- Database #25 (Access slice)

---

#### Issue #3: Policy Administrator — Session Lifecycle & JIT Workflow
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 1.5 weeks  

**Tasks:**
- [ ] Session creation after passkey auth
- [ ] Session state machine (ACTIVE → STEP_UP → KILLED → EXPIRED)
- [ ] Heartbeat endpoint (`POST /v1/sessions/{sessionId}/heartbeat`)
- [ ] Session kill endpoint (`POST /v1/sessions/{sessionId}/kill`)
- [ ] JIT request creation (`POST /v1/jit/requests`)
- [ ] JIT approval/deny workflow
- [ ] JIT state machine (PENDING → APPROVED/DENIED/CANCELLED/EXPIRED)
- [ ] Session timeout enforcement (15min idle, 8hr absolute)
- [ ] Cache invalidation on kill
- [ ] Integration tests for all state transitions

**Deliverables:**
- Session CRUD operations working
- Heartbeat response ≤ 50ms
- JIT workflow end-to-end functional
- Mid-session kill takes effect immediately

**Dependencies:**
- Issue #2 (Policy Engine)
- Database #25 (Access slice)

---

### Phase 3: Risk & Security (Week 5-6)

#### Issue #5: Rule-based Risk Scoring Engine
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 1.5 weeks  

**Tasks:**
- [ ] Implement additive scoring model (start at 100)
- [ ] Signal evaluation for all categories:
  - Identity signals (ID-01 to ID-05)
  - Device signals (DV-01 to DV-07)
  - Network signals (NW-01 to NW-06)
  - Behavioral signals (BH-01 to BH-02)
- [ ] Hard gate evaluation (before arithmetic)
- [ ] Category caps implementation
- [ ] ML adjustment integration (bounded at -15)
- [ ] Reason codes generation
- [ ] Performance optimization (target: ≤ 20ms per score)
- [ ] Unit tests for each signal

**Deliverables:**
- Score calculation works for all signal combinations
- Every point attributable to named signal
- Score calculation ≤ 20ms
- Explainable output (reason codes + deductions)

**Dependencies:**
- Issue #4 (Identity APIs)
- `docs/risk-scoring-report.md` (signal catalog)

---

#### Issue #8: Hash-chained Audit Log (Backend)
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 1 week  

**Tasks:**
- [ ] Audit event append logic
- [ ] Canonical JSON serialization (RFC 8785)
- [ ] Hash calculation (SHA-256)
- [ ] Chain linking (prev_hash → curr_hash)
- [ ] Genesis event initialization
- [ ] Append-only enforcement (no updates/deletes)
- [ ] Verifier endpoint (`POST /v1/audit/verify`)
- [ ] Export endpoint (`POST /v1/audit/export`)
- [ ] Concurrency-safe sequence numbering
- [ ] Performance testing (append ≤ 20ms)

**Deliverables:**
- Every event appends with correct hash
- Verifier detects tampering
- Export produces valid JSONL
- Append latency ≤ 20ms

**Dependencies:**
- Database #26 (Audit slice)
- Security Team #17 (cryptographic implementation)

---

#### Issue #6: ML Anomaly Adjustment Model
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 weeks  

**Tasks:**
- [ ] Feature engineering (time-of-day, geo-distance, login velocity, etc.)
- [ ] Model selection (Isolation Forest / LightGBM)
- [ ] Training pipeline setup
- [ ] Model versioning system
- [ ] Shadow mode implementation (logs only, no score impact)
- [ ] Canary deployment (10% traffic)
- [ ] Inference endpoint (`POST /v1/risk/evaluate`)
- [ ] Bounded adjustment (-15 to 0)
- [ ] Model card documentation
- [ ] Performance testing (inference ≤ 100ms)

**Deliverables:**
- ML model produces anomaly scores
- Adjustment always bounded in [-15, 0]
- Shadow mode works without affecting decisions
- Inference latency ≤ 100ms

**Dependencies:**
- Issue #5 (Risk Scoring integration point)
- AI Team #27, #28 (Model documentation)

---

## 🔄 After Core Issues Complete (Week 7+)

### Integration & Testing
- [ ] End-to-end testing with Frontend (login flow)
- [ ] End-to-end testing with Networking (proxy authorization)
- [ ] Performance benchmarking (all targets met)
- [ ] Security testing (OWASP Top 10)
- [ ] Load testing (500 concurrent users)

### Code Quality
- [ ] Code review for all PRs
- [ ] Test coverage ≥ 80%
- [ ] API documentation complete
- [ ] Deployment scripts ready

### Optimization
- [ ] Database query optimization
- [ ] Caching strategy (Redis for session/policy decisions)
- [ ] Rate limiting implementation
- [ ] Monitoring and alerting setup

### Documentation
- [ ] Architecture decision records (ADRs)
- [ ] API usage examples
- [ ] Deployment guide
- [ ] Troubleshooting guide

---

## 📊 Success Metrics

- ✅ p95 login ≤ 3 seconds (end-to-end with Frontend)
- ✅ Authorization decision ≤ 100ms (uncached)
- ✅ Authorization decision ≤ 10ms (cached)
- ✅ Audit append ≤ 20ms
- ✅ Risk score calculation ≤ 20ms
- ✅ ML inference ≤ 100ms
- ✅ All 7 issues closed
- ✅ Test coverage ≥ 80%
- ✅ Zero critical security vulnerabilities

---

## 🔗 Critical Dependencies

**Blocks these teams:**
- Frontend Team (needs #2, #4 for login)
- Networking Team (needs #2 for proxy)
- Security Team (integrates with #8)
- AI Team (integrates with #5, #6)

**Blocked by:**
- Database Team (#24, #25, #26) — MUST be ready first

---

## 📅 Recommended Timeline

```
Week 1-2:  #7 (OpenAPI) + #4 (Identity)
Week 3-4:  #2 (Policy Engine) + #3 (Sessions/JIT)
Week 5-6:  #5 (Risk Scoring) + #8 (Audit)
Week 7-8:  #6 (ML Model)
Week 9-10: Integration + Testing + Optimization
```

---

## 💡 Tips for Backend Team

1. **Start with database coordination** — Meet with Database Team on Day 1
2. **API-first development** — Get #7 done fast so Frontend can start
3. **Mock dependencies early** — Don't wait for Risk Scoring to finish Policy Engine
4. **Write tests first** — TDD for critical logic (Policy Engine, Risk Scoring)
5. **Performance from day 1** — Profile every endpoint
6. **Security mindset** — Input validation, SQL injection prevention, rate limiting
7. **Documentation as you go** — Don't leave it to the end

---

**Generated:** 2026-11-04  
**Repository:** https://github.com/mohamed-hashem182005/ZeroGate  
**Team:** Backend & AI
