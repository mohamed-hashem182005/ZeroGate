# ZeroGate — Networking Team Roadmap

## Team Responsibilities
- Lab environment setup (internal web apps + SSH servers)
- Web reverse proxy (Policy Enforcement Point)
- SSH helper CLI (transparent certificate management)
- Single Packet Authorization (port knocking)
- Network isolation and security
- Performance optimization and latency monitoring

---

## 📋 Issues Assigned to Networking Team

### Phase 1: Lab Infrastructure (Week 1-2)
**Priority: CRITICAL — All teams need the lab environment**

#### Issue #23: Lab Environment Setup ⭐
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 weeks  

**Tasks:**
- [ ] Network architecture design:
  - DMZ zone for ZeroGate components
  - Protected zone for internal resources
  - Management zone for admin access
- [ ] Internal web applications deployment:
  - Deploy 2-3 sample web apps (e.g., Wiki, Dashboard, Admin Panel)
  - Configure apps to trust ZeroGate proxy headers
  - Remove direct internet access
- [ ] Linux SSH servers deployment:
  - Deploy 3-5 Linux VMs (Ubuntu/CentOS)
  - Configure SSH to accept CA-signed certificates
  - Add CA public key to `TrustedUserCAKeys`
  - Disable password authentication
- [ ] Network isolation:
  - Firewall rules: block direct access to protected resources
  - All HTTP traffic MUST go through proxy
  - All SSH traffic MUST use CA certificates
  - Test: direct access attempts should fail
- [ ] DNS configuration:
  - Internal DNS for protected resources
  - External DNS for ZeroGate public endpoints
- [ ] TLS certificates:
  - Generate/acquire certificates for all services
  - Configure TLS 1.3 minimum
- [ ] Monitoring setup:
  - Network traffic monitoring
  - Latency monitoring
  - Resource utilization monitoring
- [ ] Lab network diagram documentation

**Deliverables:**
- Lab environment fully operational
- 2-3 web apps accessible ONLY through proxy
- 3-5 SSH servers accessible ONLY with CA certs
- Direct access blocked and verified
- Network diagram documented

**Dependencies:**
- None (can start immediately)
- Provides infrastructure for ALL teams

---

### Phase 2: Traffic Enforcement (Week 3-5)
**Priority: CRITICAL — Core enforcement point**

#### Issue #20: Web Reverse Proxy (Policy Enforcement Point)
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 weeks  

**Tasks:**
- [ ] Proxy selection (Nginx / Envoy / Traefik)
- [ ] Forward authentication configuration:
  - Every request triggers authorization subrequest
  - Call `POST /v1/authorize` with context
  - Pass: session cookie, client IP, target URL, HTTP method
- [ ] Decision caching:
  - Cache ALLOW decisions for max 60 seconds
  - Key: `session_id + resource_id`
  - Invalidate on session revocation
  - Invalidate on policy change
- [ ] Header injection (on ALLOW):
  - `X-ZeroGate-User-Id: <user_id>`
  - `X-ZeroGate-Session-Id: <session_id>`
  - `X-ZeroGate-Device-Id: <device_id>`
  - `X-ZeroGate-Decision: ALLOW`
- [ ] Non-ALLOW handling:
  - **DENY:** Return 403 Forbidden with problem details
  - **STEP_UP:** Redirect to re-authentication page
  - **APPROVAL:** Redirect to JIT request page
  - **ERROR:** Return 503 Service Unavailable
- [ ] TLS configuration:
  - TLS termination at proxy
  - Re-encryption to backend apps
  - Certificate validation
- [ ] Rate limiting:
  - Per-IP rate limits
  - Per-user rate limits
  - DDoS protection
- [ ] Request logging:
  - All requests logged (timestamp, user, resource, decision)
  - Integration with audit log
- [ ] Performance optimization:
  - Connection pooling to backend
  - Keep-alive connections
  - Compression (gzip/brotli)
- [ ] Health checks:
  - Backend app health monitoring
  - Automatic failover
- [ ] Load testing:
  - 500 concurrent users
  - Cached authorization ≤ 10ms
  - Uncached authorization ≤ 100ms

**Deliverables:**
- Proxy enforces all decisions correctly
- Cached authorization ≤ 10ms (p95)
- No bypass path exists
- Header injection works
- TLS termination and re-encryption working
- Lab demo: happy path + denial path

**Dependencies:**
- Backend #2 (Policy Engine) — CRITICAL
- Issue #23 (Lab environment)
- Backend #3 (Sessions)

---

#### Issue #21: SSH Helper CLI
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 1.5 weeks  

**Tasks:**
- [ ] CLI tool development (Go / Rust / Python):
  - Name: `zg-ssh` or similar
  - Transparent wrapper around `ssh` command
- [ ] Certificate request flow:
  - Parse target from `ssh user@host` command
  - Request short-lived cert from CA (POST /v1/ssh/certificates)
  - Save cert to temporary location
  - Pass cert to ssh via `-i` flag
