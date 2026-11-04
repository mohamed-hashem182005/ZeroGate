## Context
Set up the lab environment with internal web applications and Linux SSH servers as protected resources, with network isolation ensuring no direct access to resources (all traffic through proxy/CA).

## Requirements
- Internal web apps deployed as protected resources
- Linux SSH servers deployed as protected resources
- Network isolation: no direct access to resources
- All HTTP traffic through web reverse proxy (PEP)
- All SSH traffic through SSH CA and helper
- Lab network diagram documented

## Acceptance Criteria
- [ ] Internal web apps deployed and protected
- [ ] Linux SSH servers deployed and protected
- [ ] Network isolation verified (direct access blocked)
- [ ] All traffic flows through proxy/CA
- [ ] Lab network diagram documented

## References
- `docs/architecture.html` — Component architecture
- Team: Networking | Priority: Core
