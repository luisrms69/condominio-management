# Documento de Continuidad — condominium_management

**Fecha:** 2026-05-26
**Sesión:** Retoma de desarrollo post-campaña de tests v16

---

## Qué es este app

`condominium_management` es una app Frappe/ERPNext para administración de condominios.
Gestiona propiedades, finanzas (cuotas, facturación automática, multas), espacios físicos,
comités, asambleas y contribuciones entre sitios (arquitectura multi-site).

**Repositorio:** https://github.com/luisrms69/condominio-management
**Branch activo:** `main`
**Versión:** 0.0.1 — en desarrollo activo, no en producción

---

## Estado actual

| Ítem | Estado |
|---|---|
| `condo-v16.dev` | ✅ frappe 16.18.2 + erpnext 16.18.3 + condominium_management 0.0.1 |
| `bench migrate` en condo-v16.dev | ✅ Limpio |
| Setup wizard en condo-v16.dev | ✅ Completado — `CONDOV16/CV16`, MXN, Mexico, `setup_complete=1` |
| `test-condominium.localhost` | ✅ Creado y funcional con `allow_tests: true` |
| Seed en test site | ✅ `_Test Company` (_TC, México, MXN) como `default_company` en Global Defaults |
| Tests Financial Management | ✅ 458/458 OK — 9 skipped (database_schema deuda técnica) |
| Tests Physical Spaces | ✅ 31/31 OK |
| Tests Companies | ✅ 80/80 OK |
| Tests Committee Management | ✅ 126/126 OK |
| Tests API Documentation System | ✅ 23/23 OK — 4 skipped |
| Tests Community Contributions | ✅ 23/23 OK |
| Tests Dashboard Consolidado | ✅ 40/40 OK |
| Tests Document Generation | ✅ 21/21 OK — ISSUE #7 como deuda funcional post-migración |
| **Avance migración v16** | **97%** |

---

## PRs mergeados en main

| PR | Descripción |
|---|---|
| #29 | ADRs y documentos rescatados de branches históricas |
| #30 | Fixture de 22 roles custom |
| #31 | Filtros explícitos para evitar contaminación de fixture export |
| #32 | Infraestructura Claude v16 (CLAUDE.md, CONTINUITY.md, .claude/commands symlink) |
| #33 | Fix: `country` en setUp de tests Physical Spaces para ERPNext v16 (commit `2ef88cd`) |

---

## Campaña de tests — cierre (802 OK / 75 skipped / 0 errores)

### Financial Management — 458/458 OK, 9 skipped

| Nivel | Tests | Skipped | Estado |
|---|---|---|---|
| L1 field validation | 107 | 0 | ✅ |
| L2 business logic | 130 | 0 | ✅ |
| L3 integration | 152 | 0 | ✅ |
| L4 real (59 archivos) | 59 | 9 | ✅ |
| L4 Type C (10 archivos) | 10 | 0 | ✅ |

Excluidos deliberadamente: `credit_balance_management_l4_database_schema` (SQL con nombre de tabla en minúsculas) + 63 Type B ficticios/simulados.

### Physical Spaces — 31/31 OK

| Archivo | Tests | Estado |
|---|---|---|
| `test_space_category` | 7 | ✅ |
| `test_component_type` | 10 | ✅ |
| `test_physical_space` | 6 | ✅ |
| `test_space_component` | 8 | ✅ |

DocTypes sin tests: `allowed_child_category`, `allowed_parent_category`.

### Companies — 80/80 OK

Hooks activos sobre DocType `Company` de ERPNext (`company_hooks.py`). 27 custom fields validados.
Sin skipped. Integración con ERPNext v16 sin regresiones.

### Committee Management — 126/126 OK

| Grupo | Tests | Estado |
|---|---|---|
| Grupo A | ~42 | ✅ |
| Grupo B | ~42 | ✅ |
| Grupo C | ~42 | ✅ |

Usa `CommitteeTestBase(FrappeTestCase)` con usuario `CTEST_committee@example.com` y 4 roles en español.
2 tests con `@unittest.skip` por PR #24 (Acquisition Type fixture desactivado) — no cuentan en OK/skipped.

### API Documentation System — 23/23 OK, 4 skipped

| Archivo | Tests | Skipped | Estado |
|---|---|---|---|
| `test_api_documentation` | ~12 | 4 | ✅ |
| `test_auto_documentation` | ~11 | 0 | ✅ |

### Community Contributions — 23/23 OK

| Archivo | Tests | Estado |
|---|---|---|
| `test_contribution_category` | 7 | ✅ |
| `test_contribution_request` | 7 | ✅ |
| `test_registered_contributor_site` | 9 | ✅ |

Residuales permanentes: 12+ empresas de prueba, `test@example.com`, ~33 Contribution Categories.
Originados por `frappe.db.commit()` en `TestDataFactory.create_contribution_category()`.

