# Layer 3 Integration Testing Guide - REGLA #42

## Introducción

Layer 3 tests validan la **integración entre DocTypes** y el flujo completo de transacciones en el sistema. Estos tests aseguran que los diferentes componentes del Financial Management module interactúen correctamente y mantengan la integridad de datos.

## Principios Fundamentales

### 1. Propósito de Layer 3 Tests
- **Validar flujos de trabajo completos** entre múltiples DocTypes
- **Verificar integridad referencial** y consistencia de datos
- **Probar transacciones reales** con base de datos
- **Validar permisos y acceso** entre DocTypes relacionados
- **Verificar cálculos agregados** y reportes

### 2. Diferencias con Layer 1 y Layer 2
- **Layer 1**: Validación de campos individuales
- **Layer 2**: Lógica de negocio con mocks (sin BD)
- **Layer 3**: Integración real con base de datos y transacciones

## Arquitectura de Testing

### Estructura Base
```python
from frappe.tests.utils import FrappeTestCase
import frappe
from frappe.test_runner import get_test_record

class TestDocTypeL3Integration(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        """Setup inicial para toda la clase de tests"""
        cls.setup_test_dependencies()
        
    @classmethod
    def tearDownClass(cls):
        """Cleanup después de todos los tests"""
        cls.cleanup_test_data()
        
    def setUp(self):
        """Setup para cada test individual"""
        frappe.set_user("Administrator")
        
    def tearDown(self):
        """Cleanup después de cada test"""
        frappe.db.rollback()
```

### Patrones de Testing

#### 1. Test de Flujo Completo
```python
def test_complete_payment_flow(self):
    """Test del flujo completo: Property Account -> Payment -> Balance Update"""
    
    # 1. Crear Property Account
    property_account = frappe.get_doc({
        "doctype": "Property Account",
        "account_name": "Test Property",
        "property_registry": "TEST-001",
        "company": "_Test Company",
        "current_balance": 0.0
    })
    property_account.insert()
    
    # 2. Crear Payment Collection
    payment = frappe.get_doc({
        "doctype": "Payment Collection",
        "property_account": property_account.name,
        "payment_amount": 1500.00,
        "payment_method": "Transferencia",
        "payment_status": "Procesado"
    })
    payment.insert()
    
    # 3. Validar actualización de balance
    property_account.reload()
    self.assertEqual(property_account.current_balance, 1500.00)
    
    # 4. Validar Resident Account si existe
    if property_account.resident_account:
        resident_account = frappe.get_doc("Resident Account", property_account.resident_account)
        self.assertEqual(resident_account.current_balance, 1500.00)
```

#### 2. Test de Dependencias
```python
def test_doctype_dependencies(self):
    """Test de dependencias entre DocTypes"""
    
    # Crear documentos en orden de dependencia
    fee_structure = self.create_fee_structure()
    billing_cycle = self.create_billing_cycle(fee_structure.name)
    property_account = self.create_property_account()
    
    # Validar que las referencias funcionen
    self.assertEqual(billing_cycle.fee_structure, fee_structure.name)
    self.assertTrue(frappe.db.exists("Property Account", property_account.name))
```

#### 3. Test de Transacciones
```python
def test_transaction_integrity(self):
    """Test de integridad transaccional"""
    
    try:
        # Simular transacción que debe fallar
        with frappe.db.transaction():
            self.create_invalid_payment()
            # Forzar rollback
            raise Exception("Simulated error")
    except:
        pass
    
    # Validar que no hay datos inconsistentes
    self.assertEqual(frappe.db.count("Payment Collection", {"payment_status": "Invalid"}), 0)
```

## Mejores Prácticas

