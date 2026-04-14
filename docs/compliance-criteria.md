# Compliance Criteria (P0)

This checklist is used to validate PRs that affect licensing, distribution, or product tier boundaries.

## PR compliance checklist

- [ ] License obligations preserved (`LICENSE`, headers, attribution where required).
- [ ] `NOTICE` updated if attribution/distribution context changed.
- [ ] `THIRD_PARTY_LICENSES.md` updated if dependencies changed.
- [ ] No proprietary third-party code/assets copied without written permission.
- [ ] Free/Premium behavior reflected in `docs/free-premium-matrix.md`.
- [ ] Boundary impact reviewed in `docs/open-core-boundary.md`.
- [ ] Legal-sensitive claims marked for counsel review when needed.
- [ ] Secrets handling unchanged or improved (`.env` excluded, no credential leaks).

## Release gate checklist

- [ ] Draft legal docs exist: `docs/legal/EULA.md`, `docs/legal/PRIVACY.md`, `docs/legal/TERMS.md`.
- [ ] Legal drafts reviewed by counsel before commercial release.
- [ ] Distribution package includes `LICENSE`, `NOTICE`, and third-party notices.
- [ ] Public README/About messaging matches actual tier behavior.

