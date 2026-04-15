# Troubleshooting Run Configurations

## ⚠️ Error: "Python module name must be set"

### Problema
Al ejecutar configuraciones de test desde PyCharm, aparece el error:
```
Python module name must be set
```

### Causa
Este error ocurre cuando las configuraciones de ejecución usan `SDK_HOME` con una ruta hardcodeada al intérprete Python y `USE_MODULE_SDK=false`. PyCharm moderno requiere usar el SDK del módulo (`IS_MODULE_SDK=true`) para que las configuraciones funcionen correctamente.

### Solución Aplicada

#### 1. Para configuraciones de Python Script (main.py, analyze_windows.py, service_api_demo.py)
- Cambiar `USE_MODULE_SDK` de `false` a `true` (usando `IS_MODULE_SDK=true`)
- Eliminar o limpiar `SDK_HOME` (dejarlo vacío)
- Agregar `PARENT_ENVS=true`

#### 2. Para configuraciones de módulos Python (ruff)
- Similar a scripts, pero mantener `MODULE_MODE=true`
- Asegurar que `MODULE_NAME` esté configurado correctamente

#### 3. Para configuraciones de tests (unittest) - ✅ SOLUCIÓN ACTUALIZADA
- Cambiar el tipo de `PythonConfigurationType` a `tests` con factory `Unittests`
- **IMPORTANTE:** Usar `_new_targetType="PYTHON"` en lugar de `"PATH"`
- Target debe ser el módulo Python: `"tests.test_service_api"` en lugar de `"$PROJECT_DIR$/tests/test_service_api.py"`
- Ejemplo correcto:
  ```xml
  <option name="_new_target" value="&quot;tests.test_service_api&quot;" />
  <option name="_new_targetType" value="&quot;PYTHON&quot;" />
  ```

### Configuración de Dependencias

Además de las configuraciones, asegúrate de que:

1. **pyproject.toml está correctamente configurado:**
   - Sin BOM (Byte Order Mark) de UTF-8
   - Incluye `[tool.hatch.build.targets.wheel]` con `packages = ["wifi_optimizer"]`

2. **Dependencias instaladas:**
   ```bash
   pip install -e .
   playwright install chromium
   ```

3. **Entorno virtual configurado en PyCharm:**
   - Ir a: File > Settings > Project > Python Interpreter
   - Seleccionar o agregar el intérprete de `.venv/Scripts/python.exe`

## 📝 Verificación

Para verificar que todo funciona:

```bash
# Desde terminal
python -m unittest tests.test_service_api -v

# Debería mostrar:
# Ran 4 tests in 0.XXXs
# OK
```

## 🔄 Re-sincronización con PyCharm

Si PyCharm no reconoce los cambios en las configuraciones:

1. File > Invalidate Caches... > Invalidate and Restart
2. O simplemente cerrar y reabrir PyCharm

## 📚 Referencias

- [PyCharm Run Configurations](https://www.jetbrains.com/help/pycharm/run-debug-configuration.html)
- [Python unittest discovery](https://docs.python.org/3/library/unittest.html#test-discovery)
- [Hatchling Build Configuration](https://hatch.pypa.io/latest/config/build/)

---

**Última actualización:** 2026-04-14  
**Sesión:** P0-01 Run Configuration Fix

