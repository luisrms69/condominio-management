# ✅ CHECKLIST DE COMPLIANCE PARA UNIT TESTS

**Proyecto:** Condominium Management  
**Framework:** Frappe v15  
**Aplicar a:** TODOS los nuevos DocTypes

---

## 🎯 **USO DE ESTE CHECKLIST**

Antes de considerar **COMPLETO** cualquier DocType nuevo, verificar que cumple al 100% con este checklist. Los tests son **OBLIGATORIOS** y deben seguir las mejores prácticas de Frappe Framework.

---

## 📋 **CHECKLIST OBLIGATORIO POR DOCTYPE**

### **1. ESTRUCTURA BÁSICA DE ARCHIVOS**

- [ ] **Archivo de test existe:** `test_{doctype_name}.py` en el directorio del DocType
- [ ] **Header correcto:** Copyright header estándar presente
- [ ] **Imports correctos:** 
  ```python
  import unittest
  import frappe  
  from frappe.tests.utils import FrappeTestCase
  ```
- [ ] **Clase nombrada correctamente:** `TestDocTypeName(FrappeTestCase)`

### **2. ESTRUCTURA DE CLASE Y MÉTODOS**

- [ ] **setUpClass implementado:**
  ```python
  @classmethod
  def setUpClass(cls):
      super().setUpClass()  # CRÍTICO
      cls.create_test_dependencies()
  ```

- [ ] **Helper method para dependencies:**
  ```python
  @classmethod
  def create_test_dependencies(cls):
      if getattr(frappe.flags, 'test_doctype_deps_created', False):
          return
      # Crear dependencies...
      frappe.flags.test_doctype_deps_created = True
  ```

- [ ] **setUp method correcto:**
  ```python
  def setUp(self):
      frappe.set_user("Administrator")
      self.test_data = {...}
  ```

- [ ] **tearDown method correcto:**
  ```python
  def tearDown(self):
      frappe.set_user("Administrator") 
      # FrappeTestCase automatically handles transaction rollback
  ```

### **3. TESTS OBLIGATORIOS**

#### **Test de Creación Básica:**
- [ ] **test_{doctype}_creation implementado**
- [ ] **Usa ignore_permissions=True** en document.insert()
- [ ] **Verifica propiedades básicas** del documento creado
- [ ] **NO hace cleanup manual** (doc.delete())

#### **Test de Etiquetas Españolas:**
- [ ] **test_spanish_labels implementado**
- [ ] **Verifica DocType label** en español
- [ ] **Verifica field labels** principales en español
- [ ] **Verifica Select/MultiSelect options** en español

#### **Test de Validaciones:**
- [ ] **test_required_fields_validation implementado**
- [ ] **Usa assertRaises(frappe.ValidationError)** apropiadamente
- [ ] **Testa campos requeridos faltantes**

#### **Test de Opciones Españolas:**
- [ ] **test_spanish_options implementado** (si aplica)
- [ ] **Verifica todas las opciones** de campos Select/MultiSelect
- [ ] **Confirma opciones en español** (no inglés)

### **4. MEJORES PRÁCTICAS APLICADAS**

#### **Gestión de Test Data:**
- [ ] **Usa flags para evitar duplicación:** `frappe.flags.test_*_created`
- [ ] **Test data en self.test_data** para reutilización
- [ ] **Dependencies creadas en setUpClass** (no en setUp)

#### **Manejo de Transacciones:**
- [ ] **NO usa doc.delete()** para cleanup
- [ ] **NO usa frappe.db.rollback()** manual  
- [ ] **Confía en rollback automático** de FrappeTestCase

#### **Gestión de Usuarios:**
- [ ] **setUp establece Administrator:** `frappe.set_user("Administrator")`
- [ ] **tearDown resetea usuario:** `frappe.set_user("Administrator")`
- [ ] **Tests de permisos** usan user switching si aplicable

### **5. VALIDACIONES ESPECÍFICAS DEL PROYECTO**

#### **Conformidad con Reglas del Proyecto:**
- [ ] **Todas las etiquetas en español** verificadas
- [ ] **Opciones Select/MultiSelect en español** verificadas  
- [ ] **Traducciones agregadas** a `/translations/es.csv` si necesario
- [ ] **Referencias a DocTypes** correctas (ej: Payment Term, no Payment Terms)