- [ ] SPA knock integration:
  - Send SPA knock packet before SSH connection
  - Wait for port to open (up to 5 seconds)
  - Proceed with SSH connection
- [ ] Certificate caching:
  - Cache valid certificates (avoid re-requesting)
  - Check expiry before use
  - Auto-refresh if < 30s remaining
- [ ] User experience:
  - `zg-ssh user@host` should work exactly like `ssh`
  - Pass through all ssh flags (-p, -L, -D, etc.)
  - Display certificate expiry countdown
  - Warning when cert about to expire
- [ ] Error handling:
  - CA unreachable → clear error message
  - Certificate denied → show reason
  - SPA knock failed → retry logic
- [ ] Installation:
  - Install script for Linux/macOS/Windows
  - Shell alias setup: `alias ssh='zg-ssh'`
  - Uninstall script
- [ ] Cross-platform testing (Linux, macOS, Windows WSL)

**Deliverables:**
- `zg-ssh user@host` works transparently
- SPA knock sent automatically
- Short-lived cert requested and used
- No permanent SSH keys required
- Works on Linux, macOS, Windows

**Dependencies:**
- Security #16 (SSH CA) — CRITICAL
- Issue #22 (SPA) — optional integration
- Backend #3 (Sessions for auth)

---

### Phase 3: Advanced Security (Week 6-8)

#### Issue #22: Single Packet Authorization (SPA)
**Status:** 🟡 Not Started  
**Priority:** Add-on  
**Estimated Time:** 1.5 weeks  

**Tasks:**
- [ ] SPA packet format design:
  - `resource_id`: Target SSH server ID
  - `source_ip`: Client IP address
  - `nonce`: Random 16-byte value
  - `timestamp`: Unix timestamp (seconds)
  - `signature`: HMAC-SHA256 of above fields
- [ ] Signature calculation:
  - `signature = HMAC-SHA256(shared_secret, resource_id || source_ip || nonce || timestamp)`
  - Shared secret per user/device
- [ ] UDP listener service:
  - Listen on dedicated port (e.g., 41234)
  - Parse incoming SPA packets
  - Verify signature (constant-time comparison)
  - Check timestamp freshness (≤ 300s / 5 minutes)
  - Check nonce not seen before (replay prevention)
  - Verify source IP matches packet header
- [ ] Firewall integration:
  - On valid knock: open SSH port for source_ip
  - Time window: 300 seconds (5 minutes)
  - Execute `nftables` or `iptables` rule
  - Schedule automatic rule deletion after 300s
- [ ] Nonce cache:
  - Store seen nonces for 10 minutes
  - Reject replayed nonces
  - LRU cache with size limit
- [ ] Failed knock handling:
  - Log failed knock attempts to audit log
  - Rate limiting (max 5 knocks per minute per IP)
  - Automatic blocking after 10 failed attempts
- [ ] API endpoint:
  - `POST /v1/spa/knock` for HTTP-based knocking
  - Alternative to raw UDP
