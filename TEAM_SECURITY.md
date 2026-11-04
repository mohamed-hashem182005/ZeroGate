# ZeroGate — Security & Hardware Team Roadmap

## Team Responsibilities
- Custom FIDO2 hardware passkey integration
- SSH Certificate Authority (short-lived certificates)
- Hash-chained audit log (cryptographic implementation)
- k-of-n Shamir Secret Sharing recovery
- Threat model and attack scenarios
- Security testing and penetration testing

---

## 📋 Issues Assigned to Security Team

### Phase 1: Core Authentication (Week 1-4)
**Priority: CRITICAL — Required for passkey login**

#### Issue #15: Custom FIDO2 Passkey Integration ⭐
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 weeks  

**Tasks:**
- [ ] FIDO2 hardware selection and procurement
- [ ] Fingerprint sensor integration:
  - Fingerprint matched on-device only
  - Fingerprint template never sent to server
- [ ] Secure element integration:
  - Private key generation in secure chip
  - Private key never leaves secure element
  - Challenge signing in hardware
- [ ] WebAuthn registration flow:
  - Generate credential key pair in secure element
  - Return public key + credential ID
  - Store counter state securely
- [ ] WebAuthn authentication flow:
  - Sign challenge with private key (in hardware)
  - Increment and return signature counter
  - User verification (fingerprint) before signing
- [ ] Authenticator data parsing:
  - RP ID hash verification
  - Flag checking (UP=1, UV=1)
  - Counter regression detection
- [ ] Counter regression handling:
  - Detect counter rollback
  - Immediately revoke credential
  - Raise high-severity security alert
- [ ] Duplicate credential prevention
- [ ] Audit event generation on enrollment
- [ ] Lab testing (enrollment + 100 login cycles)

**Deliverables:**
- Custom FIDO2 hardware working in lab
- Enrollment completes successfully
- Login works with fingerprint verification
- Counter regression triggers revocation
- Private key never exposed

**Dependencies:**
- None (can start immediately)
- Integrates with Backend #4 (Identity APIs)

---

#### Issue #16: SSH Certificate Authority
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 weeks  

**Tasks:**
- [ ] CA key generation (ED25519 or RSA 4096-bit)
- [ ] CA key storage (HSM or encrypted key file)
- [ ] Certificate issuance logic:
  - Generate OpenSSH user certificate
  - Set principals (authorized usernames)
  - Set validity window (exactly 300 seconds / 5 minutes)
  - Embed key ID and serial number
  - Sign with CA private key
- [ ] Certificate format:
  - `ssh-ed25519-cert-v01@openssh.com` or
  - `rsa-sha2-512-cert-v01@openssh.com`
- [ ] Certificate revocation:
  - Maintain revoked certificate list (CRL/KRL)
  - Publish KRL to SSH servers
  - Active connection termination
- [ ] CA public key distribution (GET /v1/ssh/ca/public-key)
- [ ] Monotonic serial number generation
- [ ] Performance testing (issuance ≤ 2 seconds)
- [ ] Integration with SSH servers (authorized keys config)

**Deliverables:**
- CA issues valid short-lived certificates
- Certificates expire after exactly 300 seconds
- Revocation immediately invalidates certificates
- Issuance latency ≤ 2 seconds
- SSH servers accept CA-signed certificates

**Dependencies:**
- Backend #4 (Identity APIs)
- Networking #23 (Lab SSH servers)

---

### Phase 2: Cryptographic Infrastructure (Week 5-7)

#### Issue #17: Hash-chained Audit Log (Cryptographic)
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 weeks  

**Tasks:**
- [ ] Canonical JSON implementation (RFC 8785):
  - Deterministic key ordering
  - UTF-8 encoding
  - No extraneous whitespace
- [ ] SHA-256 hash function:
  - `payload_hash = SHA256(canonical_json(payload))`
  - `prev_hash = SHA256(canonical_json(previous_event))`
- [ ] Genesis event definition:
  - `prev_hash = SHA256("ZEROGATE_AUDIT_GENESIS_V1")`
- [ ] Chain linking logic:
  - Event n references hash of event n-1
  - Cryptographic tamper detection
- [ ] Verification algorithm:
  - Recompute all hashes from genesis
  - Compare computed vs stored hashes
  - Identify exact sequence number of break
- [ ] Tamper simulation testing:
  - Modify payload → verification fails
  - Insert row → chain breaks
  - Delete row → chain breaks
  - Reorder rows → chain breaks
- [ ] Performance optimization (verification of 1000 events ≤ 500ms)
- [ ] Standalone verification tool (CLI)

**Deliverables:**
- Audit chain cryptographically verified
- Tampering detected at exact sequence
- Verification tool working
- Chain verification of 1000 events ≤ 500ms

