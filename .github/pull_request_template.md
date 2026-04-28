<!-- PingEase PR Template -->

## Related Issue(s)
<!-- Link to related backlog issue(s): Fixes #XX -->

## Session Traceability
- Session issue: <!-- #XX -->
- Working branch: <!-- type/Pn-XX-short-slug -->

## Cross-Repo Traceability (required if roadmap-impacting)
- Peer repository: <!-- LEAR-Software/PingEase | LEAR-Software/pingease-premium -->
- Peer issue: <!-- URL or #id -->
- Peer PR: <!-- URL if already opened -->

## Description
<!-- Describe the changes in this PR. What problem does it solve? -->

## Type of Change
<!-- Mark one with an "x" -->
- [ ] Bug fix
- [ ] Feature
- [ ] Documentation
- [ ] Refactoring
- [ ] Dependency update

## Priority
<!-- From backlog: P0, P1, or P2 -->
- [ ] P0 (Must ship first)
- [ ] P1 (MVP completion)
- [ ] P2 (Post-MVP hardening)

## Checklist (before submitting)

### Functional
- [ ] Changes compile/run locally
- [ ] Tests pass locally (if applicable)
- [ ] Dry-run works unchanged (if applicable to core)

### Compliance Gate
- [ ] Obligations of `LICENSE` preserved (MIT, attribution, headers if applicable)
- [ ] `NOTICE` updated if distribution/attribution context changes
- [ ] `THIRD_PARTY_LICENSES.md` updated if dependencies change
- [ ] No proprietary/third-party code copied without written permission
- [ ] No hardcoded credentials or secrets in code
- [ ] `.env` ignored in git (no environment config in repo)

### Open-Core Boundary Check
- [ ] Reviewed against `docs/open-core-boundary.md`
- [ ] Reviewed against `docs/free-premium-matrix.md`
- [ ] No premium-sensitive logic merged into open-core without explicit approval

### Dual Release Gate (if applicable)
- [ ] Core/Premium compatibility noted (core tag or SHA referenced)
- [ ] Cross-repo issue status synced
- [ ] Release/rollback notes updated

### CI & Branch Protection
- [ ] All GitHub Actions checks pass (CI, audit, etc.)
- [ ] No merge conflicts
- [ ] If needed, rebased onto latest `main`
- [ ] Branch name is aligned with related issue (`<type>/Pn-XX-*`)

### Documentation (if applicable)
- [ ] Architecture docs updated if behavior changes
- [ ] README/user-facing docs updated if user-observable change
- [ ] Inline comments for non-obvious logic

## Testing Evidence
<!-- Attach logs, screenshots, or test output as proof of working functionality -->

## Notes
<!-- Any additional context for reviewers -->

---

**Reference Links:**
- Backlog: `docs/mvp-windows-backlog.md`
- Dual repo playbook: `docs/DUAL_REPO_PLAYBOOK.md`
- Compliance criteria: `docs/compliance-criteria.md`
- Open-core boundary: `docs/open-core-boundary.md`
- Free/Premium matrix: `docs/free-premium-matrix.md`

