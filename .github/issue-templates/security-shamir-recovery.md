## Context
Implement k-of-n Shamir's Secret Sharing for vault recovery: split the vault secret into n shares, any k shares rebuild it, k-1 shares reveal nothing.

## Requirements
- Shamir's Secret Sharing implementation (e.g., 5 shares: 3 to rebuild)
- Split vault secret into shares (held by teammates, admin, paper backup)
- Any k shares rebuild the secret
- k-1 shares reveal nothing (information-theoretically secure)
- Recovery API and integration with SecureVault
- UI in SecureVault for split and rebuild operations

## Acceptance Criteria
- [ ] Vault secret splits into n shares
- [ ] Any k shares rebuild the secret
- [ ] k-1 shares reveal nothing (information-theoretically secure)
- [ ] Recovery API functional
- [ ] SecureVault UI for split/rebuild works

## References
- `docs/functional-requirements.md` — FR-10
- Team: Security & Hardware (with Frontend) | Priority: Core
