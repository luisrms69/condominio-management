# 🤖 CLAUDE - Sistema de Gestión de Condominios

**MEMORIA OPERACIONAL PERMANENTE - CONFIGURACIÓN MODULAR**

## 📋 **REGLAS CRÍTICAS INMUTABLES**
👉 **[CONFIGURACIÓN COMPLETA](docs/core/CLAUDE_CONFIG.md)**

### **TOP 5 REGLAS MÁS CRÍTICAS:**
1. **🇪🇸 Etiquetas en español** - TODAS las labels de DocTypes en español SIEMPRE
2. **🧪 Tests obligatorios** - Cada DocType DEBE tener tests con FrappeTestCase
3. **🔧 Hooks específicos** - NO universales (bloqueados por setup wizard)
4. **🌿 Branch strategy** - Nunca trabajar en main, siempre feature/ branches
5. **✅ Verificación OBLIGATORIA** - Tests después de modificar hooks.py (REGLA #13)

### **SISTEMA DE TRADUCCIONES:**
- **Archivo:** `condominium_management/translations/es.csv`
- **Configuración:** `app_include_locale = "translations"`
- **Compilación:** `bench build` automático

---

## 🏗️ **ESTADO ACTUAL DEL PROYECTO**
👉 **[ESTADO COMPLETO](docs/operational/MODULE_STATUS.md)**

### **✅ MÓDULOS COMPLETOS (2/10):**
- **Companies** - ✅ Hooks + Tests + Framework completo
- **Document Generation** - ✅ Hooks + Tests + Framework completo

### **🔄 EN DESARROLLO:**
- **Cross-Site Architecture** - 📋 INICIANDO (APIs para community contributions)

### **📅 PLANIFICADOS (8 módulos):**
Physical Spaces, Residents, Access Control, Maintenance, Committee, Compliance, Communication, Package

---

## 🔧 **CONFIGURACIÓN DE HOOKS ACTIVA**
👉 **[CONFIGURACIÓN COMPLETA](docs/operational/HOOKS_CONFIG.md)**

### **Hooks Específicos Implementados:**
- **Companies:** Company, Service Management Contract, Company Account
- **Document Generation:** Master Template Registry, Entity Configuration
- **Scheduled:** Performance monitoring mensual

### **❌ Hooks Universales:** Desactivados (setup wizard conflicts)

---

## 🔄 **WORKFLOWS DE DESARROLLO**
👉 **[PROCESO COMPLETO](docs/workflows/NEW_MODULE_PROCESS.md)**

### **Para Nuevo Módulo:**
1. Crear branch `feature/[modulo]-implementation`
2. Aplicar `TEMPLATE_MODULE_HOOKS.py`
3. Configurar hooks en `hooks.py`
4. Implementar tests obligatorios
5. **Verificar tests funcionan** (CRÍTICO)
6. Commit limpio + PR

### **Template Automático:**
```bash
python TEMPLATE_MODULE_HOOKS.py
# generate_hooks_for_module('[modulo]')
```

---

## 📝 **COMANDOS FRECUENTES**

### **Testing (OBLIGATORIO después de hooks.py):**
```bash
# Verificar TODOS los módulos
bench --site domika.dev run-tests --app condominium_management

# Test específico por DocType  
bench --site domika.dev run-tests --doctype "DocType Name"

# Verificar pre-commit
pre-commit run --all-files
```

### **Desarrollo:**
```bash
# Migrar cambios
bench --site domika.dev migrate
bench --site domika.dev build

# Git workflow
git checkout main && git pull origin main
git checkout -b feature/[modulo]-implementation
git commit -m "feat([modulo]): descripción"
git push origin feature/[modulo]-implementation
```

### **Hooks y Performance:**
```bash
# Verificar configuración hooks
cat condominium_management/hooks.py

# Ejecutar monitoreo performance (mensual automático)
# Configurado en scheduler_events
```

---

## 🚨 **CRITERIOS DE RECHAZO AUTOMÁTICO**

Se rechaza código que:
- ❌ Tiene labels en inglés
- ❌ No tiene tests con FrappeTestCase  
- ❌ No pasa pre-commit hooks
- ❌ No usa conventional commits
- ❌ Modifica hooks.py sin verificar tests de TODOS los módulos
- ❌ Mensajes de error en inglés
- ❌ No sigue branch naming convention

---

## 📚 **ARQUITECTURA Y DECISIONES**

### **Single Site Confirmado:**
- ✅ Viable hasta 50+ condominios
- ✅ ERPNext Multi-Company para separación financiera
- ✅ Escalabilidad validada (62M registros proyectados año 10)

### **Hooks Strategy:**
- ✅ Hooks específicos por DocType (seguro, escalable)
- ❌ Hooks universales bloqueados por setup wizard
- ✅ Template automático para 13 módulos

### **Performance Monitoring:**
- ✅ Monitoreo mensual automático
- ✅ Alertas por thresholds (verde <300, rojo >3000 templates)
- ✅ Master Template Registry optimizado

---

## 🎯 **PRÓXIMOS PASOS**

1. **Inmediato:** Implementar Cross-Site Architecture
2. **Siguiente:** Aplicar template a Physical Spaces module  
3. **Futuro:** 7 módulos restantes usando workflow establecido

---

**📁 Documentación Detallada:** `/docs` folder  
**🔧 Configuración Permanente:** `docs/core/CLAUDE_CONFIG.md`  
**📊 Estado Actual:** `docs/operational/MODULE_STATUS.md`  
**🔄 Procesos:** `docs/workflows/NEW_MODULE_PROCESS.md`

**Última actualización:** 2025-07-04  
**Líneas totales:** <300 (cumple límite establecido)