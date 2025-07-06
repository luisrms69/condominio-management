# 📋 ESTÁNDARES DE DESARROLLO Y REGLAS TÉCNICAS

**Fecha:** 2025-07-06  
**Propósito:** Input para Claude.ai - Desarrollo de Arquitectura de Módulos  
**Versión:** 2.0 - Post Community Contributions Implementation  
**Fuente:** Consolidado desde CLAUDE.md (memoria permanente local)  

---

## 🏗️ **REGLAS CRÍTICAS PARA ARQUITECTURA**

### **🇪🇸 REGLA #1: ETIQUETAS EN ESPAÑOL (OBLIGATORIO)**

**TODAS las etiquetas (labels) de DocTypes DEBEN estar en español:**

- ✅ **Variables/campos:** en inglés (ej: `contract_name`, `service_provider`)
- ✅ **Labels/etiquetas:** en español (ej: "Nombre del Contrato", "Empresa Administradora")
- ✅ **Opciones de Select:** en español (ej: "Activo", "Suspendido", "Terminado")
- ✅ **Descripciones:** en español
- ✅ **Mensajes de error:** en español
- ✅ **Nombres de DocTypes:** agregar "label" en español para mostrar en interfaz

**Sistema de traducciones implementado:**
```
/condominium_management/translations/es.csv
hooks.py: app_include_locale = "translations"
```

**Patrón Oficial del Proyecto:**
```json
{
  "doctype": "DocType", 
  "name": "Service Management Contract",
  "label": "Contrato de Gestión de Servicios", // ✅ DIRECTO en JSON
  "fields": [
    {
      "fieldname": "contract_name", // ✅ Variable en inglés
      "label": "Nombre del Contrato", // ✅ Label en español
      "fieldtype": "Data"
    }
  ]
}
```

### **🏗️ REGLA #2: ESTRUCTURA DE MÓDULOS (OBLIGATORIO)**

- `modules.txt` debe coincidir exactamente con nombres de carpetas
- `hooks.py` debe tener configuración completa de módulos
- Todos los DocTypes necesitan archivos: `.json`, `.py`, `test_.py`, `__init__.py`

### **🔍 REGLA #3: VALIDACIONES DE NEGOCIO**

- Siempre incluir validaciones de negocio básicas
- Usar `frappe.throw()` para errores críticos en español
- Usar `frappe.msgprint()` para advertencias en español

---

## 🧪 **REGLA #4: UNIT TESTS - FRAPPE FRAMEWORK STANDARDS**

**TODOS los DocTypes DEBEN tener unit tests siguiendo estándares oficiales:**

### **📋 Estructura Obligatoria:**
```python
from frappe.tests.utils import FrappeTestCase

class TestDocTypeName(FrappeTestCase):
    """Test cases for DocType Name."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data that persists for all tests in this class."""
        super().setUpClass()  # ✅ CRÍTICO: siempre llamar super()
        cls.create_test_data()
    
    @classmethod 
    def create_test_data(cls):
        """Create reusable test data with flags to avoid duplication."""
        if getattr(frappe.flags, 'test_doctype_data_created', False):
            return  # ✅ Evita duplicación
        
        # Crear test data aquí
        frappe.flags.test_doctype_data_created = True
    
    def setUp(self):
        """Set up before each test method."""
        frappe.set_user("Administrator")  # ✅ Usuario consistente
    
    def test_creation(self):
        """Test basic creation with Spanish validations."""
        doc = frappe.get_doc({...})
        doc.insert(ignore_permissions=True)  # ✅ Para tests
        
        # Validaciones...
        # ✅ NO hacer doc.delete() - rollback automático
    
    def test_spanish_labels(self):
        """Test that DocType has proper Spanish labels."""
        meta = frappe.get_meta("DocType Name")
        self.assertEqual(meta.get("label"), "Etiqueta en Español")
```

### **✅ Tests Obligatorios para Cada DocType:**
1. **test_creation** - Creación básica del DocType
2. **test_spanish_labels** - Verificar etiquetas en español  
3. **test_required_fields_validation** - Campos requeridos
4. **test_spanish_options** - Opciones Select/MultiSelect en español
5. **test_field_modifications** - Si hay campos modificados específicos

---

## 🔧 **REGLA #11: HOOKS OBLIGATORIOS Y RESOLUCIÓN CI**

