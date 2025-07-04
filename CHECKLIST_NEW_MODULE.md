# ✅ CHECKLIST OBLIGATORIO PARA NUEVOS MÓDULOS

**Fecha de creación:** 2025-07-04  
**Basado en:** REPORTE_HOOKS_UNIVERSALES_Y_OPTIMIZACION.md  
**Propósito:** Workflow permanente para asegurar implementación completa de hooks  

---

## 🚨 **REGLAS CRÍTICAS**

### **❌ HOOKS UNIVERSALES NO FACTIBLES**
- Los hooks universales ("*") están **PERMANENTEMENTE DESACTIVADOS**
- **Motivo:** Conflictos con setup wizard de ERPNext
- **Solución:** Hooks específicos por DocType (estrategia segura y escalable)

### **✅ HOOKS ESPECÍFICOS OBLIGATORIOS**
- **Cada módulo DEBE implementar hooks específicos**
- **Template disponible:** `TEMPLATE_MODULE_HOOKS.py`
- **Validación obligatoria antes de completar módulo**

---

## 📋 **CHECKLIST PASO A PASO**

### **🔍 FASE 1: ANÁLISIS DE MÓDULO**

- [ ] **1.1 Identificar DocTypes críticos**
  - [ ] Listar todos los DocTypes del módulo
  - [ ] Identificar cuáles necesitan auto-detección
  - [ ] Determinar prioridad (high/medium/low)
  - [ ] Documentar razón de cada hook

- [ ] **1.2 Consultar template existente**
  - [ ] Revisar `TEMPLATE_MODULE_HOOKS.py`
  - [ ] Verificar si el módulo ya está contemplado
  - [ ] Adaptar template según necesidades específicas

- [ ] **1.3 Definir eventos necesarios**
  - [ ] `after_insert` - Para nuevos documentos
  - [ ] `on_update` - Para cambios que requieren reconfiguración
  - [ ] `validate` - Para validaciones antes de guardar
  - [ ] `before_save` - Para modificaciones automáticas

### **🔧 FASE 2: IMPLEMENTACIÓN**

- [ ] **2.1 Crear estructura de handlers**
  ```bash
  # Ejecutar desde bench console
  from TEMPLATE_MODULE_HOOKS import generate_hooks_for_module
  generate_hooks_for_module("nombre_modulo")
  ```

- [ ] **2.2 Implementar handlers específicos**
  - [ ] Crear `/módulo/hooks_handlers/`
  - [ ] Implementar cada handler según template
  - [ ] Agregar lógica específica del módulo
  - [ ] Implementar manejo de errores

- [ ] **2.3 Actualizar hooks.py**
  - [ ] Agregar configuración generada a `doc_events`
  - [ ] Verificar que paths sean correctos
  - [ ] Probar que handlers son importables

### **🧪 FASE 3: TESTING**

- [ ] **3.1 Tests unitarios de hooks**
  - [ ] Test para cada evento implementado
  - [ ] Test de casos edge (documentos sin configuración)
  - [ ] Test de manejo de errores
  - [ ] Test de performance (no debe impactar rendimiento)

- [ ] **3.2 Tests de integración**
  - [ ] Crear DocType nuevo → Verificar hook se ejecuta
  - [ ] Actualizar DocType → Verificar reconfiguración
  - [ ] Validar DocType → Verificar validaciones

- [ ] **3.3 Validación automática**
  ```bash
  # Ejecutar validación
  from TEMPLATE_MODULE_HOOKS import validate_module_hooks
  result = validate_module_hooks("nombre_modulo")
  assert result["valid"] == True
  ```

### **📊 FASE 4: DOCUMENTACIÓN**

- [ ] **4.1 Actualizar TEMPLATE_MODULE_HOOKS.py**
  - [ ] Agregar configuración del módulo al template
  - [ ] Documentar handlers específicos
  - [ ] Actualizar ejemplos si es necesario

