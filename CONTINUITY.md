# CONTINUITY.md — condominium_management

**Fecha:** 2026-06-02
**Rama activa:** `feature/committee-poll-events-kpi`
**Tarea actual:** Committee Management — Community Event implementado, pendiente PR + Committee KPI

---

## Recuperación rápida

Estoy trabajando en:
Cierre de Committee Management. Community Event implementado sobre Event nativo.
Committee Poll y Voting System congelados (documentados en deuda-tecnica.md).
Queda Committee KPI para completar el módulo.

Plan que estoy siguiendo:
Community Event validado → commit → KPI → PR → siguiente módulo.

Objetivo inmediato:
Decidir si implementar Committee KPI (parcial, muchas métricas dependen de Financial)
o abrir PR con lo que está y pasar a Condominium People.

Criterio de avance:
PR de feature/committee-poll-events-kpi mergeado. Nueva rama para siguiente bloque.

---

## Estado actual

### Ya cerrado (en este branch)
- Community Event sobre Event nativo — ciclo completo validado ✅
  - Tab Evento Comunitario, campos ce_*, status flow Planeado→Publicado→Finalizado
  - Fix tab visibility: tab.df.hidden + Tab.refresh() fix definitivo
  - mandatory_depends_on en Assembly fields (reqd:1 → mandatory_depends_on)
  - Event Checklist Item DocType (catálogo idempotente, 6 items por defecto)
  - Event Checklist Progress (child table con notes por fila)
  - Checklist auto-pobla por tipo + outdoor, reconstruye al cambiar
  - committee_header_section fix para auto-hide de Tab Comité
- Committee Poll: limpiado (target_audience simplificado, on_update fijo, JS básico)
- Committee Poll + Voting System: congelados, documentados en deuda-tecnica.md
- test_event_mandatory_fields.py: tests de regresión para mandatory_depends_on

### Pendiente inmediato
1. Decidir: implementar Committee KPI parcial O pasar a Condominium People
2. Export-fixtures (pendiente de autorización)
3. PR hacia main

### No repetir
- No usar reqd:1 en custom fields con depends_on — usar mandatory_depends_on
- No usar frm.toggle_display para Tab Breaks — usar tab.df.hidden + tab.toggle()
- No confundir frappe-infrastructure path: /home/erpnext/Developer/frappe-infrastructure/
- No commitear master_template_registry.json si solo cambió last_update
- No push ni PR sin autorización independiente

---

## Decisiones vigentes
- Community Event = Event nativo (mismo patrón que Assembly y Committee Meeting)
- Committee Poll congelado hasta Condominium People (User ↔ Property Registry)
- Voting System congelado hasta portal de autoservicio
- Event Checklist Item: solo after_migrate idempotente, NUNCA fixtures (preserva is_enabled por instalación)
- mandatory_depends_on es el mecanismo correcto para campos obligatorios condicionales en Frappe v16
- tab.df.hidden debe setearse JUNTO con tab.toggle() para que Tab.refresh() respete el estado

---

## Archivos relevantes ahora

### Leer primero
- `committee_management/event_custom_fields.py` — todos los custom fields de Event
- `committee_management/event_hooks.py` — validaciones completas
- `public/js/event_committee.js` — toggle_meeting_tabs + checklist
- `docs_new/tecnico/deuda-tecnica.md` — estado de modules congelados

### Probablemente editar (si se hace KPI)
- `committee_management/doctype/committee_kpi/committee_kpi.py`

### No tocar
- `financial_management/` — congelado
- `assembly_management/` viejo — congelado
- `community_event/` viejo — congelado (oculto en workspace)
- `hooks.py` líneas ~190-198 — ISSUE #7

---

## Riesgos / cuidados
- Committee KPI: 25+ métricas, muchas dependen de Financial Management (congelado)
  Solo assembly_participation_rate y meeting_attendance_rate son calculables hoy
- Export-fixtures pendiente antes del PR
- Condominium People es el desbloqueador de Committee Poll, Voting, RSVP y portal

---

## Información faltante
- Decisión: implementar KPI parcial vs saltar a Condominium People
- Print Format Acta de Asamblea (solo existe Convocatoria)
