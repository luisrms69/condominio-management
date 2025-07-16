# Layer 4 Testing Best Practices - Configuration & Performance Validation

**Fecha:** Enero 16, 2025  
**Metodología:** REGLA #42 - Testing Granular Híbrido (Layer 4)  
**Estado:** ✅ IMPLEMENTADO - Financial Management Module  
**Basado en:** Recomendaciones de expertos enterprise Frappe/ERPNext

---

## 🎯 **DEFINICIÓN LAYER 4 - VALIDACIÓN ENTERPRISE**

Layer 4 se subdivide en **dos subcapas especializadas** para sistemas enterprise:

### **📋 Subcapa 4A: Configuration Validation**
Valida consistencia entre meta, JSON, permisos, roles y configuración del sistema:

1. **JSON vs Meta Consistency**: DocType JSON vs `frappe.get_meta()`
2. **Permission Configuration**: Role-based access control validation
3. **Hooks & Events Validation**: Custom scripts, event handlers
4. **Metadata Integrity**: Fields, validations, autoname, track_changes
5. **Fixtures vs DB**: Comparar fixtures JSON vs datos en DB

### **⚡ Subcapa 4B: Runtime Performance Validation**
Valida latencia, rendimiento y tolerancia a carga:

1. **CRUD Performance**: Insert, Update, Delete benchmarks
2. **Query Performance**: List views, search, filters
3. **UI Load Performance**: Form loading times
4. **API Response Times**: REST endpoints latency
5. **Resource Utilization**: Memory, CPU usage patterns

---

## 📊 **MÉTRICAS ENTERPRISE RECOMENDADAS**

### **Performance Benchmarks (Layer 4B):**
| Operación | Meta Ideal | Método |
|-----------|------------|--------|
| `insert()` DocType | < 300ms | `time.perf_counter()` |
| `frappe.get_all()` con filtros | < 100ms | `time.perf_counter()` |
| Generación masiva (1000 records) | < 3s | Batch test |
| UI Load JSON | < 800ms | Selenium/Playwright |
| API REST call | < 500ms | `requests.elapsed` |
| Search functionality | < 500ms | Query benchmarks |

### **Configuration Coverage (Layer 4A):**
- **JSON Fields**: 100% validados vs Meta
- **Permissions**: Todos los roles verificados
- **Hooks**: Existencia y disparo confirmado
- **Schema**: Consistencia completa DB vs Meta

---

## 🔧 **PATRONES DE IMPLEMENTACIÓN ENTERPRISE**

### **1. JSON vs Meta Consistency (Layer 4A)**
```python
import json
import os
import frappe
from frappe.tests.utils import FrappeTestCase

class TestDocTypeConfigValidation(FrappeTestCase):
    def test_json_vs_meta_consistency(self):
        """Validar consistencia completa JSON vs Meta"""
        # 1. Cargar JSON del DocType
        doctype_name = "Property Account"
        doctype_folder = doctype_name.replace(" ", "_").lower()
        json_path = os.path.join(
            frappe.get_app_path("condominium_management"), 
            "financial_management",
            "doctype", doctype_folder, 
            f"{doctype_folder}.json"
        )
        
        with open(json_path, 'r', encoding='utf-8') as f:
            json_def = json.load(f)
        
        # 2. Obtener Meta de Frappe
        frappe_meta = frappe.get_meta(doctype_name)
        
        # 3. Validar propiedades críticas
        self.assertEqual(json_def.get("is_single"), frappe_meta.is_single)
        self.assertEqual(json_def.get("autoname"), frappe_meta.autoname)
        self.assertEqual(json_def.get("track_changes"), frappe_meta.track_changes)
        
        # 4. Validar campos completos
        json_fields = {f["fieldname"]: f for f in json_def.get("fields", [])}
        frappe_fields = {f.fieldname: f for f in frappe_meta.fields}
        
        self.assertSetEqual(
            set(json_fields.keys()), 
            set(frappe_fields.keys()),
            "Fieldnames in JSON and Frappe Meta do not match"
        )
        
        # 5. Validar propiedades por campo
        for fieldname, json_field in json_fields.items():
            frappe_field = frappe_fields.get(fieldname)
            self.assertIsNotNone(frappe_field, f"Field {fieldname} missing in Meta")
            
            # Validaciones específicas
            self.assertEqual(
                json_field.get("fieldtype"), 
                frappe_field.fieldtype,
                f"Field {fieldname} fieldtype mismatch"
            )
            self.assertEqual(
                json_field.get("reqd"), 
                int(frappe_field.reqd),
                f"Field {fieldname} required status mismatch"
            )
            
            # Validar options para Select/Link fields
            if json_field.get("options"):
                self.assertEqual(
                    json_field.get("options"), 
                    frappe_field.options,
                    f"Field {fieldname} options mismatch"
                )
```

