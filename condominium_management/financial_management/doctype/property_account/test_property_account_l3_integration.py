import unittest

import frappe

# REGLA #43A: Skip automatic test records para evitar framework issues
frappe.flags.skip_test_records = True
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, today


class TestPropertyAccountL3Integration(FrappeTestCase):
	"""Layer 3 Integration Tests for Property Account DocType"""

	@classmethod
	def setUpClass(cls):
		"""Setup inicial para toda la clase de tests"""
		frappe.db.rollback()
		cls.setup_test_dependencies()

	@classmethod
	def tearDownClass(cls):
		"""Cleanup después de todos los tests"""
		cls.cleanup_test_data()
		frappe.db.rollback()

	def setUp(self):
		"""Setup para cada test individual"""
		frappe.set_user("Administrator")

	def tearDown(self):
		"""Cleanup después de cada test"""
		frappe.db.rollback()

	@classmethod
	def setup_test_dependencies(cls):
		"""Configurar dependencias necesarias para los tests"""
		# Usar mocks para evitar dependencias complejas en Layer 3
		pass

	@classmethod
	def cleanup_test_data(cls):
		"""Limpiar datos de test"""
		# Eliminar documentos de test
		frappe.db.sql("DELETE FROM `tabProperty Account` WHERE name LIKE 'TEST-%'")
		frappe.db.sql("DELETE FROM `tabPayment Collection` WHERE property_account LIKE 'TEST-%'")
		frappe.db.sql("DELETE FROM `tabResident Account` WHERE name LIKE 'TEST-%'")
		frappe.db.commit()

	def create_test_property_account(self, **kwargs):
		"""Factory para crear Property Account de test con dependencias simplificadas"""
		from unittest.mock import patch

		# Usar patch para evitar validaciones de link fields
		with (
			patch("frappe.get_doc"),
			patch("frappe.db.exists", return_value=True),
			patch("frappe.db.get_value", return_value="TEST-VALUE"),
		):
			defaults = {
				"doctype": "Property Account",
				"account_name": "Test Property " + frappe.utils.random_string(5),
				"property_registry": "TEST-PROP-REG",
				"customer": "TEST-CUSTOMER",
				"company": "_Test Company",
				"current_balance": kwargs.get("current_balance", 0.0),
				"billing_frequency": "Monthly",
				"account_status": "Active",
			}
			defaults.update(kwargs)

			# Crear mock object que simula Property Account
			mock_property_account = type("PropertyAccount", (), defaults)()
			mock_property_account.name = "TEST-" + frappe.utils.random_string(5)
			mock_property_account.save = lambda: None
			mock_property_account.reload = lambda: None
			mock_property_account.insert = lambda: None

			return mock_property_account

	def create_test_payment_collection(self, property_account, **kwargs):
		"""Factory para crear Payment Collection de test"""
		defaults = {
			"doctype": "Payment Collection",
			"property_account": property_account,
			"payment_amount": 1500.00,
			"payment_method": "Transferencia Bancaria",
			"payment_date": today(),
			"payment_status": "Procesado",
		}
		defaults.update(kwargs)

		doc = frappe.get_doc(defaults)
		doc.insert()
		return doc

	def create_test_resident_account(self, property_account, **kwargs):
		"""Factory para crear Resident Account de test"""
		defaults = {
			"doctype": "Resident Account",
			"resident_name": "Test Resident " + frappe.utils.random_string(5),
			"property_account": property_account,
			"account_type": "Owner",
			"account_status": "Active",
			"current_balance": 0.0,
		}
		defaults.update(kwargs)

		doc = frappe.get_doc(defaults)
		doc.insert()
		return doc

	def test_complete_payment_flow(self):
		"""Test del flujo completo: Property Account -> Payment -> Balance Update"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()
		initial_balance = property_account.current_balance

		# 2. Crear Payment Collection
		payment = self.create_test_payment_collection(property_account.name)

		# 3. Validar actualización de balance
		property_account.reload()
		expected_balance = initial_balance + 1500.00
		self.assertEqual(property_account.current_balance, expected_balance)

		# 4. Validar que el pago está vinculado correctamente
		payment.reload()
		self.assertEqual(payment.property_account, property_account.name)
		self.assertEqual(payment.payment_status, "Procesado")

		# 5. Validar historial de pagos
		payment_history = frappe.get_all(
			"Payment Collection",
			filters={"property_account": property_account.name},
			fields=["payment_amount", "payment_status"],
		)
		self.assertEqual(len(payment_history), 1)
		self.assertEqual(payment_history[0].payment_amount, 1500.00)

	def test_property_resident_integration(self):
		"""Test integración entre Property Account y Resident Account"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear Resident Account vinculado
		resident_account = self.create_test_resident_account(property_account.name)

		# 3. Actualizar Property Account con referencia al residente
		property_account.resident_account = resident_account.name
		property_account.save()

		# 4. Crear pago que debe afectar ambas cuentas
		self.create_test_payment_collection(property_account.name)

		# 5. Validar que ambas cuentas se actualizaron
		property_account.reload()
		resident_account.reload()

		self.assertEqual(property_account.current_balance, 1500.00)
		self.assertEqual(resident_account.current_balance, 1500.00)

		# 6. Validar integridad referencial
		self.assertEqual(property_account.resident_account, resident_account.name)
		self.assertEqual(resident_account.property_account, property_account.name)

	def test_multiple_payments_aggregation(self):
		"""Test de agregación de múltiples pagos"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear múltiples pagos
		payment_amounts = [1000.00, 750.00, 500.00, 1200.00]
		for amount in payment_amounts:
			self.create_test_payment_collection(property_account.name, payment_amount=amount)

		# 3. Validar balance total
		property_account.reload()
		expected_total = sum(payment_amounts)
		self.assertEqual(property_account.current_balance, expected_total)

		# 4. Validar conteo de pagos
		payment_count = frappe.db.count("Payment Collection", {"property_account": property_account.name})
		self.assertEqual(payment_count, len(payment_amounts))

		# 5. Validar suma de pagos en BD
		total_payments = frappe.db.sql(
			"""
            SELECT SUM(payment_amount)
            FROM `tabPayment Collection`
            WHERE property_account = %s AND payment_status = 'Procesado'
        """,
			(property_account.name,),
		)[0][0]

		self.assertEqual(flt(total_payments), expected_total)

	def test_payment_status_workflow(self):
		"""Test del flujo de estados de pago"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear pago pendiente
		payment = self.create_test_payment_collection(property_account.name, payment_status="Pendiente")

		# 3. Validar que el balance no cambió
		property_account.reload()
		self.assertEqual(property_account.current_balance, 0.0)

		# 4. Procesar pago
		payment.payment_status = "Procesado"
		payment.save()

		# 5. Validar actualización de balance
		property_account.reload()
		self.assertEqual(property_account.current_balance, 1500.00)

		# 6. Rechazar pago
		payment.payment_status = "Rechazado"
		payment.save()

		# 7. Validar reversión de balance
		property_account.reload()
		self.assertEqual(property_account.current_balance, 0.0)

	def test_account_status_transitions(self):
		"""Test transiciones de estado de cuenta"""
		# 1. Crear Property Account activa
		property_account = self.create_test_property_account(account_status="Active")

		# 2. Crear pago exitoso
		self.create_test_payment_collection(property_account.name)

		# 3. Validar que se puede procesar pagos en cuenta activa
		property_account.reload()
		self.assertEqual(property_account.current_balance, 1500.00)

		# 4. Suspender cuenta
		property_account.account_status = "Suspended"
		property_account.save()

		# 5. Intentar crear otro pago (debe procesar normalmente)
		self.create_test_payment_collection(property_account.name, payment_amount=500.00)

		# 6. Validar que el pago se procesó
		property_account.reload()
		self.assertEqual(property_account.current_balance, 2000.00)

		# 7. Cerrar cuenta
		property_account.account_status = "Closed"
		property_account.save()

		# 8. Validar estado final
		property_account.reload()
		self.assertEqual(property_account.account_status, "Closed")

	def test_transaction_integrity(self):
		"""Test de integridad transaccional"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Simular transacción que podría fallar
		try:
			# Crear pago válido
			payment = self.create_test_payment_collection(property_account.name)

			# Validar que se creó correctamente
			self.assertTrue(frappe.db.exists("Payment Collection", payment.name))

			# Simular error en proceso posterior
			if payment.payment_amount > 0:
				# Transacción exitosa
				property_account.reload()
				self.assertEqual(property_account.current_balance, 1500.00)

		except Exception:
			# En caso de error, verificar rollback
			frappe.db.rollback()
			property_account.reload()
			self.assertEqual(property_account.current_balance, 0.0)

	def test_data_consistency_across_related_doctypes(self):
		"""Test consistencia de datos entre DocTypes relacionados"""
		# 1. Crear estructura completa
		property_account = self.create_test_property_account()
		resident_account = self.create_test_resident_account(property_account.name)

		# 2. Vincular cuentas
		property_account.resident_account = resident_account.name
		property_account.save()

		# 3. Crear múltiples pagos
		payments = []
		for i in range(3):
			payment = self.create_test_payment_collection(
				property_account.name, payment_amount=500.00 * (i + 1)
			)
			payments.append(payment)

		# 4. Validar consistencia entre cuentas
		property_account.reload()
		resident_account.reload()

		# Ambas cuentas deben tener el mismo balance
		self.assertEqual(property_account.current_balance, resident_account.current_balance)

		# 5. Validar que todos los pagos están registrados
		payment_count = frappe.db.count("Payment Collection", {"property_account": property_account.name})
		self.assertEqual(payment_count, 3)

		# 6. Validar suma total
		expected_total = 500.00 + 1000.00 + 1500.00  # 3000.00
		self.assertEqual(property_account.current_balance, expected_total)

	def test_bulk_operations_performance(self):
		"""Test de rendimiento con operaciones masivas"""
		# 1. Crear múltiples Property Accounts
		property_accounts = []
		for i in range(5):
			prop = self.create_test_property_account(account_name=f"Bulk Test Property {i}")
			property_accounts.append(prop)

		# 2. Crear pagos para cada cuenta
		total_payments = 0
		for prop in property_accounts:
			for j in range(3):
				payment = self.create_test_payment_collection(prop.name, payment_amount=100.00 * (j + 1))
				total_payments += payment.payment_amount

		# 3. Validar conteo total de pagos
		payment_count = frappe.db.count("Payment Collection", {"property_account": ["like", "TEST-%"]})
		self.assertEqual(payment_count, 15)  # 5 cuentas x 3 pagos

		# 4. Validar suma total de pagos
		total_in_db = frappe.db.sql("""
            SELECT SUM(payment_amount)
            FROM `tabPayment Collection`
            WHERE property_account LIKE 'TEST-%'
        """)[0][0]

		self.assertEqual(flt(total_in_db), total_payments)

		# 5. Validar balance individual de cada cuenta
		for prop in property_accounts:
			prop.reload()
			# Cada cuenta debe tener 100 + 200 + 300 = 600
			self.assertEqual(prop.current_balance, 600.00)

	def test_concurrent_payment_processing(self):
		"""Test procesamiento concurrente de pagos"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear múltiples pagos "simultáneos"
		payments = []
		for _ in range(5):
			payment = self.create_test_payment_collection(
				property_account.name, payment_amount=200.00, payment_status="Procesado"
			)
			payments.append(payment)

		# 3. Validar que todos los pagos se procesaron
		property_account.reload()
		expected_balance = 200.00 * 5  # 1000.00
		self.assertEqual(property_account.current_balance, expected_balance)

		# 4. Validar que no hay duplicados
		payment_count = frappe.db.count("Payment Collection", {"property_account": property_account.name})
		self.assertEqual(payment_count, 5)

		# 5. Validar integridad de cada pago
		for payment in payments:
			payment.reload()
			self.assertEqual(payment.payment_status, "Procesado")
			self.assertEqual(payment.payment_amount, 200.00)
