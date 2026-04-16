# P0-02: Add Service-Ready Execution Mode - Definition of Done Status

**Fecha de evaluación:** 2026-04-15  
**Branch:** `feature/P0-02-service-execution-mode`  
**Issue:** [#3](https://github.com/LEAR-Software/PingEase/issues/3)

---

## 📋 Definition of Done (DoD)

### ✅ 1. Servicio puede disparar ciclo y recibir resultado estructurado

**Estado:** ✅ **COMPLETADO**

**Evidencia:**

- **Modo CLI `--service-once`** implementado en `main.py` (líneas 169-197)
- **Usa `OptimizationService.run_cycle()`** internamente (ya implementado en P0-01)
- **Output JSON estructurado** a stdout con `contract_version: "v1"`
- **Exit codes apropiados:**
  - `0` para `status="success"` o `status="no_change"`
  - `1` para `status="error"`

**Características implementadas:**

```python
# main.py (líneas 169-197)
if service_once:
    import json
    from wifi_optimizer.config import OptimizerConfig
    from wifi_optimizer.service_api import OptimizationService
    
    # Load config from environment
    config = OptimizerConfig.from_env()
    
    # Instantiate service
    service = OptimizationService(config)
    
    # Run single cycle
    result = service.run_cycle(dry_run=dry_run, headed=headed)
    
    # Output structured JSON to stdout
    print(json.dumps(result.to_dict(), indent=2))
    
    # Shutdown service
    service.shutdown()
    
    # Exit with appropriate code
    sys.exit(0 if result.status in ("success", "no_change") else 1)
```

**Validación:**

- ✅ JSON output contiene campos requeridos: `contract_version`, `status`, `changed`, `reason`, `details`
- ✅ Exit code 0 para success/no_change
- ✅ Exit code 1 para error
- ✅ Compatible con `--dry-run` flag

---

### ✅ 2. Manejo de errores consistente para consumo por UI/servicio

**Estado:** ✅ **COMPLETADO**

**Evidencia:**

- **Errores normalizados** en `OptimizationResult` (ya implementado en P0-01)
- **Error payload estructurado:**
  ```json
  {
    "contract_version": "v1",
    "status": "error",
    "changed": false,
    "reason": "Router connection failed",
    "details": {
      "error_code": "SERVICE_CYCLE_FAILURE",
      "error_type": "RuntimeError",
      "error_message": "..."
    }
  }
  ```

**Comportamiento validado:**

1. **Errores de conexión al router:**
   - Status: `"error"`
   - Error code: `"SERVICE_CYCLE_FAILURE"`
   - Error type: Nombre de la excepción (`RuntimeError`, etc.)
   - Exit code: `1`

2. **Driver inválido:**
   - Status: `"error"`
   - Reason: `"Unknown ROUTER_DRIVER 'xxx'"`
   - Exit code: `1`

3. **Sin cambio necesario:**
   - Status: `"no_change"`
   - Changed: `false`
   - Exit code: `0`

4. **Cambio aplicado exitosamente:**
   - Status: `"success"`
   - Changed: `true`
   - Details contiene `old_channel_24/5` y `new_channel_24/5`
   - Exit code: `0`

---

## 📊 Resumen de Completitud

| Criterio DoD | Estado | Evidencia |
|-------------|--------|-----------|
| Servicio puede disparar ciclo y recibir resultado estructurado | ✅ Completado | `main.py` + tests + JSON output con contract v1 |
| Manejo de errores consistente para UI/servicio | ✅ Completado | Error payload normalizado + exit codes |

**DoD alcanzado:** ✅ **100%**

---

## 🧪 Tests Implementados

### Unit Tests (`tests/test_service_once_mode.py`)

**Total:** 9 tests, todos pasando ✅

1. `test_optimization_result_to_dict_includes_contract_version` ✅
   - Verifica que `to_dict()` incluye `contract_version: "v1"`

2. `test_optimization_result_to_dict_has_all_fields` ✅
   - Verifica todos los campos requeridos: `contract_version`, `status`, `changed`, `reason`, `details`

3. `test_optimization_result_success_status` ✅
   - Valida status `"success"` con `changed=true` y details poblados

4. `test_optimization_result_no_change_status` ✅
   - Valida status `"no_change"` con `changed=false` y details vacíos

5. `test_optimization_result_error_status` ✅
   - Valida status `"error"` con `error_code` y `error_type` en details

6. `test_optimization_result_json_serializable` ✅
   - Verifica que `to_dict()` es JSON-serializable

7. `test_service_once_exit_code_logic_success` ✅
   - Valida lógica de exit code 0 para status `"success"`

8. `test_service_once_exit_code_logic_no_change` ✅
   - Valida lógica de exit code 0 para status `"no_change"`

9. `test_service_once_exit_code_logic_error` ✅
   - Valida lógica de exit code 1 para status `"error"`

### Test Execution

```bash
$ python -m unittest tests.test_service_once_mode.ServiceOnceModeUnitTests -v

test_optimization_result_error_status ... ok
test_optimization_result_json_serializable ... ok
test_optimization_result_no_change_status ... ok
test_optimization_result_success_status ... ok
test_optimization_result_to_dict_has_all_fields ... ok
test_optimization_result_to_dict_includes_contract_version ... ok
test_service_once_exit_code_logic_error ... ok
test_service_once_exit_code_logic_no_change ... ok
test_service_once_exit_code_logic_success ... ok

Ran 9 tests in 0.001s
OK ✅
```

### Coverage Total del Proyecto

```bash
$ python -m unittest discover -s tests -v

Ran 14 tests in 0.008s
OK ✅
```

**Breakdown:**
- P0-01 (service_api): 5 tests
- P0-02 (service_once): 9 tests

---

## 📝 Documentación Actualizada

### Archivos Modificados

1. **`README.md`** ✅
   - Tabla de flags: agregado `--service-once` con descripción
   - Sección de uso: agregado ejemplo de `--service-once` con output JSON esperado
   - Exit codes documentados

2. **`docs/architecture/P0-02-PLAN.md`** ✅
   - Plan completo de implementación (350+ líneas)
   - Arquitectura, fases, deliverables, criterios de aceptación

3. **`docs/architecture/P0-02-DOD-STATUS.md`** ✅ (este archivo)
   - Evaluación completa del DoD
   - Evidencia de tests y funcionalidad

4. **`docs/architecture/SERVICE_API_CONTRACT_V1.md`** (sin cambios)
   - Contrato ya cubre el formato de salida de `--service-once`

---

## 🚀 Uso del Modo `--service-once`

### Sintaxis

```bash
python main.py --service-once [--dry-run] [--inspect]
```

### Ejemplo: Modo Producción

```bash
$ python main.py --service-once
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
$ echo $?
0
```

### Ejemplo: Modo Dry-Run

```bash
$ python main.py --service-once --dry-run
{
  "contract_version": "v1",
  "status": "no_change",
  "changed": false,
  "reason": "No channel change applied.",
  "details": {}
}
$ echo $?
0
```

### Ejemplo: Error

```bash
$ python main.py --service-once
{
  "contract_version": "v1",
  "status": "error",
  "changed": false,
  "reason": "Router connection failed",
  "details": {
    "error_code": "SERVICE_CYCLE_FAILURE",
    "error_type": "RuntimeError",
    "error_message": "Login appeared to succeed but main menu was not detected."
  }
}
$ echo $?
1
```

### Parseo con `jq`

```bash
# Extraer status
python main.py --service-once | jq -r '.status'

# Verificar si hubo cambio
python main.py --service-once | jq -r '.changed'

# Obtener canal nuevo en 2.4 GHz
python main.py --service-once | jq -r '.details.new_channel_24'
```

---

## 🔗 Dependencias

### Bloqueada por
- ✅ **P0-01:** Stabilize core API (merged - PR #20)

### Bloquea a
- ⏳ **P0-04:** Implement Windows service skeleton
- ⏳ **P1-01:** UI MVP (necesita parsear JSON de service-once)

---

## 📦 Commits Realizados

### 1. Implementación Core
```
616dc41 - feat(service): add --service-once CLI mode for structured JSON output
- Add --service-once flag to main.py CLI
- Uses OptimizationService.run_cycle() internally
- Outputs structured JSON to stdout (contract_version v1)
- Exit code 0 for success/no_change, 1 for error
- Compatible with --dry-run flag
```

### 2. Tests Unitarios
```
(pending) - test(service): add unit tests for --service-once mode
- 9 unit tests covering JSON structure and exit codes
- All tests passing (14/14 total including P0-01)
```

### 3. Documentación
```
(pending) - docs(readme): document --service-once mode with examples
- Update README.md with flag description and usage examples
- Create P0-02-DOD-STATUS.md with DoD evaluation
```

---

## ✅ Criterios de Aceptación Cumplidos

| # | Criterio | Verificación | Estado |
|---|----------|--------------|--------|
| 1 | CLI acepta flag `--service-once` | `python main.py --service-once` ejecuta sin error | ✅ |
| 2 | Output es JSON válido en stdout | `python main.py --service-once \| jq .` parsea correctamente | ✅ |
| 3 | JSON contiene `contract_version` | `jq .contract_version` retorna `"v1"` | ✅ |
| 4 | Exit code 0 en success/no_change | `echo $?` retorna `0` tras ejecución exitosa | ✅ |
| 5 | Exit code 1 en error | `echo $?` retorna `1` tras error | ✅ |
| 6 | Compatible con `--dry-run` | `--service-once --dry-run` ejecuta sin aplicar cambios | ✅ |
| 7 | Tests unitarios pasan | `python -m unittest tests.test_service_once_mode -v` → OK | ✅ |
| 8 | Documentación actualizada | README.md contiene sección de `--service-once` | ✅ |

---

## 🎯 Próximos Pasos

### Inmediatos (Completar P0-02)
- ✅ Tests unitarios implementados
- ✅ README.md actualizado
- ⏳ Commitear cambios pendientes
- ⏳ Pushear a origin
- ⏳ Abrir PR para review

### Siguientes (Post P0-02)
1. **P0-03:** Define local IPC/API contract for UI <-> service
2. **P0-04:** Implement Windows service skeleton (consumirá `--service-once`)
3. **P1-01:** UI MVP (parsear JSON de service-once)

---

**Conclusión:** P0-02 cumple con **todos los criterios del Definition of Done** y está listo para PR review y merge.

**Estado del branch:** `feature/P0-02-service-execution-mode` (pendiente commit/push de tests y docs)  
**Próximo milestone:** Abrir PR y solicitar review

