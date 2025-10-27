# 🔧 REPORTE: Fix Error CI PR #27

**Fecha:** 2025-10-26
**PR:** #27 - Cleanup Obsolete Scripts
**Estado:** ✅ RESUELTO

---

## 📊 RESUMEN EJECUTIVO

**Problema:** Error CI en 2 test suites después de eliminar archivos obsoletos
**Causa raíz:** Eliminación de `test_company_customizations.py` dejó de crear empresas dummy
**Solución:** Modificar tests para usar `create_test_company_with_default_fallback()`
**Resultado:** ✅ 950/950 tests passing (0 errors)

---

## 🔍 DIAGNÓSTICO COMPLETO

### **Error CI Original**

```
ERROR: setUpClass (TestServiceManagementContract)
LinkValidationError: Could not find Row #11: Company: Test Company Default

Traceback:
  File test_service_management_contract.py:37
    company.insert(ignore_permissions=True)
  File company.py:266 in on_update
    self.set_mode_of_payment_account()
```

### **Análisis Causa Raíz**

**Archivos eliminados en commit 509d2ce:**
1. `companies/install.py` (obsoleto)
2. `companies/custom_fields/company_custom_fields.py` (obsoleto)
3. `companies/test_company_customizations.py` ← **ESTE ES LA CLAVE**

**Cadena de dependencias:**
```
test_company_customizations.py
  └── usaba create_test_company_with_default_fallback()
      └── crea "Test Company Default" (empresas dummy)
          └── necesarias para ERPNext.company.set_mode_of_payment_account()

test_service_management_contract.py
  └── creaba empresas DIRECTAMENTE
      └── ERPNext busca "Test Company Default"
          └── ❌ NO EXISTE → LinkValidationError

test_factories.py (TestDataFactory)
  └── creaba empresas DIRECTAMENTE
      └── mismo problema
```

### **Verificación Archivos Eliminados**

**test_company_customizations.py contenía:**
```python
def setUp(self):
    # Creaba tipos de empresa
    self.create_test_company_types()
    # Instalaba custom fields
    self.install_custom_fields()

def install_custom_fields(self):
    from condominium_management.companies.custom_fields.company_custom_fields import (
        install_company_customizations,
    )
    install_company_customizations()
```

**test_utils.py (todavía existe) contiene:**
```python
def create_test_company_with_default_fallback(company_name, abbr, currency, country):
    # Crear empresas dummy requeridas por ERPNext
    dummy_companies = [
        {"company_name": "Test Company Default", "abbr": "TCD"},  # ← LA CLAVE
        {"company_name": "Test Condominium", "abbr": "TCS"},
        # ... 10 empresas dummy más
    ]

    for dummy_data in dummy_companies:
        if not frappe.db.exists("Company", dummy_data["company_name"]):
            dummy_company = frappe.get_doc({...})
            dummy_company.insert(ignore_permissions=True)
```

---

## 🛠️ SOLUCIÓN IMPLEMENTADA

### **Archivo 1: test_service_management_contract.py**

**Cambio:**
```python
# ❌ ANTES (creaba empresas directamente)
@classmethod
def create_test_companies(cls):
    for company_name, abbr in [("Provider Co", "PC"), ("Client Co", "CC")]:
        if not frappe.db.exists("Company", company_name):
            company = frappe.get_doc({
                "doctype": "Company",
                "company_name": company_name,
                "abbr": abbr,
                "default_currency": "MXN",
                "country": "Mexico",
            })
            company.insert(ignore_permissions=True)  # ← Falla aquí

# ✅ DESPUÉS (usa función helper)
@classmethod
def create_test_companies(cls):
    from condominium_management.companies.test_utils import create_test_company_with_default_fallback

    for company_name, abbr in [("Provider Co", "PC"), ("Client Co", "CC")]:
        # Crea "Test Company Default" y otras empresas dummy automáticamente
        create_test_company_with_default_fallback(company_name, abbr, "MXN", "Mexico")
```

### **Archivo 2: test_factories.py**

**Cambio:**
```python
# ❌ ANTES (creaba empresa directamente, 57 líneas de código)
@staticmethod
def create_test_company(company_name="Test Company Default", abbr=None):
    if not abbr:
        abbr = "".join([word[0].upper() for word in company_name.split()[:3]])

    if not frappe.db.exists("Company", company_name):
        # Limpiar datos huérfanos
        frappe.db.sql(...)

        company = frappe.get_doc({...})
        try:
            company.insert(ignore_permissions=True)  # ← Falla aquí
            return company
        except Exception as e:
            if "Row #11: Company: Test Company Default" in str(e):
                # Fallback manual
                basic_company = frappe.get_doc({...})
                basic_company.insert(ignore_permissions=True)
                return basic_company

# ✅ DESPUÉS (delega a función helper, 10 líneas)
@staticmethod
def create_test_company(company_name="Test Company Default", abbr=None):
    from condominium_management.companies.test_utils import create_test_company_with_default_fallback

    if not abbr:
        abbr = "".join([word[0].upper() for word in company_name.split()[:3]])

    # Delega a función que crea empresas dummy automáticamente
    return create_test_company_with_default_fallback(company_name, abbr, "MXN", "Mexico")
```

