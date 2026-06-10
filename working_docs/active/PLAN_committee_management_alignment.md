# Plan de Corrección — Committee Management
## Fuente de verdad de asamblea + Aislamiento multi-condominio

| Campo | Valor |
|---|---|
| **Estado** | Aprobado — implementando Fase 1 + Fase 2 |
| **Fecha** | 2026-06-07 |
| **Fuente de auditoría** | `decisiones-tecnicas-frappe.md` §6 (Asambleas y gobernanza, Votación y consultas) |
| **Decisión P1** | Aprobada — Assembly Management es la entidad canónica. Event = solo agenda/calendario. |
| **Rama activa** | `feature/committee-company-isolation` |

---

## Decisiones aprobadas (no se debaten)

| # | Decisión |
|---|---|
| D1 | `Assembly Management` = fuente de verdad de asamblea. Submittable, con quórum, acuerdos y votación. |
| D2 | `Event` = auxiliar de calendario solamente. Sin asamblea, quórum, convocatoria, votación ni acuerdos. |
| D3 | `Voting System` ligado a `Assembly Management`. `company` se agrega directamente (no solo por herencia). |
| D4 | `Agreement Tracking` ligado a `Assembly Management`. |
| D5 | `Committee Poll` = consulta separada, no asamblea formal. Sin avanzar Phase 2 hasta tener PUA. |
| D6 | Votación ponderada bloqueada hasta implementar `indiviso_percentage` en `Property Registry` (PR separado). |
| D7 | `company` es `reqd: 1` real — sin `depends_on` como sustituto. Si hay datos demo sin company, se limpian antes del migrate. |

---

## Hallazgos auditados

### CRÍTICOS
- **C1:** Sin `company` en Assembly Management, Committee Meeting, Committee Poll, Voting System, Agreement Tracking, Community Event, Committee KPI.
- **C2:** Duplicación — `Assembly Management` (DocType propio) y `Event + asm_*` (Event extendido). `event_hooks.py` valida asambleas en Event.
- **C3:** `indiviso_percentage` no existe en Property Registry — `load_all_properties_to_quorum()` lee un campo inexistente → quórum siempre 0. (Fase 3, PR separado)
- **C4:** `voting_power` no se auto-pobla en `cast_vote()`. (Fase 3, PR separado)

### MENORES
- **M1:** `Agreement Tracking.responsible_party` es Data, no Link. (Futuro PR)
- **M2:** `Community Event` sin `company`. (Incluido en Fase 2)

---

## Datos existentes en condo-v16.dev (pre-migrate)

| DocType | Registros sin company |
|---|---|
| Committee Meeting | 1 — `MTG-26-05-002` "reunion comite" — demo, sin datos operativos |
| Assembly Management | 0 |
| Committee Poll | 0 |
| Voting System | 0 |
| Agreement Tracking | 0 |
| Community Event | 0 |

**Acción antes de migrate:** `MTG-26-05-002` es un registro demo. Debe asignársele un `company` o eliminarse. Se resolverá en el paso de validación pre-migrate.

---

## FASE 1 — Congelar Event como asamblea

**Sin cambios de modelo de datos.**

### F1-A — `hooks.py`: eliminar `doc_events["Event"]`
```python
# ELIMINAR este bloque:
"Event": {
    "validate": "condominium_management.committee_management.event_hooks.validate_assembly",
},
```

### F1-B — `hooks.py`: eliminar `scripts_client["Event"]`
`event_committee.js` solo controla visibilidad de tabs `asm_*`, `ce_*`, y `committee_tab` en el Event nativo. Con la decisión P1, ese JS ya no debe ejecutarse sobre Event.
```python
# ELIMINAR:
"Event": "public/js/event_committee.js",
```

### F1-C — `event_hooks.py`: agregar encabezado de deprecación
```python
# DEPRECATED 2026-06-08 — Assembly Management es la entidad canónica de asamblea.
# Event ya no se usa para asambleas, reuniones de comité ni eventos comunitarios condominiales.
# Este archivo se conserva como referencia histórica. No agregar lógica aquí.
# Ver: Assembly Management, Community Event DocTypes.
```

### F1-D — `public/js/event_committee.js`: agregar encabezado de deprecación
El archivo se mantiene en disco (el build existente puede usarlo) pero se documenta su estado.

### Archivos de Fase 1
- `condominium_management/hooks.py`
- `condominium_management/committee_management/event_hooks.py`
- `condominium_management/public/js/event_committee.js`

