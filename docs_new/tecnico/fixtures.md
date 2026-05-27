# Fixtures — condominium_management

**Validado:** 2026-05-27

---

## Company Type — valores canónicos

`Company Type` es un DocType de catálogo. El campo `company_type` en `Company` es un Link
a este DocType. Los Links almacenan el `name` del registro (el ID técnico), no el `type_name`
(la etiqueta visible para el usuario).

| `name` (ID técnico) | `type_name` (display) |
|---|---|
| `CONDO` | Condominio |
| `ADMIN` | Administradora |
| `PROV` | Proveedor |
| `CONTR` | Contratista |

**Fixture:** `condominium_management/fixtures/company_type.json`

---

## Regla obligatoria: comparaciones usan el ID, no el display

Toda comparación técnica contra `company_type` debe usar el `name` (ID), nunca el `type_name`.

**Correcto:**

```python
if doc.company_type == "CONDO":
    ...
if doc.company_type == "ADMIN":
    ...
```

```json
"depends_on": "eval: doc.company_type == 'CONDO'"
"depends_on": "eval: doc.company_type == 'ADMIN'"
```

**Incorrecto (bug corregido 2026-05-27):**

```python
if doc.company_type == "Condominio":   # ← NUNCA — es el type_name, no el name
if doc.company_type == "Administradora":
```

```json
"depends_on": "eval: doc.company_type == 'Condominio'"   # ← NUNCA
"depends_on": "eval: doc.company_type == 'Administradora'"
```

Esta regla aplica a:
- `depends_on` en `custom_field.json`
- Comparaciones en `company_hooks.py`
- Comparaciones en `account_detection.py` y `company_detection.py`
- `frappe.db.exists("Company Type", name)` — recibe el `name`, no el `type_name`

---

## Custom Fields sobre Company — cadena insert_after (v16)

27 custom fields definidos en `condominium_management/fixtures/custom_field.json`.
Todos sobre el DocType `Company` de ERPNext.

La cadena de inserción comienza después del campo estándar `reporting_currency`
(último campo de la sección `details`, siempre visible en ERPNext v16).

```
reporting_currency          ← campo estándar ERPNext (ancla)
└── company_type            Link → Company Type  (sin depends_on — siempre visible)
    └── condominium_section Section Break        depends_on: CONDO
        └── property_usage_type                  depends_on: CONDO
            └── acquisition_type                 depends_on: CONDO
                └── property_status_type         depends_on: CONDO
                    └── cb_condominium_1         Column Break
                        └── total_units          depends_on: CONDO
                            └── total_area_sqm   depends_on: CONDO
                                └── construction_year  depends_on: CONDO
                                    └── floors_count   depends_on: CONDO
                                        └── management_section  Section Break  depends_on: ADMIN || CONDO
                                            └── management_company              depends_on: CONDO
                                                └── management_start_date       depends_on: CONDO && management_company
                                                    └── management_contract_end_date  depends_on: CONDO && management_company
                                                        └── managed_properties   depends_on: ADMIN
                                                            └── legal_section    Section Break  (sin depends_on)
                                                                └── legal_representative
                                                                    └── legal_representative_id
                                                                        └── cb_legal_1    Column Break
                                                                            └── registration_chamber_commerce
                                                                                └── registration_date
                                                                                    └── financial_section  Section Break  (sin depends_on)
                                                                                        └── monthly_admin_fee  depends_on: CONDO
                                                                                            └── reserve_fund   depends_on: CONDO
                                                                                                └── cb_financial_1  Column Break
                                                                                                    └── insurance_policy_number  depends_on: CONDO
                                                                                                        └── insurance_expiry_date  depends_on: CONDO
```

**Invariante crítico:** `company_type` debe estar antes de `condominium_section`.
Si `company_type` quedara dentro de una sección con `depends_on: CONDO`, el campo estaría
oculto hasta que se seleccione un valor — bucle imposible de romper desde la UI.

---

## Bug corregido (2026-05-27) — commit `ec362de`

Tres errores relacionados corregidos en el mismo commit:

### 1. `company_type` dentro de su propia sección condicional

**Antes:** `company_type.insert_after = "condominium_section"` — el campo quedaba
dentro de la sección que requería `company_type == 'CONDO'` para mostrarse.

**Después:** `company_type.insert_after = "reporting_currency"` — campo ancla en
sección `details` (siempre visible).

### 2. `depends_on` comparando contra `type_name` en lugar de `name`

**Antes (13 ocurrencias):** `eval: doc.company_type == 'Condominio'`
**Después:** `eval: doc.company_type == 'CONDO'`

**Antes (2 ocurrencias):** `eval: doc.company_type == 'Administradora'`
**Después:** `eval: doc.company_type == 'ADMIN'`

### 3. Hooks Python comparando contra `type_name`

Archivos corregidos:
- `companies/hooks/company_hooks.py` — 7 comparaciones
- `companies/hooks_handlers/account_detection.py` — 1 comparación
- `companies/hooks_handlers/company_detection.py` — 2 comparaciones
- `companies/doctype/property_registry/test_property_registry.py` — 1 `db.exists` con key incorrecto

---

## Referencias históricas

Los reportes de investigación que documentan el origen del problema y la migración a fixtures:

- `docs/development/pr-24-custom-fields-audit.md` — Auditoría original (2025-10-20). Contiene `depends_on` con valores obsoletos. **No usar como guía vigente.**
- `docs/development/pr-24-fixtures-investigation.md` — Investigación completa (2025-10-24). Documenta la decisión de normalizar a códigos cortos CONDO/ADMIN. **No usar como guía vigente.**
