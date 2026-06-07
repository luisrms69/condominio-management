# CONTINUITY.md — condominium_management

**Fecha:** 2026-06-06
**Rama activa:** `feature/companies-permissions-and-catalog-policy`
**Tarea actual:** PR #41 abierto — esperando merge; bench update pendiente

---

## Recuperación rápida

Estoy trabajando en:
PR #41 con Fases 3/4 del plan Companies/Property Registry (permisos + ADRs).
El usuario va a correr `bench update` en el bench v16.

Plan que estoy siguiendo:
`working_docs/active/PLAN_companies_property_registry_alignment.md` — Fases 1-4 completadas

Objetivo inmediato:
Merge del PR #41 → sync-check post-merge → decidir siguiente trabajo (Committee Poll).

Criterio de avance:
PR #41 mergeado a main → rama limpia.

---

## Estado actual

### Ya mergeado a main
- PR #40 — Companies fixture fix + Condominium People Phase 1

### En progreso (PR #41 — abierto)
- `physical_space.json` — +Property Administrator, +Condominium Manager, +Property Manager
- `condominium_information.json` — +Property Administrator
- `docs/adr/0002-catalog-hq-policy.md` — política catálogos HQ
- `docs/adr/0003-service-management-contract-level.md` — SMC = Nivel 1/2
- `mkdocs.yml` — sección ADR en nav
- `hooks.py` — política catálogos inline
- `PLAN_*.md` — Fases 3/4 cerradas

### Pendiente inmediato
1. Merge PR #41
2. sync-check post-merge
3. Decidir siguiente: Committee Poll con validación PUA

### No repetir
- No poner análisis arquitectónicos en `CLAUDE.md` — van en `docs/adr/`
- Antes de bench update: verificar que las apps tengan commits pendientes resueltos
- FrappeTestCase dispara record generation — usar UnitTestCase en test site

---

## Decisiones vigentes
- User Permissions por Company DIFERIDAS al PR del portal
- `unique` sobre `physical_space` DIFERIDO (bodegas/cajones)
- SMC = Nivel 1/2 → `docs/adr/0003`
- Catálogos HQ policy → `docs/adr/0002`
- Financial Management congelado
- Committee Poll desbloqueado — siguiente PR

---

## Archivos relevantes ahora

### Leer primero
- `working_docs/active/PLAN_companies_property_registry_alignment.md`
- `working_docs/active/ARCH_condominium-people-authorization.md`

### No tocar
- `financial_management/` — congelado
- `one_offs/` — nunca se commitean

---

## Riesgos / cuidados
- `mkdocs build` bloqueado localmente por `mkdocs-redirects` no instalado — deuda preexistente, no de este PR
- Tras bench update: verificar que `bench migrate` corra limpio en condo-v16.dev y test-condominium.localhost
