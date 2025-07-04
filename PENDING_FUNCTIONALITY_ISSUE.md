# 🚨 Issue #7: Reactivar Hooks Universales con Verificaciones de Contexto

## 📋 **Resumen**
Los hooks universales del Document Generation Framework fueron desactivados temporalmente para resolver errores de CI en el PR #6. Esta funcionalidad crítica debe ser reactivada inmediatamente después del merge.

## 🎯 **Funcionalidad Afectada**
- **Auto-detección automática** de entidades que requieren templates
- **Validación automática** de configuraciones al crear documentos  
- **Propagación automática** de templates a nuevas entidades
- **Detección de conflictos** en tiempo real

## 🚨 **Problema Original**
```
frappe.exceptions.LinkValidationError: Could not find Parent Department: All Departments
```

Los hooks universales (`"*"`) se ejecutan durante el setup wizard de ERPNext, causando errores de validación de enlaces.

## 🛠️ **Solución Propuesta**
Implementar hooks condicionales que:
1. Detecten contexto de setup wizard/instalación
2. Eviten ejecutarse durante configuración inicial
3. Mantengan funcionalidad completa en operación normal

## 🔧 **Implementación Técnica**

### Código Objetivo:
```python
doc_events = {
    "*": {
        "after_insert": "condominium_management.document_generation.hooks_handlers.auto_detection.on_document_insert_conditional",
        "on_update": "condominium_management.document_generation.hooks_handlers.auto_detection.on_document_update_conditional",
    },
}

# En auto_detection.py
def on_document_insert_conditional(doc, method):
    # Evitar ejecutar durante setup wizard o instalación
    if frappe.flags.in_install or frappe.flags.in_setup_wizard:
        return
    
    # Ejecutar solo para DocTypes relevantes del condominio
    if doc.doctype in ["Company", "Customer", "Supplier", "Item", "Project"]:
        on_document_insert(doc, method)
```

## 📊 **Criterios de Aceptación**
- [ ] Hooks universales reactivados
- [ ] CI tests pasan sin errores
- [ ] Auto-detección funciona en operación normal
- [ ] No interfiere con setup wizard
- [ ] Tests unitarios actualizados

## ⏱️ **Estimación**
- **Desarrollo:** 2 horas
- **Testing:** 1 hora
- **Total:** 3 horas

## 🔥 **Prioridad**
**CRÍTICA** - Debe resolverse inmediatamente después del merge del PR #6

## 📝 **Notas Adicionales**
- Esta funcionalidad es **esencial** para el funcionamiento óptimo del framework
- Sin ella, las administradoras tendrán que configurar entidades manualmente
- La pérdida de automatización impacta significativamente la experiencia de usuario

## 📋 **Checklist de Implementación**
- [ ] Implementar funciones condicionales en `auto_detection.py`
- [ ] Reactivar hooks universales en `hooks.py`
- [ ] Crear tests específicos para verificar contexto
- [ ] Ejecutar CI tests para confirmar que no hay regresiones
- [ ] Actualizar documentación del framework

---

**Creado:** 2025-07-03  
**Prioridad:** CRÍTICA  
**Módulo:** Document Generation Framework  
**Estimación:** 3 horas