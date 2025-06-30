# 📋 POLÍTICAS DE DESARROLLO - CONDOMINIUM MANAGEMENT

**Proyecto:** Condominium Management  
**Framework:** Frappe v15  
**Aplicable a:** TODO el desarrollo del proyecto

---

## 🎯 **REGLAS CRÍTICAS DEL PROYECTO**

### **REGLA #1: IDIOMA ESPAÑOL OBLIGATORIO**
- ✅ **TODOS los labels deben estar en español** - sin excepciones
- ✅ **Opciones de Select/MultiSelect en español**
- ✅ **Mensajes de error y validación en español**
- ✅ **Documentación y comentarios en español**
- ✅ **Docstrings completamente en español**

### **REGLA #2: CONVENTIONAL COMMITS OBLIGATORIOS**
Formato: `tipo(alcance): descripción`

**Tipos permitidos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de errores
- `docs`: Documentación
- `style`: Formato/estilo (no cambios de código)
- `refactor`: Refactorización
- `test`: Agregar/modificar tests
- `chore`: Mantenimiento

**Alcances:**
- `companies`: Módulo Companies
- `tests`: Unit tests
- `docs`: Documentación
- `config`: Configuración
- `api`: APIs
- `ui`: Interfaz de usuario
- `database`: Base de datos
- `sync`: Sincronización
- `validation`: Validaciones

**Ejemplos:**
```
feat(companies): add GPS coordinates field to Condominium Information
fix(validation): correct email format validation in Contact Information
docs(companies): update docstrings for Service Management Contract
test(companies): add unit tests for Access Point Detail
```

### **REGLA #3: DOCSTRINGS ESTÁNDAR OBLIGATORIO**

**Formato requerido:**
```python
class NombreClase(Document):
    \"\"\"
    Descripción breve en español de la funcionalidad principal.

    Funcionalidades principales:
    - Lista de funcionalidades específicas
    - Una por línea, en español
    - Describir propósito y capacidades

    Parámetros importantes:
        campo_1 (Tipo): Descripción del campo en español
        campo_2 (Tipo): Descripción del campo en español
        campo_3 (Tipo): Descripción del campo en español

    Errores comunes:
        ValidationError: Descripción del error específico
        Warning: Descripción de advertencias

    Ejemplo de uso:
        doc = frappe.new_doc("DocType Name")
        doc.campo_1 = "valor"
        doc.save()
    \"\"\"
    
    def metodo(self):
        \"\"\"
        Descripción del método en español.
        
        Explicación detallada del propósito y funcionamiento.
        
        Args:
            parametro (tipo): Descripción del parámetro
            
        Returns:
            tipo: Descripción del valor retornado
            
        Raises:
            ExceptionType: Descripción de cuándo ocurre la excepción
        \"\"\"
```

### **REGLA #4: UNIT TESTS OBLIGATORIOS**

**Estructura requerida:**
```python
class TestDocTypeName(FrappeTestCase):
    \"\"\"Test cases for DocType Name.\"\"\"
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # CRÍTICO
        cls.create_test_dependencies()
    
    def setUp(self):
        frappe.set_user("Administrator")
        self.test_data = {...}
    
    def test_doctype_creation(self):
        # Test básico de creación
    
    def test_spanish_labels(self):
        # Test obligatorio de labels en español
    
    def tearDown(self):
        frappe.set_user("Administrator")
        # NO hacer cleanup manual
```

---

## 🛠️ **HERRAMIENTAS CONFIGURADAS**

### **VS Code Extensions Instaladas:**
- ✅ **GitLens** - Control avanzado de Git
- ✅ **Conventional Commits** - Commits estandarizados  
- ✅ **autoDocstring** - Generación automática de docstrings
- ✅ **Python** - Soporte completo de Python
- ✅ **Black Formatter** - Formato automático de código
- ✅ **Flake8** - Linting de Python
- ✅ **Prettier** - Formato de JS/CSS/HTML

### **Pre-commit Hooks Configurados:**
- ✅ **Ruff** - Import sorting y linting
- ✅ **Ruff Format** - Formato de código
- ✅ **Prettier** - Formato de archivos web
- ✅ **ESLint** - Linting de JavaScript
- ✅ **Trailing whitespace** - Eliminación de espacios
- ✅ **Check merge conflicts** - Detección de conflictos
- ✅ **Check JSON/YAML** - Validación de sintaxis

---

## 📋 **WORKFLOW DE DESARROLLO**

### **1. Antes de Codificar:**
1. Crear/actualizar TODO list con `TodoWrite`
2. Marcar tarea como `in_progress`
3. Entender requerimientos en español

### **2. Durante el Desarrollo:**
1. **Código:** Seguir convenciones existentes
2. **Labels:** Siempre en español
3. **Docstrings:** Formato estándar establecido
4. **Tests:** Crear tests obligatorios

### **3. Antes del Commit:**
1. Ejecutar tests: `bench run-tests --app condominium_management`
2. Verificar pre-commit hooks: `pre-commit run --all-files`
3. Usar VS Code Conventional Commits extension
4. Completar tareas en TODO list

### **4. Commit Message:**
```
tipo(alcance): descripción en español

Cuerpo del mensaje explicando el "por qué" en español.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## ✅ **CHECKLIST DE CALIDAD**

### **Antes de considerar terminada cualquier tarea:**

**DocType Compliance:**
- [ ] Labels en español verificados
- [ ] Docstrings implementados según estándar
- [ ] Unit tests creados y pasando
- [ ] Validaciones con mensajes en español
- [ ] Pre-commit hooks pasando

**Código Quality:**
- [ ] Formato automático aplicado (Black/Ruff)
- [ ] Imports organizados
- [ ] No errores de linting
- [ ] Documentación actualizada

**Git Compliance:**
- [ ] Conventional commits usados
- [ ] Mensajes descriptivos en español
- [ ] Branch actualizado con main
- [ ] No archivos sensibles committeados

---

## 🚨 **POLÍTICAS DE RECHAZO**

**Se rechaza automáticamente código que:**
1. ❌ Tiene labels en inglés
2. ❌ No tiene docstrings estándar
3. ❌ No tiene unit tests
4. ❌ No pasa pre-commit hooks
5. ❌ No usa conventional commits
6. ❌ Mensajes de error en inglés
7. ❌ No actualiza TODO list

---

## 📚 **RECURSOS DE REFERENCIA**

- **Frappe Framework:** https://frappeframework.com/docs
- **Conventional Commits:** https://www.conventionalcommits.org/
- **Sphinx Docstrings:** https://sphinx-rtd-tutorial.readthedocs.io/
- **Unit Testing Frappe:** https://frappeframework.com/docs/user/en/testing

---

**Responsable:** Desarrollador asignado  
**Revisor:** Lead Developer  
**Enforcement:** Automático vía pre-commit hooks + manual review

**IMPORTANTE:** Estas políticas son OBLIGATORIAS y deben seguirse en TODO momento durante el desarrollo.