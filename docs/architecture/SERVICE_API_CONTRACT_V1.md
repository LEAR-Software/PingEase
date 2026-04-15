# Service API Contract v1 (`OptimizationService`)

Defines the payload returned by `OptimizationResult.to_dict()` in `wifi_optimizer/service_api.py`.

## Scope

- Producer: open-core `OptimizationService`
- Consumers: local IPC/API adapters, service host, UI bridge
- Contract version: `v1`

## Response Schema

All responses are JSON-serializable dictionaries with this shape:

```json
{
  "contract_version": "v1",
  "status": "success | no_change | error",
  "changed": true,
  "reason": "human-readable message",
  "details": {}
}
```

### Fields

- `contract_version` (`string`): fixed to `"v1"`.
- `status` (`string`): one of:
  - `success`: cycle completed and channel state changed.
  - `no_change`: cycle completed without channel state change.
  - `error`: cycle failed with normalized error details.
- `changed` (`boolean`): true only when post-cycle channel state differs from pre-cycle state.
- `reason` (`string`): human-readable status description.
- `details` (`object`): status-specific payload.

## `details` by status

### `status = success`

```json
{
  "old_channel_24": 1,
  "new_channel_24": 11,
  "old_channel_5": 36,
  "new_channel_5": 40
}
```

All keys are present in current implementation when a change is detected.
Values can be `null` if a band is not available in state.

### `status = no_change`

```json
{}
```

### `status = error`

```json
{
  "error_code": "SERVICE_CYCLE_FAILURE",
  "error_type": "RuntimeError",
  "error_message": "..."
}
```

## Dry-run semantics in v1

Current v1 behavior:

- `dry_run=True` executes cycle logic without applying router channel changes.
- Result remains compatible with the same status set (`success`, `no_change`, `error`).
- In practical terms, dry-run commonly returns `no_change` unless observable state changes.

Note: a dedicated dry-run status is intentionally deferred to a future contract version to avoid breaking consumers.

## Compatibility notes

- Consumers must branch first on `contract_version`.
- Unknown keys in `details` must be ignored for forward compatibility.
- Consumers must not assume band values are always non-null.

