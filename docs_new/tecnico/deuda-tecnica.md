# Deuda técnica — condominium_management

**Creado:** 2026-05-27
**Fuente:** Diagnóstico acumulado de implementaciones en `feature/docs-new-workflow`

Este archivo registra pendientes técnicos conocidos que no bloquean operación actual
pero requieren resolución antes de escalar el sistema a producción o nuevos módulos.

---

## Committee Poll — congelado: requiere vínculo User ↔ Property Registry

### Estado (2026-06-02)

**El módulo Committee Poll está congelado.** El DocType existe con su estructura base
pero no puede implementarse funcionalmente sin el vínculo User ↔ Property Registry.

### Por qué no se implementa ahora

La entidad que responde a una encuesta en un condominio es la **propiedad/unidad**,
no el usuario. Un usuario puede administrar varias propiedades y emitir una respuesta
por cada una. Varias personas pueden estar vinculadas a la misma propiedad y solo
la primera respuesta válida por unidad cuenta.

Esto requiere saber qué propiedades tiene autorizadas cada User — relación que no
existe todavía (Condominium People, pendiente).

### Schema correcto cuando se retome

```
Poll Response (nuevo DocType):
  - poll              Link → Committee Poll   REQD
  - property_registry Link → Property Registry REQD
  - respondent        Link → User             REQD (auditoría — quién ejecutó el voto)
  - option_selected   Data                    REQD
  - response_date     Datetime (auto)

  Unicidad: unique(poll, property_registry)
  — una respuesta por unidad por encuesta, sin importar cuántos usuarios la gestionen
```

### Interface pendiente

El self-service (condómino vota desde su teléfono) requiere:
1. Vínculo User ↔ Property Registry (Condominium People)
2. Sección de autoservicio en la experiencia del condómino

Mientras no exista ese vínculo, no hay forma de saber qué propiedades puede
representar el usuario que está logueado.

### Lo que existe hoy

`committee_poll/committee_poll.json` y `committee_poll.py` — estructura base,
validaciones de fechas y opciones. `poll_options` usa conteo manual (`response_count`)
— modelo incorrecto que debe reemplazarse con Poll Response al retomar.

### Referencia

`committee_management/doctype/committee_poll/` — DocType y controller existentes.
`deuda-tecnica.md` entrada "Committee Member — relación User ↔ Property Registry" — dependencia raíz.

---

## Space Category — Capa 2 de bloqueo pendiente

### Estado actual (post-commit `f1c9c77`)

Capa 1 implementada:
- `allow_rename = 0` en el DocType
- System Manager: solo permisos read, export, print, share (sin create/write/delete)

### Gap conocido

Administrator bypassa permisos nativamente en Frappe (`permissions.py` lines 107-108).
Un usuario con rol Administrator puede crear y editar Space Categories desde la GUI.

### Pendiente

1. **Validar con usuario funcional (no Administrator):** confirmar que un usuario con
   rol operativo no puede crear ni editar Space Categories desde la UI.

2. **Si Capa 1 no es suficiente → diseñar Capa 2:**
   - Implementar guard en `before_save` del controller (`space_category.py`)
   - El guard debe bloquear ediciones desde UI pero permitir fixture import
   - Evidencia recopilada: `frappe.flags.in_fixtures` y `frappe.flags.in_import`
     están activos durante `bench migrate` (fixture loading via `sync_fixtures()`)
   - Validate hooks SÍ corren durante fixture loading (`data_import=True` no suprime validate)
   - La lógica del guard debe checar esos flags para distinguir fixture vs UI

### Referencia

`docs_new/usuario/espacios-fisicos.md` — sección "Pendiente técnico"

---

## ISSUE #7 — Hooks universales de Document Generation desactivados

### Estado

Los hooks `"*"` (universales) en `hooks.py` líneas ~190-198 están comentados.

```python
# doc_events = {
#     "*": {
#         "after_insert": "document_generation...",
#         ...
#     }
# }
```

### Causa

Los hooks universales interferían con el Setup Wizard de ERPNext en CI. Se desactivaron
como solución de emergencia. El módulo Document Generation no detecta entidades
automáticamente.

### Impacto actual

Document Generation: operación CRUD funciona. Auto-detección de entidades: no funciona.

### Pendiente

Analizar condición de guarda para reactivar selectivamente. No reactivar sin:
- Identificar qué DocTypes necesitan el hook
- Implementar guarda que excluya el wizard y otros DocTypes de ERPNext
- Confirmar en test-condominium.localhost que no rompe CI

### Referencia

`docs_new/tecnico/hooks.md` — estado de hooks de Company y Document Generation

---

## Committee Management — separación por company no verificada

### Estado

21 DocTypes en el módulo. Ninguno tiene campo `company` directo.
La separación depende de relaciones indirectas (Committee Meeting → Physical Space → company).

### DocTypes pendientes de verificación

