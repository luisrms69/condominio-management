# Espacios físicos — condominium_management

**Validado:** 2026-05-27
**Fuente:** Implementación Space Category v1 (commit `f1c9c77`) — rama `feature/docs-new-workflow`

---

## Physical Space

Un Physical Space representa un lugar físico real del condominio: nombrado, navegable y accionable.

Un Physical Space puede recibir acciones cuando estas corresponden al espacio completo:
asignaciones, mantenimiento, reservas, restricciones de acceso, reportes. No es solo un
registro descriptivo; es el anclaje operativo de todas las actividades que ocurren en un lugar.

Ejemplos: Torre A, Piso 3, Departamento 301, Alberca, Caseta de Vigilancia, Estacionamiento B-12.

Physical Space tiene campo `company` requerido — cada espacio pertenece a un condominio específico.

---

## Space Category

Space Category clasifica tipos de lugares físicos.

### Naturaleza del catálogo

| Propiedad | Valor |
|---|---|
| Catálogo compartido del site | Sí — sin campo `company` |
| Controlado por el app | Sí — el usuario no lo modifica |
| Precargado por fixture | Sí — 51 categorías base al instalar |
| Editable libremente por usuarios | No |

Space Category no representa información de un condominio específico. Es compartido por
todas las Companies del site, igual que `Company Type` o `Property Status Type`.

### El usuario no crea Space Categories

Las Space Categories no se configuran durante la puesta en marcha del site. Vienen
precargadas automáticamente al ejecutar `bench migrate` con el app instalado.

El flujo correcto es:
1. Instalar app → `bench migrate`
2. Las 51 categorías base ya están disponibles
3. Crear Physical Spaces usando las categorías existentes

No hay un "Paso: crear categorías de espacios" en la configuración inicial.

### 51 categorías base

Al instalar condominium_management v1, se precargan 51 Space Categories cobertura para
condominios residenciales y de uso mixto.

Fixture: `condominium_management/fixtures/space_category.json`
Registrado en: `hooks.py` lista de fixtures

### category_type — 8 valores vigentes

| Valor | Descripción |
|---|---|
| Circulación y Acceso | Pasillos, lobbies, escaleras, rampas, entradas |
| Área Residencial | Departamentos, casas, lofts, estudios |
| Amenidades | Alberca, gimnasio, salón de eventos, jardines |
| Área Técnica | Cuartos de máquinas, subestaciones, cisternas |
| Área Administrativa | Oficinas, sala de juntas, recepción |
| Vialidad | Calles internas, estacionamientos, cajones |
| Servicios Comunes | Bodegas, lavanderías, basureros, correo |
| Uso Comercial | Locales comerciales, consultorios |

---

## Estado de Space Category v1

### Activo en v1

- `category_name` — nombre de la categoría
- `category_code` — código automático (3-4 chars, único)
- `category_type` — uno de los 8 valores anteriores
- `description` — descripción textual
- `is_active` — habilitada por defecto
- `icon_class` — clase CSS del ícono (fa fa-*)
- `color_code` — color hexadecimal
- `display_order` — orden de presentación
- `ps_template_code` — código de template (estructura preparada, no implementado)
- `template_version` — versión del template (default: "1.0")

### No activo en v1 (campos presentes pero desactivados funcionalmente)

| Campo | Estado |
|---|---|
| `requires_dimensions` | Presente, siempre 0 en fixtures base |
| `requires_capacity` | Presente, siempre 0 en fixtures base |
| `requires_components` | Presente, siempre 0 en fixtures base |
| `allowed_parent_categories` | Child table presente, sin registros |
| `allowed_child_categories` | Child table presente, sin registros |

Estos campos existen en el DocType para uso futuro pero no están activos en ninguna de las
51 categorías precargadas.

---

## Component Type y Space Component

### Component Type

Catálogo de tipos de componentes físicos (ventanas, puertas, equipos, etc.).
En v1: **no se tocó**. Sin fixtures, sin bloqueo de permisos. Pendiente decisión similar
a Space Category. Ver `docs_new/tecnico/deuda-tecnica.md`.

### Space Component

Child table del DocType Physical Space. Registra los componentes individuales de cada espacio.

En v1: **no se tocó**. Space Component sigue siendo child table. La decisión sobre
convertirlo en DocType standalone queda diferida hasta el diseño de CMMS.

---

## CMMS

El módulo de mantenimiento (CMMS) queda fuera de esta implementación. Los campos de
Space Category relacionados con templates (`ps_template_code`, `template_version`,
`auto_load_template`) están preparados estructuralmente pero no conectados a ningún
sistema de templates operativo.

---

## Pendiente técnico

La Capa 1 de bloqueo está implementada (`allow_rename=0` + permisos read-only para
System Manager). Sin embargo, Administrator bypassa permisos nativamente en Frappe.

**Pendiente verificar:** que un usuario con rol funcional (no Administrator) no pueda
crear ni editar Space Categories desde la UI.

Si el bloqueo no es suficiente, se diseñará una Capa 2 (before_save guard) que bloquee
ediciones desde UI sin romper el fixture import durante `bench migrate`.

Ver detalle en `docs_new/tecnico/deuda-tecnica.md`.

---

## Referencias

- Commit `f1c9c77` — implementación Space Category v1
- `condominium_management/fixtures/space_category.json` — 51 registros base
- `condominium_management/physical_spaces/doctype/space_category/space_category.json` — DocType
- `docs_new/tecnico/arquitectura.md` — clasificación de Space Category como catálogo compartido
- `docs_new/tecnico/fixtures.md` — Space Category en lista de fixtures
- `docs_new/tecnico/deuda-tecnica.md` — pendientes técnicos de Physical Spaces
