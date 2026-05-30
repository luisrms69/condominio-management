# CONTINUITY.md — condominium_management

**Fecha:** 2026-05-30
**Rama activa:** `fix/billing-cycle-field-references`
**Tarea actual:** Commit de Physical Space fixes — financial_management rechazado y en pausa

---

## Recuperación rápida

Estoy trabajando en:
Correcciones de Physical Space (space_code, space_level, referencias de jerarquía).
El bloque financiero fue detenido por rechazo arquitectónico del diseño actual.

Plan que estoy siguiendo:
Auditoría histórica del app completada esta sesión. Ver decisiones vigentes abajo.

Objetivo inmediato:
Hacer PR de los cambios de Physical Space. Luego decidir qué hacer con financial_management.

Criterio de avance:
PR abierto con solo cambios de Physical Spaces + financial_management sin tocar.

---

## Estado actual

### Ya cerrado
- PR #35: Property Registry limpio + Property Declared Owner ✅
- Physical Space: space_code read_only, space_level hidden, building/floor/zone hidden, código consecutivo `<abbr>-####` ✅
- Validación GUI Physical Space completada en condo-v16.dev ✅

### En progreso
- Commit de Physical Space fixes (en curso)

### Pendiente inmediato
1. PR de Physical Space fixes
2. Decisión arquitectónica sobre financial_management (requiere documento de diseño aprobado)
3. Limpiar rama: los archivos de financial_management modificados en esta rama deben revertirse o moverse

### No repetir
- No commitear financial_management sin documento de arquitectura aprobado primero
- No parchear financial_management con fieldnames sin resolver el diseño de Property Account
- No DROP TABLE tabProperty Copropiedad sin autorización
- No reactivar ISSUE #7 (hooks universales)
- No commitear one_offs/

---

## Decisiones vigentes
- Financial Management rechazado arquitectónicamente. Property Account tiene current_balance manual (reqd=1), billing config por cuenta, sistema paralelo a ERPNext. No se toca hasta tener documento de rediseño.
- Physical Space: NO es Tree DocType (decisión explícita — permite jerarquía libre). space_code = document name via make_autoname por company abbr.
- building_reference / floor_reference / zone_reference: ocultos y read_only. No se auto-calculan en MVP. Decisión: calcular desde jerarquía cuando haya caso de uso real.
- Fee Structure (financial): diseño correcto, conservar.
- billing_cycle.py y fee_structure.py tienen referencias a campos inexistentes — deuda conocida, no tocar hasta rediseño.

---

## Archivos relevantes ahora

### Leer primero
- `docs_new/tecnico/deuda-tecnica.md` — deuda técnica registrada
- `condominium_management/financial_management/` — modificaciones rechazadas pendientes de revertir

### Probablemente editar
- `CONTINUITY.md` — al iniciar próxima tarea

### No tocar
- `hooks.py` líneas ~190-198 — ISSUE #7
- `financial_management/doctype/billing_cycle/` y `fee_structure/` — deuda de fieldnames
- `financial_management/doctype/property_account/` — diseño rechazado

---

## Riesgos / cuidados
- La rama tiene modificaciones de financial_management que NO deben ir a PR. Deben revertirse antes de abrir PR.
- `tabProperty Copropiedad` en BD: conservar hasta validación post-PR.

---

## Información faltante
- Decisión: ¿se revierte financial_management en esta rama o se crea branch separado para el rediseño?
