# 🔐 Windows Secrets Baseline — PingEase P0-05

**Version:** 1.0  
**Status:** MVP baseline (May 2026)  
**Threat Model Scope:** Local machine only (localhost IPC, no network secrets)

---

## 📋 Overview

This document defines how PingEase manages secrets during Windows service runtime without storing credentials in the repository or leaking them into logs.

**Secrets Managed:**
- `session_id`: Ephemeral session identifier (8 bytes hex)
- `session_secret`: HMAC key for IPC authentication (32 bytes hex)
- `router_password`: Router admin password (from `OptimizerConfig`)
- Log files containing debug traces

**Critical Constraint:** Secrets are **never persisted to disk** after the service stops; bootstrap file and logs are cleaned up.

---

## 1. Storage Strategy

### 1.1 Session Credentials (Ephemeral)

**Generated at service startup:**
```python
session_id = secrets.token_hex(8)           # 16 chars: e.g. "a1b2c3d4e5f6g7h8"
session_secret = secrets.token_hex(32)      # 64 chars: cryptographically secure
```

**Stored in:**
- RAM: `ServiceRunner._session_id`, `ServiceRunner._session_secret`
- Bootstrap file: `%TEMP%/pingease-service.json` (JSON, readable by local user only)
- HTTP handler: injected into `_IPCHandler` via class attribute binding

**Lifecycle:**
- Generated on `ServiceRunner.start()`
- Written to bootstrap file immediately after
- Cleared from bootstrap file on `ServiceRunner.stop()` via `remove_bootstrap()`
- Discarded when process exits

### 1.2 Bootstrap File Format

**Path:** `%TEMP%/pingease-service.json`  
**Permissions:** Inherited from `%TEMP%` (readable by local user by default)  
**Content:**
```json
{
  "pid": 1234,
  "host": "127.0.0.1",
  "port": 56789,
  "session_id": "a1b2c3d4e5f6g7h8",
  "session_secret": "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p",
  "started_at_ms": 1777300000123
}
```

**Security Notes:**
- Created with `Path.write_text(..., encoding="utf-8")` (uses system default permissions)
- Windows `%TEMP%` folder typically has restrictive ACLs (user-only readable)
- File removed immediately on clean shutdown
- If process crashes, file may remain; should be manually deleted or ignored

### 1.3 Router Password Storage

**Source:** `OptimizerConfig.router_pass` (user-provided via config)  
**Storage:** In-memory only, in `OptimizationService.config`  
**Never Persisted:** No .env files, no config files with passwords  
**Passed to Router:** Only when instantiating `HuaweiHG8145X6` driver

---

## 2. Access Control

### 2.1 Session Authentication (IPC)

Each request to `/ipc` endpoint must include HMAC signature:

```json
{
  "contract_version": "v1",
  "request_id": "ui-001",
  "command": "run_cycle",
  "params": { "dry_run": false },
  "auth": {
    "scheme": "hmac-sha256-v1",
    "session_id": "a1b2c3d4e5f6g7h8",
    "nonce": "<uuid>",
    "ts_ms": 1777300000123,
    "signature": "<hex-hmac-sha256>"
  }
}
```

**Validation Steps:**
1. Check `auth.session_id` exists in `session_secrets` dict
2. Verify `auth.ts_ms` is within 30-second window (default `DEFAULT_AUTH_WINDOW_MS`)
3. Validate `auth.nonce` has not been seen before (replay protection)
4. Compute expected signature using `session_secret` and request body
5. Compare with provided `auth.signature` (constant-time)

**Error Codes:**
- `AUTH_REQUIRED`: Session credentials not provided
- `AUTH_INVALID`: Signature does not match or session not found
- `AUTH_REPLAY`: Nonce was already used within the auth window

### 2.2 Bootstrap File Access

**Who can read bootstrap file:**
- UI process running as same user
- Administrator (if elevated)

**Who cannot read:**
- Other local users (if folder permissions are restrictive)
- Network processes
- Processes running as SYSTEM (unless running the service)

**Recommendation:** Validate that `%TEMP%` on target Windows systems has user-only readable permissions.

---

## 3. Rotation Strategy

### 3.1 Session Credential Rotation

**Current (MVP):**
- New session credentials generated on every service **start**
- UI must re-read bootstrap file after service restart
- No in-band rotation (requires service restart)

**Future (Post-MVP):**
- Implement HTTP endpoint `/rotate-credentials` (auth-gated)
- Return new `session_secret` in response
- Cache old secret for grace period to avoid request loss during rotation

### 3.2 Bootstrap File Refresh

**Trigger:** Service startup only  
**Action:** Write new bootstrap file with new `session_id` + `session_secret`  
**Old File:** Overwritten (contents discarded)

---

## 4. Rollback & Disaster Recovery

### 4.1 Ungraceful Shutdown

**If service crashes:**
- Bootstrap file remains in `%TEMP%/pingease-service.json`
- Stale `session_id` + `session_secret` persist on disk
- UI will attempt to connect using stale credentials
- Service will not recognize requests (new session not started yet)

**Manual Recovery:**
```bash
# Windows PowerShell (admin)
Remove-Item "$env:TEMP\pingease-service.json" -Force
# Then restart service
```

**Alternative (Automatic Cleanup):**
- Future: Add startup logic to check PID in stale bootstrap file
- If PID no longer exists, auto-delete and regenerate

### 4.2 Session Key Compromise

**Scenario:** Session secret leaked or observed in logs

**Immediate Action:**
1. Restart service (generates new session secret)
2. Delete old bootstrap file manually if persisting
3. Review logs to identify exposure window
4. Rotate router password if believed compromised

