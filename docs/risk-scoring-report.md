## 1. Design intent

ZeroGate needs a trust score that a human can defend in a review. The score is therefore a **transparent additive model with a bounded anomaly adjustment**, not a black box. Every point is attributable to a named signal, every category is capped so one bad observation cannot dominate the result, and every hard gate is evaluated before arithmetic. The score never replaces policy: it is one input to the Policy Engine and one trigger for continuous re-evaluation.

> A score is a decision input, not a decision. The Policy Engine decides; the score explains how much confidence the system has in the request.

The model has four jobs:

1. **Rank** requests from 0 to 100 so the four trust bands can be applied consistently.
2. **Explain** the rank with a short list of reason codes and point deductions.
3. **Detect change** during a session, not only at login.
4. **Feed** a bounded ML anomaly adjustment without allowing the model to override a hard gate or a policy denial.

## 2. Signal catalog

Signals are grouped into five categories. Points are negative deductions from a starting score of 100. A signal is counted at most once per evaluation; when two rules describe the same observation, the more specific rule wins. The ML adjustment is separate and is capped at −15.

### 2.1 Identity signals

| ID | Signal | Condition | Points | Source |
|---|---|---|---|---|
| ID-01 | Unknown credential | Credential is not enrolled or the user handle does not match | Hard gate | Passkey verifier |
| ID-02 | Counter regression | Assertion `signCount` is less than or equal to the stored value | Hard gate, −35, revoke credential | Passkey verifier |
| ID-03 | Fresh credential | Credential enrolled less than 24 hours ago | −10 | Identity store |
| ID-04 | No user verification | WebAuthn `uv` flag is false when policy requires it | −15 | Passkey verifier |
| ID-05 | Recovery just used | A Shamir rebuild completed in the last 24 hours | −12 | SecureVault |
| ID-06 | Dormant account | No successful login for 90 days | −5 | Identity store |

### 2.2 Device signals

| ID | Signal | Condition | Points | Source |
|---|---|---|---|---|
| DV-01 | Disk encryption off | Posture reports `disk_encrypted = false` | −25 | Posture agent |
| DV-02 | Root or jailbreak | Posture reports `is_rooted = true` | −30 | Posture agent |
| DV-03 | OS out of date | Major version below the supported baseline | −10 | Posture agent |
| DV-04 | Stale posture | Last report older than 24 hours | −8 | Posture agent |
| DV-05 | Shared device | More than one active user on the device | −15 | Device registry |
| DV-06 | Screen lock off | Posture reports no lock credential | −8 | Posture agent |
| DV-07 | Revoked device | Device is in `revoked` state | Hard gate | Device registry |

### 2.3 Network and location signals

| ID | Signal | Condition | Points | Source |
|---|---|---|---|---|
| NW-01 | Impossible travel | Implied speed between consecutive logins exceeds 800 km/h | −25 | Geo-IP + session history |
| NW-02 | New country | Country not seen for this user in 30 days | −12 | Geo-IP |
| NW-03 | New ASN | ASN not seen for this user in 30 days | −8 | Geo-IP |
| NW-04 | Anonymizer | Tor, open proxy, or known hosting exit | −20 | IP reputation |
| NW-05 | Shared NAT | More than five users behind the same IP in 10 minutes | −5 | Session history |
| NW-06 | Outside allowed CIDR | Source IP is outside the policy's allowed range | −15 | Policy context |

### 2.4 Behaviour signals

| ID | Signal | Condition | Points | Source |
|---|---|---|---|---|
| BH-01 | Elevated volume | Session transfer volume above 5× the user's 30-day baseline | −12 | Proxy / SSH telemetry |
| BH-02 | Extreme volume | Session transfer volume above 15× baseline | −20 | Proxy / SSH telemetry |
| BH-03 | New resource class | First access to this resource sensitivity class | −8 | Session history |
| BH-04 | Rapid enumeration | More than 20 distinct resources requested in one minute | −15 | Proxy |
| BH-05 | Off-hours | Local time between 22:00 and 06:00 | −6 | Request context |
| BH-06 | Weekend or holiday | Local calendar is outside the working week | −3 | Request context |
| BH-07 | Failed-auth burst | More than three failed assertions in 10 minutes | −10 | Auth service |