**Dependencies:**
- Backend #8 (Audit log backend)
- Database #26 (Audit slice)

---

#### Issue #18: k-of-n Shamir Secret Sharing Recovery
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 1.5 weeks  

**Tasks:**
- [ ] Shamir's Secret Sharing implementation:
  - Algorithm over Galois Field GF(2^8)
  - Support k ∈ [2, 5], n ∈ [3, 5], k ≤ n
- [ ] Secret splitting:
  - Generate random polynomial coefficients (CSPRNG)
  - Evaluate polynomial at n points
  - Output n shares
- [ ] Secret reconstruction:
  - Lagrange interpolation over GF(2^8)
  - Reconstruct secret from any k shares
  - Verify k-1 shares reveal nothing
- [ ] Share fingerprinting:
  - `fingerprint = SHA256(share_bytes)` in hex
  - Store fingerprints only (never raw shares)
- [ ] Memory security:
  - Zero out secret buffers immediately after use
  - No secret material in logs or core dumps
- [ ] Base64url encoding (no padding)
- [ ] API endpoints:
  - `POST /v1/vault/recovery/shares` (split)
  - `POST /v1/vault/recovery/rebuild` (reconstruct)
- [ ] Rate limiting (prevent brute-force recombination)
- [ ] Audit event on rebuild
- [ ] Mathematical verification:
  - Test: any k shares → correct secret
  - Test: any k-1 shares → cannot reconstruct

**Deliverables:**
- Splitting into n shares works
- Any k shares reconstruct exact secret
- Any k-1 shares fail to reconstruct
- No raw shares in database or logs
- Audit event on rebuild

**Dependencies:**
- Backend #4 (Vault APIs)
- Frontend #13 (SecureVault UI)

---

### Phase 3: Security Validation (Week 8-10)

#### Issue #19: Threat Model & Attack Scenarios
**Status:** 🟡 Not Started  
**Priority:** Add-on  
**Estimated Time:** 1 week  

**Tasks:**
- [ ] Threat model documentation (STRIDE or MITRE ATT&CK):
  - **Spoofing:** Passkey cloning, credential theft
  - **Tampering:** Audit log modification, certificate forgery
  - **Repudiation:** Non-repudiation via audit chain
  - **Information Disclosure:** Session hijacking, credential leakage
  - **Denial of Service:** Rate limiting, DDoS mitigation
  - **Elevation of Privilege:** Policy bypass, admin takeover
- [ ] Attack scenario scripting:
  - **Replay Attack:** Reuse old WebAuthn challenge
  - **Counter Regression:** Manipulate signCount in assertion
  - **Session Hijack:** Steal session cookie, attempt reuse
  - **MITM Attack:** Intercept and tamper with proxy request
- [ ] Detection verification:
  - Replay → Challenge expiry (60s) triggers deny
  - Counter regression → Immediate credential revocation
  - Session hijack → Cookie attributes prevent theft
  - MITM → TLS + signature verification prevents tampering
- [ ] Integration with Attack Lab API:
  - Scripted attack trigger endpoints
  - Real-time event stream
- [ ] Documentation of mitigations for each threat
- [ ] Penetration testing plan

**Deliverables:**
- Threat model document complete
- 4 attack scenarios scripted and working
- Detection verified for each scenario
- Mitigations documented

**Dependencies:**
- Backend #2 (Policy Engine)
- Frontend #12 (Attack Demo Panel)
- All core features complete

---

## 🔄 After Core Issues Complete (Week 11+)

### Security Audit
- [ ] Comprehensive penetration testing:
  - OWASP Top 10 verification
  - Authentication bypass attempts
  - Authorization bypass attempts
  - Injection attacks (SQL, command, XSS)
  - Cryptographic validation
- [ ] Third-party security review (if budget allows)
- [ ] Vulnerability scanning (automated tools)
- [ ] Security audit report

### Hardening
- [ ] Input validation everywhere
- [ ] Rate limiting on all endpoints
- [ ] Brute-force protection
- [ ] CSRF protection
- [ ] Clickjacking prevention (X-Frame-Options)
- [ ] Content Security Policy (CSP)
- [ ] TLS 1.3 enforcement
- [ ] Certificate pinning

### Documentation
- [ ] Security architecture document
- [ ] Cryptographic specifications
- [ ] Threat model and mitigations
- [ ] Incident response plan
- [ ] Security testing report
- [ ] Compliance mapping (NIST SP 800-207)

---

## 📊 Success Metrics

- ✅ FIDO2 enrollment/login works in lab
- ✅ Counter regression detected and credential revoked
- ✅ SSH certificates expire after exactly 300 seconds
- ✅ Issuance latency ≤ 2 seconds
- ✅ Audit chain tampering detected 100% of the time
- ✅ Chain verification ≤ 500ms for 1000 events
- ✅ Shamir: any k shares reconstruct, any k-1 fail
- ✅ All attack scenarios detected
- ✅ Zero critical security vulnerabilities
- ✅ All 5 issues closed