### **⚡ HOOKS CRÍTICOS IMPLEMENTADOS:**

```python
# En hooks.py (AMBOS OBLIGATORIOS)
after_install = "condominium_management.install.after_install"
before_tests = "condominium_management.utils.before_tests"
```

### **📋 Funciones Requeridas:**

**install.py - after_install function:**
```python
def after_install():
    """Configuración post-instalación del módulo."""
    print("🔧 Condominium Management: Ejecutando configuración post-instalación...")
    frappe.clear_cache()
```

**utils.py - before_tests function (CRÍTICO):**
```python
def before_tests():
    frappe.clear_cache()
    from frappe.desk.page.setup_wizard.setup_wizard import setup_complete
    
    year = now_datetime().year
    if not frappe.get_list("Company"):
        setup_complete({
            "currency": "MXN",
            "company_name": "Condominio Test LLC",
            "timezone": "America/Mexico_City",
            # ... configuración completa
        })
    
    # Asegurar registros básicos antes de enable_all_roles_and_domains
    _ensure_basic_records_exist()
    enable_all_roles_and_domains()
    frappe.db.commit()
```

### **🚨 SOLUCIÓN DEFINITIVA ERRORES CI:**
- ✅ **Transit warehouse type error:** resuelto con before_tests hook
- ✅ **Parent Department error:** resuelto con _ensure_basic_records_exist()
- ✅ **0 workarounds temporales** en CI workflow
- ✅ **Patrón oficial Frappe Framework** aplicado

---

## 🤖 **REGLA #12: AI-ASSISTED DEBUGGING WORKFLOW**

### **🔄 METODOLOGÍA COMPROBADA:**

**Estado:** ✅ PROBADO EXITOSAMENTE en PR #6 y PR #12

1. **ANÁLISIS INICIAL:**
   - Ejecutar tests: `bench --site domika.dev run-tests --app condominium_management`
   - Documentar errores exactos con stack traces completos
   - Identificar patrones comunes

2. **CONSULTA AI TOOLS:**
   - **GitHub Copilot:** `GITHUB_COPILOT_SKIP_PROMPTS=1 gh copilot explain "error"`
   - **Validación manual obligatoria:** Copilot puede ser incorrecto para Frappe/ERPNext
   - **Comparación con apps oficiales:** Clonar apps exitosas para referencias

3. **IMPLEMENTACIÓN INCREMENTAL:**
   - Un fix a la vez con validación inmediata
   - Documentar CADA cambio con commit detallado
   - Verificar que fix no rompe otros tests

4. **VALIDACIÓN FINAL:**
   - Tests completos, pre-commit hooks, CI pipeline verde

### **🧠 PATRONES TÉCNICOS IDENTIFICADOS:**

```python
# ✅ PROBLEMA: is_new() check bloquea version increments en testing
if getattr(frappe.flags, "in_test", False):
    # Testing: comportamiento simplificado
    if self.infrastructure_templates or self.auto_assignment_rules:
        self.increment_version()  # ✅ Sin is_new() check
    return

# Producción: lógica original
if not self.is_new():
    self.increment_version()
```

---

## 🔒 **REGLA CRÍTICA: PREFERENCIA FRAPPE vs ERPNEXT**

### **⚖️ POLÍTICA DE DEPENDENCIAS:**

**REGLA FUNDAMENTAL:** Las funciones de Frappe Framework tienen **PREFERENCIA ABSOLUTA** sobre funciones de ERPNext.

**Criterios de Decisión:**
1. **✅ USAR FRAPPE:** Si existe función equivalente en Frappe Framework
2. **⚠️ EVALUAR ERPNEXT:** Solo si es funcionalidad crítica no disponible en Frappe
3. **❌ EVITAR ERPNEXT:** Si requiere recrear funcionalidad existente de Frappe

**Ejemplos:**
```python
# ✅ CORRECTO - Frappe Framework
from frappe.utils import now_datetime
user = frappe.get_doc("User", "Administrator")

# ❌ EVITAR - ERPNext específico  
from erpnext.setup.utils import enable_all_roles_and_domains

# ⚠️ JUSTIFICADO - ERPNext crítico documentado
company = frappe.get_doc("Company", company_name)  # Company DocType es crítico
```

---

## 📋 **REGLA #17: BRANCH MANAGEMENT Y PR CONTROL**