### Dashboard Consolidado — 40/40 OK

| Archivo | Tests | Estado |
|---|---|---|
| `test_base` (DashboardTestBaseGranular) | ~4 | ✅ |
| `test_dashboard_configuration` | ~13 | ✅ |
| `test_kpi_definition` | ~15 | ✅ |

Usa `DashboardTestBase(unittest.TestCase)` — rollback manual en tearDown, sin `frappe.db.commit()`.

### Document Generation — 21/21 OK

| Archivo | Tests | Estado |
|---|---|---|
| `test_entity_type_configuration` | 5 | ✅ |
| `test_entity_configuration` | 6 | ✅ |
| `test_master_template_registry` | 10 | ✅ |

Tests cubren CRUD y validaciones de campos. **ISSUE #7 no bloquea estos tests.**
`Master Template Registry` (Single DocType) tiene residuales post-test: 3 infra templates,
3 auto assignment rules, `update_propagation_status = "En Progreso"`.

---

## Issues técnicos pendientes / deuda post-migración

| # | Descripción | Prioridad | Acción recomendada |
|---|---|---|---|
| I-1 | `_l4_database_schema` de FM usan `DESCRIBE \`tab{lowercase}\`` → 9 skipean | Media | Corregir nombre de tabla en 10 archivos |
| I-2 | `credit_balance_management_l4_database_schema` — mismo problema | Media | Incluir en fix de I-1 |
| I-3 | 63 archivos Type B simulados/ficticios inflan conteo CI | Baja | Decisión: eliminar, mover o marcar skip explícito |
| **I-4** | **ISSUE #7 — Hooks universales desactivados** en `hooks.py` líneas 190-198 | **Alta** | **Análisis y reactivación controlada — no tocar sin plan** |
| I-5 | `Master Template Registry` singleton con residuales post-test | Baja | Limpiar antes de fixture export |
| I-6 | PR #33 abierto sin mergear (`feature/fix-physical-spaces-tests-v16`) | Media | Mergear cuando esté listo |

---

## Qué NO tocar

| Qué | Por qué |
|---|---|
| `admin1.dev` y sites v15 | Entorno de producción en desarrollo — no modificar BD |
| ISSUE #7 — hooks universales | `hooks.py` líneas 190-198 comentados — no reactivar sin análisis |
| Registro `User` en Entity Type Configuration | Decisión pendiente — no eliminar sin autorización |
| 55 registros de test en BD v15 | Limpieza pendiente con backup previo |
| `master_template_registry.last_update` | Campo volátil — puede contaminar fixtures |
| BD de cualquier site | Ningún `UPDATE`/`INSERT`/`DELETE` sin autorización explícita |

---

## Workflow documental vigente (desde 2026-05-26)

**Decisión:** No se reorganiza `docs/` con movimientos masivos.
Se construye `docs_new/` como destino de documentación validada.

Regla: un fragmento pasa a `docs_new/` solo cuando:
1. fue encontrado en `docs/` (o identificado como faltante),
2. fue revisado contra el estado real del app,
3. fue validado durante una tarea real ejecutada.

Ver `docs_new/README.md` para el workflow completo y la estructura destino.

---

## Próximos pasos post-migración

La campaña de tests v16 está completa. Los pasos siguientes son de calidad y funcionalidad:

1. **Configurar condo-v16.dev** — setup wizard + Company inicial + datos mínimos. ← wizard ✅, datos mínimos pendiente
2. **Resolver I-1/I-2** — corregir nombres de tabla en 10 archivos `_l4_database_schema`.
3. **Decidir I-3** — 63 archivos Type B ficticios: eliminar o marcar con skip explícito.
4. **Analizar ISSUE #7** — plan para reactivar hooks universales de Document Generation sin romper el setup wizard de ERPNext.
5. **Expandir fixtures** — 72 de 85 DocTypes sin fixtures; instalación nueva queda incompleta.

---

## Cómo ponerte al tanto — leer en este orden

```
1. /home/erpnext/Developer/frappe-infrastructure/.claude/CLAUDE.md  ← reglas globales del ecosistema
2. /home/erpnext/frappe-bench-v16/.claude/CLAUDE.md                 ← contexto del bench v16
3. /home/erpnext/frappe-bench-v16/apps/condominium_management/CLAUDE.md  ← este app
4. Este archivo: CONTINUITY.md
5. PRs recientes: gh pr list --state all --limit 10
```

---

## Comandos frecuentes

```bash
# Tests (site autorizado)
bench --site test-condominium.localhost run-tests --module <MODULE> --lightmode

# Desarrollo
bench --site condo-v16.dev migrate
bench --site condo-v16.dev export-fixtures --app condominium_management
bench build --app condominium_management

# Diagnóstico (read-only)
bench --site test-condominium.localhost list-apps
bench list-sites
```
