# Open-Core Boundary

This document defines what belongs in open-core vs premium/commercial layers.
It is the product-boundary source of truth for this repository.

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
- **Entitlement gate** (`evaluate_entitlement`, `EntitlementStatus`, `license_token` enforcement) — P0-07 confirmed in premium layer only

## P0 Matrix - Free vs Premium

Status key:
- `Defined today`: accepted as current boundary for implementation.
- `Pending counsel`: legal wording/packaging still needs legal review.

| Capability | Free / Shareware | Premium Personal | Premium Pro/Business | Boundary | Status |
|---|---|---|---|---|---|
| RF scan + congestion scoring | Included | Included | Included | Open-core | Defined today |
| Dry-run optimization cycle | Included | Included | Included | Open-core | Defined today |
| Real channel apply automation | Trial-limited or basic profile | Full | Full | Open-core + commercial gating layer | Defined today |
| Advanced profiles/policies | Limited presets | Full profile controls | Team policy packs | Premium layer | Defined today |
| License activation and seat/device limits | Not applicable | 1 user / 1-3 devices | Multi-device/team | Premium layer | Defined today |
| Priority support/SLA | Community only | Standard support | Priority support | Commercial ops | Defined today |
| Cloud revoke/reissue + telemetry controls | Not included | Optional | Optional + admin controls | Premium services | Pending counsel |

Reference docs:
- `docs/free-premium-matrix.md`
- `docs/compliance-criteria.md`
- `docs/mvp-windows-backlog.md`
- `docs/architecture/P0-07-boundary-gate.md` (P0-07 entitlement gate architecture note)

## Non-negotiable Legal Rules

- MIT notices must remain intact for open-core derived code.
- No proprietary third-party code/assets copied without explicit written permission.
- Legal texts (`EULA`, `Privacy`, `Terms`) require counsel validation before release.

## Change Control

If a feature touches licensing/commercial boundaries, create a short architecture note in PR:
- Scope (open-core or premium)
- Compliance impact
- Distribution impact

Every boundary-changing PR must also:
- update `docs/free-premium-matrix.md` if tier behavior changes,
- confirm `NOTICE`/`THIRD_PARTY_LICENSES.md` impact,
- mark legal-sensitive claims as `Pending counsel` when applicable.

