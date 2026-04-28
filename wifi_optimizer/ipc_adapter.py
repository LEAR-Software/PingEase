"""Local IPC adapter helpers for request/response envelope v1.

This module is transport-agnostic: HTTP, named pipe, or stdio layers can
reuse `handle_request` without changing protocol behavior.
"""

from __future__ import annotations

<<<<<<< HEAD
=======
import hashlib
import hmac
import json
import time
>>>>>>> a48e900 (feat(p0-03): harden IPC adapter with session HMAC auth)
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from wifi_optimizer.service_api import OptimizationService

CONTRACT_VERSION = "v1"
COMMAND_RUN_CYCLE = "run_cycle"

ERROR_INVALID_REQUEST = "INVALID_REQUEST"
ERROR_UNSUPPORTED_CONTRACT_VERSION = "UNSUPPORTED_CONTRACT_VERSION"
ERROR_UNSUPPORTED_COMMAND = "UNSUPPORTED_COMMAND"
ERROR_SERVICE_EXECUTION = "SERVICE_EXECUTION_ERROR"
ERROR_INTERNAL = "INTERNAL_ERROR"
ERROR_AUTH_REQUIRED = "AUTH_REQUIRED"
ERROR_AUTH_INVALID = "AUTH_INVALID"
ERROR_AUTH_REPLAY = "AUTH_REPLAY"

AUTH_SCHEME_HMAC_SHA256_V1 = "hmac-sha256-v1"
DEFAULT_AUTH_WINDOW_MS = 30_000

_NONCE_CACHE: dict[str, dict[str, int]] = {}


def reset_auth_nonce_cache() -> None:
    """Test/helper utility to reset in-memory replay cache."""
    _NONCE_CACHE.clear()


def _signing_payload(request_id: str | None, command: str, params: dict[str, Any]) -> str:
    canonical = {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_id,
        "command": command,
        "params": params,
    }
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"))


def compute_auth_signature(
    *,
    session_secret: str,
    session_id: str,
    nonce: str,
    ts_ms: int,
    request_id: str | None,
    command: str,
    params: dict[str, Any],
) -> str:
    """Compute HMAC signature for one IPC request envelope."""
    payload = _signing_payload(request_id=request_id, command=command, params=params)
    body_sha256 = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    message = f"{session_id}.{nonce}.{ts_ms}.{body_sha256}"
    return hmac.new(
        key=session_secret.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def _consume_nonce(session_id: str, nonce: str, now_ms: int, window_ms: int) -> bool:
    session_nonces = _NONCE_CACHE.setdefault(session_id, {})
    oldest_allowed = now_ms - window_ms
    stale = [n for n, seen_ms in session_nonces.items() if seen_ms < oldest_allowed]
    for key in stale:
        session_nonces.pop(key, None)

    if nonce in session_nonces:
        return False

    session_nonces[nonce] = now_ms
    return True


def _error_response(
    code: str,
    message: str,
    request_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_id,
        "ok": False,
        "result": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
    }


def _ok_response(result: dict[str, Any], request_id: str | None = None) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_id,
        "ok": True,
        "result": result,
        "error": None,
    }


