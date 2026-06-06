# CONTINUITY.md — condominium_management

**Fecha:** 2026-06-06
**Rama activa:** `feature/condominium-people-phase1`
**Tarea actual:** Listo para Commit 2 — Condominium People Phase 1 (PUA + tests 14/14 OK)

---

## Recuperación rápida

Estoy trabajando en:
Commit 2 de la rama `feature/condominium-people-phase1`: módulo Condominium People Phase 1.
Commit 1 ya está en la rama (fix Companies/Property Registry, `cb351e4`).

Plan que estoy siguiendo:
- `working_docs/active/PLAN_companies_property_registry_alignment.md` (Fases 1+2A ✅)
- `working_docs/active/ARCH_condominium-people-authorization.md` v4 (PUA)

Objetivo inmediato:
Ejecutar Commit 2 con el mensaje aprobado → luego abrir PR.

Criterio de avance:
Dos commits en la rama → PR hacia main.

---

## Estado actual

### Ya cerrado (en rama, no mergeado)
- **Commit 1** `cb351e4` — fix(companies): restore Company custom fields fixture and require physical_space
  - `companies_custom_field.json` (27 campos Company)
  - `custom_field.json` actualizado (74 Event)
  - `physical_space: reqd: 1` en Property Registry
  - `validate_physical_space_company()` en property_registry.py
  - tests actualizados + test_install.py
  - plan working_docs actualizado

### Listo para Commit 2 (tests 14/14 OK en test-condominium.localhost)
- `hooks.py` — `setup_property_relationship_types` en after_migrate
- `modules.txt` — "Condominium People"
- `condominium_people/` — módulo completo: Property Relationship Type + PUA + utils + setup
- `test_property_user_authorization.py` — 14 tests, UnitTestCase, todos pasan
- `working_docs/active/ARCH_condominium-people-authorization.md`

### Pendiente inmediato
1. Ejecutar Commit 2 con mensaje aprobado
2. Abrir PR hacia main

### No repetir
- No usar git commit directo — siempre /ship commit
- No usar reqd:1 con depends_on en Custom Fields — usar mandatory_depends_on
- No commitear master_template_registry.json si solo cambió last_update
- Frappe v16 export-fixtures sobreescribe cuando hay dos entradas para el mismo DocType — usar `prefix`
- No hacer unique sobre physical_space aún — diferido (bodegas/cajones)
- FrappeTestCase dispara generación de test records que falla en test-condominium.localhost — usar UnitTestCase

---

## Decisiones vigentes
- `physical_space: reqd: 1` activo en Property Registry
- `unique` sobre `physical_space` DIFERIDO — análisis de unidades accesorias pendiente
- Service Management Contract = Nivel 1/2 Domika↔Condominio (D2 cerrado)
- Catálogos sin company = maestros HQ/globales (D3 cerrado)
- Property Copropiedad = congelada/deprecated, no eliminar
- PUA unicidad `user + property_registry` para MVP (D2)
- PUA módulo propio `condominium_people` (D5)
- User Permissions sync DIFERIDO a Fase 3 (portal) — los helpers funcionan sin ellas
- Financial Management y Property Account: NO tocar (congelados)
- Committee Poll, Voting System: bloqueados hasta que PUA esté mergeado
- Fases 3/4 del plan Companies (permisos Physical Space, catálogos) = PR separado posterior

---

## Archivos relevantes ahora

### Leer primero
- `working_docs/active/PLAN_companies_property_registry_alignment.md`
- `working_docs/active/ARCH_condominium-people-authorization.md`

### Para el PR (después del Commit 2)
- `condominium_people/utils.py` — helpers de autorización
- `condominium_people/setup.py` — defaults idempotentes

### No tocar
- `financial_management/` — congelado
- `fixtures/master_template_registry.json` — solo revertir last_update si export lo toca

---

## Riesgos / cuidados
- Fases 3/4 de Companies (permisos Physical Space, catálogos documentados) pendientes de PR separado
- `working_docs/active/ARCH_*` incluido en Commit 2 — es parte del entregable de arquitectura
