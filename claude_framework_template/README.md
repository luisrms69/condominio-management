# 🤖 CLAUDE FRAMEWORK TEMPLATE FOR FRAPPE APPS

## 📋 **OVERVIEW**

Template reutilizable para configurar Claude Code con cualquier app de Frappe Framework, basado en la experiencia del proyecto Condominium Management.

## 🎯 **FEATURES**

### **✅ INCLUYE:**
- **Estructura docs/** modular y escalable
- **Sistema de hooks específicos** (no universales)
- **Metodología CI/CD** con AI-assisted debugging
- **Testing framework** con FrappeTestCase patterns
- **Políticas de desarrollo** con pre-commit hooks
- **Conventional commits** y branch management
- **Performance monitoring** automático
- **Troubleshooting procedures** documentados

### **🔧 CONFIGURACIÓN AUTOMÁTICA:**
- Traducciones por idioma configurable
- Comandos específicos por app
- Hooks personalizados por módulos
- Variables de ambiente por proyecto

## 🚀 **INSTALLATION**

### **Para Nueva App Frappe:**
```bash
# 1. Navegar al directorio de la app
cd /path/to/frappe-bench/apps/my_app

# 2. Ejecutar setup automático
python claude_framework_template/setup_claude_framework.py \
  --app-name "my_app" \
  --app-title "My Custom App" \
  --language "es" \
  --publisher "My Company" \
  --dev-site "my_app.dev"

# 3. Verificar configuración
python claude_framework_template/validate_setup.py
```

### **Para App Existente:**
```bash
# Backup automático + setup no destructivo
python claude_framework_template/setup_claude_framework.py \
  --app-name "existing_app" \
  --migrate-existing \
  --backup-first
```

## 📁 **STRUCTURE GENERATED**

```
your_app/
├── CLAUDE.md                     # Índice principal personalizado
├── docs/
│   ├── core/
│   │   ├── CLAUDE_CONFIG.md      # Configuración inmutable
│   │   └── DEVELOPMENT_POLICIES.md # Políticas de desarrollo
│   ├── operational/
│   │   ├── MODULE_STATUS.md      # Estado de módulos
│   │   └── HOOKS_CONFIG.md       # Configuración hooks
│   └── workflows/
│       ├── NEW_MODULE_PROCESS.md # Proceso nuevos módulos
│       └── TROUBLESHOOTING_CI.md # Troubleshooting CI/CD
├── claude_framework_template/    # Template files (para distribución)
└── scripts/
    ├── generate_module_hooks.py  # Generador hooks específicos
    └── monitor_performance.py    # Monitor de performance
```

## 🔧 **CUSTOMIZATION**

### **Variables de Configuración:**
```python
# config.py generado automáticamente
CLAUDE_CONFIG = {
    "app_name": "my_app",
    "app_title": "My Custom App",
    "app_publisher": "My Company",
    "primary_language": "es",  # es, en, fr, de, etc.
    "required_apps": ["frappe"],  # o ["erpnext"] si es necesario
    "dev_site": "my_app.dev",
    "test_sites": ["test1.dev", "test2.dev"],
    "git_main_branch": "main",
    "conventional_commit_scopes": ["module1", "module2", "tests", "docs"],
    "business_domain": "Custom Business Logic",
    "initial_modules": ["core", "setup"]
}
```

### **Personalización Post-Setup:**
```bash
# Agregar nuevo módulo
python scripts/generate_module_hooks.py --module-name "inventory"

# Actualizar configuración
python claude_framework_template/update_config.py --add-module "inventory"

# Regenerar CLAUDE.md con cambios
python claude_framework_template/regenerate_claude.py
```

## 🧪 **TESTING**

```bash
# Validar configuración completa
python claude_framework_template/validate_setup.py --full-check

# Probar hooks generados
bench --site test_site run-tests --app your_app

# Verificar compliance
pre-commit run --all-files
```

## 📋 **WORKFLOWS INCLUDED**

### **1. Nuevo Módulo:**
```bash
# Automático con template
python scripts/generate_module_hooks.py --module-name "new_module"
# Resultado: hooks.py actualizado + tests base + documentación
```

### **2. Desarrollo Diario:**
```bash
# Comandos configurados automáticamente
bench --site {{DEV_SITE}} run-tests --app {{APP_NAME}}
bench --site {{DEV_SITE}} migrate
bench --site {{DEV_SITE}} build
```

### **3. CI/CD:**
```bash
# Configuración automática en .github/workflows/
# Incluye retry strategies y troubleshooting
```

## 🔄 **UPDATES**

### **Actualizar Template:**
```bash
# Desde proyecto origen (condominium_management)
python claude_framework_template/sync_from_origin.py

# Aplicar updates a proyecto actual
python claude_framework_template/apply_updates.py --selective
```

### **Contribuir Mejoras:**
```bash
# Enviar mejoras al template base
python claude_framework_template/contribute_improvements.py
```

## 🎯 **BENEFITS**

- **⚡ Setup Time**: 2-3 horas → 5-10 minutos
- **📊 Consistency**: Mismas políticas en todos los proyectos
- **🔧 Maintenance**: Updates centralizados
- **🧪 Quality**: Testing framework probado
- **🔄 Workflows**: Procesos automatizados
- **📚 Documentation**: Estructura escalable

## 📞 **SUPPORT**

Template basado en proyecto real **Condominium Management** con:
- ✅ 2 módulos completos implementados
- ✅ CI/CD funcionando
- ✅ 6 meses de desarrollo activo
- ✅ Patrones probados y documentados

---

**Created**: 2025-07-05  
**Based on**: Condominium Management App (Frappe v15)  
**Maintained**: Active development  
**License**: MIT (compatible with Frappe Framework)