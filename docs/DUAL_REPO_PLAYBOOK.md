# Dual Repo Playbook (PingEase + PingEase-Premium)

Operational guide for running open-core and premium development in parallel without leaking premium logic into the core.

## Repositories and Roles

- Open-core: `LEAR-Software/PingEase`
- Premium: `LEAR-Software/pingease-premium`

### Source of truth

- Product backlog source: issue tracker in `LEAR-Software/PingEase`
- Premium implementation backlog: issue tracker in `LEAR-Software/pingease-premium`
- Core project board: `LEAR-Software` project `#4` (`PingEase MVP Backlog`)
- Premium project board: `LEAR-Software` project `PingEase Premium Backlog`

## Layer Boundary Rules

1. Core defines public contracts (API/IPC/service behavior).
2. Premium consumes contracts; it does not define them.
3. If premium needs a contract change, create/update a core issue first.
4. No premium policy packs, licensing logic, or commercial entitlements in open-core.
5. Any tiering change must update:
   - `docs/open-core-boundary.md`
   - `docs/free-premium-matrix.md`

## Development Order

### Phase 1: Foundation (P0)

Build/lock service-ready contracts in core first, then wire premium against released contracts.

### Phase 2: MVP completion (P1)

Deliver core MVP capabilities, then premium packaging and rollout mechanics.

### Phase 3: Hardening (P2)

Split hardening by layer: reliability/compliance in core, policy/commercial controls in premium.

## Cross-Repo Issue Model

For every premium-facing initiative:

1. Keep or create parent issue in core.
2. Create mirror issue in premium.
3. Link both sides explicitly.

Use this link block in both issues:

```markdown
## Cross-repo links
- Parent/Core issue: <url>
- Premium mirror issue: <url>
- Related PRs: <url>, <url>
```

## Cross-Repo PR Model

Every PR that impacts roadmap must include:

- Related issue in same repo (`Fixes #...`)
- Cross-repo reference (issue or PR URL)
- Boundary confirmation (`open-core-boundary` + `free-premium-matrix`)

Example (premium draft PR):

```bash
gh pr create \
  --repo LEAR-Software/pingease-premium \
  --base main \
  --head feature/P0-07-prem-entitlement-gate \
  --draft \
  --title "[P0-07-PREM] Integrate entitlement gate into premium execution flow" \
  --body "Fixes #2

Parent core issue:
- https://github.com/LEAR-Software/PingEase/issues/8"
```

## Dual Release Checklist

- [ ] Core tag created and published (SemVer)
- [ ] Premium release pinned to exact core tag/SHA
- [ ] Compatibility note added (`premium -> core version`)
- [ ] Compliance artifacts updated (`NOTICE`, `THIRD_PARTY_LICENSES.md`, legal docs if needed)
- [ ] Rollback steps validated
- [ ] Project items moved to Done in both boards

## Weekly Cadence

- Monday: backlog triage (P0/P1/P2) and dependency cleanup.
- Wednesday: PR review + boundary/compliance gate.
- Friday: release cut, version pinning, and session log update in `AGENTS.md`.

## Ownership Convention

- Core owner field: who merges in `PingEase`.
- Premium owner field: who merges in `pingease-premium`.
- A work item is complete only when both layers are complete (if both are in scope).

