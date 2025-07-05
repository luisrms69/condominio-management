# 🚀 GUÍA DE INSTALACIÓN - CLAUDE FRAMEWORK TEMPLATE

## 📋 **DESCRIPCIÓN**

Template completo para configurar Claude Code en cualquier app de Frappe Framework, basado en la experiencia exitosa del proyecto **Condominium Management**.

### **✅ QUÉ INCLUYE:**
- **Estructura docs/** escalable (core, operational, workflows)
- **Sistema de hooks específicos** (evita conflictos setup wizard)
- **Framework de testing** con FrappeTestCase patterns
- **CI/CD robusto** con AI-assisted debugging
- **Pre-commit hooks** y conventional commits
- **Performance monitoring** automático
- **Comandos personalizados** por app

## 🎯 **CASOS DE USO**

### **PARA NUEVA APP FRAPPE:**
```bash
# Setup completo en 5 minutos
cd /path/to/frappe-bench/apps/my_new_app
python claude_framework_template/setup_claude_framework.py \
  --app-name "my_new_app" \
  --app-title "My Business App" \
  --publisher "My Company" \
  --language "es"
```

### **PARA APP EXISTENTE:**
```bash
# Migración segura con backup automático
python claude_framework_template/setup_claude_framework.py \
  --app-name "existing_app" \
  --migrate-existing \
  --backup-first
```

## 📥 **INSTALACIÓN PASO A PASO**

### **1. OBTENER EL TEMPLATE:**
```bash
# Opción A: Copiar desde proyecto condominium_management
cp -r /path/to/condominium_management/claude_framework_template ./

# Opción B: Clonar desde repositorio (futuro)
# git clone https://github.com/user/claude-framework-template.git
```

### **2. EJECUTAR SETUP:**
```bash
cd /path/to/your/frappe/app
python claude_framework_template/setup_claude_framework.py \
  --app-name "your_app_name" \
  --app-title "Your App Title" \
  --publisher "Your Company" \
  --language "es" \
  --dev-site "yourapp.dev"
```

### **3. VERIFICAR INSTALACIÓN:**
```bash
# Validar configuración
python claude_framework_template/validate_setup.py

# Verificar archivos generados
ls -la CLAUDE.md docs/ scripts/

# Comprobar pre-commit hooks
pre-commit run --all-files
```

## 🔧 **OPCIONES DE CONFIGURACIÓN**

### **PARÁMETROS BÁSICOS:**
```bash
--app-name "my_app"           # Nombre técnico de la app (requerido)
--app-title "My App"          # Título descriptivo (requerido)
--publisher "My Company"      # Empresa desarrolladora (requerido)
--language "es"              # Idioma principal: es, en, fr, de
--dev-site "myapp.dev"       # Sitio de desarrollo
```

### **PARÁMETROS AVANZADOS:**
```bash
--no-backup                  # No crear backup (apps nuevas)
--migrate-existing           # Migrar app existente
--required-apps "erpnext"    # Dependencias: frappe, erpnext
--modules "core,setup"       # Módulos iniciales
```

### **CONFIGURACIÓN INTERACTIVA:**
```bash
# Setup con wizard interactivo
python claude_framework_template/setup_claude_framework.py --interactive
```

## 📁 **ESTRUCTURA GENERADA**

```
your_app/
├── CLAUDE.md                           # Índice principal personalizado
├── docs/
│   ├── core/
│   │   ├── CLAUDE_CONFIG.md           # Configuración inmutable
│   │   └── DEVELOPMENT_POLICIES.md    # Políticas de desarrollo
│   ├── operational/
│   │   ├── MODULE_STATUS.md           # Estado de módulos
│   │   └── HOOKS_CONFIG.md            # Configuración hooks
│   └── workflows/
│       ├── NEW_MODULE_PROCESS.md      # Proceso nuevos módulos
│       └── TROUBLESHOOTING_CI.md      # Troubleshooting CI/CD
├── scripts/
│   ├── generate_module_hooks.py       # Generador hooks específicos
│   └── monitor_performance.py         # Monitor de performance (si aplica)
├── claude_framework_template/         # Template para distribución
├── claude_framework_config.json       # Configuración generada
└── .pre-commit-config.yaml           # Hooks de pre-commit
```

## 🔄 **WORKFLOW POST-INSTALACIÓN**

### **1. CONFIGURAR HERRAMIENTAS:**
```bash
# Instalar pre-commit hooks
pre-commit install

# Configurar conventional commits (si usas VS Code)
# Extensión: Conventional Commits (vivaxy.vscode-conventional-commits)
```

### **2. CREAR PRIMER MÓDULO:**
```bash
# Generar hooks para nuevo módulo
python scripts/generate_module_hooks.py inventory

# Actualizar estado del módulo
# Editar docs/operational/MODULE_STATUS.md
```

### **3. CONFIGURAR CI/CD:**
```bash
# Copiar configuración CI desde template
cp claude_framework_template/.github/workflows/ci.yml .github/workflows/

# Personalizar para tu app
# Editar app_name en ci.yml
```

## 🔄 **PERSONALIZACIÓN POST-SETUP**

### **AGREGAR NUEVO MÓDULO:**
```bash
# Generar hooks automáticamente
python scripts/generate_module_hooks.py --module-name "sales"

# Actualizar configuración
python claude_framework_template/update_config.py --add-module "sales"

# Regenerar CLAUDE.md con cambios
python claude_framework_template/regenerate_claude.py
```

### **CAMBIAR CONFIGURACIÓN:**
```bash
# Editar configuración
vim claude_framework_config.json

# Aplicar cambios
python claude_framework_template/apply_config_changes.py
```

### **ACTUALIZAR TEMPLATE:**
```bash
# Sincronizar con mejoras del template origen
python claude_framework_template/sync_from_origin.py

# Aplicar updates selectivamente
python claude_framework_template/apply_updates.py --selective
```

## 🧪 **VALIDACIÓN Y TESTING**

### **VALIDAR SETUP COMPLETO:**
```bash
# Verificación completa
python claude_framework_template/validate_setup.py --full-check

# Verificar compliance
pre-commit run --all-files

# Test hooks si hay módulos implementados
bench --site test_site run-tests --app your_app
```

### **TROUBLESHOOTING COMÚN:**

**Error: Módulo no encontrado**
```bash
# Verificar PYTHONPATH
export PYTHONPATH="$PYTHONPATH:$(pwd)/claude_framework_template"
```

**Error: Permisos**
```bash
# Dar permisos de ejecución
chmod +x claude_framework_template/*.py
chmod +x scripts/*.py
```

**Error: Dependencias**
```bash
# Instalar dependencias Python si es necesario
pip install tomli  # Para leer pyproject.toml
```

## 🎯 **BENEFICIOS COMPROBADOS**

### **PRODUCTIVIDAD:**
- ⚡ **Setup time**: 2-3 horas → 5-10 minutos
- 🔧 **Consistency**: Mismas políticas en todos los proyectos
- 📊 **Quality**: Framework de testing probado

### **MANTENIMIENTO:**
- 🔄 **Updates centralizados**: Una fuente de verdad
- 🧪 **Testing automático**: Pre-commit hooks configurados
- 📚 **Documentation**: Estructura escalable

### **EXPERIENCIA REAL:**
- ✅ **Proyecto origen**: Condominium Management (6+ meses desarrollo)
- ✅ **Módulos completos**: 2 módulos implementados exitosamente
- ✅ **CI/CD funcionando**: GitHub Actions con retry strategies
- ✅ **Zero regresiones**: Framework estable y robusto

## 📞 **SOPORTE**

### **DOCUMENTACIÓN:**
- 📖 **README.md**: Información general del template
- 🔧 **CLAUDE.md**: Documentación específica de tu app
- 📋 **docs/**: Documentación modular y especializada

### **CONTRIBUCIÓN:**
```bash
# Reportar mejoras al template origen
python claude_framework_template/contribute_improvements.py

# Crear issue en proyecto origen
# Referencia: proyecto condominium_management
```

### **RECURSOS:**
- **Proyecto origen**: `condominium_management` (Frappe v15)
- **Framework base**: Frappe Framework official patterns
- **Testing**: FrappeTestCase methodology
- **CI/CD**: GitHub Actions proven strategies

---

## 🎉 **QUICK START**

```bash
# 1. Obtener template
cp -r /path/to/condominium_management/claude_framework_template ./

# 2. Setup en 1 comando
cd your_app && python claude_framework_template/setup_claude_framework.py \
  --app-name "your_app" --app-title "Your App" --publisher "Your Company"

# 3. Verificar
ls CLAUDE.md docs/ && echo "✅ Setup completo!"

# 4. Empezar desarrollo
git add . && git commit -m "feat(setup): configurar Claude Framework"
```

**¡En 5 minutos tienes el mismo framework usado en proyecto real de 6 meses!**

---

**Creado**: 2025-07-05  
**Basado en**: Condominium Management (proyecto real, Frappe v15)  
**Mantenido**: Desarrollo activo  
**Licencia**: MIT (compatible con Frappe Framework)