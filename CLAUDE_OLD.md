# 🤖 CLAUDE - Notas del Proyecto Condominium Management

## 📋 **REGLAS CRÍTICAS DEL PROYECTO**

### **🇪🇸 REGLA #1: ETIQUETAS EN ESPAÑOL**
**TODAS las etiquetas (labels) de DocTypes DEBEN estar en español**

- ✅ **Variables/campos:** en inglés (ej: `contract_name`, `service_provider`)
- ✅ **Labels/etiquetas:** en español (ej: "Nombre del Contrato", "Empresa Administradora")
- ✅ **Opciones de Select:** en español (ej: "Activo", "Suspendido", "Terminado")
- ✅ **Descripciones:** en español
- ✅ **Mensajes de error:** en español
- ✅ **Nombres de DocTypes:** agregar "label" en español para mostrar en interfaz

**Aplicar SIEMPRE, incluso si las instrucciones vienen en inglés.**

#### **🌐 SISTEMA DE TRADUCCIONES IMPLEMENTADO**

Para que los DocTypes aparezcan en español en la interfaz se implementó:

1. **Archivo de traducciones:** `/condominium_management/translations/es.csv`
2. **Configuración en hooks.py:** `app_include_locale = "translations"`
3. **Compilación:** automática con `bench build`

**Estructura del archivo de traducciones:**
```csv
source,target
Companies,Empresas
Service Management Contract,Contrato de Gestión de Servicios
Condominium Information,Información del Condominio
```

**IMPORTANTE:** Para agregar nuevos DocTypes, SIEMPRE agregar la traducción correspondiente al archivo `es.csv`

#### **🎯 FILOSOFÍA HÍBRIDA DE LABELS CONFIRMADA:**

**Patrón Oficial del Proyecto (validado en módulo Companies):**

1. **Campo "label" DIRECTO en DocTypes principales:**
   ```json
   {
     "doctype": "DocType", 
     "name": "Entity Type Configuration",
     "label": "Configuración de Tipo de Entidad",  // ✅ DIRECTO en JSON
     // ...
   }
   ```

2. **es.csv como COMPLEMENTO:**
   ```csv
   Entity Type Configuration,Configuración de Tipo de Entidad
   ```

3. **Todos los campos internos en español:**
   ```json
   {"fieldname": "entity_doctype", "label": "Tipo de Entidad DocType"}
   {"options": "Activo\nSuspendido\nTerminado"}
   ```

**REGLA:** Usar AMBOS métodos - campo "label" directo + entrada en es.csv

#### Ejemplos Correctos:
```json
// DocType con label en español
{
  "doctype": "DocType",
  "name": "Service Management Contract",    // ✅ Name técnico en inglés
  "label": "Contrato de Gestión de Servicios", // ✅ Label en español para interfaz
  "module": "Companies"
}

// Campo con label en español
{
  "fieldname": "contract_name",        // ✅ Variable en inglés
  "fieldtype": "Data",
  "label": "Nombre del Contrato",      // ✅ Label en español
  "reqd": 1
}

// Select con opciones en español
{
  "fieldname": "contract_status",
  "fieldtype": "Select", 
  "label": "Estado del Contrato",      // ✅ Label en español
  "options": "Activo\nSuspendido\nTerminado"  // ✅ Opciones en español
}
```

#### Ejemplos Incorrectos:
```json
{
  "fieldname": "contract_name",
  "label": "Contract Name",           // ❌ Label en inglés
}

{
  "fieldname": "status",
  "label": "Estado",                  // ✅ Label correcto
  "options": "Active\nSuspended"      // ❌ Opciones en inglés
}
```

### **🏗️ REGLA #2: ESTRUCTURA DE MÓDULOS**
- `modules.txt` debe coincidir exactamente con nombres de carpetas
- `hooks.py` debe tener configuración completa de módulos
- Todos los DocTypes necesitan archivos: `.json`, `.py`, `test_.py`, `__init__.py`

### **🔍 REGLA #3: VALIDACIONES**
- Siempre incluir validaciones de negocio básicas
- Usar `frappe.throw()` para errores críticos
- Usar `frappe.msgprint()` para advertencias

### **🧪 REGLA #4: UNIT TESTS - MEJORES PRÁCTICAS FRAPPE**
**TODOS los DocTypes DEBEN tener unit tests siguiendo estándares oficiales de Frappe Framework**

#### **📋 Estructura Obligatoria de Tests:**
```python
# Header estándar
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
    
    def tearDown(self):
        """Clean up after each test method."""
        frappe.set_user("Administrator")  # ✅ Reset usuario
        # ✅ FrappeTestCase maneja rollback automáticamente
```

