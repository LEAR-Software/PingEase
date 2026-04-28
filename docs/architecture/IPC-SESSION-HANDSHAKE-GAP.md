# IPC Session Handshake — Gap Documentation

**Status:** ✅ Resolved in P0-04 (`wifi_optimizer/service_runner.py` — bootstrap file approach)  
**Related issue:** [#5 \[P0-04\] Implement Windows service skeleton](https://github.com/LEAR-Software/PingEase/issues/5)  
**Context:** Identified during P0-03 hardening of `wifi_optimizer/ipc_adapter.py` with HMAC per-session auth.

---

## What is the gap

`handle_request()` in `ipc_adapter.py` requires a `session_secrets` dict injected by the caller:

```python
handle_request(request, service, session_secrets={"sess-01": "<secret>"})
```

The **HMAC auth mechanism is fully implemented** (scheme, nonce, timestamp window, replay cache).  
What is **not yet defined** is how UI and service wrapper **agree on the shared session secret**
before the first request — the "session handshake".

Without this, the transport wrapper in P0-04 must either:
- hardcode the secret (insecure), or
- leave auth disabled (`require_auth=False`) in dev mode.

---

## Why it matters

The session secret is the root of trust for all message authentication.  
If it is leaked, guessed, or never established, the HMAC layer provides no protection.

---

## Options evaluated

| Option | Security | Complexity | Recommended for |
|--------|----------|------------|-----------------|
| **Ephemeral secret in RAM** | High — dies with process | Low | MVP (P0-04) |
| Windows DPAPI | High — tied to user account | Medium | Post-MVP persistence |
| Named pipe + one-time bootstrap token | Very high | Medium | P0-04 if using named pipes |
| Env var from parent process | Medium — visible to child processes | Low | Dev/CI only |

---

## Recommended approach for P0-04 (MVP)

1. **Service wrapper generates a cryptographically random secret at startup:**

```python
import secrets
SESSION_SECRET = secrets.token_hex(32)  # 256-bit ephemeral secret
SESSION_ID = secrets.token_hex(8)
```

2. **Secret delivery to UI** via one of:
   - **Named pipe bootstrap message** (preferred for Windows): service writes `{"session_id": ..., "secret": ...}` as the very first message on the pipe before accepting commands.
   - **Parent process env var** (acceptable for subprocess launch): service launcher injects `PINGEASE_IPC_SESSION_SECRET` and `PINGEASE_IPC_SESSION_ID` into the child UI process env.

3. **Secret never touches disk** — it lives in RAM for the lifetime of the service process.  
   If the service restarts, UI must re-negotiate a new session.

4. **Wire it into `handle_request`** in the transport wrapper:

```python
session_secrets = {SESSION_ID: SESSION_SECRET}

response = handle_request(
    request,
    service,
    session_secrets=session_secrets,
    require_auth=True,
)
```

---

## Acceptance criteria for P0-04

- [ ] Service generates ephemeral `session_id` + `session_secret` at startup.
- [ ] Secret is delivered to UI client via bootstrap channel (pipe or env).
- [ ] `handle_request` called with `session_secrets` and `require_auth=True`.
- [ ] No secret appears in logs, stdout, or persisted state.
- [ ] UI can successfully send a signed `run_cycle` request end-to-end.
- [ ] After service restart, UI re-negotiates session without manual intervention.

---

## What is already done (P0-03)

- `compute_auth_signature(...)` — helper to sign requests client-side.
- `handle_request(..., session_secrets, require_auth, auth_window_ms)` — full server-side validation.
- `reset_auth_nonce_cache()` — test utility to clear replay state.
- Error codes: `AUTH_REQUIRED`, `AUTH_INVALID`, `AUTH_REPLAY`.
- Contract spec: `docs/architecture/service-api-contract.md` (auth section).
- Tests: `tests/test_ipc_adapter.py` — valid signature, invalid signature, replay, stale timestamp.

---

**Last updated:** 2026-04-28  
**Owner:** to be assigned in P0-04  
**Next action:** Implement bootstrap handshake in `wifi_optimizer/service_runner.py` (P0-04 skeleton)