| DocType | Ruta esperada | Riesgo |
|---|---|---|
| Committee Poll | Sin verificar | Mezcla de condominios |
| Agreement Tracking | Sin verificar | Mezcla de condominios |
| Community Event | Sin verificar | Mezcla de condominios |
| Voting System | Sin verificar | Mezcla de condominios |

### Pendiente

Verificar que cada uno de estos DocTypes tiene mecanismo de separación correcto.
Si no lo tiene, agregar campo `company` o relación indirecta verificada.

### Referencia

`docs_new/tecnico/arquitectura.md` — sección "DocTypes pendientes de verificación"

---

## Component Type — catálogo sin fixtures ni bloqueo

### Estado

DocType existe. Sin fixture exportado. Sin restricción de permisos.
Un usuario puede crear Component Types libremente desde la UI.

### Pendiente

Decidir si Component Type debe tratarse como catálogo controlado (igual que Space Category):
- Si sí: exportar fixture con tipos base, restringir permisos, `allow_rename=0`
- Si no: documentar la justificación

Esta decisión debe tomarse antes de activar funcionalidad de Space Components.

---

## Space Component — standalone vs child table

### Estado actual

Space Component es child table del DocType Physical Space.
Los componentes solo existen como parte de un Physical Space.

### Decisión diferida

Convertir Space Component a DocType standalone permitiría:
- Catálogo central de componentes reutilizables
- Historial de mantenimiento por componente
- Jerarquía de subcomponentes (Caldera → Quemadores)
- Asignación del mismo componente a múltiples espacios

Esta decisión afecta directamente el diseño de CMMS y no debe tomarse sin ese contexto.

### Pendiente

Retomar cuando se inicie diseño de CMMS. No tocar la estructura actual hasta entonces.

---

## Condominium Information — diseño incompleto

### Estado (2026-05-27)

| Aspecto | Problema |
|---|---|
| `autoname` | `None` → nombres hash (`bj34hq8a92`) — no garantiza 1 registro por Company |
| Duplicidad | Puede haber múltiples CI para la misma Company sin restricción |
| Campos duplicados | `total_units`, `total_area`, `construction_year` existen también en Company (custom fields) |
| Consumo en código | Solo `module_monitor.py` (conteo de registros) |
| Navegación | Sin workspace — no aparece en menú lateral |

### Pendiente

Decidir fuente de verdad para los campos duplicados cuando exista caso de uso funcional
concreto. No tomar esta decisión sin ese contexto. Hoy CI no bloquea ningún flujo operativo.

Opciones:
- Reparar: `autoname = field:company`, eliminar campos duplicados, crear workspace
- Redefinir: mover toda la metadata a custom fields de Company y eliminar CI

### Referencia

`docs_new/tecnico/arquitectura.md` — sección "Condominium Information — estado y decisión pendiente"

---

## Documentación obsoleta en docs/

### Estado

Los siguientes archivos en `docs/` contienen información contradictoria o aspiracional
que no refleja el estado actual del app:

| Archivo | Problema |
|---|---|
| `docs/development/architecture/physical-spaces.md` | Diseño aspiracional. Marca como ✅ DocTypes que no existen. Usa category_types obsoletos. |
| `docs/user-guide/physical-spaces.md` | Instruye crear Space Categories manualmente — contradice v1. |

### Pendiente

Archivar en `docs_new/archive/` con nota de reemplazo cuando los docs vigentes en
`docs_new/` estén completos. No mover hasta tener el reemplazo escrito y validado.

---

## Assembly — validaciones de fechas no implementadas (no-MVP)

### Estado actual

El hook `validate_assembly` en `committee_management/event_hooks.py` no valida
consistencia de fechas/horarios. Los campos existen pero pueden cargarse con valores
ilógicos sin recibir error.

### Gap conocido

Tres validaciones identificadas pero no implementadas por decisión de MVP:

| Regla | Campos involucrados |
|---|---|
| Primera convocatoria debe ser antes que segunda | `asm_first_call < asm_second_call` |
| Hora de inicio antes que hora de cierre | `asm_actual_start < asm_actual_end` |
| Fecha de convocatoria antes que fecha de asamblea | `asm_convocation_date < starts_on` |

### Pendiente

Agregar función `_validate_dates(doc)` en `event_hooks.py` y llamarla desde
`validate_assembly()` entre `_validate_asm_type_frozen` y `_validate_status_transition`.
La estructura de la función ya está diseñada — ver conversación de 2026-06-01.

No implementar sin confirmar comportamiento de Frappe con campos `Time` comparados
via `frappe.utils.get_time()`.

### Referencia

`committee_management/event_hooks.py` — función `validate_assembly`

---

## Voting System — congelado: requiere portal de autoservicio

### Estado (2026-06-01)

**El módulo Voting System está congelado.** No debe implementarse hasta que exista
un portal de autoservicio para condóminos.

El DocType `voting_system` existe en el codebase pero apunta a `Assembly Management`
(DocType viejo, congelado). El controller está escrito contra ese DocType y está roto.

### Por qué no se implementa ahora

