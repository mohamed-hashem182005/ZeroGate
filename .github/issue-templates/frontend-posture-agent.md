## Context
Implement the device posture agent: a background agent (no UI) that reports OS version, disk encryption state, root/jailbreak state, and a signed timestamp.

## Requirements
- Background agent with no UI
- Reports OS version, disk encryption status, root/jailbreak state, signed timestamp
- Reports arrive within 60 seconds of a change
- Tampering must be detectable
- Report contains no file contents or browsing data

## Acceptance Criteria
- [ ] Agent runs in background with no UI
- [ ] Reports OS version, disk encryption, root/jailbreak, signed timestamp
- [ ] Reports arrive within 60 s of change
- [ ] Tampering detectable
- [ ] No sensitive data (file contents, browsing) in reports

## References
- `docs/functional-requirements.md` — FR-04
- Team: Frontend | Priority: Core
