# CONTINUITY.md — condominium_management

**Fecha:** 2026-06-01
**Rama activa:** `fix/committee-member-position-redesign`
**Tarea actual:** Committee Management completo — Assembly lifecycle, Tab Bug fix, PR pendiente

---

## Recuperación rápida

Estoy trabajando en:
Rescate completo de Committee Management. Assembly lifecycle implementado y validado.
Bug de Tab Break visibility resuelto vía frm.layout.tabs.toggle(). PR pendiente.

Plan que estoy siguiendo:
Validación GUI → commit → push → PR → decidir siguiente módulo.

Objetivo inmediato:
Push + PR de fix/committee-member-position-redesign hacia main.

Criterio de avance:
PR creado, CI verde, merge autorizado.

---

## Estado actual

### Ya cerrado
- Committee Position + Committee Member rediseñado ✅
- Committee Meeting + Assembly sobre Event nativo ✅
- Convocatoria gate: Publicar Convocatoria button + congelamiento 3 capas ✅
- event_hooks.py: validaciones servidor completas ✅
- Tab Break visibility bug resuelto vía frm.layout.tabs.toggle() ✅
  (frappe-conventions SKILL.md actualizado en frappe-infrastructure)
- asm_agreements_tasks_created: gate incondicional antes de cerrar ✅
- Assembly Agenda Opción B: discussion_summary + decisions_taken ✅
- Print Format: Convocatoria Asamblea ✅
- Commits: edecd37 (Assembly lifecycle) + commit pendiente (Tab fix + closure gate)

### En progreso
- Commit en curso (autorizado)

### Pendiente inmediato
1. Ejecutar commit (ya autorizado)
2. Push → PR hacia main
3. Decidir siguiente módulo: Voting System o Committee Poll

### No repetir
- No usar frm.toggle_display ni frm.set_df_property para Tab Breaks — ver frappe-conventions SKILL.md
- No usar setTimeout para visibilidad de tabs
- No crear docs en rutas no canónicas (docs/development/ es estructura vieja)
- No commitear one_offs/
- No commitear master_template_registry.json si solo cambió last_update
- frappe-infrastructure está en /home/erpnext/Developer/frappe-infrastructure/ — NO en frappe-bench/apps/

---

## Decisiones vigentes
- Tab Break visibility: depends_on vacío + frm.layout.tabs.forEach(tab.toggle())
- Assembly closure gate: siempre requerir asm_agreements_tasks_created antes de Cerrada
- asm_status: forward-only (Planificada→Convocada→En Progreso→Cerrada)
- Voting gate: asm_status=="En Progreso" — documentado en deuda-tecnica.md
- Quórum: solo por indiviso (MVP)
- docs canónico: /home/erpnext/Developer/frappe-infrastructure/ (NO frappe-bench/apps/)

---

## Archivos relevantes ahora

### Leer primero
- `committee_management/event_hooks.py` — validaciones completas del ciclo Assembly
- `committee_management/event_custom_fields.py` — 56 custom fields sobre Event
- `public/js/event_committee.js` — toggle_meeting_tabs + toggle() directo

### Probablemente editar (siguiente PR)
- Print Format Acta de Asamblea (solo existe Convocatoria)
- `committee_management/event_hooks.py` — _validate_dates cuando sea MVP

### No tocar
- `financial_management/` — congelado
- `hooks.py` líneas ~190-198 — ISSUE #7
- `assembly_management/` viejo — congelado

---

## Riesgos / cuidados
- Tab Break toggle debe llamarse desde onload_post_render + refresh + field handlers
- master_template_registry.json: excluir de commits si solo cambió last_update
- frappe-infrastructure path correcto: /home/erpnext/Developer/frappe-infrastructure/

---

## Información faltante
- Print Format Acta de Asamblea completa
- Tests unitarios para event_hooks.py
