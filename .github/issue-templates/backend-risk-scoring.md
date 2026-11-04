## Context
Implement the rule-based risk scoring engine: a transparent additive model starting at 100 with per-signal deductions. Hard gates are evaluated before arithmetic. The ML anomaly adjustment is separate and capped at −15.

## Requirements
- Additive scoring model: start at 100, apply negative deductions per signal
- Signals grouped into five categories: identity, device, location, time, behavior
- Hard gates evaluated before arithmetic (unknown credential, counter regression)
- Each signal counted at most once per evaluation; more specific rule wins on conflict
- ML adjustment capped at −15, cannot override hard gates or policy denial
- Score feeds into Policy Engine as one input (not a decision)
- Continuous re-evaluation during a session, not only at login

## Acceptance Criteria
- [ ] Score ranges 0–100 with four trust bands applied consistently
- [ ] Every point attributable to a named signal (explainable with reason codes)
- [ ] Hard gates evaluated before arithmetic
- [ ] ML adjustment capped at −15
- [ ] Score triggers continuous re-evaluation during session

## References
- `docs/risk-scoring.html` — Risk scoring design
- `docs/risk-scoring-report.md` — Signal catalog and model design
- Team: Backend & AI | Priority: Core