#### **✅ Tests Obligatorios para Cada DocType:**
1. **test_creation** - Creación básica del DocType
2. **test_spanish_labels** - Verificar etiquetas en español  
3. **test_required_fields_validation** - Campos requeridos
4. **test_spanish_options** - Opciones Select/MultiSelect en español
5. **test_field_modifications** - Si hay campos modificados específicos

#### **🚫 Errores Comunes a Evitar:**
```python
# ❌ INCORRECTO
class TestDocType(unittest.TestCase):  # Usar FrappeTestCase
    def setUp(self):
        pass  # Sin configurar usuario
    
    def test_something(self):
        doc.insert()
        doc.delete()  # No hacer cleanup manual
        frappe.db.rollback()  # FrappeTestCase lo maneja

# ✅ CORRECTO  
class TestDocType(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # Llamar super()
    
    def setUp(self):
        frappe.set_user("Administrator")
    
    def test_something(self):
        doc.insert(ignore_permissions=True)
        # FrappeTestCase maneja rollback automático
```

#### **🎯 Comandos de Ejecución:**
```bash
# Todos los tests del módulo
bench --site domika.dev run-tests --app condominium_management

# Test específico por DocType
bench --site domika.dev run-tests --doctype "Nombre DocType"

# Test runner personalizado
python run_tests.py --doctype "Nombre DocType"
```

#### **📊 Validación de Compliance:**
Para cada nuevo DocType, verificar:
- ✅ Archivo `test_doctype.py` existe
- ✅ Hereda de `FrappeTestCase`
- ✅ Implementa `setUpClass()` con `super().setUpClass()`
- ✅ Usa `frappe.set_user("Administrator")` en setUp/tearDown
- ✅ Usa flags para evitar duplicación de test data
- ✅ No hace cleanup manual (confía en rollback automático)
- ✅ Testa etiquetas en español
- ✅ Ejecuta sin errores con `bench run-tests`

**IMPORTANTE:** Cada DocType nuevo DEBE seguir estos patrones antes de considerarse completo.

---

## 📝 **COMANDOS FRECUENTES**

```bash
# Verificar estructura
cat condominium_management/modules.txt
ls condominium_management/companies/doctype/

# Migrar cambios
bench --site domika.dev migrate
bench --site domika.dev build
bench restart

# Verificar DocTypes en sistema
bench --site domika.dev console
>>> frappe.get_all("DocType", filters={"module": "Companies"})

# ========================================
# COMANDOS DE TESTING
# ========================================

# Ejecutar todos los tests del módulo
bench --site domika.dev run-tests --app condominium_management

# Tests por DocType específico
bench --site domika.dev run-tests --doctype "Service Management Contract"
bench --site domika.dev run-tests --doctype "Access Point Detail"

# Test específico de método
bench --site domika.dev run-tests --module condominium_management.companies.doctype.nearby_reference.test_nearby_reference --test test_distance_field_options

# Test runner personalizado (desde directorio de la app)
python run_tests.py                                    # Todos los tests
python run_tests.py --verbose                          # Modo verbose
python run_tests.py --doctype "Nearby Reference"       # DocType específico

# Verificar compliance de tests
ls */doctype/*/test_*.py | wc -l                       # Contar archivos de test
grep -r "class.*FrappeTestCase" */doctype/*/test_*.py  # Verificar herencia correcta
grep -r "setUpClass" */doctype/*/test_*.py             # Verificar setUpClass

# ========================================
# COMANDOS HOOKS CRÍTICOS (REGLA #11)
# ========================================

# Verificar hooks obligatorios están habilitados
grep "after_install.*=" condominium_management/hooks.py
grep "before_tests.*=" condominium_management/hooks.py

# Verificar archivos de hooks existen
ls condominium_management/install.py condominium_management/utils.py

# Test completo con hooks (debe funcionar sin errores)
bench --site test_site set-config allow_tests true
bench --site test_site run-tests --app condominium_management

# Verificar CI sin workarounds temporales
grep -i "temporary\|workaround" .github/workflows/ci.yml || echo "✅ CI limpio"

# ========================================
# COMANDOS DE TRADUCCIONES
# ========================================

# Compilar traducciones
bench --site domika.dev build

# Verificar archivo de traducciones
cat condominium_management/translations/es.csv

# Verificar configuración de traducciones en hooks
grep "app_include_locale" condominium_management/hooks.py
```

---

## 🎯 **NOTAS DE DESARROLLO**

