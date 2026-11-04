# ZeroGate — Database Team Roadmap

## Team Responsibilities
- PostgreSQL schema design and implementation
- Database migrations and version control
- Data integrity and constraints
- Query optimization and indexing
- Backup and recovery procedures
- Database security hardening

---

## 📋 Issues Assigned to Database Team

### Phase 1: Core Schemas (Week 1)
**Priority: CRITICAL — ALL teams depend on these**

#### Issue #24: PostgreSQL Schema — Identity Slice ⭐
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 days  

**Tasks:**
- [ ] **Users table:**
  ```sql
  CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('ACTIVE', 'SUSPENDED', 'REVOKED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
  );
  CREATE INDEX idx_users_username ON users(username);
  CREATE INDEX idx_users_status ON users(status);
  ```

- [ ] **Credentials table:**
  ```sql
  CREATE TABLE credentials (
    credential_id VARCHAR(255) PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    public_key TEXT NOT NULL,
    sign_count BIGINT NOT NULL DEFAULT 0,
    rp_id VARCHAR(255) NOT NULL,
    origin VARCHAR(255) NOT NULL,
    user_handle VARCHAR(255) NOT NULL,
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL CHECK (status IN ('ACTIVE', 'REVOKED')),
    UNIQUE(user_id, credential_id)
  );
  CREATE INDEX idx_credentials_user ON credentials(user_id);
  CREATE INDEX idx_credentials_status ON credentials(status);
  ```

- [ ] **Devices table:**
  ```sql
  CREATE TABLE devices (
    device_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    device_name VARCHAR(255),
    os_name VARCHAR(100),
    os_version VARCHAR(100),
    disk_encrypted BOOLEAN,
    is_rooted BOOLEAN,
    screen_lock_enabled BOOLEAN,
    status VARCHAR(50) NOT NULL CHECK (status IN ('ENROLLED', 'COMPLIANT', 'NON_COMPLIANT', 'QUARANTINED', 'REVOKED')),
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_posture_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ
  );
  CREATE INDEX idx_devices_user ON devices(user_id);
  CREATE INDEX idx_devices_status ON devices(status);
  ```

- [ ] Migration script (V001__identity_slice.sql)
- [ ] Rollback script
- [ ] Sample seed data (test users, devices)

**Deliverables:**
- Migration runs cleanly on fresh PostgreSQL
- All foreign keys and constraints enforced
- Indexes created
- Sample data loads successfully

**Dependencies:**
- None (can start immediately)
- Blocks: Backend #4, Security #15

---

#### Issue #25: PostgreSQL Schema — Access Slice
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 days  

**Tasks:**
- [ ] **Policies table:**
  ```sql
  CREATE TABLE policies (
    policy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    rules JSONB NOT NULL,
    published BOOLEAN NOT NULL DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  );
  CREATE INDEX idx_policies_published ON policies(published);
  CREATE INDEX idx_policies_rules ON policies USING GIN(rules);
  ```

- [ ] **Sessions table:**
  ```sql
  CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    device_id UUID NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    trust_score INTEGER NOT NULL CHECK (trust_score >= 0 AND trust_score <= 100),
    state VARCHAR(50) NOT NULL CHECK (state IN ('ACTIVE', 'STEP_UP_REQUIRED', 'PENDING_APPROVAL', 'KILLED', 'EXPIRED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    killed_at TIMESTAMPTZ,
    killed_by UUID REFERENCES users(user_id),
    kill_reason TEXT
  );
  CREATE INDEX idx_sessions_user ON sessions(user_id);
  CREATE INDEX idx_sessions_device ON sessions(device_id);
  CREATE INDEX idx_sessions_state ON sessions(state);
  CREATE INDEX idx_sessions_expires ON sessions(expires_at);
  ```