def handle_request(
    request: Any,
    service: OptimizationService,
    *,
    session_secrets: dict[str, str] | None = None,
    require_auth: bool = True,
    auth_window_ms: int = DEFAULT_AUTH_WINDOW_MS,
) -> dict[str, Any]:
    """Validate and dispatch one IPC request envelope."""
    if not isinstance(request, dict):
        return _error_response(ERROR_INVALID_REQUEST, "Request must be a JSON object.")

    request_id = request.get("request_id")

    contract_version = request.get("contract_version")
    if contract_version is None:
        return _error_response(
            ERROR_INVALID_REQUEST,
            "Missing required field 'contract_version'.",
            request_id=request_id,
        )
    if contract_version != CONTRACT_VERSION:
        return _error_response(
            ERROR_UNSUPPORTED_CONTRACT_VERSION,
            f"Unsupported contract_version '{contract_version}'.",
            request_id=request_id,
            details={"expected": CONTRACT_VERSION, "received": contract_version},
        )

    command = request.get("command")
    if not isinstance(command, str) or not command.strip():
        return _error_response(
            ERROR_INVALID_REQUEST,
            "Missing required field 'command'.",
            request_id=request_id,
        )

    params = request.get("params", {})
    if params is None:
        params = {}
    if not isinstance(params, dict):
        return _error_response(
            ERROR_INVALID_REQUEST,
            "Field 'params' must be an object.",
            request_id=request_id,
        )

    auth = request.get("auth")
    if auth is None:
        if require_auth:
            return _error_response(
                ERROR_AUTH_REQUIRED,
                "Missing required field 'auth'.",
                request_id=request_id,
            )
    else:
        if not isinstance(auth, dict):
            return _error_response(
                ERROR_AUTH_INVALID,
                "Field 'auth' must be an object.",
                request_id=request_id,
            )

        scheme = auth.get("scheme")
        session_id = auth.get("session_id")
        nonce = auth.get("nonce")
        ts_ms = auth.get("ts_ms")
        signature = auth.get("signature")

        if scheme != AUTH_SCHEME_HMAC_SHA256_V1:
            return _error_response(
                ERROR_AUTH_INVALID,
                "Unsupported auth scheme.",
                request_id=request_id,
            )

        if not all(isinstance(v, str) and v.strip() for v in [session_id, nonce, signature]):
            return _error_response(
                ERROR_AUTH_INVALID,
                "Auth fields 'session_id', 'nonce' and 'signature' must be non-empty strings.",
                request_id=request_id,
            )

        if not isinstance(ts_ms, int):
            return _error_response(
                ERROR_AUTH_INVALID,
                "Auth field 'ts_ms' must be integer milliseconds.",
                request_id=request_id,
            )

        secrets = session_secrets or {}
        secret = secrets.get(session_id)
        if secret is None:
            return _error_response(
                ERROR_AUTH_INVALID,
                "Unknown auth session_id.",
                request_id=request_id,
            )

        now_ms = int(time.time() * 1000)
        if abs(now_ms - ts_ms) > auth_window_ms:
            return _error_response(
                ERROR_AUTH_INVALID,
                "Auth timestamp is outside allowed window.",
                request_id=request_id,
                details={"window_ms": auth_window_ms},
            )

        if not _consume_nonce(session_id=session_id, nonce=nonce, now_ms=now_ms, window_ms=auth_window_ms):
            return _error_response(
                ERROR_AUTH_REPLAY,
                "Auth nonce already used for this session.",
                request_id=request_id,
            )

        expected_signature = compute_auth_signature(
            session_secret=secret,
            session_id=session_id,
            nonce=nonce,
            ts_ms=ts_ms,
            request_id=request_id,
            command=command,
            params=params,
        )

        if not hmac.compare_digest(expected_signature, signature):
            return _error_response(
                ERROR_AUTH_INVALID,
                "Auth signature mismatch.",
                request_id=request_id,
            )

    if command != COMMAND_RUN_CYCLE:
        return _error_response(
            ERROR_UNSUPPORTED_COMMAND,
            f"Command '{command}' is not supported.",
            request_id=request_id,
        )

    dry_run = params.get("dry_run", False)
    headed = params.get("headed", False)

    if not isinstance(dry_run, bool):
        return _error_response(
            ERROR_INVALID_REQUEST,
            "Field 'params.dry_run' must be boolean.",
            request_id=request_id,
        )
    if not isinstance(headed, bool):
        return _error_response(
            ERROR_INVALID_REQUEST,
            "Field 'params.headed' must be boolean.",
            request_id=request_id,
        )

    try:
        result = service.run_cycle(dry_run=dry_run, headed=headed)
        result_payload = result.to_dict()
    except Exception as exc:
        return _error_response(
            ERROR_SERVICE_EXECUTION,
            f"Service execution failed: {exc}",
            request_id=request_id,
            details={"error_type": exc.__class__.__name__},
        )

    if not isinstance(result_payload, dict):
        return _error_response(
            ERROR_INTERNAL,
            "Service returned a non-object payload.",
            request_id=request_id,
        )

    return _ok_response(result_payload, request_id=request_id)