- **Proyecto:** Sistema integral de gestión de condominios
- **Cliente:** Buzola
- **Framework:** Frappe v15 / ERPNext
- **Idioma de interfaz:** Español (México)
- **Moneda base:** MXN

---

## 📚 **RECURSOS Y TEMPLATES**

### **Templates para Desarrollo:**
- **`TEMPLATE_DOCTYPE_TEST.py`** - Plantilla obligatoria para unit tests de nuevos DocTypes
- **`CHECKLIST_COMPLIANCE_TESTS.md`** - Checklist obligatorio antes de completar cualquier DocType

### **Documentación Técnica:**
- **`DOCUMENTACION_UNIT_TESTS.md`** - Documentación completa de tests implementados
- **`MEJORAS_UNIT_TESTS_FRAPPE.md`** - Análisis y mejoras aplicadas según Frappe Framework
- **`DOCUMENTACION_CAMPOS_DOCTYPES.md`** - Referencia técnica de todos los campos modificados

### **Reportes de Implementación:**
- **`REPORTE_MODIFICACIONES_IDIOMA_ES.md`** - Reporte completo de sistema de traducciones
- **`run_tests.py`** - Test runner personalizado con opciones avanzadas

### **Archivos de Configuración:**
- **`/translations/es.csv`** - Traducciones al español para la interfaz
- **`hooks.py`** - Configuración de traducciones y módulos

---

## 🔄 **PROCESO PARA NUEVOS DOCTYPES**

### **Pasos Obligatorios:**
1. **Crear DocType** con labels en español
2. **Copiar `TEMPLATE_DOCTYPE_TEST.py`** y adaptarlo
3. **Implementar todos los tests** según template
4. **Ejecutar `CHECKLIST_COMPLIANCE_TESTS.md`** completo
5. **Agregar traducciones** a `es.csv` si necesario
6. **Verificar ejecución** con `bench run-tests`
7. **Documentar modificaciones** específicas

### **Validación Final:**
```bash
# Ejecutar tests específicos
bench --site domika.dev run-tests --doctype "Nuevo DocType"

# Verificar compliance
python run_tests.py --doctype "Nuevo DocType" --verbose

# Confirmar traducciones
bench --site domika.dev build
```

**IMPORTANTE:** Ningún DocType se considera COMPLETO sin pasar el checklist de compliance al 100%.

---

## 🛠️ **REGLA #5: HERRAMIENTAS Y WORKFLOW INSTALADAS**

### **🔧 VS Code Extensions Configuradas:**
- ✅ **GitLens** (`eamodio.gitlens`) - Control avanzado de Git y historial
- ✅ **Conventional Commits** (`vivaxy.vscode-conventional-commits`) - Commits estandarizados
- ✅ **autoDocstring** (`njpwerner.autodocstring`) - Generación automática de docstrings
- ✅ **Python** (`ms-python.python`) - Soporte completo de Python
- ✅ **Black Formatter** (`ms-python.black-formatter`) - Formato automático de código
- ✅ **Flake8** (`ms-python.flake8`) - Linting de Python
- ✅ **Prettier** (`esbenp.prettier-vscode`) - Formato de JS/CSS/HTML

### **⚙️ Configuración VS Code (`.vscode/settings.json`):**
```json
{
    "autoDocstring.docstringFormat": "sphinx",
    "autoDocstring.startOnNewLine": false,
    "autoDocstring.includeExtendedSummary": true,
    "autoDocstring.guessTypes": true,
    "conventionalCommits.scopes": [
        "companies", "tests", "docs", "config", "api", "ui", "database", "sync", "validation"
    ],
    "editor.formatOnSave": true,
    "python.formatting.provider": "black"
}
```

### **🔄 Pre-commit Hooks Activos:**
- ✅ **Ruff Import Sorter** - Sorting de imports (--select=I --fix)
- ✅ **Ruff Linter** - Linting completo de Python
- ✅ **Ruff Format** - Formato automático de código Python (reformatea líneas largas)
- ✅ **Prettier** - Formato de archivos JavaScript/Vue/SCSS
- ✅ **ESLint** - Linting de JavaScript (modo --quiet)
- ✅ **Trailing whitespace** - Eliminación de espacios en blanco (excluye json/txt/csv/md/svg)
- ✅ **Check merge conflicts** - Detección de conflictos de merge
- ✅ **Check JSON/YAML/TOML** - Validación de sintaxis
- ✅ **Check AST** - Validación de sintaxis Python
- ✅ **Debug statements** - Detección de declaraciones debug