- [ ] **JIT requests table:**
  ```sql
  CREATE TABLE jit_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    target_resource VARCHAR(255) NOT NULL,
    duration_seconds INTEGER NOT NULL,
    reason TEXT NOT NULL,
    state VARCHAR(50) NOT NULL CHECK (state IN ('PENDING', 'APPROVED', 'DENIED', 'CANCELLED', 'EXPIRED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sla_expires_at TIMESTAMPTZ NOT NULL,
    decided_at TIMESTAMPTZ,
    decided_by UUID REFERENCES users(user_id),
    decision_reason TEXT
  );
  CREATE INDEX idx_jit_user ON jit_requests(user_id);
  CREATE INDEX idx_jit_state ON jit_requests(state);
  CREATE INDEX idx_jit_sla ON jit_requests(sla_expires_at);
  ```

- [ ] **SSH certificates table:**
  ```sql
  CREATE TABLE ssh_certificates (
    serial_number BIGINT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id),
    device_id UUID NOT NULL REFERENCES devices(device_id),
    target_server VARCHAR(255) NOT NULL,
    principals TEXT[] NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    revoked_by UUID REFERENCES users(user_id)
  );
  CREATE INDEX idx_ssh_certs_user ON ssh_certificates(user_id);
  CREATE INDEX idx_ssh_certs_expires ON ssh_certificates(expires_at);
  CREATE INDEX idx_ssh_certs_revoked ON ssh_certificates(revoked_at) WHERE revoked_at IS NOT NULL;
  ```

- [ ] Migration script (V002__access_slice.sql)
- [ ] Rollback script
- [ ] Sample seed data (policies, sessions)

**Deliverables:**
- Migration runs cleanly
- All foreign keys work
- State constraints enforced
- Sample data loads

**Dependencies:**
- Issue #24 (Identity slice) — foreign keys
- Blocks: Backend #2, #3

---

#### Issue #26: PostgreSQL Schema — Audit Slice
**Status:** 🟡 Not Started  
**Priority:** Core  
**Estimated Time:** 2 days  

**Tasks:**
- [ ] **Audit events table:**
  ```sql
  CREATE TABLE audit_events (
    seq BIGSERIAL PRIMARY KEY,
    event_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    correlation_id UUID,
    event_type VARCHAR(100) NOT NULL,
    actor_user_id UUID REFERENCES users(user_id),
    actor_device_id UUID REFERENCES devices(device_id),
    target_resource VARCHAR(255),
    decision VARCHAR(50),
    trust_score INTEGER,
    payload JSONB NOT NULL,
    payload_hash CHAR(64) NOT NULL,
    prev_hash CHAR(64) NOT NULL,
    curr_hash CHAR(64) NOT NULL
  );
  CREATE INDEX idx_audit_timestamp ON audit_events(timestamp DESC);
  CREATE INDEX idx_audit_correlation ON audit_events(correlation_id);
  CREATE INDEX idx_audit_type ON audit_events(event_type);
  CREATE INDEX idx_audit_actor ON audit_events(actor_user_id);
  ```

- [ ] Append-only enforcement:
  ```sql
  -- Prevent updates
  CREATE RULE audit_no_update AS ON UPDATE TO audit_events DO INSTEAD NOTHING;
  
  -- Prevent deletes
  CREATE RULE audit_no_delete AS ON DELETE TO audit_events DO INSTEAD NOTHING;
  ```

- [ ] Genesis event initialization:
  ```sql
  INSERT INTO audit_events (
    event_type,
    payload,
    payload_hash,
    prev_hash,
    curr_hash
  ) VALUES (
    'AUDIT_CHAIN_GENESIS',
    '{"version": "1.0", "system": "ZeroGate"}'::jsonb,
    encode(sha256('{"version": "1.0", "system": "ZeroGate"}'), 'hex'),
    encode(sha256('ZEROGATE_AUDIT_GENESIS_V1'), 'hex'),
    encode(sha256('...'), 'hex')  -- Computed correctly
  );
  ```

- [ ] Chain verification function:
  ```sql
  CREATE FUNCTION verify_audit_chain(from_seq BIGINT, to_seq BIGINT)
  RETURNS TABLE(seq BIGINT, valid BOOLEAN, error TEXT) AS $$
  -- Implementation in PL/pgSQL
  $$ LANGUAGE plpgsql;
  ```

