# CONTINUITY.md — condominium_management

**Fecha:** 2026-05-27
**Rama activa:** `feature/docs-new-workflow`
**Tarea actual:** Space Category v1 implementado — commit autorizado, pendiente push + PR

---

## Recuperación rápida

Estoy trabajando en:
Space Category v1 como catálogo de sistema controlado (Capa 1: permisos + allow_rename=0).
El commit incluye 51 fixtures, 8 category_types, permisos read-only para System Manager.

Plan que estoy siguiendo:
Autorización explícita del usuario en sesión 2026-05-27. Sin issue ni ADR formal — decisiones en CONTINUITY.

Objetivo inmediato:
Revisión documental de Physical Spaces (siguiente tarea después del commit).

Criterio de avance:
PR `feature/docs-new-workflow` → `main` mergeado con Space Category v1 incluido.

---

## Estado actual

### Ya cerrado
- Setup wizard condo-v16.dev ✅
- Bug Company Type IDs corregido ✅
- docs_new/ creado: instalacion-y-configuracion.md, hooks.md, fixtures.md, arquitectura.md ✅
- Diagnóstico multi-company completo ✅
- Space Category v1 Capa 1 implementada: 5 archivos, 7/7 tests OK ✅

### En progreso
- PR `feature/docs-new-workflow` → `main` (pendiente push + apertura)

### Pendiente inmediato
1. Push de `feature/docs-new-workflow`
2. Crear PR `feature/docs-new-workflow` → `main`
3. Validar Space Category con usuario no-Administrator: confirmar que es solo lectura
4. Si no queda bloqueado con Capa 1 → diseñar Capa 2 (before_save guard sin romper fixture import)
5. Revisión documental de Physical Spaces

### No repetir
- No reactivar hooks universales (ISSUE #7) sin análisis
- No reiniciar servidor fuera de `/server-restart`
- No mover `insert_after` de `company_type`
- No intentar diagnosticar con SQL directo — usar `bench execute`
- No commitear one_offs/

---

## Decisiones vigentes
- Space Category = catálogo controlado del sistema. Usuarios no pueden crear/editar registros.
- Capa 2 (before_save guard) diferida: evidencia requerida antes de autorizar.
  Flags confirmados activos durante migrate: `frappe.flags.in_fixtures`, `frappe.flags.in_import`.
  Validate hooks SÍ corren durante fixture loading (data_import=True no suprime validate).
- Administrator bypassa permisos nativamente — no necesita bloque explícito en DocType JSON.
- `company_type.insert_after = "reporting_currency"` — no cambiar
- `docs_new/` se construye progresivamente
- `one_offs/` nunca se commitea
- Condominium Information: diferida hasta caso de uso real
- ISSUE #7 (hooks universales): no reactivar sin análisis

---

## Archivos relevantes ahora

### Leer primero
- `physical_spaces/doctype/space_category/space_category.json` — DocType con Capa 1
- `fixtures/space_category.json` — 51 registros del catálogo

### Probablemente editar
- `physical_spaces/doctype/space_category/space_category.py` — si se autoriza Capa 2
- `CONTINUITY.md` — tras PR mergeado

### No tocar
- `hooks.py` líneas ~190-198 — hooks universales comentados (ISSUE #7)
- Sites v15 (`admin1.dev`, etc.)
- `test-condominium.localhost` — solo para tests

---

## Riesgos / cuidados
- Space Category Capa 1 NO bloquea a Administrator en GUI — validación pendiente con usuario funcional
- `bench migrate` aplica custom_field.json al site — no revertir sin migrate
- ISSUE #7 sigue sin resolver

---

## Información faltante
- Verificar DocTypes de Committee Management sin company confirmada (Poll, Agreement Tracking, Community Event, Voting System)
- Resultado de validación GUI de Space Category con usuario no-Administrator
