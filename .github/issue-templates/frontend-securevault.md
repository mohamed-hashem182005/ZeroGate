## Context
Implement the SecureVault desktop application (Java/JavaFX) for storing and sharing team credentials and requesting short-lived SSH certificates instead of permanent keys.

## Requirements
- Store and share team credentials (password manager functionality)
- Request short-lived SSH certificates from SSH CA
- k-of-n Shamir recovery shares UI (split secret, rebuild from k shares)
- Desktop app in Java/JavaFX (as per existing SecureVault fork)

## Acceptance Criteria
- [ ] Credentials stored and shared securely
- [ ] Short-lived SSH cert request functional
- [ ] k-of-n Shamir recovery UI works (split → rebuild)
- [ ] Desktop app runs on target platforms

## References
- `docs/functional-requirements.md` — FR-09, FR-10 (SecureVault, k-of-n recovery)
- Existing fork: `mohamed-hashem182005/SecureVault`
- Team: Frontend | Priority: Core