- [ ] Partitioning strategy (by month for long-term storage):
  ```sql
  -- Optional: partition by month if expecting > 10M events
  CREATE TABLE audit_events_2026_11 PARTITION OF audit_events
    FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');
  ```

- [ ] Migration script (V003__audit_slice.sql)
- [ ] Rollback script (careful with append-only!)
- [ ] Sample audit events

**Deliverables:**
- Audit table created with append-only enforcement
- Genesis event inserted correctly
- Verification function works
- Sample events append correctly

**Dependencies:**
- Issue #24 (Identity slice) — foreign keys
- Blocks: Backend #8, Security #17

---

## 🔄 After Core Schemas Complete (Week 2+)

### Query Optimization
- [ ] Analyze query patterns from Backend team
- [ ] Add missing indexes
- [ ] Create materialized views for dashboards:
  - Active sessions count
  - Recent audit events
  - Trust score statistics
- [ ] Query plan analysis (EXPLAIN ANALYZE)
- [ ] Slow query log review

### Data Integrity
- [ ] Referential integrity verification
- [ ] Constraint testing (all CHECK constraints)
- [ ] Trigger testing (updated_at, etc.)
- [ ] Transaction isolation testing
- [ ] Deadlock prevention

### Performance Tuning
- [ ] Connection pooling configuration (PgBouncer)
- [ ] PostgreSQL tuning:
  - `shared_buffers`
  - `work_mem`
  - `effective_cache_size`
  - `max_connections`
- [ ] Vacuum and analyze scheduling
- [ ] Index maintenance
- [ ] Table statistics update

### Backup & Recovery
- [ ] Automated backup script (pg_dump daily)
- [ ] Point-in-time recovery (PITR) setup
- [ ] Backup verification (restore test)
- [ ] Backup retention policy (30 days)
- [ ] Disaster recovery plan

### Security Hardening
- [ ] Role-based access control:
  - `zerogate_app` role (read/write)
  - `zerogate_readonly` role (read-only)
  - `zerogate_admin` role (DDL)
- [ ] Row-level security (RLS) policies
- [ ] SSL/TLS connection enforcement
- [ ] Audit logging (PostgreSQL audit extension)
- [ ] Password policy enforcement
- [ ] Principle of least privilege

### Monitoring
- [ ] Database metrics collection:
  - Connection count
  - Query duration (p50, p95, p99)
  - Lock waits
  - Cache hit rate (target: > 95%)
  - Replication lag (if applicable)
- [ ] Alerting:
  - Connection pool exhaustion
  - Long-running queries (> 10s)
  - Disk space (< 20% free)
  - Replication lag (> 1s)
- [ ] Dashboard:
  - Active connections
  - Query performance
  - Table sizes
  - Index usage

### Documentation
- [ ] Entity-Relationship Diagram (ERD)
- [ ] Schema documentation (columns, constraints, indexes)
- [ ] Migration guide
- [ ] Backup and restore procedures
- [ ] Query optimization guide
- [ ] Troubleshooting guide

---

## 📊 Success Metrics

- ✅ All 3 schemas deployed successfully
- ✅ All foreign keys and constraints working
- ✅ Sample data loads cleanly
- ✅ Query performance acceptable (< 100ms for simple queries)
- ✅ Audit chain append-only enforced
- ✅ Backup and restore tested
- ✅ All 3 issues closed
- ✅ Database documentation complete

---

## 🔗 Critical Dependencies

**Blocks ALL teams:**
- Backend #2, #3, #4, #5, #6, #7, #8
- Frontend #9, #10, #11, #13, #14
- Security #15, #16, #17, #18
- Networking #20, #21

**Blocked by:**
- None (can start immediately)

---

## 📅 Recommended Timeline

```
Day 1-2:   #24 (Identity Slice) — CRITICAL PATH
Day 3-4:   #25 (Access Slice) — CRITICAL PATH
Day 5-6:   #26 (Audit Slice) — CRITICAL PATH
Week 2+:   Optimization + Monitoring + Documentation
```

---

## 💡 Tips for Database Team

