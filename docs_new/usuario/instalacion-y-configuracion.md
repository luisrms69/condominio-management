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
No interfieren con el wizard.

## Siguiente paso

Con el wizard completo, el site está listo para configurar datos maestros del app:
- Space Categories
- Component Types
- Primera Company tipo "Condominio" (opcional — el wizard ya creó una Company base)

Ver: `docs_new/usuario/flujo-operativo.md` (pendiente de crear).

---

**Site de referencia:** `condo-v16.dev`
**No aplica a:** `test-condominium.localhost` — ese site usa `_Test Company` como seed, configurado por script, no por wizard.
