# Local IPC/API Contract v1 (UI <-> Service)

Defines the request/response envelope used between a local UI client and the PingEase service wrapper.

## Scope

- Producer: local service wrapper that invokes `OptimizationService`
- Consumer: local UI/desktop app
- Canonical service payload: `OptimizationResult.to_dict()` from `wifi_optimizer/service_api.py`
- Contract version: `v1`

## Goals

- Keep `OptimizationService` as CLI-agnostic core entrypoint.
- Preserve `--dry-run` semantics already validated in P0-01/P0-02.
- Add a stable local message contract for future transport adapters.

## Transport (MVP)

This contract is transport-agnostic. It can be carried over:

- `stdio` (quickest for local wrapper prototypes)
- localhost HTTP
- named pipes (Windows-native)

MVP recommendation: start with localhost HTTP or named pipes once P0-04 service skeleton is active.

## Request Envelope

All requests are JSON objects with this shape:

```json
{
  "contract_version": "v1",
  "request_id": "optional-string-id",
  "command": "run_cycle",
  "params": {
    "dry_run": false,
    "headed": false
  }
}
```

### Request Fields

- `contract_version` (`string`, required): must be `"v1"`.
- `request_id` (`string`, optional): caller correlation id for logs/UI tracing.
- `command` (`string`, required): currently only `"run_cycle"`.
- `params` (`object`, optional): command parameters.
  - `dry_run` (`boolean`, optional, default `false`)
  - `headed` (`boolean`, optional, default `false`)

## Response Envelope

All responses are JSON objects with this shape:

```json
{
  "contract_version": "v1",
  "request_id": "optional-string-id",
  "ok": true,
  "result": {
    "contract_version": "v1",
    "status": "success",
    "changed": true,
    "reason": "Channel change applied.",
    "details": {
      "old_channel_24": 1,
      "new_channel_24": 11,
      "old_channel_5": 36,
      "new_channel_5": 40
    }
  },
  "error": null
}
```

### Response Fields

- `contract_version` (`string`): envelope version (`"v1"`).
- `request_id` (`string|null`): echoed from request when present.
- `ok` (`boolean`): `true` when command was accepted and executed.
- `result` (`object|null`): service payload (same schema as `OptimizationResult.to_dict()`).
- `error` (`object|null`): normalized protocol-level error (when `ok=false`).

## Protocol-level Error Model

When the request cannot be processed at the envelope/command level:

```json
{
  "contract_version": "v1",
  "request_id": "abc-123",
  "ok": false,
  "result": null,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Missing required field 'command'.",
    "details": {}
  }
}
```

### Error Codes

- `INVALID_REQUEST`: malformed JSON or missing/invalid fields.
- `UNSUPPORTED_CONTRACT_VERSION`: unknown envelope version.
- `UNSUPPORTED_COMMAND`: command not implemented.
- `SERVICE_EXECUTION_ERROR`: command reached service core but failed before result mapping.
- `INTERNAL_ERROR`: unexpected wrapper failure.

## Command Semantics (`run_cycle`)

- Executes one call to `OptimizationService.run_cycle(dry_run, headed)`.
- If accepted, wrapper returns `ok=true` and places core payload in `result`.
- Core payload status remains the canonical domain outcome:
  - `success`
  - `no_change`
  - `error`

This separates protocol failure (`ok=false`) from domain execution outcome (`result.status="error"`).

## Compatibility Rules

- Consumers must validate envelope `contract_version` first.
- Consumers must branch on `ok` before reading `result`.
- Unknown keys must be ignored for forward compatibility.
- Core payload is backward-compatible with `docs/architecture/SERVICE_API_CONTRACT_V1.md`.

## Minimal Examples

### Example A: `dry_run=true`

```json
{
  "contract_version": "v1",
  "request_id": "ui-001",
  "command": "run_cycle",
  "params": {
    "dry_run": true
  }
}
```

### Example B: Unsupported command

```json
{
  "contract_version": "v1",
  "request_id": "ui-002",
  "ok": false,
  "result": null,
  "error": {
    "code": "UNSUPPORTED_COMMAND",
    "message": "Command 'reboot_router' is not supported.",
    "details": {}
  }
}
```

