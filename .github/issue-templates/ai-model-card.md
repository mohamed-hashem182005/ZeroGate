## Context
Document the model card and explainability contract for the trust scoring engine. Every point must be attributable to a named signal, every category capped, and every hard gate evaluated before arithmetic.

## Requirements
- Model card document: model overview, intended use, training data, evaluation metrics
- Explainability contract: every point attributable to a named signal
- Signal catalog with point values and conditions
- Category caps documentation (so one bad observation cannot dominate)
- Hard gates documentation (conditions that result in immediate denial)
- Guidelines for defending the model in an academic review

## Acceptance Criteria
- [ ] Model card document completed
- [ ] Explainability contract documented
- [ ] Signal catalog complete with point values and conditions
- [ ] Category caps and hard gates clearly defined
- [ ] Ready for defense presentation

## References
- `docs/risk-scoring-report.md` — Full report on risk scoring model
- Team: AI (with Backend & AI) | Priority: Core
