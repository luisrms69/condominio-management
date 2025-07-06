# 🤖 CLAUDE - Sistema de Gestión de Condominios

**MEMORIA OPERACIONAL PERMANENTE - CONFIGURACIÓN MODULAR**

## 📋 **REGLAS CRÍTICAS INMUTABLES**
👉 **[CONFIGURACIÓN COMPLETA](docs/core/CLAUDE_CONFIG.md)**

### **TOP 6 REGLAS MÁS CRÍTICAS:**
1. **🇪🇸 Etiquetas en español** - TODAS las labels de DocTypes en español SIEMPRE
2. **🧪 Tests obligatorios** - Cada DocType DEBE tener tests con FrappeTestCase
3. **🔧 Hooks específicos** - NO universales (bloqueados por setup wizard)
4. **🌿 Branch strategy** - Nunca trabajar en main, siempre feature/ branches
5. **✅ Verificación OBLIGATORIA** - Tests después de modificar hooks.py (REGLA #13)
6. **⚖️ PREFERENCIA FRAPPE** - Funciones Frappe Framework > ERPNext SIEMPRE

### **SISTEMA DE TRADUCCIONES:**
- **Archivo:** `condominium_management/translations/es.csv`
- **Configuración:** `app_include_locale = "translations"`
- **Compilación:** `bench build` automático

---

## 🏗️ **ESTADO ACTUAL DEL PROYECTO**
👉 **[ESTADO COMPLETO](docs/operational/MODULE_STATUS.md)**

### **✅ MÓDULOS COMPLETOS (3/10):**
- **Companies** - ✅ Hooks + Tests + Framework completo
- **Document Generation** - ✅ Hooks + Tests + Framework completo
- **Community Contributions** - ✅ Cross-Site APIs + Autenticación HMAC + DocTypes completos

### **🔄 EN DESARROLLO:**
- **Physical Spaces** - 📋 PRÓXIMO (aplicar template establecido)

### **📅 PLANIFICADOS (7 módulos):**
Residents, Access Control, Maintenance, Committee, Compliance, Communication, Package

---

## 🔧 **CONFIGURACIÓN DE HOOKS ACTIVA**
👉 **[CONFIGURACIÓN COMPLETA](docs/operational/HOOKS_CONFIG.md)**

### **Hooks Específicos Implementados:**
- **Companies:** Company, Service Management Contract, Company Account
- **Document Generation:** Master Template Registry, Entity Configuration
- **Community Contributions:** Registered Contributor Site, Contribution Request (cross-site)
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
6. **Ejecutar y corregir linting** (OBLIGATORIO)
7. Commit limpio + PR

### **🚨 WORKFLOW ANTI-LINTING FAILURES:**
```bash
# ANTES de cualquier commit
pre-commit run --all-files
if [ $? -ne 0 ]; then
  ruff --fix .
  git add .
  echo "✅ Linting corregido automáticamente"
fi
git commit -m "mensaje"
```

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

# Verificar pre-commit Y corregir linting ANTES de commit
pre-commit run --all-files
ruff --fix .  # Si hay errores de linting, aplicar fix automático
git add .     # Agregar correcciones aplicadas
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
- ❌ Usa funciones ERPNext cuando existe equivalente Frappe
- ❌ Hace commit sin verificar y corregir errores de linting

---

## 📚 **ARQUITECTURA Y DECISIONES**

### **⚖️ PREFERENCIA FRAPPE vs ERPNEXT:**
**REGLA FUNDAMENTAL:** Funciones Frappe Framework tienen **PREFERENCIA ABSOLUTA** sobre ERPNext.

#### **🎯 CRITERIOS DE DECISIÓN:**
1. **✅ USAR FRAPPE:** Si existe función equivalente en Frappe Framework
2. **⚠️ EVALUAR ERPNEXT:** Solo si es funcionalidad crítica no disponible en Frappe
3. **❌ EVITAR ERPNEXT:** Si requiere recrear funcionalidad existente de Frappe

#### **📊 EJEMPLOS:**
```python
# ✅ CORRECTO - Frappe Framework
from frappe.utils import now_datetime
user = frappe.get_doc("User", "Administrator")

# ❌ EVITAR - ERPNext específico  
from erpnext.setup.utils import enable_all_roles_and_domains

# ⚠️ JUSTIFICADO - ERPNext crítico documentado
company = frappe.get_doc("Company", company_name)  # Company DocType es crítico
```

#### **✅ BENEFICIOS FRAPPE:**
- Estabilidad garantizada, portabilidad máxima, testing robusto
- Mantenimiento simplificado, compatible con todos ambientes CI

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

## 🚀 **CLAUDE FRAMEWORK TEMPLATE REUTILIZABLE**

### **✅ TEMPLATE COMPLETO DISPONIBLE:**
👉 **[TEMPLATE REUTILIZABLE](claude_framework_template/)**

**Características:**
- ✅ **Setup automático** en 5 minutos para cualquier app Frappe
- ✅ **Configuración personalizable** por idioma y dependencias
- ✅ **Scripts de generación** automática de hooks y documentación
- ✅ **Validación completa** de instalación
- ✅ **Basado en experiencia real** de 6+ meses de desarrollo

### **🔧 USO PARA NUEVAS APPS:**
```bash
# Setup completo para nueva app Frappe
cd /path/to/your/frappe/app
python claude_framework_template/setup_claude_framework.py \
  --app-name "your_app" \
  --app-title "Your App Title" \
  --publisher "Your Company" \
  --language "es"

# Validar instalación
python claude_framework_template/validate_setup.py --full-check
```

### **📚 DOCUMENTACIÓN TEMPLATE:**
- 📖 **[README.md](claude_framework_template/README.md)** - Overview completo
- 🚀 **[INSTALLATION_GUIDE.md](claude_framework_template/INSTALLATION_GUIDE.md)** - Guía detallada
- ⚙️ **Scripts automatizados** - setup, validación, configuración

**PERMITE CRECIMIENTO:** Este CLAUDE.md seguirá creciendo con mejoras que beneficiarán futuras implementaciones del template.

---

## 🌐 **REGLA #18: SISTEMA CROSS-SITE COMMUNITY CONTRIBUTIONS**

### **✅ MÓDULO COMPLETADO - JULIO 2025**

**FUNCIONALIDAD:** Sistema de contribuciones entre sites independientes de administradoras  
**ESTADO:** ✅ 100% FUNCIONAL - APIs + Autenticación + DocTypes + Testing

#### **🏗️ ARQUITECTURA IMPLEMENTADA:**

**DOMIKA.DEV (Receptor Central):**
- ✅ Recibe contribuciones de administradoras externas
- ✅ Centraliza pool de templates universales  
- ✅ APIs: `receive_external_contribution`, `get_cross_site_stats`

**ADMIN1.DEV, ADMIN2.DEV (Sites Contribuyentes):**
- ✅ Envían contribuciones al central
- ✅ Autenticación HMAC con API keys únicos
- ✅ API: `submit_contribution_to_domika`

#### **🔧 COMPONENTES CLAVE:**

**DocTypes:**
- `Registered Contributor Site` - Gestión de administradoras autorizadas
- `Contribution Request` - Extendido para cross-site
- `Contribution Category` - Configuración de validaciones

**Seguridad:**
- API keys SHA-256 únicos por site
- Firmas HMAC para autenticación
- Validación de timestamps (anti-replay)
- Logs de auditoría completos

#### **📊 TESTING CONFIGURADO:**
- Sites de prueba: `admin1.test.com`, `admin2.test.com`
- Categoría operativa: `document_generation-template`
- Scripts de configuración: `configure_central.py`

#### **🚀 COMANDOS DE USO:**
```bash
# Configurar domika.dev como receptor
cd ~/frappe-bench
exec(open('apps/condominium_management/configure_central.py').read())

# Verificar sites registrados
frappe.get_all('Registered Contributor Site', fields=['site_url', 'is_active'])
```

**DOCUMENTACIÓN:** `condominium_management/community_contributions/README.md`

---

**📁 Documentación Detallada:** `/docs` folder  
**🔧 Configuración Permanente:** `docs/core/CLAUDE_CONFIG.md`  
**📊 Estado Actual:** `docs/operational/MODULE_STATUS.md`  
**🔄 Procesos:** `docs/workflows/NEW_MODULE_PROCESS.md`  
**🚀 Template Reutilizable:** `claude_framework_template/`

**Última actualización:** 2025-07-06  
**Módulos completados:** 3/10 (Companies, Document Generation, Community Contributions)  
**Template status:** ✅ PROBADO Y FUNCIONAL + CROSS-SITE ARCHITECTURE