# 📋 PingEase MVP Backlog - Guía de Uso

## 🎯 Estructura General

El backlog MVP de PingEase está organizado en **3 prioridades** y se gestiona a través de:

1. **GitHub Issues** (`LEAR-Software/PingEase`) - Crear y detallar trabajo
2. **GitHub Project** (`LEAR-Software/projects/4`) - Organizar flujo de ejecución
3. **GitHub Discussions** (futura) - Decisiones y contexto arquitectónico

### Prioridades

| Prioridad | Objetivo | Esfuerzo esperado |
|-----------|----------|------------------|
| **P0** | Must ship first (8 issues) | 2-3 semanas |
| **P1** | MVP completion (5 issues) | 2-3 semanas |
| **P2** | Post-MVP hardening (4 issues) | 6+ semanas |

---

## 🚀 Flujo de Trabajo

### Regla Operativa Obligatoria (Sesion = 1 issue + 1 rama)

- No se inicia sesion de desarrollo sin issue activo asignado.
- No se trabaja en `main`; cada issue debe tener rama dedicada.
- Si una sesion cambia de objetivo, se cierra registro de la sesion actual y se abre nueva sesion con otro issue/rama.
- Excepcion permitida: hotfix urgente, documentado en `AGENTS.md` con justificacion.

Formato recomendado de ramas:

- `feature/P0-03-local-ipc-contract`
- `fix/P1-04-router-state-bug`
- `docs/P1-05-architecture-alignment`
- `chore/P0-08-ci-hardening`

### 1. Tomar un Issue

```bash
# 1. En GitHub: buscar issue sin asignar (filtrar por label "P0", "P1", o "P2")
# 2. Asignarte a ti mismo: click "Assign me"
# 3. Mover a "In Progress" en el project board
# 4. Confirmar numero de issue que se trabajara en la sesion
```

### 2. Crear Feature Branch

```bash
# Usar patron: <tipo>/Pn-XX-short-description
# Tipos permitidos: feature | fix | docs | chore
git checkout -b feature/P0-01-stabilize-core-api

# O si es fix: fix/Pn-XX-description
git checkout -b fix/P0-01-core-api-bug
```

### Checklist de inicio de sesion (bloqueante)

- [ ] Issue asignado y en `In Progress`.
- [ ] Rama creada segun patron `<tipo>/Pn-XX-slug`.
- [ ] `AGENTS.md` actualizado con issue y rama de la sesion.

### 3. Implementar y Testear

```bash
# Asegurate que:
# ✅ Compila/ejecuta localmente
# ✅ Tests pasan
# ✅ Dry-run works (si aplica)

python -m compileall main.py wifi_optimizer
python -m pytest tests/ -v

# Si cambias dependencias:
# ✅ Actualiza THIRD_PARTY_LICENSES.md
```

### 4. Cumplir Compliance Gate

Antes de crear PR, verifica:

- [ ] **Licencia:** `LICENSE` file respeta MIT
- [ ] **Atribución:** `NOTICE` actualizado si cambia contexto de distribución
- [ ] **Terceros:** `THIRD_PARTY_LICENSES.md` refleja cambios de deps
- [ ] **Secretos:** NO hardcoded credentials, `.env` en `.gitignore`
- [ ] **Boundary:** Cambios respetan `docs/open-core-boundary.md`
- [ ] **Tier changes:** Si toca premium/free, actualiza `docs/free-premium-matrix.md`

### 5. Crear Pull Request

```bash
# Usar template .github/pull_request_template.md
# Completar checklist
# Linkar issue con "Fixes #XX"
# Seleccionar labels: backlog, P0/P1/P2

git push origin feature/P0-01-stabilize-core-api
```

### 6. Code Review & Merge

- [ ] Reviews de CODEOWNERS pasan
- [ ] CI checks (compile + audit) en verde
- [ ] Branch protection: al menos 1 aprobación requerida
- Merge a `main` (squash o rebase según política)

### Checklist de cierre de sesion

- [ ] Estado del issue actualizado (comentario con avance/bloqueos).
- [ ] Estado del project board actualizado (`In Progress`, `In Review` o `Done`).
- [ ] `AGENTS.md` actualizado con resultados y proxima accion.

---

## 📊 Organización del Project Board

### Columnas recomendadas

| Columna | Significa |
|---------|-----------|
| **Backlog** | Issues no iniciados (todos por defecto aquí) |
| **In Progress** | Asignado y en desarrollo |
| **In Review** | PR creado, esperando review |
| **Done** | PR merged |

### Filtrar y Agrupar

```bash
# Por prioridad:
# - Filtro "label:P0"
# - Filtro "label:P1"
# - Filtro "label:P2"

# Por assignee:
# - Filtro "assignee:username"

# Por milestone (crear primero):
# - Crear Milestone "Week 1", "Week 2", etc.
# - Asignar issues a cada milestone
```

---

## 🔀 Flujo de Ramas

```
main (protegida)
  ↑
  ├─ feature/P0-01-...  → PR → merge a main
  ├─ feature/P0-02-...  → PR → merge a main
  ├─ feature/P1-01-...  → PR → merge a main
  └─ fix/Pn-XX-...      → PR → merge a main
```

**Reglas:**
- Nunca commitear directamente a `main`
- Siempre crear feature/fix branch desde `main`
- Cada rama debe mapear a un issue especifico (1:1 durante la sesion)
- Rebase antes de merge para mantener historia limpia
- Eliminar branch después de merge

---

## 📖 Anatomía de un Issue