`BH-01` and `BH-02` are mutually exclusive; the higher deduction applies. Calendar signals are advisory and can be disabled by policy for on-call staff.

### 2.5 Session signals

| ID | Signal | Condition | Points | Source |
|---|---|---|---|---|
| SS-01 | Posture change mid-session | Disk, root, or OS state changes while a session is live | −25 | Posture agent |
| SS-02 | Heartbeat missed | Two consecutive heartbeats are missed | −10 | Policy Administrator |
| SS-03 | Admin kill | An administrator invokes the kill switch | Hard gate, −100 | Admin console |
| SS-04 | Policy now denies | A published policy change makes the session non-compliant | Hard gate, −100 | Policy Engine |
| SS-05 | Certificate replay | A presented SSH certificate is already bound to another live connection | Hard gate, −100 | SSH CA / host |

## 3. Scoring model

The score is computed in three steps:

1. Sum the deductions inside each category.
2. Cap each category so a single category cannot exceed its budget.
3. Add the bounded ML adjustment and clamp the result to 0–100.

```text
raw = 100
    + max(-45, identity_points)
    + max(-40, device_points)
    + max(-30, network_points)
    + max(-25, behaviour_points)
    + max(-25, session_points)
    + ml_adjustment

score = clamp(raw, 0, 100)
ml_adjustment ∈ [-15, 0]
```

The ML adjustment is deliberately one-sided. An anomaly model may lower confidence, but it may not raise a score above the rule baseline. This keeps the rule layer authoritative and prevents a model that has learned the lab's normal traffic from silently widening access.

### 3.1 Category caps

| Category | Cap | Rationale |
|---|---|---|
| Identity | −45 | Identity failure is serious, but a single stale signal should not zero the score before hard gates run |
| Device | −40 | Posture is high-signal but remediable; hard gates handle revoked devices |
| Network | −30 | Geo-IP is noisy, especially on mobile and shared NAT |
| Behaviour | −25 | Baselines are thin for new users; behaviour is supporting evidence |
| Session | −25 | Mid-session change is urgent; kill thresholds handle the terminal cases |

### 3.2 Worked examples

**Example A — normal web login.** Valid passkey, compliant known device, office network, Tuesday 10:00. Identity 0, device 0, network 0, behaviour 0. Score 100. Band: **ALLOW**. Obligations: session TTL 30 minutes, audit.

**Example B — new device, weak posture, impossible travel.** Fresh credential −10, disk encryption off −25, stale posture −8 (device category capped at −40), impossible travel −25. Score `100 − 10 − 40 − 25 = 25`. Band: **DENY**. The request never reaches policy evaluation for an allow.

**Example C — mid-session anomaly.** Last heartbeat score 89. Disk encryption is turned off (−25), transfer volume reaches 15× baseline (−20), and two heartbeats are missed (−10). Score `89 − 25 − 20 − 10 = 34`. Band: **DENY / KILL**. The Policy Administrator closes the proxy session and revokes the SSH certificate.

**Example D — approval band.** A contractor requests a production wiki at 21:30 from a new ASN. Fresh credential −10, OS out of date −10, screen lock off −8, new ASN −8, off-hours −6, new resource class −8. Score `100 − 10 − 18 − 8 − 14 = 50`. Band: **APPROVAL**. The request enters the JIT queue; an approver can grant 30 minutes. If the same request arrives during working hours with a compliant device, the score rises to 90 and the band is **ALLOW**.

