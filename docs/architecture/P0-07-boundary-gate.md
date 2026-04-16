# P0-07 Free/Premium Boundary Gate - Architecture Note

## Decision

The entitlement gate (Free/Premium check) lives entirely in `LEAR-Software/pingease-premium`.
Open-core (`LEAR-Software/PingEase`) does **not** contain any commercial entitlement logic.

## Rationale

- MIT open-core must remain free of licensing/seat/device enforcement.
- Core defines the behavioral contract (service API, channel apply, dry-run).
- Premium layer consumes the versioned core contract and applies the entitlement gate before
  allowing real channel apply operations.

## Core contract consumed by premium

- Service API contract: `docs/architecture/SERVICE_API_CONTRACT_V1.md`
- Behavioral boundaries: `docs/open-core-boundary.md` and `docs/free-premium-matrix.md`
- Premium gate entry point: `evaluate_entitlement(license_token, ...)` in premium repo

## Confirmed boundary (P0-07)

| Layer    | Responsibility                                                | Status       |
|----------|---------------------------------------------------------------|--------------|
| Core     | RF scan, dry-run cycle, channel decision, revert safety       | Open-core    |
| Core     | Router driver contracts (`BaseRouter`)                        | Open-core    |
| Premium  | Entitlement gate (`EntitlementStatus`, `evaluate_entitlement`)| Premium only |
| Premium  | Seat validation, device registration enforcement              | Premium only |
| Premium  | `license_token` handling and resolver                         | Premium only |

## Fail-closed guarantee

If the premium entitlement gate is unreachable or the resolver raises an exception,
the gate **denies** with `reason_code=resolver_error`. No premium capability is granted
by default on error.

## Cross-repo traceability

- Core issue: [#8 [P0-07] Define Free/Premium gate outside open-core](https://github.com/LEAR-Software/PingEase/issues/8)
- Premium mirror issue: [#2 [P0-07-PREM]](https://github.com/LEAR-Software/pingease-premium/issues/2)
- Premium implementation PR: https://github.com/LEAR-Software/pingease-premium/pull/5

## Compatibility note

Premium pins to a specific core tag/SHA before release.
Current status: `pending` (to be locked before first premium release).

