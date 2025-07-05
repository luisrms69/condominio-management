# 🤖 PROCESO AUTOMÁTICO PARA NUEVOS MÓDULOS

## ✅ CHECKLIST OBLIGATORIO

### **PASO 1: SETUP INICIAL**
```bash
# 1. Crear rama específica
git checkout main
git pull origin main  
git checkout -b feature/[modulo]-implementation

# 2. Actualizar estado
echo "- **[MODULO]**: 🔄 EN DESARROLLO - Hooks: ❌ | Tests: ❌" >> docs/operational/MODULE_STATUS.md
```

### **PASO 2: APLICAR TEMPLATE HOOKS**
```bash
# 3. Generar hooks automáticamente
python TEMPLATE_MODULE_HOOKS.py
# En console: generate_hooks_for_module('[modulo]')

# 4. Verificar generación
ls condominium_management/[modulo]/hooks_handlers/
# Debe contener: __init__.py + [handler_files].py
```

### **PASO 3: CONFIGURAR EN HOOKS.PY**
```python
# 5. Agregar a hooks.py manualmente (output del generador):
doc_events.update({
    "[DocType]": {
        "after_insert": "condominium_management.[modulo].hooks_handlers.[handler].after_insert",
        "on_update": "condominium_management.[modulo].hooks_handlers.[handler].on_update",
    },
})
```

### **PASO 4: IMPLEMENTAR TESTS**
```bash
# 6. Crear tests básicos
cp TEMPLATE_DOCTYPE_TEST.py condominium_management/[modulo]/doctype/[doctype]/test_[doctype].py
# Adaptar según DocType específico
```

### **PASO 5: VALIDACIÓN OBLIGATORIA**
```bash
# 7. Ejecutar tests (OBLIGATORIO según REGLA #13)
bench --site domika.dev run-tests --app condominium_management

# 8. Verificar pre-commit
pre-commit run --all-files

# 9. Verificar hooks funcionando
# Crear documento de prueba y verificar que hooks se ejecutan
```

### **PASO 6: DOCUMENTACIÓN Y COMMIT**
```bash
# 10. Actualizar status
sed -i 's/[MODULO].*🔄.*/[MODULO]: ✅ COMPLETO - Hooks: ✅ | Tests: ✅/' docs/operational/MODULE_STATUS.md

# 11. Actualizar configuración hooks
echo "[MODULO] hooks configurados $(date)" >> docs/operational/HOOKS_CONFIG.md

# 12. Commit limpio
git add condominium_management/[modulo]/ docs/
git commit -m "feat([modulo]): implementar hooks específicos y framework completo"

# 13. Push y PR
git push origin feature/[modulo]-implementation
gh pr create --title "feat([modulo]): Framework de hooks específicos" --body "..."
```

## 🚨 CRITERIOS DE ÉXITO:
- [ ] Hooks handlers creados y funcionando
- [ ] Configuración agregada a hooks.py  
- [ ] Tests básicos implementados y pasando
- [ ] Pre-commit hooks sin errores
- [ ] MODULE_STATUS.md actualizado
- [ ] HOOKS_CONFIG.md actualizado  
- [ ] Commit limpio sin contaminación
- [ ] PR creado con descripción completa

## ⚡ COMANDOS DE VERIFICACIÓN:
```bash
# Verificar hooks funcionan:
bench console
>>> from condominium_management.[modulo].hooks_handlers.[handler] import after_insert
>>> print("Hook disponible")

# Verificar tests:
bench --site domika.dev run-tests --doctype "[DocType Name]"

# Verificar estructura:
tree condominium_management/[modulo]/hooks_handlers/
```

---
**Template base**: `TEMPLATE_MODULE_HOOKS.py`  
**Checklist de compliance**: `CHECKLIST_NEW_MODULE.md`  
**Última actualización**: 2025-07-04