### **2. Permission Configuration Testing (Layer 4A)**
```python
def test_role_permissions_configuration(self):
    """Validar configuración de permisos por rol"""
    doctype_name = "Property Account"
    
    # Obtener todos los permisos
    all_perms = frappe.permissions.get_all_perms(doctype_name)
    
    # Verificar que System Manager tiene acceso completo
    if "System Manager" in all_perms:
        sm_perms = all_perms["System Manager"]
        self.assertTrue(sm_perms.get("read"), "System Manager debe tener read")
        self.assertTrue(sm_perms.get("write"), "System Manager debe tener write")
        self.assertTrue(sm_perms.get("create"), "System Manager debe tener create")
    
    # Verificar roles críticos específicos del dominio
    critical_roles = ["Property Manager", "Financial Manager"]
    for role in critical_roles:
        if role in all_perms:
            role_perms = all_perms[role]
            self.assertTrue(role_perms.get("read"), f"{role} debe tener read")
    
    # Verificar que Guest NO tiene permisos
    if "Guest" in all_perms:
        guest_perms = all_perms["Guest"]
        self.assertFalse(guest_perms.get("write"), "Guest NO debe tener write")
        self.assertFalse(guest_perms.get("delete"), "Guest NO debe tener delete")

def test_permission_denial_enforcement(self):
    """Test que los permisos se aplican correctamente"""
    # Crear usuario de prueba con rol limitado
    test_user = frappe.get_doc({
        "doctype": "User", 
        "email": f"test_{frappe.utils.random_string(5)}@example.com",
        "first_name": "Test User",
        "roles": [{"role": "Limited Role"}]  # Rol con permisos restringidos
    }).insert(ignore_permissions=True)
    
    try:
        # Cambiar a usuario limitado
        self.set_user(test_user.name)
        
        # Intentar acción que debería fallar
        with self.assertRaises(frappe.PermissionError):
            doc = frappe.get_doc({
                "doctype": "Property Account",
                "account_name": "Test Account",
                "property_code": "TEST-001",
                "account_status": "Active"
            }).insert()
            
    finally:
        # Volver a Administrator para cleanup
        self.set_user("Administrator")
        frappe.delete_doc("User", test_user.name)
```

