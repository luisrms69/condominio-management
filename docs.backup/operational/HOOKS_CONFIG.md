# 🔧 CONFIGURACIÓN ACTUAL DE HOOKS

## ✅ HOOKS ESPECÍFICOS IMPLEMENTADOS:

### **Companies Module:**
```python
"Company": {
    "after_insert": "condominium_management.companies.hooks_handlers.company_detection.after_insert",
    "on_update": "condominium_management.companies.hooks_handlers.company_detection.on_update",
},
"Service Management Contract": {
    "validate": "condominium_management.companies.hooks_handlers.contract_detection.validate",
    "on_update": "condominium_management.companies.hooks_handlers.contract_detection.on_update",
},
"Company Account": {
    "after_insert": "condominium_management.companies.hooks_handlers.account_detection.after_insert",
},
```

### **Document Generation Module:**
```python
"Master Template Registry": {
    "on_update": "condominium_management.document_generation.hooks_handlers.template_propagation.on_template_update"
},
"Entity Configuration": {
    "validate": "condominium_management.document_generation.hooks_handlers.auto_detection.validate_entity_configuration",
    "on_update": "condominium_management.document_generation.hooks_handlers.auto_detection.check_configuration_conflicts",
},
```

### **Scheduled Tasks:**
```python
scheduler_events = {
    "monthly": ["condominium_management.document_generation.scheduled.performance_monitoring"],
}
```

## ❌ HOOKS UNIVERSALES DESACTIVADOS:
```python
# TEMPORALMENTE DESACTIVADOS por setup wizard conflicts
# "*": {
#     "after_insert": "condominium_management.document_generation.hooks_handlers.auto_detection.on_document_insert",
#     "on_update": "condominium_management.document_generation.hooks_handlers.auto_detection.on_document_update",
# },
```

## 🎯 PRÓXIMOS HOOKS (PENDIENTES):
- **Physical Spaces**: Building, Space, Common Area
- **Residents**: Resident, Family Member  
- **Access Control**: Access Card, Access Point
- **[Otros 7 módulos]**: Pendientes según TEMPLATE_MODULE_HOOKS.py

---
**Archivo configuración**: `condominium_management/hooks.py`  
**Template disponible**: `TEMPLATE_MODULE_HOOKS.py`  
**Última actualización**: 2025-07-04