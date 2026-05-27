# Hooks — condominium_management

**Validado:** 2026-05-26

---

## Company hooks (activos)

**Archivo:** `condominium_management/companies/hooks/company_hooks.py`

**Eventos registrados en `hooks.py`:**
- `Company.validate` → `validate_company_fields`
- `Company.after_insert` → (ver hooks.py para lista completa)
- `Company.on_update` → (ver hooks.py para lista completa)

**Comportamiento en wizard:**
`validate_company_fields` tiene guarda de entrada:

```python
def validate_company_fields(doc, method):
    if not hasattr(doc, "company_type"):
        return
```

La Company creada por el wizard no tiene `company_type` asignado (es campo custom del app).
El hook sale sin ejecutar validaciones. **No rompe el wizard.**

## Document Generation hooks (ISSUE #7 — desactivados)

**Archivo:** `condominium_management/hooks.py` líneas ~190-199

Los hooks universales `"*"` están comentados:

```python
# doc_events = {
#   "*": {
#     "after_insert": "...auto_detection.on_document_insert",
#     "on_update": "...auto_detection.on_document_update",
#   },
# }
```

**Razón:** Causaban `LinkValidationError: Could not find Parent Department: All Departments`
durante el setup wizard de ERPNext (30+ veces). Desactivados hasta resolver ISSUE #7.

**Impacto:** El módulo Document Generation no detecta entidades automáticamente.
Los tests CRUD del módulo pasan. La auto-detección no funciona en producción.

**Referencia:** `docs/development/issue7-hooks-universales-contexto.md` (444 líneas — fuente de verdad técnica).
Ver también: `docs_new/tecnico/deuda-tecnica.md` (pendiente de crear).

## Entity Configuration y Master Template Registry hooks (activos)

```python
"Master Template Registry": {
    "on_update": "...template_propagation.on_template_update"
},
"Entity Configuration": {
    "validate": "...auto_detection.validate_entity_configuration",
    "on_update": "...auto_detection.check_configuration_conflicts",
},
```

Estos sí están activos. No afectan el wizard (no se crean durante el wizard).