**Example E — hard gate override.** A stolen credential produces a valid-looking assertion with a regressed signature counter. The rule score would be 82, but `ID-02` is a hard gate. Decision: **DENY**, credential revoked, security alert. No arithmetic can turn the decision into an allow.

## 4. Bands and hard gates

| Band | Score | Decision | Default action |
|---|---|---|---|
| ALLOW | 80–100 | `ALLOW` | Create the session, attach obligations, audit |
| STEP-UP | 60–79 | `STEP_UP_REQUIRED` | Re-authenticate within 5 minutes; re-score on success |
| APPROVAL | 40–59 | `APPROVAL_REQUIRED` | Suspend, open a JIT request, 15-minute approval SLA |
| DENY / KILL | 0–39 | `DENY` or `KILL_SESSION` | No new session; terminate any live session and revoke credentials |

Hard gates are evaluated before the score and cannot be outvoted:

| Gate | Code | Effect |
|---|---|---|
| Invalid or unknown passkey | `PASSKEY_INVALID` | Deny |
| Signature-counter regression | `PASSKEY_COUNTER_REGRESSION` | Deny, revoke credential, alert |
| Device revoked or not enrolled | `DEVICE_REVOKED` / `DEVICE_NOT_ENROLLED` | Deny |
| Resource not in the catalog | `RESOURCE_NOT_IN_CATALOG` | Deny |
| Explicit policy deny | `POLICY_DENY` | Deny |
| Session already killed | `SESSION_ALREADY_KILLED` | Return the existing kill result |
| Administrator kill | `ADMIN_KILL` | Kill immediately |
| Score below kill threshold | `SCORE_BELOW_KILL` | Kill immediately |

## 5. Continuous evaluation

The score is recomputed on a 60-second heartbeat and on any of these events:

- a posture report changes disk, root, or OS state;
- a new device is enrolled or revoked;
- a policy version is published;
- an SSH certificate is issued or replayed;
- an anomaly model crosses its alert threshold;
- an administrator presses kill.

The Policy Administrator keeps a short-lived session cache at each enforcement point. The cache TTL is at most one second, and every proxied request still carries a session identifier that is checked against the cache. This closes the window between a kill decision and an in-flight request without adding a synchronous Policy Engine call to every byte.

Kill propagation target: **p95 ≤ 2 seconds** from decision to proxy close and certificate revocation. The SSH CA publishes a revocation list every 60 seconds; short certificate lifetimes bound the residual risk.

## 6. Explainability contract

Every decision returns the same explanation shape:

```json
{
  "decision": "STEP_UP_REQUIRED",
  "band": "STEP_UP",
  "trust_score": 67,
  "reason_codes": ["SIGNAL_NEW_ASN", "SIGNAL_OFF_HOURS", "SIGNAL_NEW_RESOURCE_CLASS"],
  "signals": [
    {"code": "NW-03", "category": "network", "points": -8, "source": "geoip"},
    {"code": "BH-05", "category": "behaviour", "points": -6, "source": "context"},
    {"code": "BH-03", "category": "behaviour", "points": -8, "source": "history"}
  ],
  "ml_adjustment": -11,
  "policy_id": "pol_7f3c",
  "policy_version": 12,
  "obligations": [
    {"type": "reauth_within", "seconds": 300},
    {"type": "limit_ttl", "seconds": 1800}
  ],
  "audit_id": "evt_01J8Z9K4",
  "correlation_id": "req_5f2b1c"
}
```

The UI shows the top three reasons and the band. The audit record stores the full signal list, the model version, and the input hash, so a reviewer can replay the decision without storing raw biometric data.

Reason-code families:

| Family | Examples | Used for |
|---|---|---|
| `HARD_GATE_*` | `HARD_GATE_DEVICE_REVOKED` | Non-negotiable failures |
| `SIGNAL_*` | `SIGNAL_IMPOSSIBLE_TRAVEL` | Rule deductions |
| `MODEL_*` | `MODEL_ANOMALY_HIGH` | ML adjustment |
| `POLICY_*` | `POLICY_REQUIRES_APPROVAL` | Policy obligations |
| `BAND_*` | `BAND_APPROVAL` | Band summary |
| `SESSION_*` | `SESSION_KILLED` | Lifecycle events |

