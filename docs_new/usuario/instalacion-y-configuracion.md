# Instalación y configuración — condominium_management

**Validado:** 2026-05-26 en `condo-v16.dev` (frappe 16.18.2 / erpnext 16.18.3 / condominium_management 0.0.1)

---

## Prerequisitos

- Bench v16 con frappe, erpnext y condominium_management instalados
- `bench --site <site> migrate` ejecutado y limpio
- App disponible en el bench: `bench list-apps` muestra `condominium_management`

## Setup wizard de ERPNext

El wizard aparece automáticamente al abrir el site por primera vez (`setup_complete = 0`).
No requiere login previo.

**Valores para sitio de desarrollo de condominios (México):**

| Campo | Valor |
|---|---|
| Idioma | Español |
| País | Mexico |
| Nombre de empresa | nombre del condominio o empresa de prueba |
| Abreviación | 2-5 caracteres |

El wizard crea la Company inicial y configura Global Defaults automáticamente.

**Estado esperado al terminar:**

| Campo | Valor esperado |
|---|---|
| `setup_complete` | `1` |
| `language` | `es` |
| `default_company` | nombre ingresado |
| `default_currency` | `MXN` |
| `country` | `Mexico` |

**Verificación (read-only):**

```bash
bench --site <site> execute "frappe.db.get_singles_dict('Global Defaults')"
bench --site <site> execute "frappe.db.get_value('System Settings', None, ['setup_complete','language'])"
bench --site <site> execute "frappe.get_all('Company', fields=['name','abbr','default_currency','country'])"
```

## Comportamiento de hooks durante el wizard

Los hooks de Company (`validate_company_fields`) están activos pero tienen guarda:

```python
if not hasattr(doc, "company_type"):
    return
```

La Company creada por el wizard no tiene `company_type` (campo custom del app),
por lo que el hook sale inmediatamente sin validar. **El wizard es seguro.**

Los hooks universales `"*"` de Document Generation están desactivados (ISSUE #7).
No interfieren con el wizard. Ver: `docs_new/tecnico/hooks.md`.

## Configurar Company como Condominio

Con el wizard completo, la Company creada es el punto de partida para el site de desarrollo.

**En `condo-v16.dev`:** La Company creada por el wizard es `CONDOV16`. Esta Company
se usa como condominio real de prueba para este site.

> **Nota:** Los pasos con nombre `CONDOV16` aplican solo a `condo-v16.dev`. En otros
> sites, la Company creada por el wizard tendrá el nombre que se ingresó en el wizard
> ("Nombre de empresa"). El procedimiento es el mismo; solo cambia el nombre de la
> Company a seleccionar. En cada site nuevo, verificar que la Company creada por el
> wizard es la que se quiere configurar como condominio.

### Pasos

1. Ir a **Setup > Company > CONDOV16**
2. En el campo **Tipo de Empresa**, seleccionar **Condominio**
3. Guardar

Al guardar con `Tipo de Empresa = Condominio`, aparecen las secciones:
- **Información de Condominio** — unidades, área, años, pisos
- **Información de Administración** — empresa administradora, contrato
- **Información Legal** — representante legal, registro
- **Información Financiera** — cuota mensual, fondo de reserva, seguro

4. Seleccionar **Tipo de Uso de Propiedad = Residencial**
5. Guardar nuevamente

### Estado esperado

La Company `CONDOV16` queda con:
- `company_type = CONDO`
- Secciones de condominio visibles y completables

### Nota técnica

El campo `Tipo de Empresa` almacena el ID técnico `CONDO`, no el texto "Condominio".
Las secciones condicionales usan `depends_on: eval: doc.company_type == 'CONDO'`.
Ver: `docs_new/tecnico/fixtures.md` para la explicación completa.

---

## Siguiente paso

Con CONDOV16 configurada como condominio, el site está listo para crear Physical Spaces.

**Space Categories ya están precargadas.** Al ejecutar `bench migrate` con el app instalado,
se cargan automáticamente 51 categorías base desde el fixture del app. No es necesario
crearlas manualmente.

El siguiente paso operativo es crear Physical Spaces usando las categorías precargadas.
Ver: `docs_new/usuario/espacios-fisicos.md` — fuente vigente del flujo de Physical Spaces.

`docs_new/usuario/flujo-operativo.md` (pendiente de crear — cubrirá el flujo completo
de datos maestros y operación diaria).

---

**Site de referencia:** `condo-v16.dev`
**No aplica a:** `test-condominium.localhost` — ese site usa `_Test Company` como seed, configurado por script, no por wizard.