### **📋 Exclusiones y Configuraciones:**
- **Tests excluidos:** `condominium_management/tests/` de ruff checks
- **Archivos excluidos:** `node_modules`, `dist`, `boilerplate`, `lib` de prettier/eslint
- **Formato ruff:** Reformatea automáticamente líneas largas en múltiples líneas
- **Auto-update:** Hooks se actualizan semanalmente

### **📋 REGLA #6: CONVENTIONAL COMMITS OBLIGATORIOS**

**Formato requerido:**
```
tipo(alcance): descripción en español

Cuerpo opcional explicando el "por qué" en español.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Tipos permitidos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de errores  
- `docs`: Documentación
- `style`: Formato/estilo (no cambios de código)
- `refactor`: Refactorización de código
- `test`: Agregar/modificar tests
- `chore`: Tareas de mantenimiento

**Alcances establecidos:**
- `companies`: Módulo Companies
- `tests`: Unit tests
- `docs`: Documentación
- `config`: Configuración
- `api`: APIs y endpoints
- `ui`: Interfaz de usuario
- `database`: Base de datos
- `sync`: Sincronización
- `validation`: Validaciones

### **📝 REGLA #7: DOCSTRINGS ESTÁNDAR ESPAÑOL**

**Formato obligatorio para todas las clases y métodos:**
```python
class NombreClase(Document):
    """
    Descripción breve en español de la funcionalidad principal.

    Funcionalidades principales:
    - Lista de funcionalidades específicas
    - Una por línea, en español
    - Describir propósito y capacidades

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
    
    def metodo(self):
        """
        Descripción del método en español.
        
        Explicación detallada del propósito y funcionamiento.
        
        Args:
            parametro (tipo): Descripción del parámetro
            
        Returns:
            tipo: Descripción del valor retornado
            
        Raises:
            ExceptionType: Descripción de cuándo ocurre la excepción
        """
```

### **✅ Workflow de Desarrollo Establecido:**

1. **Antes de Codificar:**
   - Crear/actualizar TODO list con `TodoWrite`
   - Marcar tarea como `in_progress`
   - Entender requerimientos en español

2. **Durante el Desarrollo:**
   - Código: Seguir convenciones existentes
   - Labels: Siempre en español
   - Docstrings: Formato estándar establecido
   - Tests: Crear tests obligatorios

3. **Antes del Commit:**
   - Ejecutar tests: `bench run-tests --app condominium_management`
   - Verificar pre-commit: `pre-commit run --all-files`
   - Usar VS Code Conventional Commits extension
   - Completar tareas en TODO list

4. **Commit:**
   - Usar extensión Conventional Commits en VS Code
   - Mensaje descriptivo en español
   - Incluir firma Claude Code

### **🚨 Políticas de Rechazo Automático:**

**Se rechaza código que:**
- ❌ Tiene labels en inglés
- ❌ No tiene docstrings estándar en español
- ❌ No tiene unit tests
- ❌ No pasa pre-commit hooks
- ❌ No usa conventional commits
- ❌ Mensajes de error en inglés
- ❌ No actualiza TODO list
- ❌ No sigue formato de docstrings establecido

### **📄 Archivos de Política Creados:**
- ✅ **`DEVELOPMENT_POLICIES.md`** - Políticas completas de desarrollo
- ✅ **`.vscode/settings.json`** - Configuración VS Code optimizada
- ✅ **`.pre-commit-config.yaml`** - Configuración hooks (ya existía)

### **🔧 Comandos de Validación:**
```bash
# Verificar herramientas instaladas
code --list-extensions | grep -E "(gitlens|conventional|autodocstring)"
pre-commit --version

# Ejecutar validaciones
pre-commit run --all-files
bench --site domika.dev run-tests --app condominium_management

# Verificar configuración
cat .vscode/settings.json
cat DEVELOPMENT_POLICIES.md
```

**TODAS estas herramientas y políticas están ahora integradas y deben ser utilizadas en TODO momento durante el desarrollo.**

---

## 🔧 **REGLA #11: HOOKS OBLIGATORIOS Y RESOLUCIÓN DE PROBLEMAS CI**

### **⚡ HOOKS CRÍTICOS IMPLEMENTADOS (Commits afdd594, 48aad1c, 8d3cc46)**

**PROBLEMA RESUELTO DEFINITIVAMENTE:** Transit warehouse type error en CI

#### **🎯 Hooks Obligatorios para Apps Frappe:**
```python
# En hooks.py (AMBOS OBLIGATORIOS)
after_install = "condominium_management.install.after_install"
before_tests = "condominium_management.utils.before_tests"
```

#### **📋 Funciones Requeridas:**

**1. install.py - after_install function:**
```python
def after_install():
    """Configuración post-instalación del módulo."""
    print("🔧 Condominium Management: Ejecutando configuración post-instalación...")
    # Verificar que ERPNext esté correctamente instalado
    # Limpiar cache para asegurar configuración fresca
    frappe.clear_cache()
```

**2. utils.py - before_tests function (CRÍTICO):**
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
    
    enable_all_roles_and_domains()
    frappe.db.commit()
```

#### **✅ RESULTADO VERIFICADO:**
- ✅ CI ejecuta `bench run-tests --app condominium_management` exitosamente
- ✅ 0 workarounds temporales en CI workflow
- ✅ Warehouse types (incluido Transit) se crean automáticamente
- ✅ Patrón oficial de Frappe Framework aplicado

### **🧠 METODOLOGÍA DE RESOLUCIÓN DE PROBLEMAS CI**

#### **📊 Patrón Probado Exitoso:**
1. **Análisis Comparativo:** Clonar app oficial exitosa (lending app)
2. **Comparación Sistemática:** hooks.py, install.py, utils.py, workflows
3. **Identificar Diferencias Críticas:** Hooks missing vs hooks implementados
4. **Implementación Incremental:** Un hook a la vez, validar en CI
5. **Verificación Completa:** 0 fixes temporales, funcionalidad completa

#### **🚨 Errores Críticos Evitados:**
- ❌ NUNCA crear workarounds temporales complejos en CI
- ❌ NUNCA especificar DocTypes individuales vs usar `--app` flag
- ❌ NUNCA inventar soluciones custom sin revisar apps oficiales
- ✅ SIEMPRE replicar patrones de apps oficiales exitosas

#### **📍 Apps de Referencia Oficiales:**
- `/home/erpnext/lending-comparison/lending/` - Patrón de hooks implementado
- Frappe official apps en GitHub - Para consulta de patrones

### **🔍 COMMITS DE SOLUCIÓN DOCUMENTADOS:**
- **afdd594:** after_install hook implementado
- **48aad1c:** Eliminar TEMPORARY FIX y resolver conflictos
- **8d3cc46:** before_tests hook implementado (SOLUCIÓN DEFINITIVA)

**IMPORTANTE:** Esta metodología debe aplicarse a TODOS los problemas CI futuros en los 12 módulos restantes.

#### **📝 SOLUCIÓN TRANSIT WAREHOUSE TYPE DOCUMENTADA:**

**Error común:** `LinkValidationError: Could not find Warehouse Type: Transit`

**Solución definitiva (basada en módulo Companies exitoso):**
1. **Hooks obligatorios implementados:** `after_install` y `before_tests`
2. **Función `before_tests()` usa `setup_complete()`** para configuración completa ERPNext
3. **Fallback robusto:** `_create_basic_warehouse_types()` si falla setup_complete
4. **Warehouse types creados:** Stores, Work In Progress, Finished Goods, Transit
5. **Patrón oficial Frappe Framework** - validado en lending app

**NO usar workarounds temporales** - siempre aplicar solución completa.

---

## 🏗️ **REGLA #8: WORKFLOW DE GESTIÓN Y DOCUMENTACIÓN v2.0**

### **📋 Metodología Oficial del Proyecto**

**Estado:** ✅ APROBADO - Versión 2.0  
**Aplicable a:** TODO el desarrollo del proyecto  
**Enfoque:** Documentación automatizada + Gestión de GitHub + Generación de manuales

### **🔄 Workflow por Módulo (13 módulos totales):**

#### **1. Desarrollo + Testing + Documentación Integrada:**
- ✅ **Unit Tests**: Generar con Claude Code (30 min por módulo)
- ✅ **Desarrollo**: Implementar funcionalidades siguiendo estándares
- ✅ **Docstrings obligatorios**: Formato estándar español establecido
- ✅ **Documentación en código**: Comentarios explicativos en lógica compleja

#### **2. Documentación Modular:**
- ✅ **README.md del módulo**: Documentar funcionalidades principales
- ✅ **Verificación de etiquetas**: Todas las interfaces en español
- ✅ **Comentarios**: Explicar lógica de negocio compleja

#### **3. Control de Calidad:**
- ✅ **Pull Request obligatorio** con checklist de documentación y testing
- ✅ **Code Review**: Verificar documentación y tests completos
- ✅ **CI/CD**: Tests automáticos + validación + verificación docstrings

### **📚 Herramienta de Documentación Final: Docusaurus**

#### **Fuentes Automáticas:**
1. **Docstrings de Python** → API Documentation automática
2. **README.md de módulos** → Manual de Usuario automático
3. **Metadatos de DocTypes** → Especificaciones Técnicas automáticas

#### **Resultado Final:**
- ✅ **Manual Técnico**: APIs, especificaciones, arquitectura
- ✅ **Manual de Usuario**: Guías paso a paso, casos de uso
- ✅ **Manual de Administrador**: Configuración, mantenimiento

### **⏱️ Cronograma de Implementación:**

#### **✅ Inmediato (Completado esta semana):**
- ✅ **VS Code extensions instaladas** (GitLens, Conventional Commits, autoDocstring)
- ✅ **Pre-commit hooks configurados** (Ruff, Prettier, ESLint)
- ✅ **Estándares de docstrings establecidos** y templates creados
- ✅ **Sistema de unit tests uniformes** configurado
- ✅ **Ambiente de desarrollo** optimizado

#### **🔄 Por Módulo (Desarrollo iterativo):**
- [ ] Unit tests + docstrings (Claude Code - 30 min)
- [ ] README.md actualizado (Manual - 1 hora)
- [ ] PR con documentación completa (15 min)
- [ ] **Total por módulo: 2.5 horas**

#### **📅 Pendiente (Setup GitHub + Final):**
- [ ] **Configurar GitHub repository** (settings, templates, labels, boards)
- [ ] **Crear issue templates** (.github/ folder)
- [ ] **Configurar Project Boards** con automatización
- [ ] **Setup Docusaurus** (último mes del proyecto)
- [ ] **Generación manual final** (6 días concentrados al final)

### **💼 Inversión de Tiempo:**
- **Por módulo**: 2.5 horas × 13 módulos = **32.5 horas** (distribuidas en 6 meses)
- **Setup inicial**: 2 días (una sola vez)
- **Generación final**: 6 días (concentrados al final)
- **Total proyecto**: ~40 horas setup + documentación + tests
- **ROI**: 40h invertidas vs 150-200h alternativa manual

---

## 🔧 **REGLA #9: GITHUB ENHANCEMENT Y GESTIÓN AUTOMATIZADA**

### **📋 Issue Management y Templates:**

#### **Estructura de Templates (.github/ISSUE_TEMPLATE/):**
```
├── bug_report.md - Reporte de errores con pasos de reproducción
├── feature_request.md - Solicitudes con user stories
├── documentation.md - Updates de documentación
├── module_development.md - Desarrollo de nuevos módulos
└── question.md - Preguntas y consultas técnicas
```

#### **Sistema de Labels Estratificado:**
- **Tipo**: `bug`, `feature`, `docs`, `refactor`, `question`
- **Prioridad**: `critical`, `high`, `medium`, `low`
- **Módulo**: `companies`, `physical-spaces`, `residents`, `maintenance`
- **Estado**: `needs-review`, `in-progress`, `blocked`, `ready-to-test`
- **Effort**: `easy`, `medium`, `hard` (para planning)

### **🔄 Project Boards Automáticos:**

#### **Workflow Configuration:**
- **Columnas**: Backlog → In Progress → Review → Testing → Done
- **Automatización**: Issues y PRs se mueven automáticamente según labels
- **Milestones**: Organizados por módulo y releases
- **Sprint Planning**: Boards por iteración de 2 semanas

#### **Reglas de Automatización:**
- Issue `in-progress` → Mueve a "In Progress"
- PR creado → Mueve issue relacionado a "Review"
- PR merged → Mueve a "Done"
- Issue `blocked` → Resalta en rojo

### **🔒 Security y Compliance Automático:**

#### **Configuraciones de Seguridad:**
- **Dependabot**: Updates automáticos de dependencias críticas
- **Code Scanning**: Análisis de vulnerabilidades en cada commit
- **Secret Scanning**: Previene commits accidentales de API keys
- **License Compliance**: Verificación automática GPL v3

#### **Branch Protection Avanzado:**
- **Require conversation resolution**: Todos los comments resueltos antes de merge
- **Dismiss stale reviews**: Re-approval requerido en cambios nuevos
- **Restrict force push**: Previene reescritura de historial
- **Linear history**: Mantiene historial limpio y navegable

---

## 🎯 **REGLA #10: BRANCH NAMING Y CONTROL DE CALIDAD**

### **📝 Convenciones de Naming:**

#### **Branch Naming Convention:**
```
feature/[módulo]-[descripción]
fix/[módulo]-[descripción]
docs/[módulo]-[descripción]
test/[módulo]-[descripción]

Ejemplos:
feature/companies-service-contracts
fix/companies-sync-validation
docs/companies-api-documentation
test/companies-unit-tests
```

#### **PR Title Format:**
```
[TIPO](módulo): Descripción clara del cambio

Ejemplos:
[FEAT](companies): Implementar gestión de contratos de servicio
[FIX](companies): Resolver problema de sincronización duplicada
[DOCS](companies): Completar documentación de APIs
```

### **⚡ GitHub Actions para Validación:**
- **Commit message validation**: Rechaza commits mal formateados
- **Branch naming validation**: Valida nombres de ramas
- **PR title validation**: Valida títulos de PR
- **Changelog generation**: Genera changelog automático desde commits

### **🔧 Configuración de Repositorio:**
- **Squash and merge**: Mantiene historial limpio
- **Delete branch after merge**: Limpieza automática
- **Linear history**: Evita merge commits confusos

---

## ✅ **CRITERIOS DE ÉXITO ESTABLECIDOS**

### **🎯 Métricas de Compliance:**
- ✅ Todos los commits siguen conventional commits
- ✅ Todos los PRs pasan checklist completo
- ✅ 100% cobertura de tests en nuevos módulos
- ✅ Issues organizados automáticamente en project boards
- ✅ Documentación generada automáticamente desde código
- ✅ Zero manual work en gestión de proyecto

### **📊 Control de Calidad por Módulo:**
- ✅ Unit tests ejecutan en <30 segundos
- ✅ Docstrings completos en formato estándar
- ✅ README.md actualizado con funcionalidades
- ✅ Labels en español verificados
- ✅ Pre-commit hooks pasan al 100%
- ✅ Code review aprobado
- ✅ Documentation completa

---

## 🚨 **POLÍTICAS DE RECHAZO ACTUALIZADAS**

### **Se rechaza automáticamente código que:**
- ❌ Tiene labels en inglés
- ❌ No tiene docstrings estándar en español
- ❌ No tiene unit tests adecuados
- ❌ No pasa pre-commit hooks
- ❌ No usa conventional commits
- ❌ No sigue branch naming convention
- ❌ PR sin checklist completo
- ❌ Mensajes de error en inglés
- ❌ No actualiza TODO list
- ❌ No tiene README.md del módulo actualizado

---

## 📋 **RECURSOS Y DOCUMENTACIÓN ACTUALIZADA**

### **📁 Archivos de Configuración del Proyecto:**
- ✅ **`DEVELOPMENT_POLICIES.md`** - Políticas completas de desarrollo
- ✅ **`.vscode/settings.json`** - Configuración VS Code optimizada
- ✅ **`.pre-commit-config.yaml`** - Configuración hooks
- [ ] **`.github/ISSUE_TEMPLATE/`** - Templates estructurados (pendiente)
- [ ] **`.github/workflows/`** - GitHub Actions (pendiente)
- [ ] **`docusaurus.config.js`** - Configuración documentación final (pendiente)

### **🔧 Comandos de Validación Actualizados:**
```bash
# Verificar herramientas instaladas
code --list-extensions | grep -E "(gitlens|conventional|autodocstring)"
pre-commit --version

# Ejecutar validaciones completas
pre-commit run --all-files
bench --site domika.dev run-tests --app condominium_management

# Verificar configuración del proyecto
cat .vscode/settings.json
cat DEVELOPMENT_POLICIES.md
ls .github/ISSUE_TEMPLATE/ 2>/dev/null || echo "Templates pendientes"

# Validar estructura de módulo
ls */README.md 2>/dev/null | wc -l  # Contar README por módulo
find . -name "test_*.py" | wc -l    # Contar archivos de test
```

### **🎯 Estado de Implementación:**
- ✅ **Fase 1**: Herramientas de desarrollo (VS Code + pre-commit) - COMPLETADO
- ✅ **Fase 2**: Estándares y políticas de código - COMPLETADO
- ✅ **Fase 3**: Docstrings y testing framework - COMPLETADO
- 🔄 **Fase 4**: GitHub enhancement - EN PROGRESO (pendiente setup)
- 📅 **Fase 5**: Documentación final con Docusaurus - PLANIFICADO (último mes)

---

---

## 🚨 **FUNCIONALIDAD PENDIENTE CRÍTICA**

### **⚠️ HOOKS UNIVERSALES DESACTIVADOS TEMPORALMENTE**

**Estado:** Desactivados en PR #6 para resolver errores de CI  
**Prioridad:** CRÍTICA - Debe resolverse inmediatamente post-merge  
**Issue:** #7 - Reactivar hooks universales con verificaciones de contexto  
**Estimación:** 3 horas de desarrollo + testing  

#### **Funcionalidad Afectada:**
- ❌ **Auto-detección automática** de entidades que requieren templates
- ❌ **Validación automática** de configuraciones al crear documentos
- ❌ **Propagación automática** de templates a nuevas entidades
- ❌ **Detección de conflictos** en tiempo real

#### **Impacto Temporal:**
- Las administradoras deben configurar entidades **manualmente**
- Pérdida de automatización en el workflow de templates
- Framework core sigue funcionando (DocTypes, APIs, workflows)

#### **Solución Planificada:**
```python
# Implementar hooks condicionales que eviten setup wizard
def on_document_insert_conditional(doc, method):
    if frappe.flags.in_install or frappe.flags.in_setup_wizard:
        return
    # Ejecutar funcionalidad normal...
```

**ARCHIVO DE DOCUMENTACIÓN:** `PENDING_FUNCTIONALITY_ISSUE.md`

---

---

## 🔒 **REGLA CRÍTICA DE WORKFLOW**

### **⚠️ POLÍTICA DE PUSH A REPOSITORIO REMOTO**

**NUEVA REGLA ESTABLECIDA:** Los push al repositorio remoto DEBEN ser revisados por el usuario antes del envío.

**PROCESO OBLIGATORIO:**
1. ✅ Preparar commits localmente
2. ✅ Mostrar cambios al usuario para revisión
3. ⚠️ **ESPERAR APROBACIÓN** antes de hacer push
4. ✅ Solo hacer push después de confirmación explícita del usuario

**EXCEPCIONES:**
- Solo si el usuario indica explícitamente en la conversación que puede hacer push automáticamente
- En caso de urgencia crítica con autorización previa

**APLICABLE A:**
- Todos los commits y push a repositorio remoto
- Especialmente cambios que afectan CI/CD
- Modificaciones a archivos de configuración críticos

---

**Última actualización:** 3 de julio de 2025  
**Compliance Level:** Frappe Framework v15 + VS Code Extensions + Pre-commit + Workflow v2.0 - 95% ✅  
**Metodología:** Documentación automatizada + GitHub management + Generación final de manuales  
**Estado:** ✅ APROBADO - Implementación en progreso | ⚠️ FUNCIONALIDAD PENDIENTE CRÍTICA

---

## 🔒 **REGLA CRÍTICA: PREFERENCIA FRAPPE vs ERPNEXT**

### **⚖️ POLÍTICA DE DEPENDENCIAS ESTABLECIDA**

**REGLA FUNDAMENTAL:** Las funciones de Frappe Framework tienen **PREFERENCIA ABSOLUTA** sobre funciones de ERPNext.

#### **📋 CRITERIOS DE DECISIÓN:**

1. **✅ USAR FRAPPE:** Si existe función equivalente en Frappe Framework
2. **⚠️ EVALUAR ERPNEXT:** Solo si es funcionalidad crítica no disponible en Frappe
3. **❌ EVITAR ERPNEXT:** Si requiere recrear funcionalidad existente de Frappe

#### **🎯 IMPLEMENTACIÓN:**

- **Preferencia 1:** Funciones nativas de `frappe.*`
- **Preferencia 2:** DocTypes de Frappe Core (`User`, `Role`, `File`, etc.)
- **Preferencia 3:** DocTypes de ERPNext solo si son críticos (`Company`, `Currency`)
- **Último recurso:** Funciones específicas de ERPNext (con documentación de riesgo)

#### **📊 EJEMPLOS APLICADOS:**

```python
# ✅ CORRECTO - Frappe Framework
from frappe.utils import now_datetime
user = frappe.get_doc("User", "Administrator")

# ❌ EVITAR - ERPNext específico  
from erpnext.setup.utils import enable_all_roles_and_domains

# ⚠️ JUSTIFICADO - ERPNext crítico documentado
company = frappe.get_doc("Company", company_name)  # Company DocType es crítico
```

#### **🚨 RIESGOS DOCUMENTADOS DE FUNCIONES ERPNEXT:**

- **Dependencias frágiles:** Pueden cambiar entre versiones
- **Portabilidad limitada:** No funcionan en instalaciones solo-Frappe  
- **Mantenimiento complejo:** Requiere seguimiento de cambios de ERPNext
- **Testing complicado:** Pueden fallar en ambientes CI minimalistas

#### **✅ BENEFICIOS DE PREFERENCIA FRAPPE:**

- **Estabilidad garantizada:** APIs estables del framework core
- **Portabilidad máxima:** Funciona en cualquier instalación Frappe
- **Mantenimiento simplificado:** Menos dependencias externas
- **Testing robusto:** Compatible con todos los ambientes CI

**APLICABLE A:** Todo el desarrollo futuro del proyecto y revisión de código existente.