## 7. ML anomaly layer

### 7.1 Problem framing

The ML layer answers one question: **is this session behaving unlike this user's recent normal?** It is not a classifier of intent and it does not decide access. It produces a bounded deduction that is added to the rule score.

The first model is an **Isolation Forest** because it works with unlabelled traffic, is cheap to run, and is easy to explain as a distance from the normal manifold. A supervised **LightGBM** model is a later step, once the project has enough labelled incidents from the attack demo and test sessions.

### 7.2 Features

| Group | Features |
|---|---|
| Session shape | duration, requests per minute, bytes in/out, unique resources, error rate |
| Access pattern | new resource class, resource novelty, command count (SSH), download ratio |
| Identity context | credential age, minutes since login, re-auth count, failed assertions |
| Device context | device age, posture age, disk/root flags, OS major version |
| Network context | country novelty, ASN novelty, geo velocity, anonymizer flag |
| Temporal context | local hour, weekday, holiday, time since last session |

All features are numeric or low-cardinality categoricals. Raw IP addresses and precise coordinates are not features; they are converted to novelty and velocity signals before training.

### 7.3 Model and thresholds

| Stage | Model | Output | Guardrail |
|---|---|---|---|
| Baseline | Isolation Forest, 200 trees, `max_samples=256`, contamination 0.02 | Anomaly percentile | Only subtracts; max −15 |
| Supervised | LightGBM, binary incident label, temporal 5-fold CV | Calibrated probability | Only subtracts; max −15 |
| Fallback | Rules only | 0 adjustment | Used if inference exceeds 50 ms or the model is unavailable |

Adjustment mapping for the baseline:

| Anomaly percentile | Adjustment |
|---|---|
| below 0.90 | 0 |
| 0.90–0.95 | −4 |
| 0.95–0.98 | −8 |
| above 0.98 | −15 |

The model is pinned by version. A new version is trained offline, evaluated against the current version, and run in shadow mode for at least two weeks before it can subtract points. Shadow decisions are logged but not enforced.

### 7.4 Training pipeline

1. Collect session summaries from the audit chain; never copy raw content.
2. Build features at decision time, with the same code path used in production.
3. Label incidents from kill events, explicit denies, and red-team scenarios, with a 24-hour delay to avoid leakage.
4. Split temporally: 70% train, 15% validation, 15% holdout; never split random rows from the same session.
5. Train the baseline and the supervised model; calibrate the supervised probabilities with isotonic regression.
6. Evaluate against a rules-only baseline and the previous model version.
7. Register the model with a version, feature hash, training window, and evaluation report.
8. Deploy in shadow mode; promote only after the review gate.

## 8. Evaluation plan

### 8.1 Metrics

| Metric | Target | Why it matters |
|---|---|---|
| PR-AUC | ≥ 0.55 | Incidents are rare; ROC-AUC is misleading |
| Recall at 1% FPR | ≥ 0.70 | The security team can investigate a bounded queue |
| Alert volume | ≤ 5 per 100 sessions per day | Alert fatigue is a security failure |
| p95 inference latency | ≤ 15 ms | The score sits in the authorization path |
| Calibration error | ≤ 0.05 | A probability should mean what it says |
| PSI | < 0.10 | Detect feature drift before decisions drift |
| Coverage | ≥ 95% of sessions scored | A silent model is worse than no model |
| Shadow disagreement | < 10% of decisions | A new model should not surprise reviewers |

### 8.2 Test design