### **3. Hooks Configuration Testing (Layer 4A)**
```python
from unittest.mock import patch

def test_hooks_registration_and_execution(self):
    """Validar que hooks están registrados y se ejecutan"""
    # 1. Verificar que hooks están registrados
    all_hooks = frappe.get_hooks()
    
    # Verificar hooks críticos para nuestro DocType
    validate_hooks = all_hooks.get("doc_events", {}).get("Property Account", {}).get("validate", [])
    self.assertGreater(len(validate_hooks), 0, "Debe haber al menos un validate hook")
    
    # 2. Verificar que hook se dispara
    with patch('condominium_management.financial_management.hooks_handlers.property_account_validate') as mock_hook:
        doc = frappe.get_doc({
            "doctype": "Property Account",
            "account_name": "Hook Test Account",
            "property_code": "HOOK-001",
            "account_status": "Active"
        })
        
        doc.insert(ignore_permissions=True)
        
        # Verificar que el hook fue llamado
        mock_hook.assert_called_once_with(doc)

def test_hooks_execution_order(self):
    """Validar orden de ejecución de hooks"""
    # Para casos donde el orden es crítico
    execution_order = []
    
    def track_execution(hook_name):
        def wrapper(*args, **kwargs):
            execution_order.append(hook_name)
        return wrapper
    
    with patch.multiple(
        'condominium_management.financial_management.hooks_handlers',
        before_validate_hook=track_execution("before_validate"),
        validate_hook=track_execution("validate"),
        after_insert_hook=track_execution("after_insert")
    ):
        doc = frappe.get_doc({
            "doctype": "Property Account",
            "account_name": "Order Test Account",
            "property_code": "ORDER-001"
        }).insert(ignore_permissions=True)
        
        expected_order = ["before_validate", "validate", "after_insert"]
        self.assertEqual(execution_order, expected_order, "Hook execution order incorrect")
```

### **4. Performance Benchmarks (Layer 4B)**
```python
import time

def test_document_insert_performance(self):
    """Test: performance de inserción de documentos"""
    start_time = time.perf_counter()
    
    doc = frappe.get_doc({
        "doctype": "Property Account",
        "account_name": "Performance Test " + frappe.utils.random_string(5),
        "property_code": "PERF-" + frappe.utils.random_string(3),
        "account_status": "Active",
        "current_balance": 0.0,
        "company": "_Test Company"
    })
    
    doc.insert(ignore_permissions=True)
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    # Meta: < 300ms según expertos
    self.assertLess(execution_time, 0.3, 
        f"Document insert took {execution_time:.3f}s, expected < 0.3s")
    
    frappe.db.rollback()

def test_list_view_performance(self):
    """Test: performance de list view con filtros"""
    start_time = time.perf_counter()
    
    docs = frappe.get_all("Property Account",
        fields=["name", "account_name", "account_status", "current_balance"],
        filters={"account_status": "Active"},
        limit=50
    )
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    # Meta: < 100ms según expertos
    self.assertLess(execution_time, 0.1, 
        f"List view took {execution_time:.3f}s, expected < 0.1s")

def test_search_performance(self):
    """Test: performance de búsqueda"""
    start_time = time.perf_counter()
    
    results = frappe.get_list("Property Account",
        filters={"account_name": ["like", "%Test%"]},
        fields=["name", "account_name"],
        limit=20
    )
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    # Meta: < 500ms según expertos
    self.assertLess(execution_time, 0.5, 
        f"Search took {execution_time:.3f}s, expected < 0.5s")

def test_batch_operations_performance(self):
    """Test: performance de operaciones masivas"""
    batch_size = 100
    start_time = time.perf_counter()
    
    docs_created = []
    for i in range(batch_size):
        doc = frappe.get_doc({
            "doctype": "Property Account",
            "account_name": f"Batch Test {i}",
            "property_code": f"BATCH-{i:03d}",
            "account_status": "Active"
        })
        doc.insert(ignore_permissions=True)
        docs_created.append(doc.name)
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    # Meta: < 30ms por documento (3s para 100)
    time_per_doc = execution_time / batch_size
    self.assertLess(time_per_doc, 0.03, 
        f"Batch operation: {time_per_doc:.3f}s per doc, expected < 0.03s")
    
    frappe.db.rollback()
```

---

## 🔍 **DATABASE SCHEMA VALIDATION (Layer 4A)**

