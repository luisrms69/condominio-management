# Troubleshooting

Solución a problemas comunes de desarrollo.

---

## Tests Fallando

### Tests Pasan Local, Fallan en CI

**Diagnóstico:**

```bash
# 1. Verificar versiones
python --version
frappe --version

# 2. Recrear environment CI local
bench --site admin1.dev reinstall

# 3. Ejecutar con mismo comando que CI
bench --site admin1.dev run-tests --app condominium_management
```

**Soluciones comunes:**

1. **Database state difference**
   ```bash
   # CI siempre empieza con DB limpia
   bench --site admin1.dev drop-site --force
   bench new-site admin1.dev
   bench --site admin1.dev install-app condominium_management
   ```

2. **Permisos**
   ```python
   # Usar en todos los tests
   doc.insert(ignore_permissions=True)
   ```

3. **Fixtures no cargados**
   ```bash
   bench --site admin1.dev export-fixtures
   bench --site admin1.dev migrate
   ```

---

### Tests Intermitentes (Flaky)

**Causas comunes:**

1. **Order dependency**
   ```python
   # ❌ MAL - depende de test anterior
   def test_b(self):
       doc = frappe.get_doc("DocType", "TEST-001")  # Creado en test_a

   # ✅ BIEN - independiente
   def test_b(self):
       doc = frappe.get_doc({
           "doctype": "DocType",
           "name": f"TEST-{frappe.generate_hash()[:6]}"
       })
       doc.insert()
   ```

2. **Timing issues**
   ```python
   # ❌ MAL - usa timestamp actual
   now = frappe.utils.now()

   # ✅ BIEN - usa fecha fija
   test_date = "2025-01-15 10:00:00"
   ```

3. **External dependencies**
   ```python
   # ❌ MAL - llama API real
   result = external_api.call()

   # ✅ BIEN - usa mock
   with patch('module.external_api.call') as mock:
       mock.return_value = {"status": "success"}
       result = external_api.call()
   ```

---

## Migraciones Fallando

### Migration Fails on Fresh Install

**Error común:**
```
pymysql.err.OperationalError: (1054, "Unknown column...")
```

**Solución:**
```bash
# 1. Verificar orden de ejecución patches
cat condominium_management/patches.txt

# 2. Verificar que DocType existe antes de patch
# En patch file:
if not frappe.db.exists("DocType", "My DocType"):
    return

# 3. Reinstalar limpio
bench --site admin1.dev reinstall
```

---

### Migration Leaves Database Inconsistent

**Síntomas:** Campos en DB no match con JSON

**Diagnóstico:**
```bash
bench --site admin1.dev migrate --dry-run
bench --site admin1.dev doctor
```

**Solución:**
```bash
# Forzar sync de schema
bench --site admin1.dev migrate
bench --site admin1.dev clear-cache

# Si persiste, reinstalar
bench --site admin1.dev drop-site --force
bench new-site admin1.dev
bench --site admin1.dev install-app condominium_management
```

---

## Linting Errors

### Ruff Check Fails

**Error común:**
```
ruff check .
Found 45 errors
```

**Solución rápida:**
```bash
# Auto-fix lo posible
ruff check --fix .

# Ver errores restantes
ruff check .

# Corregir manualmente restantes
```

**Errores no auto-fixables comunes:**

1. **Unused imports**
   ```python
   # Eliminar imports no usados
   import frappe  # ← usado
   import json    # ← no usado, eliminar
   ```

2. **Line too long**
   ```python
   # ❌ Línea muy larga
   result = frappe.db.sql("SELECT name, status, amount FROM tabDocType WHERE status = 'Active' AND amount > 1000")

   # ✅ Dividir
   result = frappe.db.sql("""
       SELECT name, status, amount
       FROM tabDocType
       WHERE status = 'Active' AND amount > 1000
   """)
   ```

---

## Permisos

### PermissionError en Tests

**Error:**
```
frappe.exceptions.PermissionError: Not permitted
```

**Solución:**
```python
# Opción 1: ignore_permissions
doc.insert(ignore_permissions=True)

# Opción 2: Set user correcto
frappe.set_user("Administrator")
doc.insert()

# Opción 3: Agregar permisos en test
frappe.permissions.add_permission("DocType", "Read", "Test Role")
```

---

### Usuario No Tiene Permisos en UI

**Diagnóstico:**
```bash
# Verificar roles del usuario
bench --site admin1.dev console

>>> frappe.get_roles("user@example.com")
['Guest', 'System Manager']
```

