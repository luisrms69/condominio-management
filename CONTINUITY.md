# CONTINUITY.md — condominium_management

**Fecha:** 2026-06-06
**Rama activa:** `feature/companies-permissions-and-catalog-policy`
**Tarea actual:** Commit autorizado — Fases 3/4 Companies listas para commitear

---

## Recuperación rápida

Estoy trabajando en:
PR de Fases 3/4 del plan Companies/Property Registry: permisos para Physical Space y
Condominium Information + política de catálogos HQ documentada en ADRs.

Plan que estoy siguiendo:
`working_docs/active/PLAN_companies_property_registry_alignment.md` — Fases 3/4 completadas

Objetivo inmediato:
Commit → push → PR → merge.

Criterio de avance:
Commit creado con el mensaje aprobado → PR abierto hacia main.

---

## Estado actual

### Ya mergeado a main
- PR #40 — Companies fixture fix + Condominium People Phase 1

### Listo para commit (rama actual)
- `physical_space.json` — +Property Administrator (R/W/C), +Condominium Manager (R/W/C), +Property Manager (R)
- `condominium_information.json` — +Property Administrator (R/W/C)
- `hooks.py` — política catálogos HQ inline
- `docs/adr/0002-catalog-hq-policy.md` — nuevo ADR
- `docs/adr/0003-service-management-contract-level.md` — nuevo ADR
- `mkdocs.yml` — sección ADR en nav (0000-0003 todos referenciados)
- `CLAUDE.md` — reducido a notas operativas, refs a ADRs
- `PLAN_companies_property_registry_alignment.md` — Fases 3/4 marcadas completas

### Pendiente inmediato
1. Ejecutar commit con mensaje aprobado
2. Push → PR

### No repetir
- No poner análisis de decisiones en `CLAUDE.md` — van en `docs/adr/`
- No duplicar en CLAUDE.md lo que ya está en ADRs o working_docs
- El warning de `mkdocs-redirects` no instalado localmente es deuda preexistente

---

## Decisiones vigentes
- User Permissions por Company DIFERIDAS al PR del portal (Fase 3 PUA)
- `unique` sobre `physical_space` DIFERIDO (bodegas/cajones)
- SMC = Nivel 1/2 Domika↔Condominio (docs/adr/0003)
- Catálogos HQ policy (docs/adr/0002)
- Financial Management, Property Account: congelados
- Committee Poll: desbloqueado, siguiente PR

---

## Archivos relevantes ahora

### Para este commit
- `docs/adr/0002-catalog-hq-policy.md`
- `docs/adr/0003-service-management-contract-level.md`
- `working_docs/active/PLAN_companies_property_registry_alignment.md`

### No tocar
- `financial_management/` — congelado
- `one_offs/` — nunca se commitean
