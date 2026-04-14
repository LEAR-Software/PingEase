# Third-Party Licenses

This file tracks third-party dependencies and their license obligations for distribution.

## Python dependencies (current)

| Package | Purpose | License | Source |
|---|---|---|---|
| playwright | Browser automation for router UI flows | Apache-2.0 (verify release) | https://pypi.org/project/playwright/ |
| python-dotenv | Load configuration from `.env` | BSD-3-Clause (verify release) | https://pypi.org/project/python-dotenv/ |

## Notes

- Verify exact license per pinned version before shipping installer binaries.
- Add transitive dependencies when packaging distributable artifacts.
- If a dependency license changes, update this file before release.