### 1. Gestión de Datos de Test
```python
class TestDataManager:
    @staticmethod
    def create_test_company():
        if not frappe.db.exists("Company", "_Test Company"):
            company = frappe.get_doc({
                "doctype": "Company",
                "company_name": "_Test Company",
                "abbr": "TC",
                "default_currency": "USD"
            })
            company.insert()
        return "_Test Company"
    
    @staticmethod
    def create_test_property():
        return frappe.get_doc({
            "doctype": "Property Account",
            "account_name": "Test Property " + frappe.utils.random_string(5),
            "property_registry": "TEST-" + frappe.utils.random_string(5),
            "company": "_Test Company"
        })
```

### 2. Test de Permisos
```python
def test_permission_integration(self):
    """Test de permisos entre DocTypes"""
    
    # Crear usuario con permisos limitados
    user = self.create_test_user("test@property.com", ["Property Manager"])
    
    # Cambiar contexto de usuario
    frappe.set_user(user.name)
    
    # Validar acceso a Property Account
    property_account = self.create_property_account()
    self.assertTrue(frappe.has_permission("Property Account", "read", property_account))
    
    # Validar restricciones
    self.assertFalse(frappe.has_permission("Financial Report Config", "write"))
```

### 3. Test de Cálculos Agregados
```python
def test_aggregate_calculations(self):
    """Test de cálculos que involucran múltiples DocTypes"""
    
    # Crear estructura de test
    properties = [self.create_property_account() for _ in range(3)]
    
    # Crear pagos para cada propiedad
    for prop in properties:
        payment = frappe.get_doc({
            "doctype": "Payment Collection",
            "property_account": prop.name,
            "payment_amount": 1000.00
        })
        payment.insert()
    
    # Validar cálculos agregados
    total_collected = frappe.db.sql("""
        SELECT SUM(payment_amount) 
        FROM `tabPayment Collection` 
        WHERE payment_status = 'Procesado'
    """)[0][0]
    
    self.assertEqual(total_collected, 3000.00)
```

## Patrones Específicos del Financial Management

### 1. Flujo Property Account → Payment Collection
```python
def test_property_payment_flow(self):
    """Test flujo completo de pago de propiedad"""
    
    # Setup
    property_account = self.create_property_account()
    initial_balance = property_account.current_balance
    
    # Crear pago
    payment = frappe.get_doc({
        "doctype": "Payment Collection",
        "property_account": property_account.name,
        "payment_amount": 1500.00,
        "payment_method": "Transferencia Bancaria",
        "payment_date": frappe.utils.today()
    })
    payment.insert()
    payment.submit()
    
    # Validaciones
    property_account.reload()
    self.assertEqual(
        property_account.current_balance, 
        initial_balance + 1500.00
    )
    
    # Validar historial de pagos
    payment_history = frappe.get_all("Payment Collection", 
        filters={"property_account": property_account.name},
        fields=["payment_amount", "payment_status"]
    )
    self.assertEqual(len(payment_history), 1)
    self.assertEqual(payment_history[0].payment_status, "Procesado")
```

### 2. Flujo Billing Cycle → Multiple Properties
```python
def test_billing_cycle_integration(self):
    """Test integración de ciclo de facturación"""
    
    # Setup
    fee_structure = self.create_fee_structure()
    billing_cycle = self.create_billing_cycle(fee_structure.name)
    properties = [self.create_property_account() for _ in range(5)]
    
    # Procesar ciclo de facturación
    billing_cycle.generate_invoices()
    
    # Validaciones
    for prop in properties:
        invoices = frappe.get_all("Sales Invoice", 
            filters={"customer": prop.customer}
        )
        self.assertEqual(len(invoices), 1)
        
        # Validar monto de factura
        invoice = frappe.get_doc("Sales Invoice", invoices[0].name)
        self.assertEqual(invoice.total, fee_structure.base_amount)
```

