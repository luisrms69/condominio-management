# CONTINUITY.md — condominium_management

**Fecha:** 2026-05-27
**Rama activa:** `feature/docs-new-workflow`
**Tarea actual:** Documentación de arquitectura multi-company completada

---

## Recuperación rápida

Estoy trabajando en:
Cierre de la rama `feature/docs-new-workflow` para abrir PR a `main`.

Plan que estoy siguiendo:
CONTINUITY.md sección "Pendiente inmediato" → ítems 1 y 2 completados, falta PR.

Objetivo inmediato:
Push de `feature/docs-new-workflow` + abrir PR a `main`.

Criterio de avance:
PR mergeado y main actualizado. Si el PR incluye cambios de fixtures/código ya aplicados localmente, validar después el estado de condo-v16.dev.

---

## Estado actual

### Ya cerrado
- Setup wizard condo-v16.dev ✅ (CONDOV16/CV16, MXN, Mexico)
- Bug Company Type IDs corregido: `'Condominio'`→`'CONDO'`, `'Administradora'`→`'ADMIN'`
- insert_after de custom_field.json corregido — company_type visible en form
- CONDOV16 guardada con `company_type=CONDO` + `property_usage_type=Residencial` ✅
- Registro Condominium Information creado para CONDOV16 (`bj34hq8a92`) ✅
- docs_new/ creado: instalacion-y-configuracion.md, hooks.md, fixtures.md, arquitectura.md
- Diagnóstico multi-company completo: clasificación de todos los DocTypes documentada

### En progreso
- PR de `feature/docs-new-workflow` → pendiente de push + autorización para crear PR

### Pendiente inmediato
1. Push de `feature/docs-new-workflow`
2. Crear PR `feature/docs-new-workflow` → `main`
3. Post-merge: Space Categories en condo-v16.dev (catálogo para Physical Spaces)

### No repetir
- No mover `insert_after` de `company_type` — ya está en `"reporting_currency"` y funciona
- No reiniciar servidor fuera de `/server-restart`
- No intentar diagnosticar con SQL directo — usar `bench execute`
- No crear sección nueva para company_type
- No tomar decisión sobre Condominium Information sin caso de uso concreto

---

## Decisiones vigentes
- `company_type.insert_after = "reporting_currency"` — no cambiar
- `docs_new/` se construye progresivamente — no hacer movimientos masivos de `docs/`
- `one_offs/` nunca se commitea
- Condominium Information: decisión diferida hasta caso de uso real
- Committee Management gaps: no son bloqueantes — diferidos
- ISSUE #7 (hooks universales): no reactivar sin análisis

---

## Archivos relevantes ahora

### Leer primero
- `docs_new/tecnico/arquitectura.md` — modelo multi-company confirmado
- `docs_new/tecnico/fixtures.md` — Company Type IDs y cadena insert_after

### Probablemente editar
- `CONTINUITY.md` — actualizar tras merge del PR

### No tocar
- `hooks.py` líneas ~190-198 — hooks universales comentados (ISSUE #7)
- Sites v15 (`admin1.dev`, etc.)
- `test-condominium.localhost` — solo para tests

---

## Riesgos / cuidados
- `bench migrate` aplica custom_field.json al site — no revertir sin migrate
- ISSUE #7 sigue sin resolver
- Committee Poll, Agreement Tracking, Community Event, Voting System — company no verificada

---

## Información faltante
- Verificar DocTypes de Committee Management sin company confirmada (Poll, Agreement Tracking, Community Event, Voting System)