### Titulo (required)
```
[Pn-XX] Descripción breve en máx 60 caracteres
```
Ejemplos:
- `[P0-01] Stabilize core API surface for service integration`
- `[P1-03] Installer and update strategy (MSI/winget/manual) + rollback`

### Body (usar template `.github/ISSUE_TEMPLATE/backlog-p0-p1-p2.md`)

```markdown
## Contexto
Describe el problema u oportunidad en 3-5 lineas.

## Prioridad y esfuerzo
- Prioridad: P0 | P1 | P2
- Esfuerzo: S (≤2 dias) | M (3-5 dias) | L (6-10 dias)
- Owner sugerido: 
- Fecha objetivo:

## Dependencias
- Bloqueada por: [lista de issues]
- Bloquea a: [lista de issues]

## Boundary check (open-core vs premium)
- Alcance: Open-core | Premium layer | Commercial ops
- [ ] Revisado contra docs/open-core-boundary.md
- [ ] Revisado contra docs/free-premium-matrix.md

## Definicion de Done (DoD)
- [ ] Resultado funcional implementado
- [ ] Criterio minimo del backlog cumplido (de mvp-windows-backlog.md)
- [ ] Evidencia adjunta
- [ ] Documentacion actualizada si aplica

## Compliance gate (PR)
- [ ] Obligaciones de licencia preservadas
- [ ] NOTICE actualizado si aplica
- [ ] THIRD_PARTY_LICENSES.md actualizado
- [ ] No codigo privativo sin permiso
- [ ] Cambios de tiers reflejados
- [ ] Impacto de frontera revisado
- [ ] Manejo de secretos sin regresion

## Referencias
- Backlog base: docs/mvp-windows-backlog.md
- Compliance: docs/compliance-criteria.md
```

---

## 🔗 Enlaces Útiles

- **Project Board:** https://github.com/orgs/LEAR-Software/projects/4
- **Open-core Repo:** https://github.com/LEAR-Software/PingEase
- **Premium Repo:** https://github.com/matiasmlforever/PingEase-Premium
- **Backlog Decisions:** `docs/mvp-windows-backlog.md`
- **Compliance Criteria:** `docs/compliance-criteria.md`
- **Open-core Boundary:** `docs/open-core-boundary.md`
- **Free/Premium Matrix:** `docs/free-premium-matrix.md`

---

## ⚙️ Herramientas Útiles

### GitHub CLI (gh)

```bash
# Listar issues
gh issue list --repo LEAR-Software/PingEase --label "P0"

# Ver detalles de un issue
gh issue view 2 --repo LEAR-Software/PingEase

# Crear issue
gh issue create --repo LEAR-Software/PingEase --title "[P0-XX] Title" --body "Content"

# Asignarte a un issue
gh issue edit 2 --repo LEAR-Software/PingEase --add-assignee @me

# Ver project
gh project view 4 --owner LEAR-Software
```

### Git

```bash
# Clonar repo
git clone https://github.com/LEAR-Software/PingEase.git

# Crear rama
git checkout -b feature/P0-01-api

# Commit con referencia
git commit -m "feat: stabilize core API surface

Fixes #2"

# Pushear
git push origin feature/P0-01-api
```

---

## 📝 Cadencia Sugerida (2-6 semanas)

```
Week 1: P0-01, P0-02, P0-03, P0-08
Week 2: P0-04, P0-05, P0-06, P0-07
Week 3-4: P1-01, P1-04
Week 4-5: P1-02, P1-03, P1-05
Week 6+: P2 hardening items
```

### Puntos de Control Semanales
- Lunes: triage de nuevos issues
- Miércoles: review de PRs
- Viernes: cierre de ciclo, replanificación

---

## 🆘 Problemas Comunes

### "Issue bloqueado por otro"
→ Esperar a que se cierre el issue de dependencia, o priorizar
→ Verificar en issue si hay alternativas (ej. mock objects para testing)

### "No sé dónde comenzar"
→ Ver "Prioridad y esfuerzo" en issue
→ Si es `S` (≤2 dias): puedes empezar hoy
→ Si es `L`: desglosar en sub-tasks o PRs incrementales

### "CI check falló"
→ Ver logs en GitHub: Actions tab
→ Errores comunes:
  - `compileall`: sintaxis Python. Ejecuta localmente: `python -m compileall main.py`
  - `audit`: dependencia vulnerable. Actualiza en `pyproject.toml`
  - `import`: módulo faltante. Instala: `pip install -e .`

### "Necesito cambiar la prioridad/esfuerzo"
→ Editar issue → "Edit" → actualizar campos
→ Notificar en comentario @CODEOWNERS si es cambio material

---

## 🔐 Seguridad & Privacidad

- **NUNCA commitear:** credenciales, API keys, tokens
- **Usar:** archivos `.env` (ignorados en git) para secrets
- **Si exportas logs:** sanitizar valores sensibles
- **Diagnostic packages:** NO incluir archivos de config con credentials

---

## 📚 Lectura Recomendada (antes de empezar)

1. `docs/mvp-windows-backlog.md` - Scope y objetivos
2. `docs/compliance-criteria.md` - Qué debe verificar cada PR
3. `docs/open-core-boundary.md` - Qué va en open-core vs premium
4. `docs/free-premium-matrix.md` - Tier feature mapping
5. `README.md` - Producto, instalación, uso

---

**Última actualización:** 2026-04-14
**Autor:** GitHub Copilot (setup automation)
**Responsable:** @CODEOWNERS

