# ADR-0001: Reconciliación de Branches antes de Migración v15→v16

**Fecha:** 2026-05-20  
**Estado:** Propuesta — requiere aprobación humana antes de ejecutar eliminaciones  
**Autor:** Diagnóstico automatizado vía Claude Code  
**Relacionado con:** ADR-0000 (estado real pre-migración)

---

## Contexto

Antes de iniciar la migración v15→v16, el repo tiene 12 branches remotas sin mergear a `origin/main` y
10 branches locales sin push. El diagnóstico previo identificó que la historia fue reescrita mediante
`filter-branch`, creando un commit "grafted" (`3d2c046`) como raíz sintética de `main`. Esto dejó todas
las branches `feature/*` como snapshots históricos desconectados de la nueva historia limpia.

Este ADR documenta el análisis 1×1 de cada branch, la decisión propuesta para cada una, y los riesgos
abiertos antes de proceder con la migración.

---

## El rewrite y el commit grafted

La historia del repo fue reescrita en algún momento entre julio 2025 y enero 2026. El mecanismo fue
`filter-branch` (evidencia: `stash@{0}: filter-branch: rewrite`). El resultado:

- **`3d2c046`** (`chore: eliminar scripts obsoletos`, PR #27) es el commit "grafted" — raíz sintética
  que contiene **todo el código consolidado** de todos los módulos, limpio de scripts de instalación
  manual.
- **`e0676aa`** (PR #28, infra-setup via squash-merge) es el HEAD actual de `origin/main`.
- Las branches `feature/*` apuntan a commits **anteriores al rewrite**, desconectados de la nueva
  historia limpia.
- `git branch -r --no-merged origin/main` reporta todas las feature branches como "no mergeadas",
  pero esto es un artefacto del rewrite — su código ya está incorporado en main.

**Baseline confirmado: `origin/main` commit `e0676aa`**

---

## Análisis de branches remotas

### Branches confirmadas en `git branch -r` post-fetch

Total: 12 branches remotas sin mergear a `origin/main` + `origin/main` itself.

---

### 1. `origin/develop`

| Campo | Valor |
|-------|-------|
| Tip commit | `4ec3b27` |
| Fecha último commit | 2025-06-27 |
| Commits únicos vs main | 5 |
| Diff vs main | 700 archivos, +137 / −121,158 líneas |

**Archivos únicos:** Scaffold inicial del proyecto (`README.md`, `.gitignore`), scripts legacy de
instalación (`run_tests.py`, `show_warehouse_types.py`, etc.), docs tempranas (`DEVELOPMENT_POLICIES.md`,
`ARCHITECTURE_MODULE_1_COMPANIES.md`), y un archivo erróneo:
`condominium_management/condominium_management/__init__.py` (directorio doblemente anidado, artefacto
de error). También tiene `ci.yml` sin el sufijo `.disabled` — la versión anterior del CI.

**Evaluación técnica:** Los datos muestran divergencia total de historia respecto a main y contenido
significativamente menor. Sin embargo, `develop` es una rama semántica del flujo Git (convención
Gitflow/Frappe). Su eliminación requiere decisión estratégica explícita sobre el modelo de ramas
del proyecto, no puede tratarse como limpieza de snapshot.

**Decisión propuesta:** 🔒 NO ELIMINAR POR AHORA — GRUPO C  
**Razón:** Rama semántica de desarrollo. No se elimina por lote. Requiere decisión explícita
posterior sobre estrategia de ramas (¿se mantiene develop como rama de integración? ¿se migra
a main como única rama estable?).  
**Confirmación humana:** CONGELADA — no eliminar sin decisión estratégica explícita

---

### 2. `origin/emergency/reset-to-48ea382`

| Campo | Valor |
|-------|-------|
| Tip commit | `48ea382` |
| Fecha último commit | 2025-07-16 |
| Commits únicos vs main | 73 |
| Diff vs main | 273 archivos, +6,555 / −25,848 líneas |

**Archivos únicos vs main:**
- `user_type` DocType (ver sección de user_type más abajo)
- Scripts legacy de instalación
- `companies/custom_fields/company_custom_fields.py`
- `companies/install.py`
- Diferencia trivial en `master_template_registry.py`: solo un ejemplo de docstring (1 línea: `# Configurar templates y reglas` → `registry.company = "Empresa Admin"`)

**Evaluación:** Snapshot de emergencia creado durante una sesión de debugging. El nombre sugiere que fue
un punto de rescate al commit `48ea382`. Tiene exactamente el mismo diff que `feature/financial-management`
vs main. La diferencia en `master_template_registry.py` es cosmética (docstring de ejemplo). No contiene
código de producción ausente en main (excluyendo `user_type`, decisión documentada más abajo).

**Decisión propuesta:** ✂️ ELIMINAR  
**Confirmación humana:** ✅ AUTORIZADA PARA ELIMINAR — 2026-05-20  
**Razón aceptada:** Rama de rescate/debug. `user_type` excluido intencionalmente (conflicto DocType nativo Frappe). Sin código ausente en main. Sin documentación útil única. Scripts legacy removidos deliberadamente.  
**Comando sugerido (no ejecutar todavía):**
```bash
git push origin --delete emergency/reset-to-48ea382
```

---

### 3. `origin/feature/audit-ux-testing-hallazgos-criticos`

| Campo | Valor |
|-------|-------|
| Tip commit | `ac94a9e` |
| Fecha último commit | 2026-01-23 |
| Commits únicos vs main | 2 |
| Diff vs main | 11 archivos, +2,262 / −517 líneas |

**Archivos únicos vs main:**
- `docs/audit/HALLAZGO-ROLES-SIN-FIXTURE.md` — Hallazgo crítico: 22 roles custom usados en
  permisos de DocTypes sin fixture que los defina. Incluye lista completa de roles y análisis
  de impacto en zero-config deployment.
- `docs/audit/REPORTE-UX-TESTING-2025-10-27.md` — Reporte completo de auditoría UX/UI: 9 hallazgos
  documentados (2 críticos, 4 altos, 3 medios), validación operativa del sistema.
- `ci.yml` sin `.disabled` — versión anterior del CI.

**Evaluación:** La única branch que tiene documentación de auditoría **no presente en main** y con
valor real para la migración. El hallazgo de roles sin fixture es directamente relevante: 22 roles
custom existen en la BD de dev pero no como fixtures, comprometiendo deployments limpios (incluyendo
v16). Esta información debe rescatarse antes de eliminar la branch.

**Decisión propuesta:** 📥 RESCATAR DOCUMENTACIÓN Y LUEGO REVISAR ELIMINACIÓN  
**Confirmación humana:** RESCATE AUTORIZADO — ELIMINACIÓN PENDIENTE — 2026-05-20  
**Confirmación humana:** ✅ AUTORIZADA PARA ELIMINAR — 2026-05-20  
**Razón:** Documentos únicos rescatados. Branch ya sin contenido único. El CI anterior restante no tiene valor vigente.  
**Documentos rescatados:**
- `docs/audit/hallazgo-roles-sin-fixture.md` ✅ (524 líneas)
- `docs/audit/reporte-ux-testing-2025-10-27.md` ✅ (892 líneas)  
**Comando sugerido (no ejecutar todavía):**
```bash
git push origin --delete feature/audit-ux-testing-hallazgos-criticos
```

---

### 4. `origin/feature/claude-memory-permanent-structure`

| Campo | Valor |
|-------|-------|
| Tip commit | `198cecf` |
| Fecha último commit | 2025-07-05 |
| Commits únicos vs main | 17 |
| Diff vs main | 647 archivos, +9,506 / −109,138 líneas |

**Archivos únicos:** Documentación de desarrollo (`ARCHITECTURE_MODULE_1_COMPANIES.md`,
`DEVELOPMENT_POLICIES.md`, `CHECKLIST_COMPLIANCE_TESTS.md`, etc.), `docs.backup/` con versiones
anteriores de docs, `docs/` con documentación de módulos, templates (`TEMPLATE_DOCTYPE_TEST.py`,
`TEMPLATE_MODULE_HOOKS.py`), scripts de diagnóstico. **Ningún archivo de producción de la app.**

**Evaluación:** Branch de documentación/templates de desarrollo. Toda la documentación aquí es
anterior y fue reemplazada por el CLAUDE.md reestructurado en PR #28. Los templates podrían tener
algún valor histórico pero no código funcional.

**Decisión propuesta:** ✂️ ELIMINAR  
**Confirmación humana:** ✅ AUTORIZADA PARA ELIMINAR — 2026-05-20  
**Razón:** Documentación operacional/Claude legacy supersedida. Sin contenido único vigente. ISSUE #7 ya cubierto por `issue7-hooks-universales-contexto.md`.  
**Comando sugerido (no ejecutar todavía):**
```bash
git push origin --delete feature/claude-memory-permanent-structure
```

---

### 5. `origin/feature/committee-management-clean`

| Campo | Valor |
|-------|-------|
| Tip commit | `1b5ade5` |
| Fecha último commit | 2025-07-12 |
| Commits únicos vs main | 48 |
| Diff vs main | 435 archivos, +4,508 / −82,351 líneas |

**Archivos únicos de código vs main:**
- `user_type` DocType (mismos archivos que en financial-management)
- `companies/custom_fields/company_custom_fields.py`
- `companies/install.py`
- `companies/test_company_customizations.py`

**No tiene** el código de Committee Management que no esté en main. El "clean" en el nombre se refiere
a una versión limpia durante el desarrollo, no a una versión más completa.

**Evaluación:** Snapshot histórico del desarrollo del módulo Committee Management + Companies.
Tiene 82,351 líneas menos que main — es sustancialmente menos completo. El único código diferencial
es `user_type` (excluido deliberadamente, ver abajo). La historia de 48 commits es el desarrollo
iterativo que ya fue squash-mergeado en main.

**Decisión propuesta:** 🔒 CONSERVAR TEMPORALMENTE / ARCHIVAR  
**Confirmación humana:** NO AUTORIZADA PARA ELIMINAR POR AHORA — 2026-05-20  
**Razón:** Conserva 48 commits de historia del desarrollo de Committee Management con valor de auditoría/trazabilidad. Mismo criterio aplicado a `origin/feature/financial-management`.  
**Acción propuesta posterior:** Mantener remota, o crear tag de archivo antes de eliminar:
```
archive/committee-management-pre-rewrite
```
**Comando sugerido (no ejecutar todavía):**
```bash
git push origin --delete feature/committee-management-clean
```

---

### 6. `origin/feature/community-contributions-cross-site`

| Campo | Valor |
|-------|-------|
| Tip commit | `fa6dd85` |
| Fecha último commit | 2025-07-06 |
| Commits únicos vs main | 18 |
| Diff vs main | 643 archivos, +10,003 / −107,611 líneas |

**Archivos únicos de código vs main:** Ninguno. El diff `comm -23` entre esta branch y origin/main
para archivos `.py` de producción no devuelve resultados.

**Evaluación:** Snapshot histórico del desarrollo del módulo Community Contributions. Tiene 107,611
líneas menos que main. No tiene ningún archivo de producción que no esté en main. La funcionalidad
cross-site ya está en main.

**Decisión propuesta:** ✂️ ELIMINAR  
**Confirmación humana:** ✅ AUTORIZADA PARA ELIMINAR — 2026-05-20  
**Razón:** Snapshot documental/operativo desactualizado. Sin código de producción único. Sin historia sustancial de desarrollo del módulo. Docs únicos son contexto operativo de julio 2025, desactualizados. No aplica criterio de conservación histórica de fm/committee.  
**Comando sugerido (no ejecutar todavía):**
```bash
git push origin --delete feature/community-contributions-cross-site
```

---

### 7. `origin/feature/document-generation-framework`

| Campo | Valor |
|-------|-------|
| Tip commit | `9a08397` |
| Fecha último commit | 2025-07-05 |
| Commits únicos vs main | 34 |
| Diff vs main | 642 archivos, +12,669 / −109,552 líneas |

**Archivos únicos vs main:** Un solo archivo:
`condominium_management/condominium_management/__init__.py` — directorio doblemente anidado, artefacto
de error de estructura (el directorio `condominium_management/condominium_management/` no debería
existir).

**Evaluación:** Snapshot histórico del desarrollo del Document Generation framework. Tiene 109,552
líneas menos que main. El único archivo "único" es un artefacto de error. El framework de Document
Generation ya está en main (con ISSUE #7 de hooks desactivados, documentado en ADR-0000).

**Decisión propuesta:** 📥 RESCATAR DOCUMENTACIÓN Y LUEGO REVISAR ELIMINACIÓN  
**Confirmación humana:** RESCATE AUTORIZADO — ELIMINACIÓN PENDIENTE — 2026-05-20  
**Razón:** Contenía `REPORTE_HOOKS_UNIVERSALES_Y_OPTIMIZACION.md`, reporte técnico relevante para ISSUE #7. Documento rescatado antes de eliminar.  
**Rescate ejecutado:** `REPORTE_HOOKS_UNIVERSALES_Y_OPTIMIZACION.md` → `docs/development/issue7-hooks-universales-contexto.md` ✅  
**Nota:** Renombrado para evitar patrón `REPORTE_*.md` en `.gitignore`.  
**Confirmación humana:** ✅ AUTORIZADA PARA ELIMINAR — 2026-05-20  
**Comando sugerido (no ejecutar todavía):**
```bash
git push origin --delete feature/document-generation-framework
```

---

### 8. `origin/feature/financial-management`

| Campo | Valor |
|-------|-------|
| Tip commit | `fabb991` |
| Fecha último commit | 2025-07-16 |
| Commits únicos vs main | 73 |
| Diff vs main | 273 archivos, +6,555 / −25,848 líneas |

**Archivos únicos vs main:**
- `user_type` DocType completo (JSON, Python, test, `__init__.py`)
- `condominium_management/fixtures/user_type.json` (4 registros: Administrador, Residente, Portero, Contador)
- `companies/custom_fields/company_custom_fields.py`
- `companies/install.py`
- `companies/test_company_customizations.py`
- ~30 scripts legacy en raíz del repo (removidos en PR #27)
- `bench_test.sh`, `comprehensive_test.sh`, etc.
- `.github/workflows/ci.yml` activo (vs `.disabled` en main)

**Evaluación:** El snapshot de desarrollo más reciente y completo de las feature branches. Tiene
25,848 líneas menos que main (main es más completo). El código diferencial clave es `user_type`
(ver sección dedicada). Los scripts legacy fueron removidos deliberadamente. La branch de 73 commits
representa la historia completa del módulo Financial Management antes del squash.

**Decisión propuesta:** 🔒 CONSERVAR TEMPORALMENTE / ARCHIVAR  
**Confirmación humana:** NO AUTORIZADA PARA ELIMINAR POR AHORA — 2026-05-20  
**Razón:** El código final parece consolidado en origin/main, pero la branch conserva historia detallada de desarrollo (73 commits) con valor de auditoría y trazabilidad. No eliminar hasta definir estrategia de archivo histórico.  
**Acción propuesta posterior:** Mantener remota, o crear tag de archivo antes de eliminar:
```
archive/financial-management-pre-rewrite
```
**Comando sugerido (no ejecutar todavía):**
```bash
git push origin --delete feature/financial-management
```

---

### 9. `origin/feature/financial-management-clean`

| Campo | Valor |
|-------|-------|
| Tip commit | `fabb991` ← **IDÉNTICO a financial-management** |
| Fecha último commit | 2025-07-16 |
| Commits únicos vs main | 73 |
| Diff vs main | idéntico a financial-management |

**Evaluación:** **Duplicado exacto** de `feature/financial-management`. Mismo tip commit `fabb991`,
mismo diff, misma historia. No aporta información adicional.

**Decisión propuesta:** ✂️ ELIMINAR  
**Confirmación humana:** ✅ AUTORIZADA PARA ELIMINAR — 2026-05-20  
**Razón:** Duplicado exacto de `origin/feature/financial-management` (mismo commit `fabb991`). Se conserva fm como archivo histórico; esta referencia es redundante.  
**Comando sugerido (no ejecutar todavía):**
```bash
git push origin --delete feature/financial-management-clean
```

---

### 10. `origin/feature/financial-management-rebase-experts`

| Campo | Valor |
|-------|-------|
| Tip commit | `67e4117` |
| Fecha último commit | 2025-07-16 |
| Commits únicos vs main | 73 |
| Diff vs main | 273 archivos, +6,555 / −25,848 líneas (idéntico a fm) |

**Evaluación:** Versión rebased de `feature/financial-management`. Misma fecha, misma cantidad de
commits, mismo diff vs main. Los commits tienen hashes distintos porque fueron rebaseados, pero el
contenido del árbol es equivalente.

**Decisión propuesta:** ✂️ ELIMINAR  
**Confirmación humana:** ✅ AUTORIZADA PARA ELIMINAR — 2026-05-20  
**Razón:** Versión rebased redundante de `origin/feature/financial-management`, sin contenido único. fm se conserva como archivo histórico.  
**Comando sugerido (no ejecutar todavía):**
```bash
git push origin --delete feature/financial-management-rebase-experts
```

---

### 11. `origin/feature/financial-management-reconstruction`

| Campo | Valor |
|-------|-------|
| Tip commit | `e1745ce` |
| Fecha último commit | 2025-07-16 |
| Commits únicos vs main | 21 |
| Diff vs main | 366 archivos, +5,757 / −68,925 líneas |

**Evaluación:** Intento temprano de reconstrucción del módulo Financial Management (el mensaje del
tip es "Financial Management Module iniciado - Property Account completo"). Mucho menos completo
que la branch `financial-management` y que main. 21 commits de una reconstrucción parcial que fue
superada por la branch principal.

**Decisión propuesta:** ✂️ ELIMINAR  
**Confirmación humana:** ✅ AUTORIZADA PARA ELIMINAR — 2026-05-20  
**Razón:** Reconstrucción temprana e incompleta (21 commits, solo Property Account). Cubierta en su totalidad por `origin/feature/financial-management` (73 commits). Sin documentación útil única. Artefactos en estructura incorrecta.  
**Comando sugerido (no ejecutar todavía):**
```bash
git push origin --delete feature/financial-management-reconstruction
```

---

### 12. `origin/feature/infra-setup` (branch actual de trabajo)

| Campo | Valor |
|-------|-------|
| Tip commit | `3a9f2cc` |
| Fecha último commit | 2026-04-30 |
| Commits únicos vs main | 5 |
| Diff vs main | 0 archivos únicos en ninguna dirección |

**Evaluación:** Es la branch de trabajo actual (HEAD). Sus 5 commits fueron squash-mergeados en
`origin/main` como PR #28 (commit `e0676aa`). Los archivos son idénticos entre esta branch y
`origin/main` — el squash-merge logró paridad de contenido. La razón de que `git merge-base
--is-ancestor` devuelva NO es que un squash-merge no establece relación de ancestro con los
commits individuales.

Esta branch no tiene archivos únicos respecto a main y no tiene archivos faltantes. Es efectivamente
una copia del contenido de main con otra historia de commits.

**Decisión propuesta:** 🔒 CONSERVAR TEMPORALMENTE — es la branch de trabajo activa.
Eliminar después de que el PR con el ADR-0001 sea mergeado a main.  
**Comando sugerido (no ejecutar todavía):**
```bash
git push origin --delete feature/infra-setup
```

---

## Branches locales sin remote

Estas branches existen solo en el repositorio local. No están en origin.

| Branch local | Fecha | Evidencia | Decisión propuesta |
|-------------|-------|-----------|-------------------|
| `feature/access-control` | 2025-06-27 | Mismo tip que develop (`4ec3b27`) — scaffold inicial | ✂️ Eliminar local |
| `feature/companies-module` | 2025-06-27 | Mismo tip que develop | ✂️ Eliminar local |
| `feature/physical-spaces` | 2025-06-27 | Mismo tip que develop | ✂️ Eliminar local |
| `hotfix/critical-bug-fix` | 2025-06-27 | Mismo tip que develop | ✂️ Eliminar local |
| `release/v1.0.0` | 2025-06-27 | Mismo tip que develop | ✂️ Eliminar local |
| `fix/module-structure-standardization` | 2025-06-30 | "agregar template bug report" | 👁 Revisar antes de eliminar |
| `feature/hooks-framework-implementation` | 2025-07-04 | "implementar framework completo" (#6) | 👁 Revisar: posible código de hooks no en main |
| `feature/financial-management-fixed` | 2025-07-13 | "Dashboard Consolidado completo" (#20) | 👁 Revisar: posible código de dashboard |
| `feature/audit-reportes-pendientes-revision` | 2025-10-29 | "auditoría UX/UI sistema completo - 9 hallazgos" — **mismo contenido que audit-ux-testing** | 📥 Rescatar docs → eliminar local |

---

## El caso `user_type` DocType

### Qué es

DocType `User Type` en módulo Companies, con 7 campos:
`user_type_name`, `can_access_admin`, `can_manage_policies`, `can_manage_complaints`,
`can_manage_finances`, `can_view_reports`, `is_active`.

Fixture con 4 registros: Administrador, Residente, Portero, Contador.

Lógica de controller: validaciones de permisos, prevención de rename/delete si hay User Profiles
usando el tipo.

### Por qué no está en origin/main

El hooks.py de `origin/main` lo documenta explícitamente:

```python
# "User Type",  # ❌ ELIMINADO (2025-10-26) - DocType legacy que hacía override incorrecto de Frappe core
#               # Sin implementación real (0 referencias código), conflicto arquitectónico (duplica Roles)
#               # DocType nativo Frappe restaurado. Ver commit para detalles completos.
```

### Conclusión

**Eliminado deliberadamente el 2025-10-26** por conflicto con el DocType nativo de Frappe llamado
también "User Type". No es código perdido por el rewrite — fue una decisión arquitectónica documentada.
Los 4 registros del fixture (Administrador, Residente, Portero, Contador) deberían modelarse como
Roles de Frappe, no como un DocType propio.

**Acción recomendada:** Documentar como excluido. No rescatar. Los perfiles de usuario del sistema
deben implementarse via Roles de Frappe (relevante para la migración v16).

---

## Hallazgo crítico adicional: 22 roles sin fixture

Identificado en `feature/audit-ux-testing-hallazgos-criticos` (`HALLAZGO-ROLES-SIN-FIXTURE.md`,
2025-10-27). **22 roles custom** son usados en permisos de DocTypes en `origin/main` pero
**no existe un fixture de Roles** que los defina:

```
Administrador Financiero, Administrator Condominio, API Manager, API User,
Assembly Participant, Comité Administración, Committee Member, Committee President,
Committee Secretary, Company Administrator, Condominium Manager, Condómino,
Configuration Approver, Configuration Manager, Contador Condominio, Event Organizer,
Gestor de Dashboards, Master Template Manager, Property Administrator,
Property Manager, Residente Propietario, Usuario de Dashboards
```

Estos roles existen en la BD de `admin1.dev` pero no están en code. Cualquier instalación
nueva (incluyendo v16) quedará con DocTypes que referencian roles inexistentes.

**Impacto para migración v16:** BLOQUEANTE. Antes de instalar en v16, se necesita crear un
fixture de Roles.

---

## Clasificación para eliminación por lote

Aplicando las 10 condiciones obligatorias. Una sola falla descalifica del lote.
Criterio adicional: `develop` y `main` nunca entran al lote por convención semántica,
independientemente de su contenido técnico.

### GRUPO A — Autorizables en lote

**Vacío.** Ninguna branch remota cumple las 10 condiciones en este momento.

Razón: Todas las branches restantes tienen al menos uno de estos problemas:
- DocType `user_type` + fixture ausentes en main (condición #2)
- Documentación potencialmente útil no rescatada (condición #3)
- Son ramas semánticas o activas que no entran al lote por convención

### GRUPO B — Requieren revisión 1×1

| Branch | Condición que falla | Razón de la falla |
|--------|-------------------|------------------|
| `origin/emergency/reset-to-48ea382` | #2 | `user_type` DocType + fixture ausentes en main |
| `origin/feature/audit-ux-testing-hallazgos-criticos` | #3 | 2 docs de auditoría no en main (HALLAZGO-ROLES-SIN-FIXTURE.md, REPORTE-UX-TESTING-2025-10-27.md) |
| `origin/feature/claude-memory-permanent-structure` | #3 | Docs operacionales no en main (MODULE_STATUS.md, TROUBLESHOOTING_CI.md, HOOKS_CONFIG.md, INFORMACION_CONTEXTO_CRITICA.md, PENDING_FUNCTIONALITY_ISSUE.md) |
| `origin/feature/committee-management-clean` | #2 | `user_type` DocType + fixture ausentes en main |
| `origin/feature/community-contributions-cross-site` | #3 | Docs no en main (INFORMACION_CONTEXTO_CRITICA.md, PENDING_FUNCTIONALITY_ISSUE.md, GITHUB_WORKFLOW_LESSONS.md, MODULE_STATUS.md) |
| `origin/feature/document-generation-framework` | #3 | Docs no en main incluyendo REPORTE_HOOKS_UNIVERSALES_Y_OPTIMIZACION.md (relevante ISSUE #7) y DISEÑO_ARQUITECTURA_CROSS_SITE.md |
| `origin/feature/financial-management` | #2 | `user_type` DocType + fixture ausentes en main |
| `origin/feature/financial-management-clean` | #2 | Duplicado exacto de financial-management — misma falla |
| `origin/feature/financial-management-rebase-experts` | #2 | Rebased de financial-management — misma falla |
| `origin/feature/financial-management-reconstruction` | #2 | `user_type` DocType + fixture ausentes en main |

### GRUPO C — No eliminar por ahora

| Branch | Razón |
|--------|-------|
| `origin/develop` | Rama semántica de desarrollo. No se elimina por lote. Requiere decisión explícita posterior sobre estrategia de ramas |
| `origin/feature/infra-setup` | Branch activa de trabajo actual |

---

## Resumen de decisiones

### Branches remotas

| Branch | Grupo | Estado | Razón |
|--------|-------|--------|-------|
| `origin/develop` | **C** | 🔒 NO ELIMINAR — congelada | Rama semántica; decisión estratégica pendiente |
| `origin/emergency/reset-to-48ea382` | B | ✅ AUTORIZADA PARA ELIMINAR | Rama de rescate/debug. `user_type` excluido intencionalmente. Sin código ausente en main. |
| `origin/feature/audit-ux-testing-hallazgos-criticos` | B | ✅ AUTORIZADA PARA ELIMINAR | Rescate completo: hallazgo-roles-sin-fixture.md y reporte-ux-testing en docs/audit/. |
| `origin/feature/claude-memory-permanent-structure` | B | ✅ AUTORIZADA PARA ELIMINAR | Docs operacionales legacy supersedidos. ISSUE #7 cubierto por issue7-hooks-universales-contexto.md. |
| `origin/feature/committee-management-clean` | B | 🔒 CONSERVAR TEMPORALMENTE | 48 commits historia Committee Management. Mismo criterio que fm. |
| `origin/feature/community-contributions-cross-site` | B | ✅ AUTORIZADA PARA ELIMINAR | Sin código único ni historia sustancial. Docs desactualizados. |
| `origin/feature/document-generation-framework` | B | ✅ AUTORIZADA PARA ELIMINAR | Rescate completo: issue7-hooks-universales-contexto.md en docs/development/. |
| `origin/feature/financial-management` | B | 🔒 CONSERVAR TEMPORALMENTE | Historia de 73 commits con valor de auditoría. Pendiente estrategia de archivo histórico. |
| `origin/feature/financial-management-clean` | B | ✅ AUTORIZADA PARA ELIMINAR | Duplicado exacto de fm (mismo commit). fm se conserva como archivo histórico. |
| `origin/feature/financial-management-rebase-experts` | B | ✅ AUTORIZADA PARA ELIMINAR | Versión rebased redundante de fm. Sin contenido único. |
| `origin/feature/financial-management-reconstruction` | B | ✅ AUTORIZADA PARA ELIMINAR | Reconstrucción temprana incompleta, cubierta por fm (73 commits). |
| `origin/feature/infra-setup` | C | 🔒 Conservar | Branch activa de trabajo |

### Branches locales (todas pendientes de revisión 1×1)

| Branch local | Estado |
|-------------|--------|
| `feature/access-control` | 👁 Revisión 1×1 pendiente |
| `feature/companies-module` | 👁 Revisión 1×1 pendiente |
| `feature/physical-spaces` | 👁 Revisión 1×1 pendiente |
| `hotfix/critical-bug-fix` | 👁 Revisión 1×1 pendiente |
| `release/v1.0.0` | 👁 Revisión 1×1 pendiente |
| `fix/module-structure-standardization` | 👁 Revisión 1×1 pendiente |
| `feature/hooks-framework-implementation` | 👁 Revisión 1×1 pendiente |
| `feature/financial-management-fixed` | 👁 Revisión 1×1 pendiente |
| `feature/audit-reportes-pendientes-revision` | 👁 Revisión 1×1 pendiente |

---

## Branches que NO deben borrarse todavía

1. **`origin/develop`** — rama semántica congelada; decisión estratégica pendiente.
2. **`origin/feature/infra-setup`** — branch de trabajo activa.
3. ~~`origin/feature/audit-ux-testing-hallazgos-criticos`~~ — autorizada para eliminar. Rescate completo.
4. **`origin/emergency/reset-to-48ea382`** y todas las branches con `user_type` — pendiente decisión 1×1.
5. Todas las branches locales — pendiente revisión 1×1.

---

## Riesgos abiertos

| Riesgo | Severidad | Estado |
|--------|-----------|--------|
| 22 roles sin fixture | **CRÍTICO** | No resuelto — bloqueante para v16 |
| `user_type` DocType excluido deliberadamente | RESUELTO | Documentado como excluido (conflicto Frappe core) |
| Branches locales sin revisar (`hooks-framework`, `financial-fixed`) | MEDIO | Pendiente revisión manual |
| `feature/audit-ux-testing` docs no en main | MEDIO | Rescatar antes de eliminar |
| CI desactivado | ALTO | Documentado en ADR-0000, se resolverá en migración |
| `layer4_complex_tests_backup/` en raíz del repo | BAJO | Directorio huérfano no commiteado, eliminar |

---

## Próximo paso recomendado

**Antes de cualquier eliminación de branches:**

1. Confirmar decisión sobre `user_type` — ✅ Documentada como excluida (no rescatar)
2. Rescatar docs de `feature/audit-ux-testing-hallazgos-criticos` → copiar a `docs/audit/` en esta branch
3. Revisar branches locales `feature/hooks-framework-implementation` y `feature/financial-management-fixed`
4. Obtener autorización explícita para eliminación de cada grupo de branches
5. Crear fixture de Roles (22 roles) — puede ser un PR independiente antes de la migración

**Después de las eliminaciones:**

6. Pull `origin/main` para sincronizar local main
7. Crear `feature/migration-v16` desde `origin/main`

---

## Mensaje de commit propuesto para este ADR

```
docs: add branch reconciliation ADR (ADR-0001) pre-v16 migration

Documents 1x1 analysis of 12 remote branches and 9 local-only branches.
Confirms origin/main (e0676aa) as migration baseline.
Identifies critical gap: 22 custom roles used in DocType permissions
without Role fixture — blocker for clean v16 deployment.
Documents user_type exclusion as intentional (Frappe core conflict).
```
