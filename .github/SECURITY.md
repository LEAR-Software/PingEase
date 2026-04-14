# Security Policy

## Supported Scope

This repository currently covers the open-core baseline for PingEase.

In-scope reports:
- Credential leaks (`.env`, router passwords, API keys, tokens)
- Unsafe command execution or shell injection
- Privilege escalation in local service flows
- Insecure local API exposure (if service/API components are added)
- Dependency vulnerabilities in shipped artifacts

Out-of-scope reports:
- Router firmware vulnerabilities outside this codebase
- Self-host misconfiguration on user devices

## How To Report

Please do not open public issues for security vulnerabilities.

Report privately via one of these channels:
- GitHub Security Advisories (preferred)
- Maintainer email (configure in repo settings)

Include:
- Affected version / commit
- Reproduction steps
- Impact and suggested fix
- Whether secrets may have been exposed

## Response Targets

- Initial acknowledgment: 72 hours
- Triage decision: 7 days
- Fix timeline: based on severity and reproducibility

## Secret Handling Rules

- Never commit `.env`, dumps, or router credentials.
- Rotate any exposed credential immediately.
- Use masked CI secrets; never print secrets in logs.
- Keep diagnostic HTML artifacts (`router_*.html`) out of git.

## Disclosure

We follow coordinated disclosure. Public details should wait until a fix is available or risk is accepted by maintainers.