- **Temporal holdout:** the last 30 days of sessions, with no session split across folds.
- **Ablation:** rules-only, rules + Isolation Forest, rules + LightGBM, and rules + both.
- **Scenario tests:** replay, stolen certificate, impossible travel, 15× download, credential stuffing, insider slow-and-low.
- **Stability:** bootstrap confidence intervals for PR-AUC and recall; report the interval, not only the point estimate.
- **Fairness:** compare false-positive rates across teams, device types, and coarse regions. Do not use protected attributes as features. Investigate gaps above 2×.
- **Adversarial:** red-team attempts to evade the model by staying under volume thresholds, rotating ASNs, or mimicking normal hours. The rule layer is the backstop.

### 8.3 Rollout

| Phase | Duration | Gate |
|---|---|---|
| Offline evaluation | 2 weeks | Metrics table complete; no leakage |
| Shadow mode | 2 weeks | Disagreement < 10%; no hard-gate overrides |
| Canary | 1 week | 10% of sessions; p95 latency within budget |
| General availability | — | Review sign-off; rollback plan tested |
| Monitoring | continuous | Weekly PSI, monthly review, retrain on drift |

## 9. NIST and control mapping

| Reference | Mapping |
|---|---|
| NIST SP 800-207 §2.1 | Policy Decision Point and Policy Enforcement Point separation |
| NIST SP 800-207 §3.1 | A concrete trust algorithm with named inputs and outputs |
| NIST SP 800-207 §3.3 | Continuous evaluation and mid-session termination |
| NIST SP 800-207A §3.2 | Short-lived SSH credentials and a CA that never exports its key |
| NIST SP 800-207A §3.3 | SecureVault secret storage and Shamir recovery |
| NIST SP 800-63B | Passkey authentication, re-authentication, recovery |
| NIST SP 800-53 AC-3 | Policy enforcement and deny-by-default |
| NIST SP 800-53 AC-12 | Session termination |
| NIST SP 800-53 AU-9 | Protection of audit information |
| NIST SP 800-53 IA-2 / IA-5 | Identity proofing and authenticator management |
| NIST SP 800-53 SC-8 / SC-12 / SC-13 | Transmission protection and key management |
| NIST SP 800-53 SI-4 | Monitoring and anomaly detection |

## 10. Limitations and open questions

1. **No production data.** Weights are expert-set priors, calibrated against synthetic traffic and test-participant sessions. They are a defensible starting point, not a validated production model.
2. **Geo-IP is noisy.** Mobile carriers, corporate NAT, and VPNs produce false positives. The network category is capped at −30 for this reason.
3. **New users have no baseline.** Behaviour signals are suppressed for the first 14 days; identity and device signals carry the decision.
4. **ML labels are scarce.** The supervised model is a later step; the Isolation Forest is the honest baseline.
5. **Score does not encode resource sensitivity.** A wiki and a production database can receive the same score. Resource sensitivity is a policy input and an obligation, not a score signal.
6. **No multi-tenancy.** The model and the schema assume one organization; per-tenant calibration is future work.
7. **Attack demo is not a penetration test.** It is a repeatable demonstration of specific failure modes, not evidence that the system is unhackable.

## Appendix A — Decision response for the kill sequence

```json
{
  "decision": "KILL_SESSION",
  "band": "DENY",
  "trust_score": 34,
  "reason_codes": [
    "SIGNAL_DISK_ENCRYPTION_OFF",
    "SIGNAL_EXTREME_VOLUME",
    "SIGNAL_HEARTBEAT_MISSED"
  ],
  "ml_adjustment": 0,
  "policy_id": "pol_live_session",
  "policy_version": 8,
  "obligations": [
    {"type": "terminate_session", "session_id": "ses_01J8Z8"},
    {"type": "revoke_ssh_certificate", "certificate_id": "sshcert_77a1"},
    {"type": "notify_admin", "channel": "security"}
  ],
  "audit_id": "evt_01J8ZA7Q",
  "correlation_id": "req_9b3e2a"
}
```
