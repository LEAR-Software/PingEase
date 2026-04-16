# P0-02: Add Service-Ready Execution Mode and Structured Results

**Issue:** [#3](https://github.com/LEAR-Software/PingEase/issues/3)  
**Branch:** `feature/P0-02-service-execution-mode`  
**Prioridad:** P0  
**Esfuerzo:** M  
**Status:** 🚧 In Progress

---

## 🎯 Objetivo

Agregar modo de ejecución service-ready (`--service-once` o contrato interno equivalente) para ejecución segura por servicio Windows, con resultados estructurados consumibles por UI/IPC.

---

## 📋 Definition of Done (DoD)

### 1. Servicio puede disparar ciclo y recibir resultado estructurado

- ✅ (ya implementado en P0-01) `OptimizationService.run_cycle()` retorna `OptimizationResult`
- ⏳ Modo CLI `--service-once` que usa `OptimizationService` en lugar de llamar directamente a `run_optimization_cycle()`
- ⏳ Output JSON estructurado cuando se usa `--service-once` (stdout compatible con parseo)

### 2. Manejo de errores consistente para consumo por UI/servicio

- ✅ (ya implementado en P0-01) Errores normalizados en `OptimizationResult` con `error_code`
- ⏳ Output JSON incluye stack trace opcional en modo `--debug`
- ⏳ Exit codes apropiados para diferentes tipos de errores

---

## 🏗️ Arquitectura

### Componentes Involucrados

```
┌─────────────────────────────────────────┐
│          CLI Entry (main.py)            │
│  ┌──────────────┬───────────────────┐   │
│  │ Daemon Mode  │ Service-Once Mode │   │
│  │ (existing)   │ (NEW)             │   │
│  └──────┬───────┴───────┬───────────┘   │
│         │               │               │
│         ▼               ▼               │
│  run_optimization  OptimizationService  │
│       _cycle()          .run_cycle()    │
│                                         │
└─────────────────────────────────────────┘
                 │
                 ▼
        OptimizationResult
         (structured JSON)
```

### Flujo de `--service-once`

1. **Parse arguments:** Detectar flag `--service-once`
2. **Build config:** Crear `OptimizerConfig` desde env vars
3. **Instantiate service:** `service = OptimizationService(config)`
4. **Run cycle:** `result = service.run_cycle(dry_run=dry_run, headed=headed)`
5. **Output JSON:** `print(json.dumps(result.to_dict()))` a stdout
6. **Exit with code:** `sys.exit(0)` si success/no_change, `sys.exit(1)` si error

---

## 🔨 Implementación

### Fase 1: CLI Flag `--service-once`

**Archivo:** `main.py`

**Cambios:**

1. Agregar detección de flag `--service-once`:
   ```python
   service_once = "--service-once" in args
   ```

2. Nueva rama condicional para service mode:
   ```python
   if service_once:
       # Build OptimizerConfig from env vars
       config = OptimizerConfig(
           router_url=ROUTER_URL,
           router_user=ROUTER_USER,
           router_pass=ROUTER_PASS,
           router_driver=os.getenv("ROUTER_DRIVER", "huawei_hg8145x6"),
           # ... rest of config from env
       )
       
       # Instantiate service
       service = OptimizationService(config)
       
       # Run cycle
       result = service.run_cycle(dry_run=dry_run, headed=headed)
       
       # Output JSON to stdout
       import json
       print(json.dumps(result.to_dict(), indent=2))
       
       # Exit with appropriate code
       sys.exit(0 if result.status in ("success", "no_change") else 1)
   ```

### Fase 2: Helper para construir `OptimizerConfig` desde ENV

**Archivo:** `wifi_optimizer/config.py`

**Agregar método estático:**

```python
@staticmethod
def from_env() -> OptimizerConfig:
    """
    Build OptimizerConfig from environment variables.
    
    Useful for CLI and service modes.
    """
    import os
    
    # Mini profile resolver (copy from main.py)
    _PROFILE_DEFAULTS = {
        "balanced": {
            "ping_ms": 40,
            "jitter_ms": 20,
            "hysteresis": 0.50,
            "cooldown_s": 3600,
        },
        "aggressive": {
            "ping_ms": 30,
            "jitter_ms": 12,
            "hysteresis": 0.35,
            "cooldown_s": 1800,
        },
    }
    
    profile = os.getenv("GAMING_PROFILE", "balanced").strip().lower()
    if profile not in _PROFILE_DEFAULTS:
        profile = "balanced"
    
    p = _PROFILE_DEFAULTS[profile]
    
    return OptimizerConfig(
        router_url=os.getenv("ROUTER_URL", "http://192.168.100.1"),
        router_user=os.getenv("ROUTER_USER", "admin"),
        router_pass=os.getenv("ROUTER_PASS", "admin"),
        router_driver=os.getenv("ROUTER_DRIVER", "huawei_hg8145x6"),
        scan_interval_seconds=int(os.getenv("SCAN_INTERVAL_SECONDS", "300")),
        change_cooldown_seconds=int(os.getenv("CHANGE_COOLDOWN_SECONDS", "3600")),
        hysteresis_threshold=float(os.getenv("HYSTERESIS_THRESHOLD", "0.40")),
        trial_period_seconds=int(os.getenv("TRIAL_PERIOD_SECONDS", "300")),
        ping_threshold_ms=int(os.getenv("PING_DEGRADATION_MS", "20")),
        jitter_threshold_ms=int(os.getenv("JITTER_DEGRADATION_MS", "15")),
        speed_drop_pct=float(os.getenv("SPEED_DEGRADATION_PCT", "0.40")),
        baseline_good_ping_ms=int(os.getenv("BASELINE_GOOD_PING_MS", "15")),
        baseline_good_jitter_ms=int(os.getenv("BASELINE_GOOD_JITTER_MS", "5")),
        emergency_ping_ms=int(os.getenv("EMERGENCY_PING_MS", str(p["ping_ms"]))),
        emergency_jitter_ms=int(os.getenv("EMERGENCY_JITTER_MS", str(p["jitter_ms"]))),
        emergency_hysteresis=float(os.getenv("EMERGENCY_HYSTERESIS", str(p["hysteresis"]))),
        emergency_cooldown_seconds=int(os.getenv("EMERGENCY_COOLDOWN_SECONDS", str(p["cooldown_s"]))),
    )
```

### Fase 3: Tests para `--service-once`

**Archivo:** `tests/test_service_once_mode.py` (nuevo)

**Tests a implementar:**

1. `test_service_once_outputs_json_on_success`
2. `test_service_once_exits_with_0_on_success`
3. `test_service_once_exits_with_1_on_error`
4. `test_service_once_json_contains_contract_version`
5. `test_service_once_dry_run_compatible`

### Fase 4: Documentación

**Actualizar archivos:**

1. `README.md`: Agregar sección de `--service-once` mode
2. `SERVICE_API_OVERVIEW.md`: Documentar flujo de service-once CLI
3. `SERVICE_API_CONTRACT_V1.md`: Confirmar compatibilidad con service-once output

---

## 🧪 Testing Strategy

### Unit Tests

- ✅ `OptimizationService.run_cycle()` (ya cubierto en P0-01)
- ⏳ `OptimizerConfig.from_env()` (validar construcción desde env vars)
- ⏳ Service-once mode (mock subprocess, validar JSON output)

### Integration Tests

- ⏳ Ejecutar `main.py --service-once` y validar JSON output parseado
- ⏳ Validar exit codes (0 para success/no_change, 1 para error)
- ⏳ Validar compatibilidad con `--dry-run --service-once`

### Manual Tests

- ⏳ Ejecutar desde CLI: `python main.py --service-once`
- ⏳ Ejecutar desde CLI con dry-run: `python main.py --service-once --dry-run`
- ⏳ Validar que JSON output es parseado correctamente por `jq`

---

## 📦 Deliverables

### Código

- [ ] `main.py`: Agregar branch para `--service-once` mode
- [ ] `wifi_optimizer/config.py`: Agregar método `OptimizerConfig.from_env()`
- [ ] `tests/test_service_once_mode.py`: Tests para service-once mode

### Documentación

- [ ] `README.md`: Documentar `--service-once` flag
- [ ] `SERVICE_API_OVERVIEW.md`: Actualizar con flujo de service-once
- [ ] `P0-02-DOD-STATUS.md`: Reporte de evaluación del DoD

---

## 🔗 Dependencias

### Bloqueada por
- ✅ **P0-01:** Stabilize core API (merged)

### Bloquea a
- ⏳ **P0-04:** Implement Windows service skeleton
- ⏳ **P1-01:** UI MVP (necesita parsear JSON de service-once)

---

## 🚀 Plan de Ejecución

### Sprint 1: Implementación Core (1-2 días)

1. ✅ Crear branch `feature/P0-02-service-execution-mode`
2. ✅ Crear `P0-02-PLAN.md` (este documento)
3. ⏳ Implementar `OptimizerConfig.from_env()` en `config.py`
4. ⏳ Implementar branch `--service-once` en `main.py`
5. ⏳ Tests unitarios para `from_env()`

### Sprint 2: Testing y Validación (1 día)

1. ⏳ Tests de integración para service-once mode
2. ⏳ Manual testing con diferentes configuraciones
3. ⏳ Validación de exit codes

### Sprint 3: Documentación y DoD (0.5 días)

1. ⏳ Actualizar README.md con ejemplos de uso
2. ⏳ Actualizar SERVICE_API_OVERVIEW.md
3. ⏳ Crear P0-02-DOD-STATUS.md
4. ⏳ Abrir PR y solicitar review

---

## 📝 Notas de Diseño

### Exit Codes

```python
EXIT_SUCCESS = 0        # status in ("success", "no_change")
EXIT_ERROR = 1          # status == "error"
```

### JSON Output Format (ejemplo)

```json
{
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
}
```

### Compatibilidad con Flags Existentes

- `--service-once` es compatible con:
  - `--dry-run`: Ejecuta sin aplicar cambios
  - `--inspect`: Abre browser en modo headed (debug)
  - `--debug`: Agrega stack trace a JSON output (futuro)

- `--service-once` NO es compatible con:
  - Daemon mode (implica `--once`)
  - `--monitor`: Modo independiente
  - `--analyze`: Modo independiente

---

## ✅ Criterios de Aceptación

| # | Criterio | Verificación |
|---|----------|--------------|
| 1 | CLI acepta flag `--service-once` | `python main.py --service-once` ejecuta sin error |
| 2 | Output es JSON válido en stdout | `python main.py --service-once \| jq .` parsea correctamente |
| 3 | JSON contiene `contract_version` | `jq .contract_version` retorna `"v1"` |
| 4 | Exit code 0 en success/no_change | `echo $?` retorna `0` tras ejecución exitosa |
| 5 | Exit code 1 en error | `echo $?` retorna `1` tras error |
| 6 | Compatible con `--dry-run` | `--service-once --dry-run` ejecuta sin aplicar cambios |
| 7 | Tests unitarios pasan | `python -m unittest tests.test_service_once_mode -v` → OK |
| 8 | Documentación actualizada | README.md contiene sección de `--service-once` |

---

**Próxima sesión:** Implementar `OptimizerConfig.from_env()` y branch `--service-once` en `main.py`

