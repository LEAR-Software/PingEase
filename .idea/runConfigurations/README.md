# JetBrains Run Configurations - PingEase

Este directorio contiene configuraciones de ejecución (Run Configurations) para PyCharm/IDEA.

## 📋 Configuraciones Disponibles

### 1. **pingease:main**
- **Archivo:** `pingease_main.xml`
- **Propósito:** Ejecutar el punto de entrada principal del proyecto
- **Script:** `main.py`
- **Uso:** Ejecución estándar del optimizador WiFi

### 2. **pingease:tests**
- **Archivo:** `pingease_tests.xml`
- **Propósito:** Ejecutar todos los tests unitarios del proyecto
- **Comando:** `python -m unittest discover -s tests -v`
- **Uso:** Validación completa de la suite de tests

### 3. **pingease:ruff**
- **Archivo:** `pingease_ruff.xml`
- **Propósito:** Ejecutar el linter ruff sobre todo el proyecto
- **Comando:** `python -m ruff check .`
- **Uso:** Validación de calidad de código y estándares

### 4. **pingease:service_api_demo**
- **Archivo:** `pingease_service_api_demo.xml`
- **Propósito:** Demostración del módulo service_api
- **Script:** `wifi_optimizer/service_api.py`
- **Uso:** Testing manual del contrato v1 de OptimizationService

### 5. **pingease:test_service_api**
- **Archivo:** `pingease_test_service_api.xml`
- **Propósito:** Ejecutar tests específicos del módulo service_api
- **Comando:** `python -m unittest tests.test_service_api -v`
- **Uso:** Validación del contrato de servicio (P0-01)

### 6. **pingease:analyze_windows**
- **Archivo:** `pingease_analyze_windows.xml`
- **Propósito:** Ejecutar utilidad de análisis de ventanas óptimas
- **Script:** `analyze_windows.py`
- **Uso:** Análisis de configuración de Windows para optimización

## 🔧 Configuración Común

Todas las configuraciones comparten:

- **Intérprete:** SDK del módulo PingEase (usa el intérprete configurado en PyCharm para el proyecto)
- **Working Directory:** `$PROJECT_DIR$` (raíz del proyecto)
- **Module:** PingEase
- **Add content roots:** ✅ Enabled
- **Add source roots:** ✅ Enabled

### ⚙️ Nota sobre configuración de intérprete

Las configuraciones usan `IS_MODULE_SDK=true` en lugar de hardcodear la ruta del intérprete.
Esto permite que PyCharm use automáticamente el Python configurado para el proyecto
(típicamente el entorno virtual en `.venv/`).

## 📝 Notas

- Estas configuraciones fueron actualizadas para usar el SDK del módulo correctamente
- Las configuraciones de test usan el tipo `tests` con factory `Unittests` para mejor integración con PyCharm
- **IMPORTANTE:** Las configuraciones de test usan `_new_targetType="PYTHON"` (módulo Python) en lugar de `"PATH"` (archivo)
  - Ejemplo: `target="tests.test_service_api"` en lugar de `target="$PROJECT_DIR$/tests/test_service_api.py"`
  - Esto permite que PyCharm descubra y ejecute los tests correctamente
- El entorno virtual debe estar creado en `.venv/` y configurado en PyCharm
- Si el intérprete no se encuentra, PyCharm solicitará configurarlo manualmente

### ✅ Cambio Reciente (2026-04-14)
Se corrigió el error "Python module name must be set" cambiando las configuraciones de test:
- De: `_new_targetType="PATH"` + `_new_target="$PROJECT_DIR$/tests/..."`
- A: `_new_targetType="PYTHON"` + `_new_target="tests.test_service_api"`

Ver `README_TROUBLESHOOTING.md` para más detalles.

## 🚀 Uso Rápido

Para ejecutar cualquier configuración desde PyCharm:

1. Abre el selector de configuraciones (esquina superior derecha)
2. Selecciona la configuración deseada (ej: `pingease:tests`)
3. Click en ▶️ Run o 🐛 Debug

O usa el atajo de teclado:
- **Run:** `Shift + F10`
- **Debug:** `Shift + F9`

## 🔗 Referencias

- Documentación P0-01: `docs/architecture/P0-01-PLAN.md`
- Contrato Service API: `docs/architecture/SERVICE_API_CONTRACT_V1.md`
- Proyecto hermano: `C:\Users\matias\PycharmProjects\PingEase-Premium`

---

**Última actualización:** 2026-04-14  
**Sesión:** P0-01 Contract Stabilization

