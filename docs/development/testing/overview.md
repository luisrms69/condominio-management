# Testing - Overview

Visión general de la estrategia de testing del proyecto.

---

## Framework: Testing Granular Híbrido

El proyecto implementa metodología de testing en múltiples layers especializados.

---

## Layers de Testing

### Layer 3: Integración DocTypes
**Propósito:** Validar flujos completos entre múltiples DocTypes.

**Características:**
- Base de datos real
- Transacciones completas
- Validación integridad referencial

**[Ver guía completa →](layer3-guide.md)**

---

### Layer 4A: Configuration Validation
**Propósito:** Validar consistencia configuración y metadata.

**Validaciones:**
- JSON vs Meta consistency
- Permission configuration
- Hooks validation
- Schema integrity

**[Ver guía completa →](layer4-guide.md)**

---

### Layer 4B: Performance Validation
**Propósito:** Validar rendimiento y benchmarks.

**Métricas:**
- insert() < 300ms
- get_all() < 100ms
- Search < 500ms
- Batch operations

**[Ver guía completa →](layer4-guide.md)**

---

## Principios Fundamentales

### 1. Determinismo Absoluto
- Sin red
- Sin timestamps reales
- Resultados reproducibles 100%

### 2. Aislamiento Completo
- Cada test crea sus datos
- No compartir estado
- Cleanup automático

### 3. Simplicidad
- Probar lógica de negocio, NO UI
- Mocks solo para boundaries externos
- Sin over-engineering

---

## Comandos Esenciales

```bash
# Tests completos
bench --site admin1.dev run-tests --app condominium_management

# Tests específicos Layer 3
bench --site admin1.dev run-tests --module "...test_l3_integration"

# Tests específicos Layer 4B
bench --site admin1.dev run-tests --module "...test_l4b_performance"

# Con coverage
bench --site admin1.dev run-tests --coverage --app condominium_management
```

---

## Estructura Base Test

```python
from frappe.tests.utils import FrappeTestCase
import frappe

class TestDocTypeIntegration(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        self.test_id = "TEST-" + frappe.generate_hash()[:6]

    def tearDown(self):
        frappe.db.rollback()  # Automático

    def test_business_rule(self):
        """Test regla de negocio específica"""
        doc = frappe.get_doc({
            "doctype": "Physical Space",
            "space_name": f"Test-{self.test_id}"
        })
        doc.insert()
        self.assertTrue(frappe.db.exists("Physical Space", doc.name))
```

---

## REGLAs de Testing (42-59)

Metodología completa documentada en **[Best Practices](best-practices.md)**:

- REGLA #42: Testing Granular Core
- REGLA #43: Skip Test Records & Mocking
- REGLA #44: CI/CD Testing Mastery
- REGLA #46: Layer 4 Debugging
- REGLA #48: Company Creation Workaround
- REGLA #51: Linting Resolution
- REGLA #52: Framework Limits
- REGLAS #56-57: Layer 4 Advanced
- REGLA #59: Testing Completion Criteria

---

## Definition of Done

Para considerar módulo "completo":

- ✅ Layer 3 Coverage: 80%+ flujos críticos
- ✅ Layer 4A: 100% config validation
- ✅ Layer 4B: Performance < benchmarks
- ✅ CI/CD: Pipeline passing
- ✅ 0 Flaky Tests
- ✅ Docs: Testing methodology documentada

---

## Recursos Adicionales

- [Layer 3 Guide](layer3-guide.md) - Integración completa
- [Layer 4 Guide](layer4-guide.md) - Config & Performance
- [Best Practices](best-practices.md) - REGLAs 42-59 consolidadas
- [Framework Knowledge](../framework-knowledge/known-issues.md) - Known issues
- [CI/CD](../workflows/ci-cd.md) - Integración continua

---

**Actualizado:** 2025-10-17
**Metodología:** REGLA #42 - Testing Granular Híbrido