1. **Coordinate on Day 1** — Get representative from each team in kickoff meeting
2. **Version control everything** — All migrations in Git
3. **Test migrations** — Rollback script for every migration
4. **Document as you go** — ERD, column descriptions, sample queries
5. **Performance first** — Index correctly from the start
6. **Backup early, backup often** — Test restore before disaster
7. **Monitor from day 1** — Don't wait for production issues
8. **Security by default** — Least privilege, SSL, audit logging

---

## 🛠️ Recommended Tech Stack

**Database:**
- PostgreSQL 15+ (for gen_random_uuid(), JSONB, etc.)

**Migration Tool:**
- **Flyway** or **Liquibase** (Java-based, version control for DB)
- **golang-migrate** (if using Go backend)
- **Alembic** (if using Python backend)

**Connection Pooling:**
- **PgBouncer** (lightweight, battle-tested)

**Monitoring:**
- **pgAdmin** (GUI for development)
- **Prometheus + postgres_exporter** (metrics)
- **Grafana** (dashboards)
- **pg_stat_statements** (query performance analysis)

**Backup:**
- **pg_dump** (logical backup)
- **pgBackRest** (physical backup + PITR)
- **Barman** (backup and recovery manager)

---

## 🧪 Testing Checklist

### Schema Integrity (#24, #25, #26)
- [ ] Migrations run cleanly on fresh database
- [ ] Rollback scripts work (test on copy)
- [ ] All foreign keys enforce referential integrity
- [ ] All CHECK constraints prevent invalid data
- [ ] UNIQUE constraints prevent duplicates
- [ ] NOT NULL constraints enforced
- [ ] Indexes created successfully

### Data Validation
- [ ] Insert valid data → success
- [ ] Insert invalid data → constraint violation
- [ ] Delete parent → cascades to children (where appropriate)
- [ ] Update triggers fire correctly (updated_at)

### Performance
- [ ] Simple SELECT ≤ 10ms
- [ ] JOIN queries ≤ 50ms
- [ ] Audit append ≤ 20ms
- [ ] Index usage verified (EXPLAIN ANALYZE)
- [ ] Cache hit rate > 95%

### Audit Chain (#26)
- [ ] Genesis event exists (seq = 1)
- [ ] Subsequent events chain correctly
- [ ] Verification function detects tampering
- [ ] Append-only rules prevent UPDATE/DELETE

### Backup & Recovery
- [ ] Backup completes successfully
- [ ] Restore to new database works
- [ ] Restored data matches original
- [ ] PITR restores to specific timestamp

---

## 📐 Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐         ┌────────────────┐
│    Users    │────1:N──│  Credentials │         │    Policies    │
│             │         │              │         │                │
│  user_id PK │         │ credential_id│         │  policy_id PK  │
│  username   │         │ user_id FK   │         │  name          │
│  email      │         │ public_key   │         │  version       │
│  status     │         │ sign_count   │         │  rules (JSONB) │
└──────┬──────┘         └──────────────┘         └────────────────┘
       │
       │1:N
       │
┌──────▼──────┐         ┌──────────────┐         ┌────────────────┐
│   Devices   │         │   Sessions   │         │  JIT Requests  │
│             │────1:N──│              │         │                │
│  device_id  │         │ session_id PK│         │  request_id PK │
│  user_id FK │         │ user_id FK   │         │  user_id FK    │
│  os_name    │         │ device_id FK │         │  target        │
│  status     │         │ trust_score  │         │  state         │
└─────────────┘         │ state        │         │  reason        │
                        └──────────────┘         └────────────────┘

                        ┌──────────────┐         ┌────────────────┐
                        │SSH Certs     │         │  Audit Events  │
                        │              │         │                │
                        │ serial_no PK │         │  seq PK        │
                        │ user_id FK   │         │  event_type    │
                        │ device_id FK │         │  correlation_id│
                        │ target       │         │  payload (JSON)│
                        │ expires_at   │         │  prev_hash     │
                        └──────────────┘         │  curr_hash     │
                                                 └────────────────┘
```

---

**Generated:** 2026-11-04  
**Repository:** https://github.com/mohamed-hashem182005/ZeroGate  
**Team:** Database (Cross-team)