**Solución:**
```python
# Agregar rol
user = frappe.get_doc("User", "user@example.com")
user.append("roles", {"role": "Property Manager"})
user.save()

# Verificar permisos DocType
frappe.permissions.get_all_perms("Property Account")
```

---

## Performance Issues

### Queries Lentas

**Diagnóstico:**
```python
# Enable query logging
frappe.db.sql_list.clear()

# Ejecutar operación
docs = frappe.get_all("Physical Space",
    filters={"status": "Active"},
    fields=["name", "space_name"]
)

# Ver queries
for query in frappe.db.sql_list:
    print(query)
```

**Soluciones:**

1. **Agregar índices**
   ```json
   // En DocType JSON
   {
       "fieldname": "status",
       "fieldtype": "Select",
       "in_list_view": 1,
       "search_index": 1  // ← Agregar índice
   }
   ```

2. **Limitar fields**
   ```python
   # ❌ Trae todos los campos
   docs = frappe.get_all("Physical Space")

   # ✅ Solo campos necesarios
   docs = frappe.get_all("Physical Space",
       fields=["name", "space_name"]
   )
   ```

3. **Usar pluck para single field**
   ```python
   # ❌ Menos eficiente
   names = [d.name for d in frappe.get_all("Physical Space")]

   # ✅ Más eficiente
   names = frappe.get_all("Physical Space", pluck="name")
   ```

---

## Cache Issues

### Changes Not Reflecting in UI

**Solución:**
```bash
# Clear cache completo
bench --site admin1.dev clear-cache

# Clear cache específico
bench --site admin1.dev clear-cache --doctype "Physical Space"

# Rebuild assets
bench build --app condominium_management
```

---

## Database Locks

### Database is Locked Error

**Síntomas:**
```
pymysql.err.OperationalError: (1205, 'Lock wait timeout exceeded')
```

**Solución:**
```bash
# Ver transactions activas
bench --site admin1.dev mariadb

> SHOW PROCESSLIST;
> SHOW ENGINE INNODB STATUS\G

# Kill transaction bloqueada
> KILL [process_id];
```

**Prevención en tests:**
```python
def tearDown(self):
    # SIEMPRE hacer rollback
    frappe.db.rollback()
```

---

## Import Errors

### ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'condominium_management.companies'
```

**Soluciones:**

1. **Verificar __init__.py existe**
   ```bash
   find condominium_management/companies -name "__init__.py"
   ```

2. **Reinstalar app**
   ```bash
   bench --site admin1.dev uninstall-app condominium_management
   bench --site admin1.dev install-app condominium_management
   ```

3. **Verificar path en imports**
   ```python
   # ✅ Correcto
   from condominium_management.companies.doctype.service_management_contract import ServiceManagementContract

   # ❌ Incorrecto
   from companies.doctype.service_management_contract import ServiceManagementContract
   ```

---

## Bench Commands Failing

### Bench Command Not Found

**Error:**
```
bench: command not found
```

**Solución:**
```bash
# Activar environment
cd /path/to/frappe-bench
source env/bin/activate

# O usar path absoluto
/path/to/frappe-bench/env/bin/bench --site admin1.dev migrate
```

---

### Bench Hangs/Freezes

**Solución:**
```bash
# Ctrl+C para cancelar
# Ver procesos bench
ps aux | grep bench

# Kill si necesario
pkill -f bench

# Restart
bench start
```

---

## Fixtures Not Loading

### Fixtures No Aparecen Después de Migrate

**Diagnóstico:**
```bash
# Verificar fixtures en hooks.py
cat condominium_management/hooks.py | grep fixtures

# Export fixtures manualmente
bench --site admin1.dev export-fixtures --app condominium_management
```

**Solución:**
```bash
# Reimport fixtures
bench --site admin1.dev migrate
bench --site admin1.dev clear-cache

# Si persiste, check JSON syntax
python -m json.tool fixtures/space_category.json
```

---

## Recursos Adicionales

- [Git Workflow](git-workflow.md) - Problemas git
- [CI/CD](ci-cd.md) - Problemas pipeline
- [Known Issues](../framework-knowledge/known-issues.md) - Framework limitations
- [Testing Best Practices](../testing/best-practices.md) - Testing troubleshooting

---

## Emergency Contacts

**Si nada funciona:**

1. Check GitHub Issues del proyecto
2. Consultar [Frappe Documentation](https://frappeframework.com/docs)
3. Crear issue con información completa:
   - Error exacto
   - Pasos para reproducir
   - Versiones (frappe, python, OS)
   - Logs relevantes

---

**Actualizado:** 2025-10-17
**Basado en:** Lessons learned del proyecto