**Beneficios:**
- ✅ Eliminadas 57 líneas de código duplicado
- ✅ Lógica centralizada en `test_utils.py`
- ✅ Mantenimiento más fácil
- ✅ Consistencia entre todos los tests

---

## ✅ VERIFICACIÓN COMPLETA

### **Tests Específicos Reparados**

**1. TestServiceManagementContract:**
```bash
bench --site admin1.dev run-tests \
  --app condominium_management \
  --module condominium_management.companies.doctype.service_management_contract.test_service_management_contract

Ran 10 tests in 33.821s
OK ✅
```

**2. TestMasterTemplateRegistry:**
```bash
bench --site admin1.dev run-tests \
  --app condominium_management \
  --module condominium_management.document_generation.doctype.master_template_registry.test_master_template_registry

Ran 10 tests in 23.728s
OK ✅
```

### **Suite Completa**

**Resultado final:**
```bash
bench --site admin1.dev run-tests --app condominium_management

Ran 950 tests in 110.412s
OK (skipped=82) ✅

✅ 0 errors
✅ 0 failures
✅ 950 tests passing
✅ 82 tests skipped (esperado)
```

**Comparación con PR #26:**
```
PR #26 (antes cleanup):  957/957 tests passing (82 skipped)
PR #27 (después cleanup): 950/950 tests passing (82 skipped)
```

**Nota:** Diferencia de 7 tests se debe a eliminación de `test_company_customizations.py` que tenía 7 tests.

---

## 📝 COMMITS CREADOS

### **Commit 1: c5feeb4 - Fix tests**
```
fix(tests): reparar error CI causado por eliminación test_company_customizations.py

Archivos modificados:
- test_service_management_contract.py (12 líneas cambiadas)
- test_factories.py (57 líneas eliminadas → 10 líneas)

Resultado: 950/950 tests passing
```

### **Commit 2: 1d7951c - Update CHANGELOG**
```
docs(changelog): actualizar con fix error CI PR #27

Agregado en sección Fixed:
- PR #27: Error CI reparado usando create_test_company_with_default_fallback()
```

---

## 🎯 ESTADO FINAL PR #27

### **Branch:** `chore/cleanup-obsolete-scripts`

**Commits totales:**
1. `509d2ce` - chore(companies): eliminar scripts obsoletos instalación custom fields
2. `94757b2` - docs(changelog): actualizar con PR #26 y eliminación scripts obsoletos
3. `c5feeb4` - fix(tests): reparar error CI causado por eliminación test_company_customizations.py
4. `1d7951c` - docs(changelog): actualizar con fix error CI PR #27

**Archivos eliminados:**
- companies/install.py (obsoleto)
- companies/custom_fields/company_custom_fields.py (obsoleto)
- companies/test_company_customizations.py (obsoleto)

**Archivos modificados:**
- test_service_management_contract.py (fix CI)
- test_factories.py (fix CI)
- CHANGELOG.md (actualizado 2x)

**Verificación CI:** ✅ Todos los tests pasan localmente

---

## 🚀 PRÓXIMOS PASOS

**Pendiente:**
1. ⏳ Push a GitHub (requiere autorización explícita usuario)
2. ⏳ Actualizar PR #27 con nuevos commits
3. ⏳ Verificar CI GitHub Actions pasa
4. ⏳ Merge PR #27 a main

**NO HACER SIN AUTORIZACIÓN:**
- ❌ `git push` (RC-005: Autorización explícita obligatoria)
- ❌ Modificar PR sin permiso
- ❌ Merge automático

---

## 📚 REFERENCIAS

**Archivos clave:**
- `condominium_management/companies/test_utils.py` - Función helper con empresas dummy
- `docs/development/REPORTE-FIXTURES-SOBRESCRITURA.md` - Análisis previo fixtures

**Reglas aplicables:**
- **RG-009:** Fixtures obligatorios (zero-config deployment)
- **RG-003:** Testing framework (test isolation)
- **RC-005:** Autorización explícita obligatoria

**Lecciones aprendidas:**
1. ✅ Analizar dependencias tests antes de eliminar archivos test
2. ✅ Tests pueden depender de setup de otros tests (via shared utilities)
3. ✅ ERPNext Company.on_update() requiere empresas dummy para validaciones
4. ✅ Centralizar lógica creación test data evita duplicación y errores

---

**Generado:** 2025-10-26
**Verificado por:** Claude Code
**Estado:** ✅ RESUELTO - Esperando autorización push