#### **Tests de Modificaciones Específicas:**
- [ ] **Campos modificados testados** (ej: distance Float→Select)
- [ ] **Nuevos campos testados** (ej: GPS coordinates, access control)
- [ ] **Estructura de pestañas verificada** si aplica
- [ ] **Precisión de campos** verificada (ej: decimales)

### **6. EJECUCIÓN Y VALIDACIÓN**

#### **Tests Ejecutan Sin Errores:**
- [ ] **bench run-tests individual:** 
  ```bash
  bench --site domika.dev run-tests --doctype "Nombre DocType"
  ```
- [ ] **Test runner personalizado:**
  ```bash
  python run_tests.py --doctype "Nombre DocType"
  ```
- [ ] **Bench run-tests completo:**
  ```bash
  bench --site domika.dev run-tests --app condominium_management
  ```

#### **Performance y Limpieza:**
- [ ] **Tests ejecutan rápido** (<30 segundos por DocType)
- [ ] **No dejan data residual** en la base de datos
- [ ] **No generan errores/warnings** durante ejecución

### **7. DOCUMENTACIÓN Y MANTENIMIENTO**

#### **Código Documentado:**
- [ ] **Docstrings en español** para todos los métodos
- [ ] **Comentarios explicativos** en lógica compleja
- [ ] **Variables con nombres descriptivos**

#### **Compatibilidad Futura:**
- [ ] **Fácil de extender** para nuevos campos
- [ ] **Helper methods reutilizables** 
- [ ] **Patterns consistentes** con otros tests del módulo

---

## 🚀 **COMANDOS DE VALIDACIÓN RÁPIDA**

### **Verificar Compliance Básico:**
```bash
# Contar archivos de test
find . -name "test_*.py" | grep companies/doctype | wc -l

# Verificar herencia correcta
grep -r "class.*FrappeTestCase" */companies/doctype/*/test_*.py

# Verificar setUpClass
grep -r "def setUpClass" */companies/doctype/*/test_*.py | wc -l

# Verificar super().setUpClass()
grep -r "super().setUpClass()" */companies/doctype/*/test_*.py | wc -l

# Verificar frappe.set_user
grep -r "frappe.set_user" */companies/doctype/*/test_*.py | wc -l
```

### **Ejecutar Test Específico:**
```bash
# Test individual completo
bench --site domika.dev run-tests --doctype "{NOMBRE_DOCTYPE}" --verbose

# Test runner con detalles
python run_tests.py --doctype "{NOMBRE_DOCTYPE}" --verbose
```

---

## ⚠️ **CRITERIOS DE RECHAZO**

**Un DocType NO se considera completo si:**

1. ❌ No tiene archivo de test
2. ❌ Tests fallan al ejecutar
3. ❌ No hereda de FrappeTestCase
4. ❌ No implementa setUpClass() correctamente
5. ❌ No tiene test_spanish_labels
6. ❌ Usa cleanup manual (doc.delete())
7. ❌ No verifica etiquetas en español
8. ❌ Deja data residual en la base de datos
9. ❌ No sigue el patrón establecido

---

## ✅ **CERTIFICACIÓN DE COMPLIANCE**

**Para certificar un DocType como COMPLIANT:**

1. **Ejecutar checklist completo** - todos los items ✅
2. **Ejecutar tests sin errores** - 100% success rate
3. **Revisar con test runner** - output limpio
4. **Validar performance** - <30 segundos ejecución
5. **Confirmar cleanup** - no data residual

**Una vez certificado, agregar al registro:**

| DocType | Fecha Certificación | Tests Count | Status |
|---------|-------------------|-------------|--------|
| Ejemplo DocType | 2025-06-28 | 8 tests | ✅ COMPLIANT |

---

**Responsable:** Desarrollador asignado  
**Revisor:** Lead Developer  
**Framework:** Frappe v15 - 100% Compliance Required  

**IMPORTANTE:** Este checklist es OBLIGATORIO y debe ser completado antes de considerar cualquier DocType como "terminado".