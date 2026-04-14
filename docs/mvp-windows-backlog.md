# MVP Windows Backlog (P0/P1/P2)

Purpose: convert product/compliance decisions into executable work for a 2-6 week Windows-first MVP.

Scope assumptions:
- Open-core remains in this repository under MIT obligations.
- Premium licensing/activation layer stays outside this repository unless explicitly approved.
- Legal text remains draft until counsel validation.

Sizing scale:
- S: <= 2 days
- M: 3-5 days
- L: 6-10 days

## P0 - Must ship first

| ID | Work item | Effort | Depends on | Minimum DoD |
|---|---|---|---|---|
| P0-01 | Stabilize core API surface (`run_optimization_cycle`, config schema) for service integration | M | Current `main.py`, `wifi_optimizer/optimizer.py` | Core entrypoint callable by service wrapper without CLI-only assumptions; dry-run works unchanged |
| P0-02 | Add service-ready command mode (`--service-once` or equivalent internal API contract) | M | P0-01 | Service can trigger safe cycle and get structured result (`status`, `changed`, `reason`) |
| P0-03 | Define local IPC/API contract draft for UI <-> service (JSON schema + error model) | S | P0-01 | `docs/architecture/service-api-contract.md` with request/response examples and error codes |
| P0-04 | Windows service skeleton (install/start/stop/log/healthcheck) | L | P0-02, P0-03 | Service starts on boot, exposes health endpoint/pipe, writes rotated logs |
| P0-05 | Secrets baseline for Windows runtime (no plaintext in repo, env loading policy, credential storage decision) | M | P0-04 | `docs/architecture/secrets.md` defines storage, access, rotation, and rollback rules |
| P0-06 | Compliance release bundle v1 (`LICENSE`, `NOTICE`, `THIRD_PARTY_LICENSES`, legal drafts linked) | S | Existing docs | `docs/compliance-criteria.md` release checklist passes for draft release |
| P0-07 | Free/Premium gate definition (outside repo) with open-core boundaries frozen | M | `docs/free-premium-matrix.md` | Tier behavior mapped to matrix; no premium lock logic merged into open-core code |
| P0-08 | CI hardening minimum (compile check + dependency audit + required status checks) | S | Existing workflows | PR fails on compile/audit failure; branch protection checks are active |

## P1 - MVP completion

| ID | Work item | Effort | Depends on | Minimum DoD |
|---|---|---|---|---|
| P1-01 | UI MVP (status, run cycle, metrics view, profile config) | L | P0-03, P0-04 | UI reads service status and safely triggers cycle with user feedback |
| P1-02 | Structured telemetry (opt-in) and diagnostics package export | M | P0-04 | User can export sanitized diagnostics without credentials |
| P1-03 | Installer and update strategy draft (MSI/winget/manual) + rollback flow | M | P1-01 | Install/update/uninstall tested on clean Windows VM |
| P1-04 | Router driver test harness with mockable `BaseRouter` contract | M | P0-01 | Contract tests validate read/apply behavior and error mapping |
| P1-05 | Docs alignment: PingEase naming in both READMEs + architecture docs | S | Current docs | No stale `WifiChannelOptimizer` naming in user-facing product sections |

## P2 - Post-MVP hardening

| ID | Work item | Effort | Depends on | Minimum DoD |
|---|---|---|---|---|
| P2-01 | Multi-router roadmap and plugin packaging model | M | P1-04 | Driver onboarding template + compatibility matrix published |
| P2-02 | Premium Pro/Business policy packs and multi-device controls (outside repo) | L | P0-07, P1-03 | Commercial controls validated in staging with license server |
| P2-03 | Binary signing and trust pipeline (code signing cert + verification) | M | P1-03 | Signed artifacts verified pre-release |
| P2-04 | Performance and reliability benchmarks (cycle latency, failure recovery) | M | P1-01 | Baseline metrics documented and tracked per release |

## Compliance gates by priority

- P0 PRs must satisfy all items in `docs/compliance-criteria.md` PR checklist.
- Any tier change must update `docs/free-premium-matrix.md` in the same PR.
- Any legal-sensitive wording must be marked pending counsel until reviewed.

## Suggested execution cadence (2-6 weeks)

- Week 1: P0-01, P0-02, P0-03, P0-08
- Week 2: P0-04, P0-05, P0-06, P0-07
- Week 3-4: P1-01, P1-04
- Week 4-5: P1-02, P1-03, P1-05
- Week 6+: P2 hardening items

## Next 48h (recommended)

1. Freeze P0 scope and owners per item.
2. Create issues from P0 table with DoD copied verbatim.
3. Draft `docs/architecture/service-api-contract.md` and `docs/architecture/secrets.md`.
4. Start P0-01 with a small refactor PR that introduces service-safe core entrypoints.

