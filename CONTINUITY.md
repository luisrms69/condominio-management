# CONTINUITY.md — condominium_management

**Fecha:** 2026-05-27
**Rama activa:** `feature/docs-new-workflow`
**Tarea actual:** Documentación Physical Spaces v1 commiteada — pendiente push + PR

---

## Recuperación rápida

Estoy trabajando en:
Cierre de la rama `feature/docs-new-workflow` para PR a `main`.
Incluye: Company Type fix, docs_new/ arquitectura multi-company, Space Category v1 (código + docs).

Plan que estoy siguiendo:
Autorización explícita del usuario en sesión 2026-05-27. Sin issue ni ADR formal — decisiones en CONTINUITY.

Objetivo inmediato:
Push de `feature/docs-new-workflow` + abrir PR a `main`.

Criterio de avance:
PR mergeado. `main` actualizado con Space Category v1 y documentación validada.

---

## Estado actual

### Ya cerrado
- Setup wizard condo-v16.dev ✅
- Bug Company Type IDs corregido ✅
- docs_new/: instalacion-y-configuracion.md, hooks.md, fixtures.md, arquitectura.md ✅
- Diagnóstico multi-company completo ✅
- Space Category v1 Capa 1: 5 archivos código, 7/7 tests OK (commit `f1c9c77`) ✅
- Documentación Physical Spaces v1: espacios-fisicos.md, deuda-tecnica.md, fixtures.md actualizado ✅

### En progreso
- PR `feature/docs-new-workflow` → `main` (pendiente push + apertura)

### Pendiente inmediato
1. Push de `feature/docs-new-workflow`
2. Crear PR `feature/docs-new-workflow` → `main`
3. Validar Space Category con usuario no-Administrator (confirmar solo lectura)
4. Si Capa 1 no bloquea → diseñar Capa 2 (before_save guard sin romper fixture import)

### No repetir
- No reactivar hooks universales (ISSUE #7) sin análisis
- No reiniciar servidor fuera de `/server-restart`
- No mover `insert_after` de `company_type`
- No intentar diagnosticar con SQL directo — usar `bench execute`
- No commitear one_offs/
- No mover ni archivar docs/ viejo hasta tener reemplazos en docs_new/ completos

---

## Decisiones vigentes
- Space Category = catálogo controlado del sistema. Usuarios no pueden crear/editar registros.
- Capa 2 diferida: flags `frappe.flags.in_fixtures` / `frappe.flags.in_import` confirmados activos
  durante migrate. Validate hooks SÍ corren con data_import=True.
- Administrator bypassa permisos nativamente — no necesita bloque explícito en DocType JSON.
- `company_type.insert_after = "reporting_currency"` — no cambiar
- `docs_new/` se construye progresivamente — un fragmento a la vez, solo lo validado
- `one_offs/` nunca se commitea
- Condominium Information: diferida hasta caso de uso real
- ISSUE #7 (hooks universales): no reactivar sin análisis

---

## Archivos relevantes ahora

### Leer primero
- `docs_new/tecnico/deuda-tecnica.md` — registro vigente de pendientes técnicos
- `docs_new/usuario/espacios-fisicos.md` — fuente vigente de Physical Spaces / Space Category

### Probablemente editar
- `physical_spaces/doctype/space_category/space_category.py` — si se autoriza Capa 2
- `CONTINUITY.md` — tras PR mergeado

### No tocar
- `hooks.py` líneas ~190-198 — hooks universales comentados (ISSUE #7)
- `docs/` — no mover ni archivar sin reemplazo validado en docs_new/
- Sites v15 (`admin1.dev`, etc.)
- `test-condominium.localhost` — solo para tests

---

## Riesgos / cuidados
- Space Category Capa 1 NO bloquea a Administrator en GUI — validación pendiente
- `bench migrate` aplica custom_field.json al site — no revertir sin migrate
- ISSUE #7 sigue sin resolver

---

## Información faltante
- Resultado de validación GUI de Space Category con usuario no-Administrator
- DocTypes Committee Management sin company verificada (Poll, Agreement Tracking, Community Event, Voting System)
