# Contributing

Thanks for contributing to PingEase.

## Security and Secrets

- Never commit `.env`, credentials, or generated router dumps.
- If you accidentally expose a secret, rotate it immediately and notify maintainers.
- Use GitHub Security Advisories for sensitive vulnerabilities.

## Legal and Compliance Rules

- Respect MIT obligations for open-core files.
- Do not copy code or assets from proprietary third-party software.
- Prefer integration via API/CLI/plugin wrappers over source copying.
- Keep `NOTICE` and `THIRD_PARTY_LICENSES.md` updated when dependencies change.
- Keep `docs/free-premium-matrix.md` updated when tier behavior changes.
- Use `docs/compliance-criteria.md` as PR checklist for legal/commercial-impact changes.

## Open-Core Boundary

- Contributions in this repository target the open-core baseline.
- Premium-only behavior must remain outside this repository unless explicitly documented.
- See `docs/open-core-boundary.md` for allowed scope.
- Product tiers and feature mapping live in `docs/free-premium-matrix.md`.

## Pull Request Rules

- Small, focused PRs with clear rationale.
- Include risk notes for router automation changes.
- Update docs when behavior or compliance obligations change.
- For roadmap items, create issues using `.github/ISSUE_TEMPLATE/backlog-p0-p1-p2.md`.

