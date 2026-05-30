# Deuda técnica — condominium_management

**Creado:** 2026-05-27
**Fuente:** Diagnóstico acumulado de implementaciones en `feature/docs-new-workflow`

Este archivo registra pendientes técnicos conocidos que no bloquean operación actual
pero requieren resolución antes de escalar el sistema a producción o nuevos módulos.

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
