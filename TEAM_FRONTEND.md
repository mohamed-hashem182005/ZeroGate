# ZeroGate — Frontend Team Roadmap

## Team Responsibilities
- Login portal with WebAuthn passkey UI
- Admin dashboard (policies, devices, sessions, kill button)
- Live latency monitoring dashboard
- Attack demonstration panel
- SecureVault desktop application (Java/JavaFX)
- Device posture agent (background service)

---

## 📋 Issues Assigned to Frontend Team

### Phase 1: Independent Work (Week 1-2)
**Can start immediately — no dependencies**

#### Issue #14: Device Posture Agent
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 1.5 weeks  

**Tasks:**
- [ ] Background service implementation (no UI)
- [ ] OS version detection (Windows/macOS/Linux)
- [ ] Disk encryption status check:
  - Windows: BitLocker status
  - macOS: FileVault status
  - Linux: LUKS status
- [ ] Root/jailbreak detection
- [ ] Signed timestamp generation
- [ ] Report transmission to `POST /v1/devices/{deviceId}/posture`
- [ ] Change detection (trigger on system changes)
- [ ] Heartbeat (every 24 hours)
- [ ] Offline queue (retry when connection restored)
- [ ] Resource optimization (< 50MB RAM, < 1% CPU)
- [ ] Installer/uninstaller scripts

**Deliverables:**
- Agent binary for target platforms
- Reports within 60s of system change
- No sensitive data in reports
- Tamper detection working

**Dependencies:**
- None (can start immediately)
- Eventually integrates with Backend #4

---

### Phase 2: Core Authentication UI (Week 3-4)
**Priority: CRITICAL — Required for system demo**

#### Issue #9: Login Portal — WebAuthn Passkey UI ⭐
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 weeks  

**Tasks:**
- [ ] Login page UI design
- [ ] WebAuthn enrollment flow:
  - Call `POST /v1/auth/passkey/options` (purpose: registration)
  - Invoke `navigator.credentials.create()`
  - Submit attestation to backend
  - Display success/error messages
- [ ] WebAuthn authentication flow:
  - Call `POST /v1/auth/passkey/options` (purpose: authentication)
  - Invoke `navigator.credentials.get()`
  - Submit assertion to `POST /v1/auth/passkey/verify`
  - Redirect to dashboard on success
- [ ] Session cookie handling (HttpOnly - never read in JS)
- [ ] User dashboard:
  - Device status badge (COMPLIANT/NON_COMPLIANT/QUARANTINED/REVOKED)
  - Trust score display (0-100 with color coding)
  - Active obligations list
  - Session lifetime countdown
- [ ] Idle timeout warning (at 13 minutes)
- [ ] Logout functionality
- [ ] Error handling (cancel, timeout, hardware unsupported)
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Performance testing (total flow ≤ 3 seconds)

**Deliverables:**
- End-to-end passkey enrollment works
- End-to-end login works (p95 ≤ 3s)
- Session timeouts enforced (15min idle, 8hr absolute)
- Private key never exposed to JavaScript

**Dependencies:**
- Backend #2 (Policy Engine)
- Backend #4 (Identity APIs)
- Security #15 (FIDO2 integration)

---

### Phase 3: Management Interfaces (Week 5-7)

#### Issue #10: Admin Dashboard
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 weeks  

**Tasks:**
- [ ] Admin authentication and role verification
- [ ] Policy management UI:
  - Policy list view (GET /v1/policies)
  - Policy editor (create/edit)
  - Policy versioning display
  - Policy publish button
  - What-if testing interface (POST /v1/policies/test)
- [ ] Device management UI:
  - Device list with status
  - Device enrollment form
  - Device revocation button (with confirmation)
  - Device details view (posture history)
- [ ] Live sessions view:
  - Real-time session list (poll or SSE)
  - Session details (user, device, trust score, start time)
  - Kill button (POST /v1/sessions/{sessionId}/kill)
  - Kill confirmation modal
- [ ] Admin overview panel:
  - Active users count
  - Service health status
  - Recent security events
- [ ] Responsive design (desktop + tablet)

**Deliverables:**
- Admins can manage policies end-to-end
- Device enrollment/revocation works
- Kill button terminates sessions immediately
- Real-time session updates

**Dependencies:**
- Backend #2, #3, #4 (APIs)
- Issue #9 (login for admin access)

---

#### Issue #11: Live Latency Dashboard
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 1 week  

**Tasks:**
- [ ] Real-time metrics collection (GET /v1/operations/metrics)
- [ ] Per-endpoint latency display:
  - `/v1/authorize` (target: ≤ 100ms)
  - `/v1/auth/passkey/verify` (target: ≤ 3s)
  - `/v1/sessions/heartbeat` (target: ≤ 50ms)
  - `/v1/ssh/certificates` (target: ≤ 2s)
- [ ] Enforcement point latency (proxy)
- [ ] P95 percentile calculation
- [ ] Time-series charts (last 1hr, 24hr, 7d)
- [ ] Target threshold indicators (green/yellow/red)
- [ ] Alert when targets exceeded
- [ ] Auto-refresh (every 10 seconds)

**Deliverables:**
- Real-time latency monitoring
- All targets displayed and tracked
- Historical trends visible
- p95 login ≤ 3s verified

**Dependencies:**
- Backend #2, #3, #4 (running endpoints)
- Networking #20 (proxy metrics)

---

#### Issue #13: SecureVault Desktop App
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 weeks  

