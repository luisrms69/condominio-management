# Testing Best Practices - REGLAs 42-59 Consolidadas

**Metodología:** Testing Granular Híbrido
**Basado en:** Framework knowledge acumulado 2025-01-15
**Estado:** ✅ IMPLEMENTADO en Financial Management Module

---

## 🎯 Filosofía General de Testing

El proyecto implementa **Testing Granular Híbrido** con 4 layers especializados:

| Layer | Propósito | Herramientas | Velocidad |
|-------|-----------|--------------|-----------|
| **Layer 3** | Integración DocTypes | FrappeTestCase + BD | Media |
| **Layer 4A** | Config Validation | Meta + JSON + Permisos | Rápida |
| **Layer 4B** | Performance | time.perf_counter | Media |
| **CI/CD** | Automatización | GitHub Actions | Variable |

---

## 📚 REGLA #42: Testing Granular Híbrido Core

### Principios Fundamentales

1. **Separación clara de responsabilidades**
   - Layer 3: Flujos de trabajo completos
   - Layer 4A: Configuración y metadata
   - Layer 4B: Performance y benchmarks

2. **Determinismo absoluto**
   - Sin dependencias externas
   - Sin red, sin reloj real
   - Tests reproducibles 100%

3. **Aislamiento completo**
   - Cada test crea sus datos
   - No compartir estado entre tests
   - Cleanup garantizado con rollback

4. **Simplicidad sobre complejidad**
   - Probar reglas de negocio, NO UI
   - Mocks solo para boundaries externos
   - Sin over-engineering

### Estructura Base Requerida

```python
from frappe.tests.utils import FrappeTestCase
import frappe

class TestDocTypeIntegration(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        # IDs únicos, no hardcode
        self.test_id = "TEST-" + frappe.generate_hash()[:6]

    def tearDown(self):
        # Framework maneja rollback automático
        frappe.db.rollback()

    def test_business_rule(self):
        """Test de regla de negocio específica"""
        doc = frappe.get_doc({
            "doctype": "Property Account",
            "account_name": f"Test-{self.test_id}"
        })
        doc.insert()
        self.assertTrue(frappe.db.exists("Property Account", doc.name))
```

---

## 🔧 REGLA #43: Skip Test Records & Mocking Consistency

### Problema Framework

Frappe genera test records automáticamente que pueden causar conflictos.

### Solución Estándar

```python
# tests/__init__.py - Setup global UNA vez
import frappe
frappe.flags.skip_test_records = True  # Evita framework issues
```

### Mocking Correcto

```python
# ✅ CORRECTO - Mock boundary externo
from unittest.mock import patch

with patch("condominium_management.integrations.api_client.call") as mock_api:
    mock_api.return_value = {"status": "success", "data": {}}
    result = doc.process_external()

# ❌ PROHIBIDO - Mock framework core
with patch("frappe.get_doc") as mock:
    # Efectos colaterales impredecibles
```

### Consistencia Mocks

- Mock SOLO adaptadores externos
- Respuestas mínimas "contrato"
- NO mock `frappe.get_doc`, `frappe.db`, métodos core

---

## 🚀 REGLA #44: CI/CD Testing Mastery

### GitHub Actions Configuration

```yaml
name: Testing Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Frappe
        run: |
          # Setup bench environment

      - name: Run Tests
        run: |
          bench --site test_site run-tests --app condominium_management

      - name: Performance Tests
        run: |
          bench --site test_site run-tests --module "...test_l4b_performance"
```

### Issues Comunes CI/CD

1. **Permission Errors**
   - Usar `ignore_permissions=True` en tests
   - Verificar setup de usuarios/roles

2. **Database State**
   - Garantizar cleanup con rollback
   - No depender de orden de ejecución

3. **Environment Differences**
   - Variables consistentes entre local/CI
   - Fixtures para datos base

---

## ⚡ REGLA #46: Layer 4 Debugging Methodology

### Debugging Performance Issues

```python
import time

def test_with_timing(self):
    """Test con medición precisa de tiempo"""
    start = time.perf_counter()

    # Operación a medir
    doc.complex_operation()

    elapsed = time.perf_counter() - start

    # Log para debugging
    print(f"Operation took: {elapsed:.3f}s")

    # Assertion con margen
    self.assertLess(elapsed, 0.3, f"Too slow: {elapsed:.3f}s")
```

### Profiling Queries

```python
def test_query_performance(self):
    """Test performance de queries"""

    # Enable query logging
    frappe.db.sql_list.clear()

    # Operación
    docs = frappe.get_all("Property Account",
        filters={"status": "Active"},
        fields=["name", "balance"]
    )

    # Verificar queries ejecutadas
    queries = frappe.db.sql_list
    print(f"Queries executed: {len(queries)}")

    # Detectar N+1 problems
    self.assertLess(len(queries), 5, "Too many queries (N+1 problem?)")
```

---

## 🛠️ REGLA #48: Company Creation Emergency Workaround

### Problema