```python
def test_database_schema_consistency(self):
    """Validar consistencia entre Meta y esquema DB"""
    doctype_name = "Property Account"
    table_name = f"tab{doctype_name.replace(' ', '')}"
    
    # Obtener columnas de la tabla
    table_columns = frappe.db.get_table_columns(table_name)
    meta = frappe.get_meta(doctype_name)
    
    # Verificar que todos los campos Meta existen en DB
    for field in meta.fields:
        if field.fieldtype not in ["Section Break", "Column Break", "HTML", "Heading"]:
            self.assertIn(field.fieldname, table_columns, 
                f"Field {field.fieldname} missing in DB table")
    
    # Verificar campos standard de Frappe
    standard_fields = ["name", "creation", "modified", "owner", "docstatus", "idx"]
    for field_name in standard_fields:
        self.assertIn(field_name, table_columns, 
            f"Standard field {field_name} missing in DB")

def test_index_optimization(self):
    """Validar que índices críticos están configurados"""
    table_name = "tabProperty Account"
    
    # Obtener índices de la tabla
    indexes = frappe.db.sql(f"""
        SHOW INDEX FROM `{table_name}`
    """, as_dict=True)
    
    index_columns = [idx.Column_name for idx in indexes]
    
    # Verificar índices críticos para performance
    critical_indexes = ["account_status", "property_code"]
    for column in critical_indexes:
        self.assertIn(column, index_columns, 
            f"Critical index missing for {column}")
```

---

## 🛠️ **HERRAMIENTAS RECOMENDADAS**

### **Para Layer 4A (Configuration):**
- `frappe.get_meta()` - Meta validation
- `frappe.permissions.get_all_perms()` - Permission testing
- `frappe.get_hooks()` - Hook registration validation
- `unittest.mock.patch` - Hook execution testing

### **Para Layer 4B (Performance):**
- `time.perf_counter()` - Mediciones precisas
- `pytest-benchmark` - Benchmark comparison
- `frappe.recorder` - Request analysis
- `MariaDB Slow Query Log` - DB optimization

### **Para CI/CD Integration:**
- GitHub Actions jobs separados para 4A y 4B
- Frequency: 4A en cada push, 4B en staging/pre-prod
- Performance baselines con `pytest-benchmark`

---

## 🚨 **ERRORES COMUNES Y SOLUCIONES**

### **Error 1: JSON vs Meta Inconsistency**
```
AssertionError: Field 'account_name' fieldtype mismatch
```
**Solución**: `bench migrate` y verificar sincronización

### **Error 2: Performance Degradation**
```
AssertionError: Operation took 450ms, expected < 300ms
```
**Solución**: Revisar índices DB y optimizar queries

### **Error 3: Hook Not Firing**
```
AssertionError: Hook was not called
```
**Solución**: Verificar registro en `hooks.py` y recargar

---

## 📈 **BENEFICIOS ENTERPRISE**

1. **Detección Temprana**: Configuration drift detection
2. **Performance Monitoring**: Continuous baseline validation
3. **Deployment Safety**: Pre-production validation
4. **Compliance**: Role-based permission auditing
5. **Scalability**: Performance regression detection
6. **Reliability**: Hook and event validation

---

## 🎯 **COMANDOS DE EJECUCIÓN**

```bash
# Layer 4A: Configuration Tests
bench --site admin1.dev run-tests --module "condominium_management.financial_management.doctype.property_account.test_property_account_l4a_configuration"

# Layer 4B: Performance Tests  
bench --site admin1.dev run-tests --module "condominium_management.financial_management.doctype.property_account.test_property_account_l4b_performance"

# Performance profiling con benchmark
bench --site admin1.dev run-tests --profile --module "..."

# Health checks para producción
bench --site admin1.dev run-tests --test-file "health_checks/l4_config_validation.py"
```

---

## 🔄 **CONSIDERACIONES FUTURAS (Layer 5)**

**Candidatos para Layer 5 - Operational Validation:**
- **Load Testing**: Locust/JMeter para stress testing
- **End-to-End UI**: Selenium/Playwright testing
- **Batch Logic**: Concurrency y deadlock testing
- **Production Health**: Automated monitoring

---

**AUTOR:** Claude Code Assistant  
**VALIDADO:** Expertos enterprise Frappe/ERPNext  
**APLICABILIDAD:** Todos los módulos enterprise del proyecto  
**REFERENCIA:** Recomendaciones implementadas en Financial Management Module