- [ ] **4.2 Documentar en README del módulo**
  - [ ] Explicar qué hooks están implementados
  - [ ] Documentar casos de uso
  - [ ] Agregar ejemplos de testing

- [ ] **4.3 Actualizar CLAUDE.md**
  - [ ] Agregar módulo a lista de módulos con hooks
  - [ ] Actualizar comandos de validación
  - [ ] Documentar cualquier particularidad

### **🔍 FASE 5: VALIDACIÓN FINAL**

- [ ] **5.1 Ejecutar suite completa de tests**
  ```bash
  bench --site domika.dev run-tests --app condominium_management --module nombre_modulo
  ```

- [ ] **5.2 Verificar CI pipeline**
  - [ ] Tests pasan en CI
  - [ ] No hay errores de setup wizard
  - [ ] Performance no se ve afectada

- [ ] **5.3 Validar en sitio limpio**
  ```bash
  bench --site test_site_clean install-app condominium_management
  bench --site test_site_clean run-tests --app condominium_management --module nombre_modulo
  ```

---

## 🔧 **COMANDOS ÚTILES**

### **Generar hooks automáticamente:**
```bash
bench console
>>> from TEMPLATE_MODULE_HOOKS import generate_hooks_for_module
>>> generate_hooks_for_module("companies")  # Reemplazar con módulo real
```

### **Validar implementación:**
```bash
bench console
>>> from TEMPLATE_MODULE_HOOKS import validate_module_hooks
>>> result = validate_module_hooks("companies")
>>> print(result)
```

### **Verificar handlers existentes:**
```bash
find condominium_management -name "hooks_handlers" -type d
ls condominium_management/*/hooks_handlers/
```

### **Ejecutar tests específicos:**
```bash
bench --site domika.dev run-tests --app condominium_management --module nombre_modulo
python run_tests.py --doctype "DocType Específico" --verbose
```

---

## 🚨 **ERRORES COMUNES A EVITAR**

### **❌ NO HACER:**
- Activar hooks universales ("*") - CAUSARÁN ERRORES
- Olvidar manejo de errores en handlers
- No validar que DocTypes existan antes de usar hooks
- Implementar hooks sin tests correspondientes
- Hacer cambios masivos sin validar en sitio limpio

### **✅ HACER SIEMPRE:**
- Usar template `TEMPLATE_MODULE_HOOKS.py` como base
- Implementar manejo de errores con try/catch
- Validar que hooks no interfieran con setup wizard
- Agregar logs detallados para debugging
- Probar en sitio limpio antes de merge

---

## 🎯 **CRITERIOS DE ÉXITO**

### **✅ MÓDULO COMPLETO CUANDO:**
- [ ] Todos los DocTypes críticos tienen hooks implementados
- [ ] Tests unitarios pasan al 100%
- [ ] Validación automática es exitosa
- [ ] CI pipeline está verde
- [ ] Documentación está actualizada
- [ ] Template está actualizado con el módulo

### **📊 MÉTRICAS DE CALIDAD:**
- **Cobertura de tests:** >95% en handlers
- **Performance:** <50ms adicionales por hook
- **Reliability:** 0 errores en CI pipeline
- **Maintainability:** Documentación completa

---

## 📁 **ARCHIVOS RELACIONADOS**

- **`TEMPLATE_MODULE_HOOKS.py`** - Template base para generar hooks
- **`REPORTE_HOOKS_UNIVERSALES_Y_OPTIMIZACION.md`** - Análisis completo y conclusiones
- **`condominium_management/hooks.py`** - Configuración actual de hooks
- **`condominium_management/document_generation/hooks_handlers/`** - Handlers de referencia
- **`CLAUDE.md`** - Reglas del proyecto y referencias

---

**🚨 ESTE CHECKLIST ES OBLIGATORIO PARA TODOS LOS MÓDULOS NUEVOS**  
**No se considera completo un módulo sin pasar 100% de este checklist**