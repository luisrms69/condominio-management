# CONTINUITY.md — condominium_management

**Fecha:** 2026-06-01
**Rama activa:** `fix/committee-member-position-redesign`
**Tarea actual:** PR #37 abierto — Committee Management MVP, pendiente de merge

---

## Recuperación rápida

Estoy trabajando en:
Módulo Committee Management. PR #37 abierto con Committee Position, Meeting y Assembly MVP.

Plan que estoy siguiendo:
PR #37 → merge → nueva rama → Voting System (reescritura contra Event).

Objetivo inmediato:
Merge del PR #37 o decisión de arquitectura para Voting System.

Criterio de avance:
PR #37 mergeado en main. Nueva rama abierta para Voting System.

---

## Estado actual

### Ya cerrado (en PR #37)
- Committee Position: catálogo por company, after_migrate ✅
- Committee Member: rediseñado con Committee Position ✅
- Committee Meeting sobre Event nativo ✅
- Assembly sobre Event nativo — ciclo completo ✅
  - Publicar Convocatoria + congelamiento 3 capas
  - event_hooks.py: validaciones completas
  - Quorum snapshot
  - Gate de acuerdos (asm_agreements_tasks_created)
  - Print Format Convocatoria Asamblea
- Tab Break visibility fix (frm.layout.tabs.toggle) ✅
- frappe-conventions SKILL.md actualizado en frappe-infrastructure ✅

### Pendiente inmediato
1. Merge PR #37
2. Diagnóstico arquitectónico Voting System completado — ver análisis en sesión
3. Decidir e implementar Voting System (nueva rama)

### No repetir
- No usar frm.toggle_display para Tab Breaks — ver frappe-conventions SKILL.md
- No commitear one_offs/
- No commitear master_template_registry.json si solo cambió last_update
- frappe-infrastructure path correcto: /home/erpnext/Developer/frappe-infrastructure/
- Leer ~/.claude/CLAUDE.md completo al inicio de sesiones que toquen docs del ecosistema

---

## Decisiones vigentes
- Assembly vive sobre Event nativo — DocType Assembly Management congelado
- asm_status gate: Planificada→Convocada→En Progreso→Cerrada (forward-only)
- Voting System: reescribir assembly link de Assembly Management → Event
- Quórum: solo por indiviso (MVP)
- Agreement Tracking: abandonado, se usa Task nativo
- Tab Break visibility: depends_on vacío + frm.layout.tabs[n].toggle()

---

## Archivos relevantes ahora

### Leer primero (Voting System)
- `committee_management/doctype/voting_system/voting_system.py` — controller a reescribir
- `committee_management/doctype/voting_system/voting_system.json` — autoname roto
- `committee_management/doctype/vote_record/vote_record.json` — owner_name → voter_name
- `committee_management/event_hooks.py` — agregar gates de votación aquí

### No tocar
- `financial_management/` — congelado
- `assembly_management/` — congelado
- `hooks.py` líneas ~190-198 — ISSUE #7

---

## Riesgos / cuidados
- Voting System.autoname usa assembly.assembly_number (Assembly Management) — ROTO
- Vote Record tiene owner_name (campo reservado Frappe) — renombrar a voter_name
- Poll Option no pertenece a Voting System — mover a Committee Poll
- event_hooks.py sin tests unitarios — deuda documentada

---

## Información faltante
- Decisión final de arquitectura Voting System (en progreso)
- Print Format Acta de Asamblea completa
