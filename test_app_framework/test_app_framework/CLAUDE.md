# 🤖 CLAUDE - Test ERP System

**MEMORIA OPERACIONAL PERMANENTE - CONFIGURACIÓN MODULAR**

## 📋 **REGLAS CRÍTICAS INMUTABLES**
👉 **[CONFIGURACIÓN COMPLETA](docs/core/CLAUDE_CONFIG.md)**

### **TOP 5 REGLAS MÁS CRÍTICAS:**
1. **🇪🇸 Etiquetas en español** - TODAS las labels de DocTypes en es SIEMPRE
2. **🧪 Tests obligatorios** - Cada DocType DEBE tener tests con FrappeTestCase
3. **🔧 Hooks específicos** - NO universales (bloqueados por setup wizard)
4. **🌿 Branch strategy** - Nunca trabajar en main, siempre feature/ branches
5. **✅ Verificación OBLIGATORIA** - Tests después de modificar hooks.py

## 🏗️ **ESTADO ACTUAL DEL PROYECTO**
👉 **[ESTADO COMPLETO](docs/operational/MODULE_STATUS.md)**

### **🔄 EN DESARROLLO:**
- **Test ERP System** - Iniciando desarrollo

## 📝 **COMANDOS FRECUENTES**

### **Testing (OBLIGATORIO después de hooks.py):**
```bash
# Verificar TODOS los módulos
bench --site test.dev run-tests --app test_erp

# Test específico por DocType  
bench --site test.dev run-tests --doctype "DocType Name"
```

### **Desarrollo:**
```bash
# Migrar cambios
bench --site test.dev migrate
bench --site test.dev build
```

---

**Última actualización:** 2025-07-05  
**Líneas totales:** <300 (cumple límite establecido)