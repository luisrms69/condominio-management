# Property Registry / Ownership — MVP

| Campo       | Valor                                              |
|-------------|----------------------------------------------------|
| **Versión** | 1.1                                                |
| **Fecha**   | 2026-05-28                                         |
| **Estado**  | Aprobado para implementación                       |

> Para la arquitectura compleja evaluada y descartada (Property Ownership Transfer submittable, delta, cancel/amend) ver el documento legacy: `property_registry_ownership_architecture.md`

---

## Qué resuelve este MVP

Control administrativo de titulares declarados de una unidad privativa. El sistema no es autoridad registral. No valida propiedad ante el RPP. Solo lleva el expediente operativo del condominio.

---

## DocTypes involucrados

| DocType | Tipo | Rol |
|---|---|---|
| `Property Registry` | Principal | Expediente de la unidad: datos físicos, indiviso, titulares |
| `Property Declared Owner` | Child table (istable:1) | Historial de titulares declarados — cada fila es un período de titularidad |
| `Acquisition Type` | Catálogo | Tipos de adquisición (no se modifica) |
| `Physical Space` | Linked | Espacio físico del inventario |

---

## Modelo: Property Declared Owner como historial

Cada fila de `Property Declared Owner` representa un período de titularidad declarada:

- `is_current = 1` → titular activo hoy
- `is_current = 0` + `end_date` → titular histórico

No hay DocType transaccional. No hay submit/cancel. El historial es una tabla editable con control humano.

### Campos de `Property Declared Owner`

| Fieldname | Fieldtype | Reqd | Notas |
|---|---|---|---|
| `owner_name` | Data | Sí | |
| `owner_id` | Data | No | RFC / CURP / Identificación — opcional |
| `owner_type` | Select | No | `Persona Física / Persona Moral` |
| `ownership_percentage` | Float | Sí | Porcentaje de titularidad declarada |
| `is_current` | Check | No | default 1 — titular activo hoy |
| `start_date` | Date | No | Cuándo inició esta titularidad |
| `end_date` | Date | No | Cuándo terminó (vacío = sigue activo) |
| `notes` | Small Text | No | Observaciones libres |
| `source_reference` | Data | No | "Escritura 1234", "Declaración verbal", etc. |
| `acquisition_date` | Date | No | Legado |
| `acquisition_type` | Link | No | Legado |
| `is_active` | Check | No | Legado — no usar en lógica nueva |

### Campos relevantes en `Property Registry`

| Fieldname | Fieldtype | Reqd | Descripción |
|---|---|---|---|
| `indiviso_percentage` | Percent | Sí | % de la unidad dentro del condominio |
| `current_owner_display` | Data | No | Read-only — calculado: nombre o "Copropiedad (N)" |
| `current_owners_total_percentage` | Float | No | Read-only — suma de titulares actuales |
| `declared_owners` | Table | No | Child table → `Property Declared Owner` |
| `ownership_notes` | Small Text | No | Notas generales sobre titularidad |

---

## Reglas de negocio

| Regla | Implementación |
|---|---|
| Titulares con `is_current=1` deben sumar 100% (±0.01%) | `validate_declared_owners()` filtrando `is_current=1` |
| `end_date` no puede ser anterior a `start_date` | Validación por fila |
| Fechas incompletas permitidas | Ningún campo de fecha es obligatorio |
| `owner_id` vacío no bloquea | `reqd:0` + warn-only si tiene valor |
| Sin documentos obligatorios | Ningún campo de escritura/notaría es obligatorio |
| `indiviso_percentage > 0` | Validación mínima — no valida suma global todavía |

---

## Consultas de historial

Sin infraestructura adicional — todo desde `tabProperty Declared Owner`:

```python
# Titulares actuales
[c for c in doc.declared_owners if c.is_current]

# Historial completo ordenado
frappe.get_all("Property Declared Owner",
    filters={"parent": name, "parenttype": "Property Registry"},
    fields=["owner_name", "ownership_percentage", "start_date", "end_date", "is_current", "notes"],
    order_by="start_date asc")

# Propiedades por titular
frappe.get_all("Property Declared Owner",
    filters={"owner_name": ["like", f"%{nombre}%"], "is_current": 1},
    fields=["parent", "owner_name", "ownership_percentage"])
```

---

## Migración de datos (post-rename)

Al renombrar `Property Copropiedad` → `Property Declared Owner`, se ejecutan dos patches en `[post_model_sync]`:

1. `remove_property_registry_deprecated_fields` — elimina columnas obsoletas de `tabProperty Registry`
2. `migrate_property_copropiedad_to_declared_owner` — copia filas de la child table antigua a la nueva, mapea `copropiedad_percentage` → `ownership_percentage` y `parentfield` `copropiedades_table` → `declared_owners`

La tabla `tabProperty Copropiedad` no se elimina en el primer migrate — se conserva como respaldo hasta validar GUI y tests.

---

## Fases

### Fase 1 — Implementado
- Historial de titulares declarados en `Property Declared Owner`
- Limpieza de `Property Registry` (eliminación de campos de nivel edificio)
- Rename completo: `Property Copropiedad` → `Property Declared Owner`
- `bench migrate` en `test-condominium.localhost` y `condo-v16.dev`

### Fase 2 — Reportes
- Titulares actuales por unidad
- Historial por unidad
- Propiedades por titular
- Unidades sin titular declarado
- Unidades sin `indiviso_percentage`
- Unidades con porcentaje ≠ 100%

### Fase 3+ — Solo si hay caso de cliente
Ver roadmap completo en `property_registry_ownership_architecture.md` §22.