**Tasks:**
- [ ] Fork and adapt existing `mohamed-hashem182005/SecureVault` repo
- [ ] Credential storage and encryption (Java)
- [ ] Team credential sharing:
  - Vault create/open
  - Add credentials (username/password/notes)
  - Share vault with team members
- [ ] SSH certificate request:
  - Request short-lived cert from CA (POST /v1/ssh/certificates)
  - Display cert expiry countdown
  - Auto-refresh before expiry
- [ ] k-of-n Shamir recovery UI:
  - Split secret interface (choose k, n)
  - Display shares to holders (never store on server)
  - Rebuild interface (collect k shares)
- [ ] Platform-specific builds (Windows .exe, macOS .app, Linux .deb)
- [ ] Auto-update mechanism

**Deliverables:**
- Desktop app runs on target platforms
- Credentials stored securely
- SSH cert request works
- Shamir split/rebuild functional

**Dependencies:**
- Security #16 (SSH CA)
- Security #18 (Shamir implementation)
- Backend #4 (Vault APIs)

---

### Phase 4: Add-ons & Demo (Week 8-9)

#### Issue #12: Attack Demo Panel
**Status:** 🟡 Not Started  
**Priority:** Add-on  
**Estimated Time:** 1 week  

**Tasks:**
- [ ] Attack scenario selector dropdown
- [ ] Scenario execution:
  - Replay attack (reuse old challenge)
  - Counter regression (manipulate signCount)
  - Session hijack attempt (steal cookie)
  - MITM simulation (tamper with request)
- [ ] Real-time visualization:
  - Attack detection event stream
  - Trust score drop animation
  - Session kill trigger
  - Audit log entries
- [ ] Explainable decision display:
  - Reason codes highlighted
  - Point deductions breakdown
  - Final decision (DENY/KILL)
- [ ] Reset button (clean state for next demo)

**Deliverables:**
- 4 attack scenarios working
- Detection visualized in real-time
- Explainable output displayed

**Dependencies:**
- Backend #2 (Policy Engine decisions)
- Backend #5 (Risk Scoring signals)
- Security #19 (Attack scenarios)

---

## 🔄 After Core Issues Complete (Week 10+)

### Testing & Quality
- [ ] Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- [ ] Responsive design testing (desktop, tablet, mobile)
- [ ] Accessibility compliance (WCAG 2.1 AA):
  - Keyboard navigation
  - Screen reader support
  - Color contrast
  - Focus indicators
- [ ] Usability testing with real users
- [ ] Performance optimization (bundle size, lazy loading)

### Integration
- [ ] End-to-end testing with Backend
- [ ] Error handling and edge cases
- [ ] Loading states and skeleton screens
- [ ] Offline handling (graceful degradation)

### Documentation
- [ ] User documentation (how to enroll, login, manage devices)
- [ ] Admin documentation (policy management, session monitoring)
- [ ] Setup guide for SecureVault
- [ ] Device agent installation guide
- [ ] Video tutorials (enrollment, login, JIT approval)

---

## 📊 Success Metrics

- ✅ p95 login flow ≤ 3 seconds (end-to-end)
- ✅ WebAuthn works on all major browsers
- ✅ Admin dashboard real-time updates work
- ✅ Session kill takes effect immediately
- ✅ Latency dashboard shows all targets
- ✅ SecureVault runs on all target platforms
- ✅ Device agent runs silently (< 50MB RAM, < 1% CPU)
- ✅ WCAG 2.1 AA compliance verified
- ✅ All 6 issues closed

---

## 🔗 Critical Dependencies

**Blocked by:**
- Backend #2 (Policy Engine) — needed for #9, #10
- Backend #4 (Identity APIs) — needed for #9
- Security #15 (FIDO2) — needed for #9
- Security #16 (SSH CA) — needed for #13, #21
- Security #18 (Shamir) — needed for #13

**Blocks:**
- None (Frontend is mostly at the end of dependency chain)

---

## 📅 Recommended Timeline

```
Week 1-2:  #14 (Posture Agent) — start immediately
Week 3-4:  #9 (Login Portal) — CRITICAL PATH
Week 5-6:  #10 (Admin Dashboard) + #13 (SecureVault)
Week 7-8:  #11 (Latency Dashboard) + #13 (SecureVault)
Week 9:    #12 (Attack Demo Panel)
Week 10+:  Testing + Polish
```

---

## 💡 Tips for Frontend Team

1. **Start with mockups** — Design all UIs before coding
2. **Component library** — Create reusable components early (Button, Modal, Chart, etc.)
3. **Mock APIs** — Don't wait for Backend, use mock data
4. **Accessibility first** — Keyboard nav and ARIA from day 1
5. **Performance budget** — Keep bundle size < 500KB
6. **Error states** — Design for loading, error, empty states
7. **Browser testing** — Test on real devices, not just Chrome DevTools
8. **User feedback** — Get usability testing early

---

## 🛠️ Recommended Tech Stack

**Web Portal (Issues #9, #10, #11, #12):**
- React.js or Vue.js
- TypeScript
- TailwindCSS or Material-UI
- Recharts or Chart.js (for #11)
- WebAuthn browser API

**SecureVault (Issue #13):**
- Java 17+
- JavaFX 21+
- Maven or Gradle
- BouncyCastle (crypto)

**Posture Agent (Issue #14):**
- Go or Rust (for lightweight binary)
- Native OS APIs
- Systemd/launchd/Windows Service

---

**Generated:** 2026-11-04  
**Repository:** https://github.com/mohamed-hashem182005/ZeroGate  
**Team:** Frontend
