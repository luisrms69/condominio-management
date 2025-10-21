# Frappe Framework - Workarounds

Soluciones a limitaciones conocidas del framework.

---

## Referencia Rápida

Para detalles completos de cada issue, ver: [known-issues.md](known-issues.md)

---

## Workaround #1: Mandatory Field Validation en Tests

**Problema:** Frappe mandatory validation no funciona confiablemente en tests.

**Solución:**
```python
def test_functional_validation(self):
    """
    Test funcional positivo en lugar de test de validación negativa.

    GitHub Issue #1638 - Framework limitation documentada.
    """
    # Test positivo: documento válido se crea correctamente
    doc = frappe.get_doc({
        "doctype": "Your DocType",
        "required_field": "value"  # Todos los campos required
    })
    doc.insert(ignore_permissions=True)

    # Validar creación exitosa
    self.assertTrue(doc.name)
    self.assertEqual(doc.required_field, "value")
```

---

## Workaround #2: Labels en Testing Environment

**Problema:** Labels de JSON no se aplican a meta cache en tests.

**Solución:**
```python
import json
import os

def test_labels_from_json(self):
    """Test labels leyendo JSON directamente"""
    json_path = os.path.join(os.path.dirname(__file__), "doctype.json")

    with open(json_path, "r", encoding="utf-8") as f:
        doctype_def = json.load(f)

    # Validar labels desde JSON
    for field in doctype_def.get("fields", []):
        if field.get("fieldname") == "target_field":
            self.assertEqual(field.get("label"), "Expected Label")
```

---

## Workaround #3: Skip Test Records

**Problema:** Frappe genera test records que causan conflictos.

**Solución:**
```python
# tests/__init__.py
import frappe
frappe.flags.skip_test_records = True
```

---

## Workaround #4: Company Creation en Tests

**Problema:** ERPNext Company requiere fixtures complejos.

**Solución:**
```python
@classmethod
def setUpClass(cls):
    """Setup Company para tests"""
    if not frappe.db.exists("Company", "_Test Company"):
        from erpnext.setup.doctype.company.test_company import create_test_company
        create_test_company()

    cls.company = "_Test Company"
```

---

## Workaround #5: Nested Set Performance

**Problema:** Actualizaciones costosas en árboles grandes.

**Solución:**
```python
# Batch updates cuando sea posible
frappe.db.auto_commit_on_many_writes = True

for node in nodes:
    node.save()

frappe.db.auto_commit_on_many_writes = False

# Rebuild tree solo cuando necesario
frappe.get_doc("Physical Space", space_name).rebuild_tree()
```

---

## Workaround #6: Permission Queries Lentas

**Problema:** Queries lentas con muchos roles.

**Solución:**
```python
# 1. Simplificar estructura de roles
# 2. Agregar índices a campos permission-related

# 3. Cache manual cuando appropriate
def get_allowed_spaces(user):
    cache_key = f"allowed_spaces:{user}"
    cached = frappe.cache().get_value(cache_key)

    if cached:
        return cached

    spaces = frappe.get_all("Physical Space",
        filters={"owner": user},
        fields=["name", "space_name"]
    )

    frappe.cache().set_value(cache_key, spaces, expires_in_sec=300)
    return spaces
```

---

## Workaround #7: Meta Loading Performance

**Problema:** `get_meta()` puede ser lento.

**Solución:**
```python
# Cache meta manualmente si se usa frecuentemente
class MyDocType(Document):
    _meta_cache = None

    @classmethod
    def get_cached_meta(cls):
        if cls._meta_cache is None:
            cls._meta_cache = frappe.get_meta("MyDocType")
        return cls._meta_cache
```

---

## Recursos Adicionales

- [Known Issues](known-issues.md) - Documentación completa de issues
- [Testing Best Practices](../testing/best-practices.md) - REGLAs 42-59
- [Layer 3 Guide](../testing/layer3-guide.md) - Testing integración
- [Layer 4 Guide](../testing/layer4-guide.md) - Testing configuration/performance

---

**Actualizado:** 2025-10-17
**Basado en:** Workarounds implementados en módulos del proyecto