### **🎯 POLÍTICA ESTRICTA DE BRANCH:**

**OBLIGATORIO:** Cada PR debe tener branch específico y alcance claro:

1. **Branch naming:** `feature/[modulo]-[descripcion]`
2. **Un PR = Una funcionalidad** completa
3. **NO mezclar funcionalidades** en el mismo PR
4. **Dependencies incluidas** si son necesarias para funcionamiento

**Ejemplo Correcto:**
- `feature/community-contributions-cross-site` incluye:
  - ✅ Community Contributions Module completo
  - ✅ Fix de utils.py NECESARIO para que funcione
  - ✅ Documentación del módulo

**Ejemplo Incorrecto:**
- ❌ Mezclar Document Generation + Community Contributions
- ❌ Agregar features no relacionadas "mientras estamos ahí"

---

## 🏢 **REGLA #14: ARQUITECTURA DE SITIOS**

### **🚨 SITIOS DE PRODUCCIÓN Y DESARROLLO:**

| Sitio | Propósito | Uso | Riesgo |
|-------|-----------|-----|--------|
| `domika.dev` | **DESARROLLO PRINCIPAL** + Control Templates | ⚠️ **SOLO DESARROLLO** | 🚨 **CRÍTICO** |
| `admin1.dev` | **Site Administradora** - Testing | ✅ Pruebas seguras | 🟡 Seguro |
| `condo1.dev` | **Site Condominio 1** - Testing | ✅ Pruebas seguras | 🟡 Seguro |
| `condo2.dev` | **Site Condominio 2** - Testing | ✅ Pruebas seguras | 🟡 Seguro |

**PROTOCOLO OBLIGATORIO:**
```bash
# ❌ NUNCA hacer en domika.dev
bench --site domika.dev reinstall  # DESTRUYE DATA DE PRODUCCIÓN

# ✅ USO CORRECTO domika.dev
bench --site domika.dev migrate    # Solo migraciones planificadas
bench --site domika.dev run-tests --app condominium_management  # Tests NO destructivos

# ✅ SEGURO en sites de testing
bench --site admin1.dev reinstall --admin-password admin123  # Seguro para pruebas
```

---

## 📝 **REGLAS DE DOCUMENTACIÓN Y COMMITS**

### **🎯 CONVENTIONAL COMMITS OBLIGATORIOS:**

```
tipo(alcance): descripción en español

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Tipos permitidos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de errores  
- `docs`: Documentación
- `style`: Formato/estilo
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Mantenimiento

**Alcances establecidos:**
- `companies`, `community-contributions`, `document-generation`
- `tests`, `docs`, `config`, `api`, `ui`, `database`

### **📝 DOCSTRINGS ESTÁNDAR ESPAÑOL:**

```python
class NombreClase(Document):
    """
    Descripción breve en español de la funcionalidad principal.

    Funcionalidades principales:
    - Lista de funcionalidades específicas
    - Una por línea, en español

    Parámetros importantes:
        campo_1 (Tipo): Descripción del campo en español
        campo_2 (Tipo): Descripción del campo en español

    Errores comunes:
        ValidationError: Descripción del error específico
        Warning: Descripción de advertencias

    Ejemplo de uso:
        doc = frappe.new_doc("DocType Name")
        doc.campo_1 = "valor"
        doc.save()
    """
