# Open-Core Boundary

This document defines what belongs in open-core vs premium/commercial layers.

## Open-Core (this repository)

- RF scanning and congestion analysis
- Channel decision logic and safe revert behavior
- Router driver contracts (`BaseRouter`) and documented integrations
- Local logging and quality metrics
- Compliance artifacts (`LICENSE`, `NOTICE`, third-party notices)

## Premium / Commercial (outside this repository)

- Paid activation, seat management, device limits
- Commercial UI bundles and installer flows
- Business-only orchestration and enterprise policies
- Cloud services for licensing/telemetry (if any)

## Non-negotiable Legal Rules

- MIT notices must remain intact for open-core derived code.
- No proprietary third-party code/assets copied without explicit written permission.
- Legal texts (`EULA`, `Privacy`, `Terms`) require counsel validation before release.

## Change Control

If a feature touches licensing/commercial boundaries, create a short architecture note in PR:
- Scope (open-core or premium)
- Compliance impact
- Distribution impact