### Riesgo F1: BAJO
Solo se desconectan validaciones del Event. Ningún dato se toca.

---

## FASE 2 — Aislamiento por `company` en DocTypes operativos

### DocTypes con `company` requerido (reqd: 1)

| DocType | Posición en field_order |
|---|---|
| `Assembly Management` | Después de `convocation_section` (primer campo) |
| `Committee Meeting` | Después de `basic_information_section` |
| `Committee Poll` | Después de `poll_configuration_section` |
| `Voting System` | Después de `voting_configuration_section` |
| `Agreement Tracking` | Después de `agreement_information_section` |
| `Community Event` | Después de `event_information_section` |

### DocTypes con `company` opcional

| DocType | Justificación |
|---|---|
| `Committee KPI` | Indicadores de reportes — útil para filtrar pero no bloquea operación |

### Correcciones de lógica en Python

#### `assembly_management.py`
- `set_assembly_number()`: agregar `"company": self.company` al filtro del count → numeración por condominio.
- `load_all_properties_to_quorum()`: el filtro `if self.company:` ya existe; con el campo declarado funcionará automáticamente.
- `get_upcoming_assemblies()` y `get_assembly_history()` (métodos estáticos): aceptar parámetro `company=None` y filtrarlo si se pasa.
- `create_agreement_tracking_items()`: pasar `"company": self.company` al crear `Agreement Tracking`.

#### `committee_poll.py`
- `calculate_eligible_voters()`:
  - "Solo Comité": `{"is_active": 1, "company": self.company}`
  - "Todos los Propietarios": `{"is_active": 1, "company": self.company}`
- `is_eligible_respondent()`:
  - Verificar que `respondent_id` pertenece al mismo `company` del poll.

### Archivos de Fase 2

**JSONs:**
- `committee_management/doctype/assembly_management/assembly_management.json`
- `committee_management/doctype/committee_meeting/committee_meeting.json`
- `committee_management/doctype/committee_poll/committee_poll.json`
- `committee_management/doctype/voting_system/voting_system.json`
- `committee_management/doctype/agreement_tracking/agreement_tracking.json`
- `committee_management/doctype/community_event/community_event.json`
- `committee_management/doctype/committee_kpi/committee_kpi.json`

**Python:**
- `committee_management/doctype/assembly_management/assembly_management.py`
- `committee_management/doctype/committee_poll/committee_poll.py`

### Riesgo F2: MEDIO
- `reqd: 1` en UI — registros existentes sin company no pueden guardarse hasta asignar.
- 1 registro demo en Committee Meeting (MTG-26-05-002) sin company → resolución pre-migrate.
- `bench migrate` requerido en ambos sites.

---

## Tests requeridos

- `bench migrate` limpio en `condo-v16.dev` y `test-condominium.localhost`.
- Tests existentes de `committee_management` deben seguir pasando.
- Test nuevo: `Assembly Management` sin `company` debe fallar validación.
- Test nuevo: `calculate_eligible_voters` en `Committee Poll` filtra por `company`.

---

## Lo que NO entra en este PR

| Excluido | Razón |
|---|---|
| `indiviso_percentage` en Property Registry | PR separado — toca finanzas y votación ponderada |
| `voting_power` auto-poblar en `cast_vote()` | Depende de `indiviso_percentage` |
| Poll Response DocType | Analizar en Fase 4 |
| PUA en Committee Poll (`can_respond_polls`) | Fase 4 posterior |
| Eliminación de custom fields `asm_*/ce_*` de Event | Fase 5 — requiere patch de BD |
| `Agreement Tracking.responsible_party` → Link | PR futuro |
| User Permissions por Company | PR portal condominial |

---

## Pendientes explícitos (fuera de este plan)

| Pendiente | Bloqueante | PR esperado |
|---|---|---|
| `indiviso_percentage` en Property Registry | Votación ponderada | Fase 3 (PR separado) |
| Eliminar `asm_*/ce_*` custom fields de Event | No | Fase 5 (PR limpieza técnica) |
| `responsible_party` → Link trazable | No | PR futuro |
| Poll Response para trazabilidad por respondente | No | Analizar en Fase 4 |
| Committee Poll + PUA (`can_respond_polls`) | No | Fase 4 posterior |

---

*Estado: Aprobado. Implementando Fase 1 + Fase 2 en `feature/committee-company-isolation`.*
