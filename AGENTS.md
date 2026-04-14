# 🤖 AGENTS.md - Sesiones de Trabajo del Proyecto PingEase

**Propósito:** Registro cronológico de avances y estado del proyecto para continuar de una sesión a otra sin perder contexto.

---

## 📍 Sesión 2026-04-14 (ÚLTIMA - Definición Transversal Open-Core/Premium)

### 🎯 Objetivo
Definir el modelo operativo dual-repo (open-core + premium), documentarlo en plantillas/playbook, y dejar lista la carga de issues/proyectos en GitHub.

### ✅ Completado
- Se validó operación transversal entre `LEAR-Software/PingEase` y `LEAR-Software/pingease-premium`.
- Se fijó estrategia: contrato nace en open-core; premium consume contrato versionado (nunca al revés).
- Se creó `docs/DUAL_REPO_PLAYBOOK.md` con flujo de issue espejo, PR cruzado y release dual.
- Se actualizaron templates:
  - `.github/ISSUE_TEMPLATE/backlog-p0-p1-p2.md`
  - `.github/pull_request_template.md`
- Se verificó GitHub CLI en entorno local:
  - `gh version` OK
  - `gh auth status` OK (scope incluye `project`, `repo`, `workflow`)
- Se creó project premium en org `LEAR-Software`:
  - `PingEase Premium Backlog` (#5)
  - URL: `https://github.com/orgs/LEAR-Software/projects/5`
- Se crearon issues premium espejo en `LEAR-Software/pingease-premium`:
  - `#2` `[P0-07-PREM]` gate Free/Premium
  - `#3` `[P1-03-PREM]` installer/update + rollback
  - `#4` `[P2-02-PREM]` policy packs Pro/Business
- Se agregaron issues al project premium (#5) y se sincronizó trazabilidad con comentarios en core (`#8`, `#12`, `#16`).
- Se aseguró carga de issues core (`#2`-`#18`) en `PingEase MVP Backlog` (#4).
- Se commitearon y pushearon los cambios de gobernanza dual-repo en rama `feature/P0-01-stabilize-core-api`.
- Se asignó owner `@matiasmlforever` a premium issues `#2`, `#3`, `#4`.
- Se confirmó estado inicial `Todo` de los 3 items en project premium #5.

### ⚠️ Pendiente
- Evaluar si los items premium (`P0-07`, `P1-03`, `P2-02`) se mantienen como espejo o se transfieren oficialmente fuera de core en una etapa posterior.
- Abrir primer par de PRs cross-repo para `P0-07` con enlaces espejo obligatorios.

### 🔗 Enlaces Críticos
- Open-core repo: `https://github.com/LEAR-Software/PingEase`
- Premium repo: `https://github.com/LEAR-Software/pingease-premium`
- Core project: `https://github.com/orgs/LEAR-Software/projects/4`
- Premium project: `https://github.com/orgs/LEAR-Software/projects/5`
- Playbook dual: `docs/DUAL_REPO_PLAYBOOK.md`

### 💾 Estado Final
- Rama: `feature/P0-01-stabilize-core-api`
- Cambio clave: gobernanza dual-repo documentada y templates listos para trazabilidad cruzada.
- Commit: `b2679aa` (`docs: add dual-repo playbook and cross-repo templates`)

### 🚀 Recomendación para Next Session
1. Abrir primer par de PRs cross-repo para `P0-07` (`PingEase#8` <-> `pingease-premium#2`).
2. Definir política de cierre: cuándo cerrar issue core padre vs issue premium espejo.
3. Crear milestones (Week 1..6+) y asignarlos a los issues premium espejo.

---

## 📍 Sesión 2026-04-14 (Setup Backlog MVP - Histórica)

### 🎯 Objetivo
Completar setup de backlog MVP en GitHub Project #4 con 17 issues (P0/P1/P2), migración de Premium repo, y documentación operativa.

### ✅ Completado

#### 1. Repositorio Premium Creado
- **Nombre:** `PingEase-Premium`
- **URL:** `https://github.com/matiasmlforever/PingEase-Premium`
- **Tipo:** Privado
- **Propósito:** Capa de características premium y licenciamiento
- **Estado:** Creado, listo para desarrollo

#### 2. GitHub Project #4 Creado
- **Proyecto:** `PingEase MVP Backlog`
- **URL:** `https://github.com/orgs/LEAR-Software/projects/4`
- **Estado:** Operativo, contiene 17 issues

#### 3. Issues Creados y Agregados al Project
**P0 (Must ship first):** 8 issues (#2-#9)
- P0-01: Stabilize core API surface for service integration
- P0-02: Add service-ready execution mode and structured results
- P0-03: Define local IPC/API contract for UI <-> service
- P0-04: Implement Windows service skeleton
- P0-05: Define Windows secrets baseline
- P0-06: Complete compliance release bundle v1
- P0-07: Define Free/Premium gate outside open-core
- P0-08: Harden CI minimum and required checks

**P1 (MVP completion):** 5 issues (#10-#14)
- P1-01: UI MVP (status, run cycle, metrics view, profile config)
- P1-02: Structured telemetry (opt-in) and diagnostics package export
- P1-03: Installer and update strategy (MSI/winget/manual) + rollback
- P1-04: Router driver test harness with mockable BaseRouter contract
- P1-05: Docs alignment: PingEase naming in READMEs + architecture

**P2 (Post-MVP hardening):** 4 issues (#15-#18)
- P2-01: Multi-router roadmap and plugin packaging model
- P2-02: Premium Pro/Business policy packs and multi-device controls
- P2-03: Binary signing and trust pipeline (code signing cert + verification)
- P2-04: Performance and reliability benchmarks (cycle latency, failure recovery)

#### 4. Labels Creados
- `backlog` - Identifica items del backlog
- `P0` - Prioridad 0: Must ship first
- `P1` - Prioridad 1: MVP completion
- `P2` - Prioridad 2: Post-MVP hardening
- `needs-triage` - Requiere revisión inicial

#### 5. Documentación Agregada
- **`.github/pull_request_template.md`** - Template para PRs con compliance gate y checklist completo
- **`docs/BACKLOG_GUIDE.md`** - Guía operativa de 300+ líneas: cómo usar el backlog, flujo de trabajo, comandos gh/git, anatomía de issues, troubleshooting
- **`BACKLOG_SETUP.md`** - Resumen de setup completado
- **`.github/ISSUE_TEMPLATE/backlog-p0-p1-p2.md`** - Template estándar para crear nuevos backlog items

#### 6. PRs en Repositorio Open-Core
- **PR #1:** Mergeado ✅ (setup inicial de backlog)
- **PR #19:** Abierto 🟡 (chore/backlog-docs-followup)
  - URL: `https://github.com/LEAR-Software/PingEase/pull/19`
  - Contiene: templates y guías de uso
  - Estado: Pendiente merge (branch limpio, sin conflictos)

### ⚠️ Pendiente

#### Corto Plazo (Antes de Next Session)
1. **Mergear PR #19** - Documentación operativa faltante
2. **Crear Milestones** en GitHub (Week 1, Week 2, Week 3-4, Week 4-5, Week 6+)
   - Ejemplo comando: `gh milestone create "Week 1" --repo LEAR-Software/PingEase`
3. **Asignar owners** a cada P0 issue según disponibilidad
4. **Iniciar P0-01** - Crear PR feature/P0-01-stabilize-core-api con refactor de core API para service integration

#### Mediano Plazo
- Configurar CI checks en branch protection (compile + audit + requerido)
- Establecer cadencia de reviews (weekly standup/PR reviews)
- Crear decisiones de arquitectura para P0-03 (IPC/API contract)
- Documentar secrets management (P0-05)

### 📊 Estadísticas
| Métrica | Valor |
|---------|-------|
| Repositorios Activos | 2 (open-core + premium) |
| Issues Totales | 17 |
| Project Boards | 1 (LEAR-Software #4) |
| PRs Abiertos | 1 (PR #19) |
| PRs Mergeados | 1 (PR #1) |
| Documentación Creada | 4 archivos |

### 🔗 Enlaces Críticos
- **Project Board:** `https://github.com/orgs/LEAR-Software/projects/4`
- **Open-core Repo:** `https://github.com/LEAR-Software/PingEase`
- **Premium Repo:** `https://github.com/matiasmlforever/PingEase-Premium`
- **Backlog Decisions:** `docs/mvp-windows-backlog.md`
- **Guía Operativa:** `docs/BACKLOG_GUIDE.md` (NUEVA)
- **Compliance Gate:** `docs/compliance-criteria.md`
- **Open-core Boundary:** `docs/open-core-boundary.md`
- **Free/Premium Matrix:** `docs/free-premium-matrix.md`

### 💾 Rama Actual
- Rama: `chore/backlog-docs-followup`
- Estado: Limpio, sin cambios sin commit
- Commits: 3 (docs: BACKLOG_SETUP.md, docs: BACKLOG_GUIDE.md, etc.)
- Push: ✅ Pusheado a origin

### 🚀 Recomendación para Next Session
1. Mergear PR #19 (debería estar en verde; revisar CI)
2. Checkout a `main` tras merge
3. Crear milestones para las 6 semanas planificadas
4. Asignar P0 issues a sprint/owner
5. Iniciar P0-01 development branch

### 📝 Notas Especiales
- Los issues **no se migran** entre repos de GitHub manteniendo todo (se pueden transferir pero cambia número)
  → Decisión: mantener backlog MVP en open-core, manejar premium en repo separado
- El label `setup` no existe (intentó crearse pero gh lo eliminó); usar `documentation` + `backlog` en su lugar
- CI workflow ya configurado (ci.yml + deps-audit.yml)
- Branch protection activada en `main`

---

## 📋 Template para Próximas Sesiones

Cuando continúes, actualiza esta sección con:

```markdown
## 📍 Sesión YYYY-MM-DD

### 🎯 Objetivo
[Qué se va a hacer en esta sesión]

### ✅ Completado
- [Item 1]
- [Item 2]

### ⚠️ Pendiente
- [Item 1]
- [Item 2]

### 🔗 Enlaces Críticos
[Solo los que sean relevantes esta sesión]

### 💾 Estado Final
- Rama: [rama actual]
- PR: [número si aplica]
- Cambios: [resumen de cambios]

### 🚀 Recomendación para Next Session
[Qué hacer apenas se retome]
```

---

**Última Actualización:** 2026-04-14 13:35 UTC  
**Sesión:** Definición transversal open-core/premium + ejecución operativa en proyectos/issues  
**Status:** ✅ Completada (playbook + templates + project premium + issues espejo + owners/estado inicial)  
**Próxima:** Abrir primer par de PRs cross-repo para P0-07

