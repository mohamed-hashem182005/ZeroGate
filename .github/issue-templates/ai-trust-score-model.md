## Context
Implement the trust score ML model: a transparent additive model with bounded anomaly adjustment, not a black box. Every point must be attributable to a named signal.

## Requirements
- Additive model starting at 100 with per-signal deductions
- Five signal categories: identity, device, location, time, behavior
- Hard gates evaluated before arithmetic (unknown credential, counter regression)
- Bounded anomaly adjustment capped at −15
- Continuous re-evaluation during a session
- Model card documenting signals, categories, caps, and hard gates
- Output explainable reason codes + point deductions for every score

## Acceptance Criteria
- [ ] Model produces score 0–100 with explainable reason codes
- [ ] Hard gates evaluated before arithmetic
- [ ] Bounded anomaly adjustment capped at −15
- [ ] Continuous re-evaluation triggers on signal change
- [ ] Model card documented and reviewed
- [ ] Inference latency ≤ 100ms

## References
- `docs/risk-scoring.html` — Risk scoring design
- `docs/risk-scoring-report.md` — Signal catalog and model design
- Team: AI (with Backend & AI) | Priority: Core