---

## 🔗 Critical Dependencies

**Blocks these teams:**
- Frontend #9 (Login Portal) — needs #15
- Frontend #13 (SecureVault) — needs #16, #18
- Networking #21 (SSH Helper) — needs #16
- Backend #8 (Audit Log) — integrates with #17

**Blocked by:**
- Backend #4 (Identity APIs) — needed for #15
- Database #26 (Audit slice) — needed for #17
- Networking #23 (Lab servers) — needed for #16 testing

---

## 📅 Recommended Timeline

```
Week 1-2:  #15 (FIDO2 Passkey) — CRITICAL PATH
Week 3-4:  #16 (SSH CA) — CRITICAL PATH
Week 5-6:  #17 (Audit Chain)
Week 7-8:  #18 (Shamir Recovery)
Week 9-10: #19 (Threat Model + Attack Scenarios)
Week 11+:  Security Audit + Penetration Testing
```

---

## 💡 Tips for Security Team

1. **Hardware procurement early** — FIDO2 hardware can take time to arrive
2. **Test cryptography rigorously** — Use test vectors from standards
3. **Memory security** — Zero buffers, avoid logging secrets
4. **Constant-time operations** — Prevent timing attacks (HMAC comparison, etc.)
5. **Never trust client data** — Validate everything server-side
6. **Defense in depth** — Multiple layers of security
7. **Document everything** — Security decisions, threat model, mitigations
8. **Think like an attacker** — Try to break your own system

---

## 🔐 Key Cryptographic Standards

### WebAuthn / FIDO2
- **Standard:** W3C WebAuthn Level 3
- **Algorithms:** ES256 (ECDSA P-256 + SHA-256), RS256 (RSA + SHA-256)
- **Challenge:** 32 bytes CSPRNG, base64url, single-use, 60s expiry
- **Counter:** Monotonic signature counter, detect cloning

### SSH Certificates
- **Format:** OpenSSH certificate (RFC 8709)
- **CA Key:** ED25519 (preferred) or RSA 4096-bit
- **Validity:** Exactly 300 seconds (5 minutes)
- **Serial:** 64-bit monotonic integer
- **Revocation:** KRL (Key Revocation List)

### Audit Chain
- **Hash:** SHA-256 (256-bit)
- **Encoding:** Canonical JSON (RFC 8785)
- **Genesis:** `SHA256("ZEROGATE_AUDIT_GENESIS_V1")`
- **Chaining:** `prev_hash_n = SHA256(event_{n-1})`

### Shamir Secret Sharing
- **Field:** GF(2^8) / Galois Field
- **Threshold:** k ∈ [2, 5]
- **Shares:** n ∈ [3, 5], k ≤ n
- **Security:** Information-theoretically secure
- **Encoding:** Base64url, no padding

### General
- **Random:** CSPRNG (crypto.randomBytes or equivalent)
- **TLS:** TLS 1.3 minimum
- **Key Storage:** HSM or encrypted at rest
- **Memory:** Zero secrets after use

---

## 🧪 Testing Checklist

### FIDO2 Testing
- [ ] Enrollment on Chrome, Firefox, Safari, Edge
- [ ] Login on all browsers
- [ ] User verification required
- [ ] Counter increments correctly
- [ ] Counter regression detected
- [ ] Duplicate credential rejected
- [ ] Challenge replay rejected
- [ ] Challenge expiry (60s) enforced

### SSH CA Testing
- [ ] Certificate issuance works
- [ ] Certificate expires after 300s
- [ ] SSH connection succeeds with valid cert
- [ ] SSH connection fails with expired cert
- [ ] SSH connection fails with revoked cert
- [ ] Serial numbers monotonic and unique
- [ ] CA public key distributed correctly

### Audit Chain Testing
- [ ] Genesis event initialized correctly
- [ ] Hashes chain correctly
- [ ] Verification passes on clean chain
- [ ] Verification fails on tampered payload
- [ ] Verification fails on inserted row
- [ ] Verification fails on deleted row
- [ ] Verification fails on reordered rows
- [ ] Performance: 1000 events ≤ 500ms

### Shamir Testing
- [ ] Split secret into 5 shares (k=3, n=5)
- [ ] Any 3 shares reconstruct exact secret
- [ ] All 10 combinations of 3 shares work
- [ ] Any 2 shares fail to reconstruct
- [ ] Fingerprints match share data
- [ ] No raw shares in database
- [ ] Memory zeroed after split/rebuild

---

**Generated:** 2026-11-04  
**Repository:** https://github.com/mohamed-hashem182005/ZeroGate  
**Team:** Security & Hardware
