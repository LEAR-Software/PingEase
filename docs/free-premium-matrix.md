# Free vs Premium Matrix (P0)

Purpose: define product boundaries for PingEase without breaking MIT open-core obligations.

## Product tiers

- Free / Shareware: trial (7-14 days) or limited feature set.
- Premium Personal: 1 user, 1-3 devices.
- Premium Pro/Business: optional enterprise tier.

## Capability matrix

| Capability | Free / Shareware | Premium Personal | Premium Pro/Business | Implementation location | Legal note |
|---|---|---|---|---|---|
| RF monitor (`--monitor`) | Yes | Yes | Yes | Open-core repo | MIT notices required |
| Window analysis (`--analyze`) | Yes | Yes | Yes | Open-core repo | MIT notices required |
| Dry-run optimization (`--once --dry-run`) | Yes | Yes | Yes | Open-core repo | MIT notices required |
| Real router apply | Limited (trial/quota/profile limits) | Full | Full | Open-core behavior + premium gate outside repo | Validate final gating language with counsel |
| Emergency profile controls | Basic | Advanced | Advanced + policy packs | Premium layer | Commercial terms apply |
| License activation (offline signed) | No | Yes | Yes | Premium layer | EULA + counsel review |
| Online activation/revocation | No | Optional | Optional + admin | Premium services | Privacy/Terms + counsel review |
| Priority support | No | Standard | Priority/SLA | Commercial ops | Terms of Sale required |

## Guardrails

- Do not remove MIT copyright/license notices from open-core derived files.
- Do not copy proprietary third-party code/assets without explicit written permission.
- Keep premium-only licensing logic out of open-core unless explicitly documented and approved.

## Change protocol

When changing tier behavior:
1. Update this file.
2. Update `docs/open-core-boundary.md` if boundaries changed.
3. Update `docs/compliance-criteria.md` checklist references.
4. Mark legal-sensitive text as pending counsel if not yet validated.

