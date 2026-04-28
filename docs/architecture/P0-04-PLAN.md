# P0-04 Plan — Windows Service Skeleton

**Issue:** [#5 \[P0-04\] Implement Windows service skeleton](https://github.com/LEAR-Software/PingEase/issues/5)  
**Branch:** `feature/P0-04-windows-service-skeleton`  
**Base:** `main` (after P0-03 merge)  
**Status:** In progress

---

## Objective

Implement a long-running Windows service skeleton that:
1. Generates an ephemeral session (id + secret) at startup.
2. Delivers those credentials to the UI via a well-known bootstrap file in `%TEMP%`.
3. Exposes an authenticated HTTP IPC endpoint (`POST /ipc`) backed by `handle_request`.
4. Exposes a lightweight health probe (`GET /health`).
5. Writes rotating log files to the system temp directory.
6. Shuts down cleanly on stop, removing the bootstrap file.

---

## Architecture

```
main.py --service
    └── ServiceRunner.run_forever()
            ├── generate ephemeral session_id + session_secret (secrets.token_hex)
            ├── write_bootstrap() → %TEMP%\pingease-service.json
            ├── HTTPServer(127.0.0.1:<random_port>)
            │       ├── GET  /health  → {"ok": true, "status": "running", "ts_ms": ...}
            │       └── POST /ipc    → handle_request() → OptimizationService.run_cycle()
            └── serve_forever() [daemon thread]
```

### Bootstrap file schema

```json
{
  "pid": 12345,
  "host": "127.0.0.1",
  "port": 54321,
  "session_id": "<8-byte hex>",
  "session_secret": "<32-byte hex>",
  "started_at_ms": 1714262400000
}
```

Path: `%TEMP%\pingease-service.json`  
Lifecycle: written on `start()`, deleted on `stop()`.  
**Security note:** the secret is in plaintext on the local filesystem.  
This is acceptable for MVP (same user, no multi-tenant) but should be replaced by a named-pipe bootstrap in a future iteration.

---

## Files Changed

| File | Change |
|------|--------|
| `wifi_optimizer/service_runner.py` | New — `ServiceRunner`, `write_bootstrap`, `remove_bootstrap`, `configure_logging` |
| `main.py` | Added `--service` flag dispatching to `ServiceRunner.run_forever()` |
| `tests/test_service_runner.py` | New — 20 tests covering bootstrap, lifecycle, `/health`, `/ipc` (no-auth + HMAC) |
| `docs/architecture/P0-04-PLAN.md` | This file |

---

## Session Handshake (gap closed)

The gap documented in `IPC-SESSION-HANDSHAKE-GAP.md` is resolved via the bootstrap file approach:

1. Service generates `session_id` + `session_secret` using `secrets.token_hex`.
2. Both values are written to `%TEMP%\pingease-service.json` at startup.
3. UI reads the bootstrap file to discover `host`, `port`, `session_id`, and `session_secret`.
4. UI signs every request with `compute_auth_signature(...)` from `ipc_adapter.py`.
5. Service validates HMAC, nonce, and timestamp on every `POST /ipc` request.

---

## CLI Usage

```
# Start authenticated service (production)
python main.py --service

# Start unauthenticated service (dev / dry-run)
python main.py --service --dry-run
```

---

## Definition of Done

- [x] `ServiceRunner` implemented in `wifi_optimizer/service_runner.py`
- [x] Ephemeral `session_id` + `session_secret` generated at startup
- [x] Bootstrap file written to `%TEMP%\pingease-service.json`
- [x] Bootstrap file removed on clean shutdown
- [x] `GET /health` returns `{"ok": true, ...}`
- [x] `POST /ipc` validates HMAC auth and dispatches `run_cycle`
- [x] Rotating log file in `%TEMP%\pingease-service.log`
- [x] `--service` flag wired in `main.py`
- [x] 20 unit tests — all passing
- [x] Full suite: 60/60 tests green
- [ ] PR opened and CI passing
- [ ] `docs/architecture/IPC-SESSION-HANDSHAKE-GAP.md` updated to `Resolved`

---

## Known Limitations (post-MVP)

| Limitation | Future improvement |
|---|---|
| Bootstrap secret in plaintext tempfile | Replace with named-pipe one-time token |
| Single-process HTTP server | Consider `asyncio` / `uvicorn` for concurrent requests |
| No Windows SCM integration (install/start/stop as service) | Use `pywin32` or `NSSM` wrapper |
| No restart-on-crash policy | Implement in installer (P1-03) |

---

**Last updated:** 2026-04-28