ERPNext Company creation requiere fixtures complejos.

### Workaround

```python
@classmethod
def setUpClass(cls):
    """Setup de Company para tests"""
    if not frappe.db.exists("Company", "_Test Company"):
        # Usar fixtures existentes cuando sea posible
        from erpnext.setup.doctype.company.test_company import create_test_company
        create_test_company()

    cls.company = "_Test Company"
```

---

## 🎯 REGLA #51: Linting Resolution Methodology

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
```

### Resolución Sistemática

```bash
# 1. Auto-fix lo posible
ruff check --fix .

# 2. Verificar cambios
git diff

# 3. Corregir manualmente restantes
# 4. Commit sin --no-verify
git commit -m "fix: resolve linting issues"
```

---

## 📊 REGLA #52: Framework Limits Exceeded

### Límites Conocidos Frappe

1. **Nested Set limitations**
   - Actualizaciones costosas en árboles grandes
   - Mitigación: Cache, batch operations

2. **Permission System**
   - Queries lentas con muchos roles
   - Mitigación: Índices, simplificar roles

3. **Metadata Loading**
   - get_meta() puede ser lento
   - Mitigación: Cache manual cuando necesario

### Workarounds Documentados

Ver: `docs/development/framework-knowledge/known-issues.md`

---

## 🔥 REGLAS 56-57: Layer 4 Advanced (Type B/C)

### Type B: Critical Performance

**Metas enterprise:**
- insert() < 300ms
- get_all() < 100ms
- Search < 500ms
- Batch 1000 records < 3s

### Type C: Advanced Integration

**Validaciones:**
- Cross-DocType workflows
- Transacciones complejas
- Reportes agregados
- Permisos multi-rol

Ver guías específicas:
- `layer3-guide.md` - Integración
- `layer4-guide.md` - Configuration & Performance

---

## 🎓 REGLA #59: Testing Completion Criteria

### Definition of Done Testing

**Para considerar módulo "completo":**

1. ✅ **Layer 3 Coverage**: 80%+ flujos críticos
2. ✅ **Layer 4A**: 100% config validation
3. ✅ **Layer 4B**: Performance < benchmarks
4. ✅ **CI/CD**: Pipeline passing
5. ✅ **0 Flaky Tests**: Determinismo 100%
6. ✅ **Docs**: Testing methodology documentada

### Checklist por Módulo

```markdown
- [ ] Layer 3 tests implementados (>= 10 tests)
- [ ] Layer 4A config validation completa
- [ ] Layer 4B performance benchmarks passing
- [ ] CI/CD pipeline configured
- [ ] Pre-commit hooks configured
- [ ] Testing docs actualizadas
- [ ] 0 tests flakey detectados
```

---

## 📖 Referencias Rápidas

| Regla | Tema | Archivo Original |
|-------|------|------------------|
| 42 | Testing Granular Core | REGLA_42_TESTING_GRANULAR_HIBRIDO.md |
| 43 | Mocking & Skip Records | REGLA_43_*.md |
| 44 | CI/CD Mastery | REGLA_44_CI_CD_TESTING_MASTERY.md |
| 46 | Debugging Layer 4 | REGLA_46_LAYER4_DEBUGGING_METHODOLOGY.md |
| 47 | CI/CD L4 Compatibility | REGLA_47_CI_CD_LAYER4_COMPATIBILITY.md |
| 48 | Company Workaround | REGLA_48_COMPANY_CREATION_EMERGENCY_WORKAROUND.md |
| 51 | Linting Resolution | REGLA_51_LINTING_RESOLUTION_METHODOLOGY.md |
| 52 | Framework Limits | REGLA_52_FRAMEWORK_LIMITS_EXCEEDED.md |
| 56 | Layer4 Type C | REGLA_56_LAYER4_TYPE_C_ADVANCED_INTEGRATION.md |
| 57 | Layer4 Type B | REGLA_57_LAYER4_TYPE_B_CRITICAL_PERFORMANCE.md |
| 59 | Completion Criteria | REGLA_59_COMPLETION.md |

---

## 🚀 Comandos Esenciales

```bash
# Tests completos
bench --site admin1.dev run-tests --app condominium_management

# Tests específicos Layer 3
bench --site admin1.dev run-tests --module "...test_l3_integration"

# Tests específicos Layer 4B
bench --site admin1.dev run-tests --module "...test_l4b_performance"

# Con coverage
bench --site admin1.dev run-tests --coverage --app condominium_management

# Linting
ruff check --fix .

# Pre-commit manual
pre-commit run --all-files
```

---

## Recursos Adicionales

- [Overview Testing](overview.md) - Estrategia testing general
- [Layer 3 Guide](layer3-guide.md) - Testing integración
- [Layer 4 Guide](layer4-guide.md) - Config & performance
- [Known Issues](../framework-knowledge/known-issues.md) - Limitaciones framework

---

**Actualizado:** 2025-10-17
**Basado en:** REGLAs 42-59 consolidadas