- [ ] Integration with SSH helper (#21)
- [ ] Testing:
  - Valid knock opens port within 500ms
  - Replayed knock rejected
  - Expired timestamp rejected
  - Wrong source IP rejected
  - Port closes after 300s

**Deliverables:**
- SPA knock opens SSH port for authorized IP
- Replay attacks prevented
- Port remains closed without valid knock
- Port auto-closes after 300 seconds
- Failed knocks logged

**Dependencies:**
- Issue #23 (Lab environment)
- Issue #21 (SSH helper integration)

---

## 🔄 After Core Issues Complete (Week 9+)

### Performance Optimization
- [ ] Latency reduction:
  - Proxy response time optimization
  - Connection pooling tuning
  - Cache hit rate optimization (target: > 95%)
- [ ] Throughput testing:
  - 1000+ requests per second
  - 500+ concurrent users
  - Load balancing configuration
- [ ] Network tuning:
  - TCP keep-alive settings
  - Buffer sizes
  - MTU optimization

### Security Hardening
- [ ] DDoS mitigation:
  - Rate limiting per IP
  - SYN flood protection
  - Connection limits
- [ ] Intrusion detection:
  - Monitor for suspicious patterns
  - Port scanning detection
  - Brute-force detection
- [ ] Network segmentation:
  - VLAN isolation
  - Firewall rules audit
  - Least privilege access

### Monitoring & Alerting
- [ ] Metrics collection:
  - Request latency (p50, p95, p99)
  - Request rate
  - Error rate
  - Cache hit rate
- [ ] Dashboards:
  - Real-time network traffic
  - Proxy performance metrics
  - SSH connection monitoring
- [ ] Alerting:
  - High latency alerts
  - Error rate spikes
  - Resource exhaustion

### Documentation
- [ ] Network architecture diagram
- [ ] Proxy configuration guide
- [ ] SSH helper user guide
- [ ] Firewall rules documentation
- [ ] Troubleshooting guide
- [ ] Performance tuning guide

---

## 📊 Success Metrics

- ✅ Lab environment operational for all teams
- ✅ Direct access to protected resources blocked
- ✅ Proxy cached authorization ≤ 10ms (p95)
- ✅ Proxy uncached authorization ≤ 100ms (p95)
- ✅ SSH helper works transparently
- ✅ SPA knock opens port within 500ms
- ✅ All 4 issues closed
- ✅ Load testing: 500+ concurrent users
- ✅ Zero network security vulnerabilities

---

## 🔗 Critical Dependencies

**Blocks these teams:**
- ALL teams need #23 (Lab environment)
- Frontend #9 (Login Portal) — needs #20 for protected app access
- Frontend #13 (SecureVault) — needs #21 for SSH
- Backend #2 (Policy Engine) — tested via #20

**Blocked by:**
- Backend #2 (Policy Engine) — needed for #20
- Security #16 (SSH CA) — needed for #21

---

## 📅 Recommended Timeline

```
Week 1-2:  #23 (Lab Environment) — CRITICAL PATH
Week 3-5:  #20 (Web Proxy) — CRITICAL PATH
Week 5-6:  #21 (SSH Helper)
Week 7-8:  #22 (SPA)
Week 9+:   Performance + Security Hardening
```

---

## 💡 Tips for Networking Team

1. **Lab first, everything else second** — #23 is blocking everyone
2. **Document the network** — Clear diagrams prevent confusion
3. **Automate infrastructure** — Use IaC (Terraform, Ansible)
4. **Test isolation thoroughly** — Try every bypass path
5. **Monitor from day 1** — Add instrumentation early
6. **Performance baseline** — Measure before optimizing
7. **Security mindset** — Default deny, least privilege
8. **Backup configs** — Version control for all network configs

---

## 🛠️ Recommended Tech Stack

**Reverse Proxy:**
- **Nginx** (simple, battle-tested) or
- **Envoy** (modern, observability) or
- **Traefik** (easy config, dynamic)

**SSH Helper:**
- **Go** (fast, single binary, cross-platform) or
- **Rust** (performance, memory safety) or
- **Python** (rapid development, but needs runtime)

**SPA Service:**
- **Go** or **Rust** (low latency, efficient)

**Infrastructure:**
- **Docker** + **Docker Compose** (local dev/lab)
- **Terraform** (infrastructure as code)
- **Ansible** (configuration management)

**Monitoring:**
- **Prometheus** + **Grafana** (metrics + dashboards)
- **Loki** (log aggregation)
- **Jaeger** (distributed tracing)

---

## 🧪 Testing Checklist

### Lab Environment (#23)
- [ ] Web apps accessible only through proxy
- [ ] Direct HTTP access blocked (test with curl)
- [ ] SSH servers accept only CA-signed certs
- [ ] Password auth disabled on SSH servers
- [ ] Direct SSH access blocked (firewall)
- [ ] DNS resolution works
- [ ] TLS certificates valid
- [ ] Network isolation verified

### Web Proxy (#20)
- [ ] Unauthenticated request → 401 Unauthorized
- [ ] Valid session → request proxied to backend
- [ ] Denied decision → 403 Forbidden
- [ ] Step-up decision → redirect to re-auth
- [ ] Approval decision → redirect to JIT
- [ ] Headers injected correctly (X-ZeroGate-*)
- [ ] Cached decision served in ≤ 10ms
- [ ] Cache invalidated on session kill
- [ ] TLS termination and re-encryption work
- [ ] Load test: 500 concurrent users

### SSH Helper (#21)
- [ ] `zg-ssh user@host` connects successfully
- [ ] Certificate requested from CA
- [ ] Certificate used for SSH auth
- [ ] No permanent key required
- [ ] Certificate cached and reused
- [ ] Certificate auto-refreshed before expiry
- [ ] SPA knock sent (if #22 implemented)
- [ ] Error messages clear and helpful
- [ ] Works on Linux, macOS, Windows WSL

### SPA (#22)
- [ ] Valid knock opens port within 500ms
- [ ] Port accessible only from knocking IP
- [ ] Replayed knock rejected (same nonce)
- [ ] Expired timestamp rejected (> 300s old)
- [ ] Wrong source IP rejected
- [ ] Port closes after 300s automatically
- [ ] Failed knocks logged to audit
- [ ] Rate limiting prevents brute force

---

## 🔐 Security Considerations

### Network Isolation
- Default deny all traffic
- Explicit allow rules only
- No direct access to protected resources
- DMZ for public-facing components

### TLS/SSL
- TLS 1.3 minimum
- Strong cipher suites only
- Valid certificates (no self-signed in prod)
- Certificate pinning (optional)

### Rate Limiting
- Per-IP limits (prevent DDoS)
- Per-user limits (prevent abuse)
- Failed auth attempt limits
- SPA knock rate limits

### Monitoring
- Log all requests (timestamp, user, decision)
- Alert on suspicious patterns
- Track failed authentication attempts
- Monitor for port scanning

---

**Generated:** 2026-11-04  
**Repository:** https://github.com/mohamed-hashem182005/ZeroGate  
**Team:** Networking
