# Documento de Continuidad — condominium_management

**Fecha:** 2026-05-24
**Sesión:** Campaña de tests v16 — Financial Management + Physical Spaces completados

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
| `test-condominium.localhost` | ✅ Creado y funcional con `allow_tests: true` |
| Seed en test site | ✅ Warehouse Types (Transit, Finished Goods, Raw Material, Work In Progress) + `_Test Company` (_TC, México, MXN) |
| Tests Financial Management | ✅ 458/458 OK (L1+L2+L3+L4 real+L4 TypeC), 9 skipped (database_schema deuda técnica) |
| Tests Physical Spaces | ✅ 31/31 OK — todos los 4 DocTypes con tests cubiertos |
| Tests Committee Management | ⏳ Pendiente |
| Tests Companies | ⏳ Pendiente |
| Tests Document Generation | ⏳ Pendiente |
| Tests Dashboard Consolidado | ⏳ Pendiente |
| Tests Community Contributions | ⏳ Pendiente |
| Tests API Documentation System | ⏳ Pendiente |

---

## PRs mergeados en main

| PR | Descripción |
|---|---|
| #29 | ADRs y documentos rescatados de branches históricas |
| #30 | Fixture de 22 roles custom |
| #31 | Filtros explícitos para evitar contaminación de fixture export |
| #32 | Infraestructura Claude v16 (CLAUDE.md, CONTINUITY.md, .claude/commands symlink) |

## PR abierto — pendiente de merge

| PR | Branch | Descripción |
|---|---|---|
| #33 (abierto) | `feature/fix-physical-spaces-tests-v16` | Fix: `country` en setUp de tests Physical Spaces para ERPNext v16 |

---

## Campaña de tests completada

### Financial Management — 458/458 OK

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

---

## Issues técnicos pendientes / deuda de testing

| # | Descripción | Acción recomendada |
|---|---|---|
| I-1 | Todos los `_l4_database_schema` de FM usan `DESCRIBE \`tab{lowercase}\`` → skipean universalmente | Corregir nombre de tabla en 10 archivos |
| I-2 | `credit_balance_management_l4_database_schema` — mismo problema, excluido explícitamente | Incluir en fix de I-1 |
| I-3 | 63 archivos Type B simulados/ficticios existen en repo e inflan conteo CI | Decisión: eliminar, mover o marcar skip explícito |

---

## Qué NO tocar

| Qué | Por qué |
|---|---|
| `admin1.dev` y sites v15 | Entorno de producción en desarrollo — no modificar BD |
| ISSUE #7 — hooks universales | `hooks.py` líneas 190-198 comentados por razón documentada |
| Registro `User` en Entity Type Configuration | Decisión pendiente — no eliminar sin autorización |
| 55 registros de test en BD v15 | Limpieza pendiente con backup previo |
| `master_template_registry.last_update` | Campo volátil — puede contaminar fixtures |
| BD de cualquier site | Ningún `UPDATE`/`INSERT`/`DELETE` sin autorización explícita |

---

## Próximo paso recomendado

**Siguiente módulo recomendado: Companies o Committee Management.**

- **Companies** (23 DocTypes): alto valor — involucra custom fields sobre el DocType `Company` de ERPNext y hooks activos en `company_hooks.py`. Validar que la integración con ERPNext v16 no introdujo regresiones.
- **Committee Management** (21 DocTypes, el más grande): conviene inventariar sus archivos de test antes de iniciar, para estimar el esfuerzo y detectar dependencias.

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