### 3. Flujo Fine Management → Property Account
```python
def test_fine_integration(self):
    """Test integración de multas con cuentas de propiedad"""
    
    # Setup
    property_account = self.create_property_account()
    
    # Crear multa
    fine = frappe.get_doc({
        "doctype": "Fine Management",
        "property_account": property_account.name,
        "fine_amount": 500.00,
        "fine_category": "Ruido excesivo",
        "fine_status": "Pendiente"
    })
    fine.insert()
    
    # Procesar pago de multa
    fine.process_payment(500.00)
    
    # Validaciones
    fine.reload()
    self.assertEqual(fine.fine_status, "Pagada")
    
    property_account.reload()
    self.assertEqual(property_account.pending_fines, 0.00)
```

## Configuración de Test Environment

### 1. Test Database Setup
```python
# En conftest.py o setup
def setup_test_database():
    """Configurar base de datos para tests"""
    frappe.db.sql("DELETE FROM `tabProperty Account` WHERE name LIKE 'TEST-%'")
    frappe.db.sql("DELETE FROM `tabPayment Collection` WHERE property_account LIKE 'TEST-%'")
    frappe.db.commit()
```

### 2. Test Data Factory
```python
class TestDataFactory:
    @staticmethod
    def create_property_account(**kwargs):
        defaults = {
            "doctype": "Property Account",
            "account_name": "Test Property " + frappe.utils.random_string(5),
            "property_registry": "TEST-" + frappe.utils.random_string(5),
            "company": "_Test Company",
            "current_balance": 0.0
        }
        defaults.update(kwargs)
        
        doc = frappe.get_doc(defaults)
        doc.insert()
        return doc
```

## Comandos de Testing

### Ejecutar Layer 3 Tests
```bash
# Ejecutar todos los tests Layer 3
bench --site test_site run-tests --doctype "Property Account" --test-type "integration"

# Ejecutar test específico
bench --site test_site run-tests --module "condominium_management.financial_management.doctype.property_account.test_property_account_l3_integration"

# Ejecutar con coverage
bench --site test_site run-tests --coverage --doctype "Property Account"
```

### Debugging Tests
```bash
# Ejecutar con verbose output
bench --site test_site run-tests --verbose --doctype "Property Account"

# Ejecutar single test method
bench --site test_site run-tests --test "test_complete_payment_flow"
```

## Métricas de Quality Assurance

### 1. Coverage Requirements
- **Minimum Coverage**: 80% de cobertura de código
- **Integration Coverage**: 100% de flujos críticos
- **Edge Cases**: Cobertura de casos extremos

### 2. Performance Benchmarks
- **Test Execution Time**: < 2 minutos por DocType
- **Database Operations**: < 100ms por operación
- **Memory Usage**: < 100MB por test suite

### 3. Test Reliability
- **Flaky Tests**: 0% tolerancia
- **Test Isolation**: Cada test debe ser independiente
- **Data Cleanup**: 100% cleanup después de cada test

## Troubleshooting

### Problemas Comunes

1. **Database Lock Issues**
   - Usar `frappe.db.rollback()` en tearDown
   - Evitar transacciones anidadas
   - Usar `frappe.db.commit()` solo cuando necesario

2. **Permission Errors**
   - Validar que el usuario tenga permisos correctos
   - Usar `frappe.set_user("Administrator")` para tests
   - Verificar roles y permisos en setup

3. **Data Inconsistency**
   - Limpiar datos de test antes de cada test
   - Usar nombres únicos para documentos de test
   - Validar estado de base de datos en tearDown

## Integración con CI/CD

### GitHub Actions Configuration
```yaml
name: Layer 3 Integration Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Test Environment
        run: |
          bench --site test_site run-tests --doctype "Property Account" --test-type "integration"
          bench --site test_site run-tests --doctype "Payment Collection" --test-type "integration"
```

---

## Recursos Adicionales

- [Overview Testing](overview.md) - Estrategia testing general
- [Layer 4 Guide](layer4-guide.md) - Config & performance testing
- [Best Practices](best-practices.md) - REGLAs 42-59 consolidadas
- [Known Issues](../framework-knowledge/known-issues.md) - Limitaciones framework

---

**Actualizado:** 2025-10-17
**Basado en:** REGLA #42 - Testing Granular Híbrido