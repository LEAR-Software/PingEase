"""Local IPC adapter helpers for request/response envelope v1.

This module is transport-agnostic: HTTP, named pipe, or stdio layers can
reuse `handle_request` without changing protocol behavior.
"""

from __future__ import annotations

from typing import Any

from wifi_optimizer.service_api import OptimizationService

CONTRACT_VERSION = "v1"
COMMAND_RUN_CYCLE = "run_cycle"

ERROR_INVALID_REQUEST = "INVALID_REQUEST"
ERROR_UNSUPPORTED_CONTRACT_VERSION = "UNSUPPORTED_CONTRACT_VERSION"
ERROR_UNSUPPORTED_COMMAND = "UNSUPPORTED_COMMAND"
ERROR_SERVICE_EXECUTION = "SERVICE_EXECUTION_ERROR"
ERROR_INTERNAL = "INTERNAL_ERROR"


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


def handle_request(request: Any, service: OptimizationService) -> dict[str, Any]:
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