En una asamblea de 100-200 unidades, el secretario no puede capturar votos individuales
manualmente en tiempo real. El análisis realizado (2026-06-01) concluye:

- **Sin autoservicio**: solo se puede capturar totales (`75% a favor / 20% en contra`),
  lo que reduce el módulo a una hoja de cálculo con pasos extra — sin valor suficiente
- **Con autoservicio**: cada condómino se autentica y vota desde su dispositivo —
  viable, con trazabilidad real, pero requiere portal que no existe

La dependencia es bloqueante: **Voting System operativo requiere portal de condóminos**.

### Qué sí funciona hoy en su lugar

El campo `decisions_taken` en cada fila de `asm_formal_agenda` captura el resultado
de la votación como texto libre:

```
"Aprobado por mayoría simple — 78% de los indivisos presentes votaron a favor"
"Rechazado — no alcanzó el quórum calificado requerido del 75%"
"Aprobado por unanimidad"
```

Suficiente para el acta y para protocolización notarial en el MVP.

### Arquitectura diseñada (no implementar hasta tener portal)

El análisis completo del flujo está documentado en la sesión de 2026-06-01.
Los puntos clave para cuando se retome:

**Relación correcta:**
```
Event Assembly
  → asm_formal_agenda (punto con requires_vote = 1)
  → Voting System
      → Vote Record (uno por unidad)
```

**Cambios de schema pendientes al retomar:**
- `voting_system.assembly`: Link → `Event` (hoy apunta a `Assembly Management` — roto)
- `voting_system.autoname`: `format:VOT-{assembly}-{motion_number}`
- `voting_system.agenda_item`: Link → renglón de `asm_formal_agenda` (nuevo)
- `voting_system.pre_vote_notes`: Text — dudas y aclaraciones previas a la votación
- `voting_system.clarifications_resolved`: Check — gate antes de abrir votos
- `vote_record.voter_name`: renombrar desde `owner_name` (campo reservado Frappe)
- `vote_record.voting_power`: fetch desde snapshot de `asm_quorum_registration`,
  no desde `Property Registry` dinámico
- Eliminar `poll_options` child table de Voting System — pertenece a Committee Poll

**Gates a implementar:**
- Solo crear votación si `asm_status == "En Progreso"` AND `asm_quorum_reached == 1`
- Solo votar si la unidad está en `asm_quorum_registration` con Presente/Representado/Virtual
- Una unidad = un voto por votación (bloquear doble voto)
- No cerrar asamblea si hay Voting System en status "Abierta"
- Votos congelados cuando Voting System pasa a "Cerrada"

**Estados de Voting System:**
```
Abierta → Cerrada
Abierta → Cancelada (solo sin votos emitidos)
```

**Cálculo de mayoría simple (default MVP):**
`votos_a_favor > total_votó × 50%`
Advertencia: algunos reglamentos usan `total_quórum_presente` como base, no `total_votó`.
Documentar como configurable antes de hardcodear.

**Representados/proxies:**
El voto se registra a nombre de la propiedad original (no del representante).
El `proxy_document` ya queda en `asm_quorum_registration`.

### Referencia de código actual (roto, no tocar)

`committee_management/doctype/voting_system/voting_system.py` — controller completo
a reescribir cuando se retome. Referencia de `Assembly Management` en todas las validaciones.

`committee_management/hooks_handlers/voting_system_validation.py` — handler viejo,
apunta a Assembly Management. Reescribir o eliminar al retomar.

`committee_management/event_hooks.py` — `_STATUS_FLOW` (líneas ~14-20) — el gate
`asm_status == "En Progreso"` ya está implementado y listo para conectar.

---

## Committee Member — relación User ↔ Property Registry pendiente de arquitectura

### Estado actual (2026-05-31)

`Committee Member` vincula directamente `user` → `property_registry` como solución operativa temporal. El campo `property_registry` es seleccionable manualmente, filtrado por `company`.

### Gap conocido

No existe un vínculo formal entre un `User` de Frappe y su(s) unidad(es) en `Property Registry`. La arquitectura correcta requiere un módulo intermedio:

```
Property Registry
  → Condominium Person Profile   ← módulo pendiente de implementar
      → frappe_user (Link → User, opcional)
      → person_category
      → vigencia / estado
  → Committee Member
```

### Por qué no se resuelve hoy

- `Condominium People` no está implementado.
- No se usa `Property Account` (módulo financiero congelado).
- No se agrega `user` a `Property Declared Owner` como decisión definitiva.

### Impacto actual

- El admin asigna manualmente `property_registry` al crear un `Committee Member`.
- No hay validación de que el usuario realmente sea titular de esa propiedad.
- El selector de `user` filtra por rol `Condómino` como aproximación de elegibilidad.

### Pendiente

Cuando exista `Condominium People`, `Committee Member` debe migrar hacia validar elegibilidad contra `Condominium Person Profile`. La relación directa `Committee Member.property_registry` puede conservarse como snapshot o eliminarse según el diseño final.
