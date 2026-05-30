# CONTINUITY.md — condominium_management

**Fecha:** 2026-05-29
**Rama activa:** `feature/docs-new-workflow`
**Tarea actual:** Ejecutando /ship commit — dos commits separados en progreso

---

## Recuperación rápida

Estoy trabajando en:
Cierre de la implementación de Property Declared Owner + limpieza de Property Registry.
Dos commits listos para ejecutar, luego PR hacia main.

Plan que estoy siguiendo:
`docs_new/arquitectura/property_registry_ownership_mvp.md` — v1.1 ya actualizado.

Objetivo inmediato:
Ejecutar commit 1 (Property Registry / Declared Owner) → commit 2 (Property Account) → PR.

Criterio de avance:
Dos commits creados + git status limpio + PR abierto.

---

## Estado actual

### Ya cerrado
- Space Category v1 + docs Physical Spaces commiteados (`b1f62e3`) ✅
- Property Declared Owner implementado (rename completo desde Property Copropiedad) ✅
- Property Registry limpio (23 campos obsoletos eliminados) ✅
- Patches: `remove_property_registry_deprecated_fields` + `migrate_property_copropiedad_to_declared_owner` ✅
- bench migrate limpio en test-condominium.localhost y condo-v16.dev ✅
- Tests: 4/4 + 12/12 + 11/11 OK post-linter ✅
- Validación GUI completada en condo-v16.dev ✅

### En progreso
- /ship commit — preparando commit 1 y commit 2

### Pendiente inmediato
1. Commit 1: `feat(companies): implement declared owners and clean property registry`
2. Commit 2: `feat(financial): add billing relationship type to property account`
3. PR hacia main

### No repetir
- No hacer DROP TABLE tabProperty Copropiedad hasta validar PR mergeado
- No reactivar ISSUE #7 (hooks universales)
- No agregar tower/floor/unit_number a Property Registry
- No commitear one_offs/
- No tocar Billing Cycle / Fee Structure (tienen deuda de ownership_percentage preexistente)

---

## Decisiones vigentes
- Property Registry = expediente de unidad privativa. Dirección/compliance/seguros → Company.
- `tabProperty Copropiedad` conservada como respaldo hasta PR mergeado — sin DROP todavía.
- `total_copropiedades_percentage` sigue en BD como columna legacy; `current_owners_total_percentage` es la activa.
- Tests usan `UnitTestCase` / `IntegrationTestCase` (Frappe 16) — no `FrappeTestCase` deprecado.
- `billing_cycle.py:382` y `fee_structure.py:201` leen `ownership_percentage`/`area_sqm` inexistentes — deuda preexistente, fuera de alcance.

---

## Archivos relevantes ahora

### Leer primero
- `docs_new/arquitectura/property_registry_ownership_mvp.md` — decisiones v1.1

### Probablemente editar
- `CONTINUITY.md` — post-PR

### No tocar
- `hooks.py` líneas ~190-198 — ISSUE #7
- `financial_management/doctype/billing_cycle/` y `fee_structure/`
- Sites v15

---

## Riesgos / cuidados
- `billing_cycle.py:382` y `fee_structure.py:201` fallarán cuando se active cálculo real de cuotas.
- Space Category Capa 1: validación con usuario no-Administrator aún pendiente.

---

## Información faltante
- Número de PR (aún no creado)
