# CONTINUITY.md — condominium_management

**Fecha:** 2026-06-01
**Rama activa:** `fix/committee-member-position-redesign`
**Tarea actual:** Assembly lifecycle sobre Event — implementado y validado, pendiente PR

---

## Recuperación rápida

Estoy trabajando en:
Rescate completo de Committee Management. Assembly opera sobre Event nativo con
ciclo de vida formal: Publicar Convocatoria → quórum → cierre → acta.

Plan que estoy siguiendo:
Validación GUI progresiva → commit → PR → siguiente módulo (Voting o Agreement Tracking).

Objetivo inmediato:
Push y PR de fix/committee-member-position-redesign hacia main.

Criterio de avance:
PR creado, CI verde, merge autorizado.

---

## Estado actual

### Ya cerrado
- Committee Position + Committee Member rediseñado ✅
- Committee Meeting sobre Event nativo ✅
- Assembly sobre Event nativo — ciclo completo validado ✅
  - Publicar Convocatoria: validación JS + congelamiento 3 capas (JS + read_only_depends_on + servidor)
  - event_hooks.py: asm_type freeze, status forward-only, Decimal-safe comparison, Event.status sync
  - Mesa de Asamblea: presiding officer, secretary, quorum declared on
  - Formalización del Acta: minutes status, document, protocolization flag
  - Assembly Agenda Opción B: presenter → Data, decisions_taken sin action_items
  - Acuerdos de seguimiento: botón + widget solo después de publicada
  - Print Format: Convocatoria Asamblea (Jinja2)
  - Quorum snapshot al cerrar (pasos 9 y 10 validados en EV00006) ✅
- deuda-tecnica.md: entries para date validations (no-MVP) y voting gate ✅
- Commit pendiente de ejecutar (autorizado en sesión 2026-06-01)

### En progreso
- `/ship commit` en curso — commit local autorizado, pendiente de ejecutar

### Pendiente inmediato
1. Ejecutar el commit (autorizado)
2. Push a origin
3. Abrir PR hacia main
4. Decidir próximo módulo: Voting System o Agreement Tracking

### No repetir
- No usar python3 directo con frappe.init/connect para modificar BD
- No crear Custom Fields sin usar fixtures + bench migrate
- No commitear one_offs/
- No push ni PR sin autorización independiente
- No revertir trabajo sin autorización explícita
- master_template_registry.json: excluir de commits si solo cambió last_update (timestamp volátil)

---

## Decisiones vigentes
- Assembly vive sobre Event nativo — no DocType propio
- Committee Meeting vive sobre Event nativo — DocType viejo congelado
- asm_status es el gate del ciclo: Planificada→Convocada→En Progreso→Cerrada (forward-only)
- Voting System depende de asm_status=="En Progreso" — ver deuda-tecnica.md
- Quórum: solo por indiviso (MVP) — no por conteo de unidades
- Opción B en Assembly Agenda: campos de convocatoria frozen, execution fields editables
- Date validations: no-MVP, estructura diseñada, documentada en deuda-tecnica.md
- docs_new/tecnico/ es la ruta válida y activa para docs técnicos en este repo

---

## Archivos relevantes ahora

### Leer primero
- `committee_management/event_hooks.py` — validación completa del ciclo Assembly
- `committee_management/event_custom_fields.py` — 54 custom fields sobre Event
- `public/js/event_committee.js` — UI de Committee Meeting + Assembly

### Probablemente editar (siguiente PR)
- `committee_management/event_hooks.py` — agregar _validate_dates cuando sea MVP
- Print Format Acta de Asamblea — solo existe Convocatoria, falta el Acta completa

### No tocar
- `financial_management/` — congelado
- `hooks.py` líneas ~190-198 — ISSUE #7
- `assembly_management/` viejo — congelado

---

## Riesgos / cuidados
- `asm_convener` (Link → Committee Member): read_only_depends_on correcto en BD;
  el botón × de Frappe puede aparecer visualmente pero el servidor rechaza cambios
- Decimal comparison bug resuelto en event_hooks._vals_equal — no volver a str()
- `bench migrate` es obligatorio después de cualquier cambio en CUSTOM_FIELDS
- `export-fixtures` es obligatorio después de migrate para que los cambios queden en código

---

## Información faltante
- Print Format del Acta de Asamblea (solo existe Convocatoria)
- Tests unitarios para event_hooks.py (ninguno escrito todavía)
- Validación de asm_convener en contexto multi-condominio (si hay varios condominios)
