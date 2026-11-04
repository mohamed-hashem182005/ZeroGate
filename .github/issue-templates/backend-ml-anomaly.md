## Context
Implement the ML anomaly adjustment model that feeds a bounded adjustment (−15 cap) into the trust score. The model must never override a hard gate or a policy denial.

## Requirements
- Train/detect behavioral anomalies during a session (not just at login)
- Model card + explainability contract: every point attributable to a named signal
- Bounded adjustment capped at −15
- Model cannot override hard gates or policy denials
- Feeds into Policy Engine as one input among many
- Inference latency ≤ 100ms

## Acceptance Criteria
- [ ] Model card documented (signals, categories, caps, hard gates)
- [ ] Anomaly detection works during-session, not only at login
- [ ] Adjustment capped at −15
- [ ] Model cannot override hard gates or policy denial
- [ ] Reason codes + point deductions provided for every score
- [ ] Inference completes in ≤ 100ms

## References
- `docs/risk-scoring-report.md` — ML anomaly adjustment design
- Team: Backend & AI | Priority: Core
