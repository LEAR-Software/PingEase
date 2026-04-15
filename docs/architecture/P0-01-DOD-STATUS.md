# P0-01: Stabilize Core API - Definition of Done Status

**Fecha de evaluación:** 2026-04-15  
**Branch:** `feature/P0-01-stabilize-core-api`  
**PR:** [#20](https://github.com/LEAR-Software/PingEase/pull/20)

---

## 📋 Definition of Done (DoD)

### ✅ 1. Entrypoint core invocable por wrapper de servicio sin supuestos de CLI

**Estado:** ✅ **COMPLETADO**

**Evidencia:**

- **Archivo:** `wifi_optimizer/service_api.py`
- **Clase principal:** `OptimizationService`
- **Método de invocación:** `run_cycle(dry_run: bool = False, headed: bool = False) -> OptimizationResult`

**Características implementadas:**

```python
# Constructor independiente de CLI
service = OptimizationService(config: OptimizerConfig)

# Invocación sin sys.exit() ni CLI args
result = service.run_cycle(dry_run=False, headed=False)

# Resultado estructurado, no side effects
assert isinstance(result, OptimizationResult)
assert result.status in ("success", "no_change", "error")
```

**Validación:**

- ✅ No usa `sys.argv` ni `argparse`
- ✅ No llama `sys.exit()` (retorna `OptimizationResult` con status normalizado)
- ✅ Configurable mediante `OptimizerConfig` (objeto puro)
- ✅ Lazy-initialization del router (conexión solo cuando se ejecuta `run_cycle()`)
- ✅ Manejo de errores normalizado (status `"error"` con `error_code`)

---

### ✅ 2. Flujo --dry-run se mantiene sin regresiones

**Estado:** ✅ **COMPLETADO**

**Evidencia:**

- **Test unitario:** `tests/test_service_api.py::test_run_cycle_dry_run_preserves_semantics`
- **CLI legacy:** `main.py` (línea 171-172, 194-195, 200)
- **Service API:** `wifi_optimizer/service_api.py` (línea 131, 156-159, 168)

**Comportamiento validado:**

1. **En CLI (`main.py`):**
   ```python
   dry_run = "--dry-run" in args
   # ...
   cycle_kwargs = dict(
       router=router,
       state=state,
       dry_run=dry_run,  # ✅ Passed to cycle
       # ...
   )
   run_optimization_cycle(**cycle_kwargs)
   ```

2. **En Service API (`service_api.py`):**
   ```python
   def run_cycle(self, dry_run: bool = False, headed: bool = False) -> OptimizationResult:
       # ...
       if not dry_run:
           self.state["current_24"], self.state["current_5"] = (
               self.router.read_channels()
           )
       # ...
       cycle_kwargs = {
           "router": self.router,
           "state": self.state,
           "dry_run": dry_run,  # ✅ Passed to core cycle
           # ...
       }
       run_optimization_cycle(**cycle_kwargs)
   ```

**Tests ejecutados:**

```bash
$ python -m unittest tests.test_service_api -v
test_run_cycle_dry_run_preserves_semantics ... ok
test_run_cycle_error_is_normalized ... ok
test_run_cycle_invalid_driver_returns_error ... ok
test_run_cycle_no_change ... ok
test_run_cycle_success_when_state_changes ... ok

Ran 5 tests in 0.009s

OK ✅
```

**Semántica actual de dry_run (v1):**

- `dry_run=True`: Ejecuta lógica de ciclo SIN aplicar cambios al router
- Resultado típico: `status="no_change"` (compatible con contrato v1)
- Sin lectura de canales actuales del router (línea 156-159)
- Flags internos pasados a `run_optimization_cycle()`

**Nota sobre evolución futura:**

Según `SERVICE_API_CONTRACT_V1.md` (línea 69-76), un status dedicado para dry-run (ej. `"dry_run_success"`) se difiere a una futura versión del contrato para evitar breaking changes en consumidores actuales.

---

### ✅ 3. Cambios documentados en arquitectura/core contract

**Estado:** ✅ **COMPLETADO**

**Evidencia:**

1. **Contrato versionado:**
   - **Archivo:** `docs/architecture/SERVICE_API_CONTRACT_V1.md`
   - **Versión:** `v1`
   - **Alcance:** Define payload de `OptimizationResult.to_dict()`

2. **Overview de arquitectura:**
   - **Archivo:** `docs/architecture/SERVICE_API_OVERVIEW.md`
   - **Contenido:** Contexto, motivación, separación CLI vs Service API

3. **Plan de implementación:**
   - **Archivo:** `docs/architecture/P0-01-PLAN.md`
   - **Contenido:** Roadmap de P0-01, criterios de aceptación, dependencias

**Estructura del contrato v1:**

```json
{
  "contract_version": "v1",
  "status": "success | no_change | error",
  "changed": true,
  "reason": "human-readable message",
  "details": {
    // Status-specific payload
  }
}
```

**Documentación de dry_run:**

Incluida en `SERVICE_API_CONTRACT_V1.md` (sección "Dry-run semantics in v1"):

- Define comportamiento actual (`dry_run=True` → compatible con status set existente)
- Documenta decisión de diferir status dedicado a versión futura
- Establece compatibilidad forward: consumidores deben ignorar keys desconocidas en `details`

---

## 📊 Resumen de Completitud

| Criterio DoD | Estado | Evidencia |
|-------------|--------|-----------|
| Entrypoint core sin CLI | ✅ Completado | `service_api.py` + tests + sin `sys.exit()` |
| Flujo `--dry-run` sin regresiones | ✅ Completado | Tests pasando + CLI legacy funcional |
| Cambios documentados | ✅ Completado | 3 archivos de arquitectura (CONTRACT_V1, OVERVIEW, PLAN) |

**DoD alcanzado:** ✅ **100%**

---

## 🔄 Próximos Pasos

Según AGENTS.md, la siguiente sesión debe:

1. **Mergear PR #20** con los cambios de P0-01
2. **Iniciar P0-02:** "Add service-ready execution mode and structured results"
   - Integrar `OptimizationService` en modo servicio standalone
   - Definir formato de respuesta IPC/local API (basado en CONTRACT_V1)
3. **Iniciar P0-03:** "Define local IPC/API contract for UI <-> service"
   - Diseñar protocolo de comunicación (HTTP local, named pipes, o stdio)
   - Documentar formato de request/response extendido

---

## 📝 Notas Técnicas

### Cambios realizados en esta sesión (adicionales)

- ✅ Agregado test `test_run_cycle_dry_run_preserves_semantics` para validación explícita de dry_run
- ✅ Total de tests: 5/5 pasando
- ✅ Coverage de rutas críticas: success, no_change, error, invalid_driver, dry_run

### Commits clave

- `5aa348d`: `feat(service): stabilize OptimizationService contract and add tests`
- (Pendiente): Commit de test dry_run adicional

### Dependencias validadas

```bash
# Package instalado en modo editable
$ pip list | grep wifi-optimizer
wifi-optimizer    0.1.0    C:\Users\matias\PycharmProjects\PingEase

# Tests discovery funcionando
$ python -m unittest discover -s tests -v
Ran 5 tests in 0.009s
OK
```

---

**Conclusión:** P0-01 cumple con **todos los criterios del DoD** y está listo para merge. 🚀