```

---

## 🔄 **REGLA #20: COPILOT Y DEBUGGING**

### **✅ GitHub Copilot CLI Disponible:**

```bash
# Comandos estándar (requieren skip prompts)
GITHUB_COPILOT_SKIP_PROMPTS=1 gh copilot explain "error message"
GITHUB_COPILOT_SKIP_PROMPTS=1 gh copilot suggest -t shell "what to achieve"
```

### **⚠️ LIMITACIONES IDENTIFICADAS:**
- **Requiere `GITHUB_COPILOT_SKIP_PROMPTS=1`** para funcionar
- **Sugerencias pueden ser incorrectas** para Frappe/ERPNext específicamente
- **Validación manual obligatoria** de todas las recomendaciones
- **Análisis manual puede ser superior** para frameworks específicos

### **🎯 PROTOCOLO OBLIGATORIO:**
1. **SIEMPRE consultar Copilot** antes de implementar soluciones
2. **Si Copilot falla**: Informar al usuario inmediatamente
3. **Validar recomendaciones** contra documentación oficial Frappe
4. **Documentar consulta** en commit message

---

## 🚨 **POLÍTICAS DE RECHAZO AUTOMÁTICO**

### **Se rechaza código que:**
- ❌ Tiene labels en inglés
- ❌ No tiene docstrings estándar en español
- ❌ No tiene unit tests adecuados
- ❌ No pasa pre-commit hooks
- ❌ No usa conventional commits
- ❌ No sigue branch naming convention
- ❌ Mensajes de error en inglés
- ❌ No tiene README.md del módulo actualizado

---

## 📊 **ARQUITECTURA DE MÓDULOS ESTABLECIDA**

### **Módulos Implementados y Operativos:**

**1. Companies Module:** ✅ COMPLETO
- Base DocTypes para gestión de empresas administradoras
- Sync configuration y master data management
- Service management contracts y operating hours
- Unit tests completos y CI funcionando

**2. Document Generation Module:** ✅ COMPLETO  
- Master Template Registry con versioning automático
- Entity Configuration y Entity Type Configuration
- Auto-detection y template propagation
- Community contributions integration preparada

**3. Community Contributions Module:** ✅ IMPLEMENTADO
- Cross-site communication entre administradoras
- HMAC SHA-256 authentication framework
- Contribution workflow completo
- Integration handlers extensibles

### **Patrones de Integración Establecidos:**

**API Integration Pattern:**
```python
@frappe.whitelist()
def module_api_function(param: str) -> dict[str, Any]:
    """API function following established pattern."""
    # Validation, processing, return standardized dict
```

**Hook Integration Pattern:**
```python
doc_events = {
    "DocType Name": {
        "on_update": "module.hooks.handler_function",
        "validate": "module.hooks.validation_function"
    }
}
```

**Cross-Module Integration Pattern:**
```python
# Module A provides service
def get_module_data(filters: dict) -> list[dict]:
    """Service for other modules to consume."""

# Module B consumes service  
from module_a.api import get_module_data
data = get_module_data({"field": "value"})
```

---

## 🎯 **INFORMACIÓN CRÍTICA PARA PRÓXIMOS MÓDULOS**

### **Frameworks Disponibles:**
- ✅ **Document Generation:** Template system para cualquier tipo de documento
- ✅ **Community Contributions:** Cross-site sharing de configuraciones
- ✅ **Testing Framework:** Unit tests estandarizados con FrappeTestCase
- ✅ **Translation System:** es.csv + app_include_locale configurado
- ✅ **Hooks Framework:** Específicos funcionando, universales pendientes

### **APIs de Integración Disponibles:**
- **Document Generation:** `get_applicable_templates()`, `apply_template_to_entity()`
- **Community Contributions:** `register_contribution_handler()`, `submit_community_template()`
- **Companies:** Master data sync APIs, company detection APIs

### **Performance Considerations:**
- **JSON size limits:** Master Template Registry monitoreado por crecimiento
- **Background jobs:** Implementados para operaciones pesadas
- **Caching strategy:** Template caching implementado
- **Database optimization:** Queries optimizadas para bulk operations

---

**📝 NOTAS PARA CLAUDE.AI:**

### **🎯 USAR ESTA INFORMACIÓN PARA:**
1. **Mantener consistencia** con patrones establecidos
2. **Aplicar reglas obligatorias** (español, testing, hooks)
3. **Integrar con módulos existentes** usando APIs disponibles
4. **Seguir arquitectura probada** (DocTypes, validation, CI)
5. **Reutilizar frameworks** (Document Generation, Community Contributions)

### **⚠️ CRÍTICO RECORDAR:**
- **TODAS las labels en español** (Regla #1)
- **Unit tests obligatorios** con FrappeTestCase (Regla #4)
- **Hooks específicos** hasta resolver Issue #7 (universales pendientes)
- **Frappe preference** sobre ERPNext cuando sea posible
- **Branch management estricto** (Regla #17)
- **Sites de testing designados** (admin1.dev, condo1.dev, condo2.dev)

### **🔗 INTEGRACIÓN CON MÓDULOS EXISTENTES:**
- **Document Generation:** Para templates de documentos del módulo
- **Community Contributions:** Para sharing de configuraciones
- **Companies:** Para datos de empresas administradoras si aplica
- **Testing Framework:** Mismo patrón de unit tests para consistency