# Service API Overview (`v1`)

Este documento presenta de forma visual la capa `service_api` para entender rapido como se ejecuta un ciclo y como se expone el contrato estable hacia servicio/IPC.

## 1) Rol de `wifi_optimizer/service_api.py`

- Expone `OptimizationService` como wrapper seguro para servicio (sin `sys.exit()`).
- Estandariza salida con `OptimizationResult`.
- Publica `contract_version` en cada payload (`v1`).
- Encapsula inicializacion del router y manejo de errores normalizado.

## 2) Componentes y dependencias

```mermaid
flowchart LR
    A["OptimizationService<br/>service_api.py"] --> B["OptimizerConfig<br/>config.py"]
    A --> C["run_optimization_cycle<br/>optimizer.py"]
    A --> D["Router Driver Registry"]
    D --> E["HuaweiHG8145X6<br/>routers/huawei_hg8145x6.py"]
    E --> F["BaseRouter<br/>routers/base.py"]
    A --> G["OptimizationResult<br/>status changed reason details"]
    G --> H["to_dict contract_version v1"]
```

## 3) Flujo de `run_cycle()`

```mermaid
flowchart TD
    S["run_cycle dry_run headed"] --> I{"router inicializado"}
    I -->|no| B["build router"]
    I -->|si| R["usar router existente"]
    B --> R

    R --> D{"dry_run"}
    D -->|no| PRE["leer canales actuales<br/>state current_24 current_5"]
    D -->|si| SNAP["tomar snapshot de state"]
    PRE --> SNAP

    SNAP --> EXEC["run_optimization_cycle"]
    EXEC --> CMP["comparar before vs after<br/>current_24 current_5"]

    CMP --> CH{"hubo cambio"}
    CH -->|si| OK["OptimizationResult success<br/>changed true<br/>details old new channels"]
    CH -->|no| NC["OptimizationResult no_change<br/>changed false<br/>details vacio"]

    S -->|exception| ER["OptimizationResult error<br/>changed false<br/>error_code SERVICE_CYCLE_FAILURE"]
```

## 4) Estado de salida (`OptimizationResult`)

```mermaid
stateDiagram
    [*] --> success: ciclo ejecutado + cambio detectado
    [*] --> no_change: ciclo ejecutado + sin cambio
    [*] --> error: excepcion en ciclo

    success: changed=true
    success: details incluye old/new 2.4 y 5 GHz

    no_change: changed=false
    no_change: details vacio

    error: changed=false
    error: details.error_code=SERVICE_CYCLE_FAILURE
    error: details.error_type/error_message
```

## 5) Contrato de respuesta (`to_dict()`)

Payload base serializable:

```json
{
  "contract_version": "v1",
  "status": "success | no_change | error",
  "changed": true,
  "reason": "...",
  "details": {}
}
```

## 6) Notas operativas importantes

- Validaciones de constructor:
  - `config` debe ser `OptimizerConfig`.
  - `router_driver` no puede estar vacio.
- `status` usa `Literal` para mantener contrato acotado.
- La deteccion de cambio se basa en snapshot pre/post (`current_24/current_5`).
- Error normalizado para IPC/servicio: `SERVICE_CYCLE_FAILURE`.
- `dry_run` actualmente no introduce estado dedicado; tipicamente termina en `no_change`.

## 7) Referencias

- `wifi_optimizer/service_api.py`
- `docs/architecture/SERVICE_API_CONTRACT_V1.md`
- `tests/test_service_api.py`


