# Contexto del proyecto

Estoy trabajando sobre `WifiChannelOptimizer` (Python, Windows-first, licencia MIT en el repo actual).
Objetivo: evolucionarlo hacia un producto privativo con acceso fácil para usuario final, incluyendo **UI en Windows** y **servicio en segundo plano**.

Repositorio actual (referencias principales):
- `main.py`
- `wifi_optimizer/optimizer.py`
- `wifi_optimizer/decision.py`
- `wifi_optimizer/scanner.py`
- `wifi_optimizer/quality.py`
- `wifi_optimizer/monitor.py`
- `wifi_optimizer/routers/base.py`
- `wifi_optimizer/routers/huawei_hg8145x6.py`
- `pyproject.toml`
- `README.md`
- `README.us.md`
- `LICENSE` (MIT)

---

## Tu misión (próximo agente)

Diseñar y ejecutar una propuesta para convertir este proyecto en una solución privativa para Windows, **sin comprometer cumplimiento legal** y maximizando mantenibilidad.

## Reglas clave (obligatorias)

1. **Licencias/compliance primero**
   - Verifica obligaciones de `LICENSE` (MIT) del proyecto base.
   - Si aparece software privativo de terceros, **NO** asumir permiso de fork/redistribución/modificación.
   - Regla: **evitar fork de software privativo tercero salvo autorización explícita por escrito**.
   - Prioriza integración por API/CLI/plugin/wrapper desacoplado antes que copiar código de terceros.

2. **Arquitectura recomendada**
   - Separar en capas:
     - `core` (lógica optimización/canales)
     - `service` Windows (daemon/controlador local)
     - `ui` (desktop o web local)
   - Comunicación entre UI y servicio por API local (localhost) o IPC seguro.
   - Mantener `BaseRouter` como contrato de drivers y evitar acoplar UI con automatización Playwright.

3. **Producto privativo sin romper base técnica**
   - Permitir roadmap híbrido:
     - opción A: core abierto + capa privativa
     - opción B: distribución privativa completa (si legalmente viable)
   - Documentar implicancias legales de cada opción.

4. **Nada de afirmaciones no verificadas**
   - Si no puedes verificar algo, márcalo como supuesto.
   - Cualquier decisión legal debe quedar como “validar con abogado/licensing counsel”.

---

## Resultado esperado de tu trabajo

Entrega un paquete de salida con:

1. **Decisión de estrategia (fork vs no fork)**
   - Recomendación explícita con justificación legal/técnica.
   - Matriz comparativa:
     - fork directo
     - wrapper desacoplado
     - plugin/driver externo
     - integración por API
   - Conclusión recomendada por riesgo/velocidad/mantenibilidad.

2. **Arquitectura objetivo Windows**
   - Diagrama textual de componentes.
   - Fronteras entre módulos.
   - Contratos de integración (inputs/outputs/eventos).
   - Manejo de secretos (`.env`, credenciales de router, cifrado en reposo si aplica).

3. **Plan por fases (ejecutable)**
   - Fase 0: auditoría licencias y dependencias
   - Fase 1: refactor mínimo para exponer core como librería estable
   - Fase 2: servicio Windows (instalable, autostart, logs, healthcheck)
   - Fase 3: UI (MVP) con acciones: estado, ejecutar ciclo, ver métricas, configurar perfil
   - Fase 4: empaquetado/distribución (instalador, actualización, rollback)
   - Fase 5: hardening (errores, telemetría opcional, QA)

4. **Checklist de compliance**
   - Avisos de licencia obligatorios.
   - Third-party notices.
   - Política de contribuciones.
   - Política de uso de marcas y redistribución.
   - Decisiones de “qué código NO se copia”.

5. **Entregables técnicos concretos**
   - Estructura de carpetas propuesta.
   - Archivos nuevos recomendados (`NOTICE`, `THIRD_PARTY_LICENSES`, docs de arquitectura).
   - Backlog priorizado (P0/P1/P2) con esfuerzo estimado.

6. **Criterios de aceptación (DoD)**
   - Servicio Windows inicia/parar correctamente.
   - UI puede leer estado del servicio y disparar acciones seguras.
   - Flujo de optimización en modo dry-run y modo real validado.
   - Evidencia de cumplimiento legal/documental mínima incluida.

7. **Riesgos + mitigación**
   - Legales, técnicos, operacionales, UX.
   - Probabilidad/impacto y plan de mitigación por riesgo.

8. **Preguntas abiertas (bloqueantes)**
   - Modelo comercial deseado (closed total vs híbrido).
   - Stack UI preferido (nativo .NET, Electron, web local).
   - Soporte multi-router y roadmap de drivers.
   - Estrategia de updates y firma de binarios.

---

## Restricción de diseño importante

Si decides que habrá fork:
- Es fork de **este** proyecto (MIT) y no de software privativo de terceros.
- Mantén trazabilidad de cambios y headers de licencia donde corresponda.
- No elimines créditos/licencia MIT exigidos.

Si hay interacción con software privativo tercero:
- Tratarlo como dependencia externa o integración contractual.
- No copiar código ni assets salvo permiso explícito.

---

## Formato de salida que quiero

Responde en este orden:
1. Recomendación ejecutiva (5-10 líneas)
2. Matriz de decisión (tabla)
3. Arquitectura objetivo (bullets + diagrama textual)
4. Roadmap por fases con hitos y duración estimada
5. Checklist legal/compliance
6. Backlog priorizado (P0/P1/P2)
7. Riesgos y mitigaciones
8. Preguntas abiertas y próxima acción recomendada en 48h
