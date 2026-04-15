---
name: "Backlog item (P0/P1/P2)"
about: "Crear una tarea ejecutable con DoD, dependencias y gate de compliance"
title: "[P0-XX] "
labels: ["backlog", "needs-triage"]
assignees: []
---

## Contexto

Describe el problema u oportunidad en 3-5 lineas.

## Prioridad y esfuerzo

- Prioridad: <!-- P0 | P1 | P2 -->
- Esfuerzo: <!-- S (<=2 dias) | M (3-5 dias) | L (6-10 dias) -->
- Owner sugerido:
- Fecha objetivo:

## Dependencias

- Bloqueada por: <!-- ej. P0-01, PR #123, decision legal -->
- Bloquea a:

## Coordinacion cross-repo

- Repo objetivo: <!-- LEAR-Software/PingEase | LEAR-Software/pingease-premium -->
- Project objetivo: <!-- LEAR-Software #4 | PingEase Premium Backlog -->
- Issue espejo (si aplica): <!-- URL o #id -->
- PR cross-repo relacionado (si aplica):

## Boundary check (open-core vs premium)

- Alcance: <!-- Open-core | Premium layer | Commercial ops -->
- [ ] Revisado contra `docs/open-core-boundary.md`
- [ ] Revisado contra `docs/free-premium-matrix.md`
- [ ] No se agrega logica premium sensible dentro del open-core sin aprobacion explicita

## Definicion de Done (DoD)

- [ ] Resultado funcional implementado
- [ ] Criterio minimo del backlog cumplido (copiar desde `docs/mvp-windows-backlog.md`)
- [ ] Evidencia adjunta (logs, capturas, salida de comandos o tests)
- [ ] Documentacion actualizada si aplica

### Criterios de aceptacion

1. 
2. 
3. 

## Compliance gate (PR)

- [ ] Obligaciones de licencia preservadas (`LICENSE`, atribucion, headers si aplica)
- [ ] `NOTICE` actualizado si cambia contexto de distribucion/atribucion
- [ ] `THIRD_PARTY_LICENSES.md` actualizado si cambian dependencias
- [ ] No se copia codigo/assets privativos de terceros sin permiso escrito
- [ ] Cambios de tiers reflejados en `docs/free-premium-matrix.md`
- [ ] Impacto de frontera revisado en `docs/open-core-boundary.md`
- [ ] Texto legal sensible marcado como pending counsel cuando aplique
- [ ] Manejo de secretos sin regresion (`.env` fuera de git, sin credenciales en logs)

## Riesgos y mitigacion

- Riesgo principal:
- Probabilidad: <!-- Baja | Media | Alta -->
- Impacto: <!-- Bajo | Medio | Alto -->
- Mitigacion:

## Validacion tecnica

- [ ] Compila/ejecuta localmente
- [ ] Checks de CI aplicables en verde
- [ ] No rompe flujo `--dry-run` (si aplica al core)

## Fuera de alcance (explicitamente)

- 

## Referencias

- Backlog base: `docs/mvp-windows-backlog.md`
- Playbook dual: `docs/DUAL_REPO_PLAYBOOK.md`
- Compliance: `docs/compliance-criteria.md`
- PR/commits relacionados:


