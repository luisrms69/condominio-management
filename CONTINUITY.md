# CONTINUITY.md — condominium_management

**Fecha:** 2026-06-09
**Rama activa:** `feature/committee-company-isolation`
**Tarea actual:** WIP — Committee Management: aislamiento por company + congelamiento de Event como entidad de asamblea. Commit defensivo pre-bench-update.

---

## Recuperación rápida

Estoy trabajando en:
Revisión sistemática del código contra la fuente de verdad técnica de Domika:
- `frappe-infrastructure/projects/domika/arquitectura-producto-alcance.md` (v2.0)
- `frappe-infrastructure/projects/domika/decisiones-tecnicas-frappe.md` (v1.0)

El módulo en curso es **Committee Management**. Plan activo:
`working_docs/active/PLAN_committee_management_alignment.md` — Fases 1 y 2 implementadas, pendiente tests y PR.

Objetivo inmediato:
Correr `bench update --reset` en bench v16. Luego retomar `feature/committee-company-isolation` para completar tests y abrir PR.

Criterio de avance:
bench update limpio → retomar rama → verificar migrate → tests → PR

---

## Auditoría de módulos — estado global

| Módulo | Estado |
|---|---|
| Aislamiento multi-condominio (Companies) | ✅ Corregido — PR #40 + PR #41 mergeados |
| Espacios físicos (Physical Spaces) | ✅ Parcial — permisos + reqd en property_registry |
| Registro de unidades (Property Registry) | ✅ Parcial — physical_space reqd, company validation |
| Personas del condominio (Condominium People) | ✅ Fase 1 — PUA implementado (PR #40) |
| **Asambleas y gobernanza (Committee Management)** | ⚙️ En progreso — `feature/committee-company-isolation` |
| Votación y consultas (Committee Poll) | ⚙️ Incluido en plan Committee (Fase 4 pendiente) |
| Gestión financiera | ❄️ CONGELADO |
| Generación de documentos | ⚠️ ISSUE #7 — hooks universales comentados |
| Dashboard Consolidado | — Sin auditar |
| Community Contributions | — Sin auditar (multi-site no verificado) |

---

## Estado actual de la rama

### Ya cerrado (en main)
- PR #40 — Companies fixtures + Condominium People Fase 1
- PR #41 — Permisos Companies + ADRs (0002, 0003)

### En progreso — `feature/committee-company-isolation` (WIP, NO listo para PR)

**Fase 1 ✅ — Event congelado**
- `hooks.py`: `doc_events["Event"]` y `doctype_js["Event"]` comentados
- `event_hooks.py`: encabezado de deprecación
- `event_committee.js`: encabezado de deprecación

**Fase 2 ✅ — company en DocTypes operativos**
- `company` (reqd=1) en: Assembly Management, Committee Meeting, Committee Poll, Voting System, Agreement Tracking, Community Event
- `company` (reqd=0) en: Committee KPI
- Lógica corregida: `set_assembly_number()`, `calculate_eligible_voters()`, `is_eligible_respondent()`, `create_agreement_tracking_items()`, `get_upcoming_assemblies()`, `get_assembly_history()`
- `bench migrate` limpio en `condo-v16.dev` y `test-condominium.localhost` ✅
- committee_member tests: 7/7 OK — PUA tests: 14/14 OK ✅

### Pendiente al retomar
1. `bench update --reset` en bench v16 (usuario lo corre manualmente)
2. Retomar `feature/committee-company-isolation` post-update
3. Verificar `bench migrate` limpio post-update en ambos sites
4. Agregar tests con company para Assembly Management y Committee Poll
5. PR con documentación

### No repetir
- No poner análisis arquitectónicos en CLAUDE.md — van en docs/adr/
- Financial Management congelado — no tocar
- FrappeTestCase dispara Payment Gateway error en test site — usar UnitTestCase para tests nuevos
- CommitteeTestBase usa FrappeTestCase — preexistente, no introducido por este PR
- `bench update --reset` requiere trabajo guardado en remoto antes de correr

---

## Decisiones vigentes
- Assembly Management = fuente de verdad de asamblea (D1, decisiones-tecnicas-frappe.md §6)
- Event = solo auxiliar de calendario (D2)
- Voting System sin ponderación por indiviso hasta implementar `indiviso_percentage` en Property Registry (D6 — PR separado)
- Committee Poll sin PUA hasta Fase 4 del plan Committee Management
- Fases 3-5 del plan Committee Management son PRs separados
- User Permissions por Company diferidas al PR del portal condominial
- `unique` sobre `physical_space` diferido (análisis bodegas/cajones pendiente)
- `indiviso_percentage` en Property Registry → PR separado (ver `docs_new/arquitectura/property_registry_ownership_architecture.md`)

---

## Archivos relevantes ahora

### Leer primero
- `working_docs/active/PLAN_committee_management_alignment.md` — plan activo con fases
- `frappe-infrastructure/projects/domika/decisiones-tecnicas-frappe.md` — fuente de verdad técnica

### Trabajo pendiente relacionado
- `working_docs/active/ARCH_condominium-people-authorization.md` — Condominium People Fases 2-5 pendientes (stakeholders, portal, User Permissions sync)

### No tocar
- `financial_management/` — congelado
- `one_offs/` — nunca se commitean
- `working_docs/active/PLAN_committee_management_correction.md` — obsoleto, reemplazado por PLAN_committee_management_alignment.md

---

## Riesgos / cuidados
- `mkdocs build` bloqueado localmente por `mkdocs-redirects` no instalado — deuda preexistente, afecta validación de docs en este PR
- `bench update --reset` puede generar conflictos en la rama — verificar con git status post-update
- Verificar `bench migrate` limpio en ambos sites después del bench update
- CommitteeTestBase (FrappeTestCase) falla con Payment Gateway en test site — preexistente
- `test_agreement_tracking.py` llama `nowdate()` a nivel de clase sin contexto Frappe — preexistente