**Prevention (see Logging Hardening below):**
- Secrets are never logged
- Only `session_id` may appear in logs (identifier only, not secret)

---

## 5. Logging Hardening & No-Leak Guarantees

### 5.1 Session Secret Handling

**RULE: `session_secret` never appears in logs**

Current implementation:
- `ServiceRunner._session_secret` stored in instance variable
- Only passed to `BoundHandler.session_secrets` dict (not logged)
- Used in `compute_auth_signature()` internally (no log output)
- Never stringified or included in exception messages

**Audit Points:**
- `service_runner.py`: Line 226 — secret generation
- `service_runner.py`: Line 274 — secret injected into handler
- `ipc_adapter.py`: Line 66 — secret used in HMAC (no logging)

### 5.2 Session ID Logging (Permitted)

**RULE: `session_id` MAY appear in logs for debugging, but never the secret**

Current implementation:
- Line 287: `"Service listening on %s:%d"` — port logged, no credentials
- Line 305: `"PingEase service runner started (pid=%d, port=%d)"` — no credentials
- Future debug logs may include `session_id` for request tracing

### 5.3 Router Password Handling

**RULE: Router password never appears in logs**

Current implementation:
- `OptimizerConfig.router_pass` stored in instance
- Passed only to router driver instantiation
- Drivers handle auth internally (Playwright, etc.)
- No logging of password in `service_api.py` or `ipc_adapter.py`

**Audit Points:**
- `service_api.py`: Line 137 — password passed to driver
- `service_runner.py`: Bootstrap file excludes router password

### 5.4 Exception Message Sanitization

**Current Behavior:**
- Exceptions from `run_optimization_cycle()` are caught
- `str(exc)` is included in response `details.error_message`
- If exception contains sensitive info, it leaks to UI via HTTP response

**MVP Acceptable:** Local IPC only (no network exposure)  
**Future Hardening:** Before adding network transport, sanitize exception messages or filter sensitive fields

---

## 6. Minimal Threat Model

### 6.1 Trust Assumptions

✅ **In Scope (Trusted):**
- Same-user UI process and service process
- Localhost-only HTTP (no routing outside machine)
- `%TEMP%` folder has restrictive permissions (Windows default)

❌ **Out of Scope (Untrusted):**
- Other local user accounts
- Network-accessible endpoints (future post-MVP)
- Malware with admin privileges
- Unencrypted disk access

### 6.2 Attack Vectors & Mitigations

| Attack | Vector | Mitigation | Status |
|--------|--------|-----------|--------|
| **Eavesdropping (localhost)** | Packet capture on 127.0.0.1 | HTTP only on localhost; future: consider HTTPS for defense-in-depth | ⚠️ MVP |
| **Replay** | Reuse old request + signature | Nonce + timestamp window (30s default) | ✅ Implemented |
| **Session hijacking** | Steal `session_id` + `session_secret` | Only in bootstrap file; removed on shutdown | ✅ Implemented |
| **Bootstrap file theft** | Read from `%TEMP%` as other user | Windows ACLs; assume user-only readable | ⚠️ System-dependent |
| **Log exposure** | Grep logs for secrets | Secrets never logged; `session_id` only | ✅ Implemented |
| **Crash dump** | Read memory from crash dump | Secrets in RAM; no persistent backup | ⚠️ User must secure crash dump |
| **Process detach** | Attach debugger to running service | No mitigation (Windows limitation) | ⚠️ System-dependent |

---

## 7. DoD Checklist for P0-05

- [x] `docs/architecture/secrets.md` defines storage, access, rotation, rollback (this file)
- [x] No secrets persisted to repo (no `.env`, no hardcoded passwords)
- [x] No secrets in `main.py` or CLI arguments
- [x] `session_secret` never logged (code audit above)
- [x] Bootstrap file removed on clean shutdown
- [x] HMAC replay protection implemented (nonce + timestamp)
- [x] Rollback procedure documented (Section 4)
- [ ] Tests added for secret handling edge cases (future)
- [ ] Windows ACL verification script (future, not MVP)

---

## 8. Future Enhancements (Post-MVP)

1. **HTTPS for /ipc endpoint:**
   - Self-signed cert on localhost
   - Prevents eavesdropping on HTTP

2. **In-band credential rotation:**
   - `/rotate-credentials` endpoint
   - Grace period for old secret during transition

3. **Automatic cleanup of stale bootstrap:**
   - On startup, check PID in old bootstrap file
   - If PID dead, auto-delete

4. **Secrets in OS credential store:**
   - Windows Credential Manager for router password (instead of config)
   - Requires elevation but more secure

5. **Request signing with ED25519:**
   - Move from HMAC to asymmetric key (more robust)
   - Requires key rotation strategy

6. **Audit logging to secure location:**
   - All auth failures, secret access, rotations
   - Separate from regular logs

---

## 9. References

- **Service Implementation:** `wifi_optimizer/service_runner.py`
- **IPC Contract:** `docs/architecture/service-api-contract.md`
- **HMAC Signing:** `wifi_optimizer/ipc_adapter.py` (functions `compute_auth_signature`, `_consume_nonce`)
- **Bootstrap Schema:** `wifi_optimizer/service_runner.py` (function `write_bootstrap`)
- **Windows Security:** [Microsoft: Protecting user secrets](https://docs.microsoft.com/en-us/windows/win32/secbp/best-practices-for-the-security-apis)

---

**Document Owner:** PingEase Core Team  
**Last Updated:** 2026-04-29  
**Classification:** Internal (MVP public repository, no sensitive data exposed)

