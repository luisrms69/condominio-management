# CONTINUITY.md — condominium_management

**Fecha:** 2026-06-06
**Rama activa:** `feature/condominium-people-phase1`
**Tarea actual:** Commit 1/2 de la rama: corrección Companies/Property Registry (Fases 1+2A) lista para commitear

---

## Recuperación rápida

Estoy trabajando en:
Dos líneas de trabajo en esta rama:
1. **Fases 1+2A** (Companies/Property Registry alignment) — lista para Commit 1
2. **Condominium People Phase 1** (PUA module) — lista para Commit 2 después

Plan que estoy siguiendo:
- `working_docs/active/PLAN_companies_property_registry_alignment.md` (Fases 1+2A)
- `working_docs/active/ARCH_condominium-people-authorization.md` v4 (PUA)

Objetivo inmediato:
Ejecutar Commit 1 (Fases 1+2A) → verificar → Commit 2 (Condominium People Phase 1).

Criterio de avance:
Dos commits en la rama → PR hacia main.

---

## Estado actual

### Ya cerrado (mergeado a main)
- PR #37 — Committee Position + Assembly sobre Event nativo ✅
- PR #38 — Community Event + mandatory_depends_on fix ✅
- PR #39 — CI rehabilitado para Frappe v16 ✅

### Completado en esta rama (listo para Commit 1)
- **Fase 1:** `hooks.py` con `prefix: "companies"` para fixture Company; `companies_custom_field.json` (27 campos); `custom_field.json` actualizado (74 Event)
- **Fase 2A:** `physical_space` obligatorio en Property Registry; `validate_physical_space_company()` en `property_registry.py`; tests actualizados + 2 nuevos; registro demo `PROP-2026-00004` eliminado
- `companies/test_install.py` — test de instalación de campos críticos Company
- Plan actualizado en `working_docs/active/PLAN_companies_property_registry_alignment.md`

### Completado en esta rama (listo para Commit 2 — después del Commit 1)
- `condominium_people/` — módulo completo (Property Relationship Type + Property User Authorization + utils.py + setup.py)
- `modules.txt` — agrega "Condominium People"
- `hooks.py` — línea `setup_property_relationship_types` en after_migrate (temporalmente retirada del staging de Commit 1; restaurar antes de Commit 2)

### Pendiente inmediato
1. Confirmar Commit 1 por el usuario → ejecutar git add + git commit
2. Verificar status limpio post-Commit 1
3. Restaurar la línea de `setup_property_relationship_types` en `hooks.py` (ya retirada temporalmente)
4. Ejecutar Commit 2 con condominium_people + módulos

### No repetir
- No usar git commit directo — siempre /ship commit
- No usar reqd:1 con depends_on en Custom Fields — usar mandatory_depends_on
- No commitear master_template_registry.json si solo cambió last_update
- Frappe v16 export-fixtures sobreescribe cuando hay dos entradas para el mismo DocType — usar `prefix` para separarlas
- No hacer unique sobre physical_space aún — diferido (bodegas/cajones)

---

## Decisiones vigentes
- `property_registry.json` — `physical_space: reqd: 1` activo
- `unique` sobre `physical_space` DIFERIDO — requiere análisis de unidades accesorias
- Service Management Contract = Nivel 1/2 Domika↔Condominio (D2 cerrado)
- Catálogos sin company = maestros HQ/globales (D3 cerrado)
- Property Copropiedad = congelada/deprecated, no eliminar
- Condominium People PUA: unicidad `user + property_registry` para MVP (D2), módulo propio `condominium_people` (D5)
- User Permissions sync DIFERIDO a Fase 3 (portal) — los helpers funcionan sin ellas
- Financial Management y Property Account: NO tocar (congelados)
- Committee Poll, Voting System: bloqueados hasta que PUA esté mergeado

---

## Archivos relevantes ahora

### Leer primero
- `working_docs/active/PLAN_companies_property_registry_alignment.md` — estado de Fases 1-5
- `working_docs/active/ARCH_condominium-people-authorization.md` — arquitectura PUA v4

### Probablemente editar (Commit 2)
- `hooks.py` — restaurar línea `setup_property_relationship_types` antes del commit
- `modules.txt` — ya tiene Condominium People

### No tocar
- `financial_management/` — congelado
- `hooks.py` líneas ISSUE #7 (~190-198) — doc_events comentados
- `fixtures/master_template_registry.json` — solo revertir last_update si export lo toca

---

## Riesgos / cuidados
- `hooks.py` tiene la línea `setup_property_relationship_types` TEMPORALMENTE RETIRADA para el Commit 1 — debe restaurarse antes del Commit 2
- No hacer bench migrate en condo-v16.dev mientras hooks.py esté sin la línea de condominium_people (el módulo está en disco pero no registrado en after_migrate)
- Fases 3/4 del plan Companies (permisos, catálogos) quedan pendientes para PR separado
