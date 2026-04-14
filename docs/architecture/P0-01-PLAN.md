# P0-01 Implementation Plan: Stabilize Core API Surface

## 📋 Overview
**Issue:** #2 (P0-01)  
**Goal:** Extract service-safe core API from CLI entry point so Windows service can invoke without CLI overhead.

## Current State Analysis

### Entry Point (main.py)
- All logic mixed in `main()` function
- Configuration loaded from `.env` via CLI flags
- Router instantiation happens inside `main()`
- Cycle execution tightly coupled to CLI args parsing

### Problems
1. Service wrapper needs to call core without parsing CLI args
2. Configuration schema not standardized
3. Error handling returns `sys.exit(1)` (not suitable for service)
4. State management embedded in main loop

## Refactoring Strategy

### Phase 1: Extract Config Schema
Create `wifi_optimizer/config.py`:
```python
from dataclasses import dataclass

@dataclass
class OptimizerConfig:
    """Core configuration for optimization cycle."""
    router_url: str
    router_user: str
    router_pass: str
    router_driver: str = "huawei_hg8145x6"
    scan_interval_s: int = 300
    change_cooldown_s: int = 3600
    hysteresis_threshold: float = 0.40
    # ... (all other params)
    
    @classmethod
    def from_env(cls) -> "OptimizerConfig":
        """Load from environment variables."""
        # Move all env parsing logic here
```

### Phase 2: Extract Service API
Create `wifi_optimizer/service_api.py`:
```python
from dataclasses import dataclass
from wifi_optimizer.config import OptimizerConfig

@dataclass
class OptimizationResult:
    """Service-safe result from a cycle."""
    status: str  # "success", "no_change", "error"
    changed: bool
    reason: str
    details: dict

class OptimizationService:
    """Service-safe API for Windows service to call."""
    
    def __init__(self, config: OptimizerConfig):
        self.config = config
        self.state = {"current_24": None, "current_5": None, ...}
    
    def run_cycle(self, dry_run: bool = False) -> OptimizationResult:
        """Execute one optimization cycle; return structured result."""
        try:
            # Call run_optimization_cycle with structured params
            # Return result object instead of sys.exit
        except Exception as e:
            return OptimizationResult(
                status="error",
                changed=False,
                reason=str(e),
                details={}
            )
```

### Phase 3: Refactor main.py
- Keep CLI entry point
- Delegate to `OptimizationService`
- Remove config logic (move to `OptimizerConfig.from_env()`)
- Keep monitor/analyze modes

## Minimum DoD
- [ ] `wifi_optimizer/config.py` created with `OptimizerConfig` dataclass
- [ ] `wifi_optimizer/service_api.py` created with `OptimizationService` class
- [ ] `OptimizationResult` dataclass for structured responses
- [ ] `run_optimization_cycle()` accepts structured config instead of kwargs
- [ ] CLI `main()` still works: `python main.py --dry-run` unchanged
- [ ] Dry-run mode works identically (regression test)
- [ ] Service wrapper can import and use `OptimizationService` without CLI
- [ ] No secrets hardcoded; config from env or function params

## Testing
```python
# Example: service can import and use core
from wifi_optimizer.service_api import OptimizationService
from wifi_optimizer.config import OptimizerConfig

config = OptimizerConfig(
    router_url="...",
    router_user="...",
    router_pass="...",
)
service = OptimizationService(config)
result = service.run_cycle(dry_run=True)
assert result.status in ["success", "no_change", "error"]
```

## Files to Create/Modify
- **NEW:** `wifi_optimizer/config.py`
- **NEW:** `wifi_optimizer/service_api.py`
- **MODIFY:** `main.py` (use new service)
- **MODIFY:** `wifi_optimizer/optimizer.py` (accept `OptimizerConfig` instead of kwargs)
- **UPDATE:** `docs/architecture/core-contract.md` (document service API)

## PR Checklist
- [ ] Backward compatible: `--dry-run` still works
- [ ] No CLI-only assumptions in core logic
- [ ] Service import works: `from wifi_optimizer.service_api import OptimizationService`
- [ ] Config from env or programmatic setup both work
- [ ] Exceptions don't call `sys.exit()` in service layer
- [ ] Tests pass: `python -m compileall . && python -c "import wifi_optimizer"`
- [ ] Compliance gate checklist in `.github/pull_request_template.md` passes

---

**Start:** Create `wifi_optimizer/config.py`  
**Depends on:** None (foundation work)  
**Blocks:** P0-02, P0-03

