import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, today


class TestPaymentCollectionL3Integration(FrappeTestCase):
	"""Layer 3 Integration Tests for Payment Collection DocType"""

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
		# Crear Company de test si no existe
		if not frappe.db.exists("Company", "_Test Company"):
			company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "_Test Company",
					"abbr": "TC",
					"default_currency": "USD",
				}
			)
			company.insert()
			frappe.db.commit()

		# Crear Property Registry de test si no existe
		property_registry_name = "TEST-PROP-REG-001"
		if not frappe.db.exists("Property Registry", property_registry_name):
			property_registry = frappe.get_doc(
				{
					"doctype": "Property Registry",
					"name": property_registry_name,
					"property_title": "Test Property Registry",
					"property_address": "Test Address 123",
					"company": "_Test Company",
				}
			)
			property_registry.insert()
			frappe.db.commit()

		# Crear Customer de test si no existe
		customer_name = "_Test Customer Property"
		if not frappe.db.exists("Customer", customer_name):
			customer = frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": customer_name,
					"customer_type": "Individual",
					"customer_group": "Individual",
					"territory": "All Territories",
				}
			)
			customer.insert()
			frappe.db.commit()

	@classmethod
	def cleanup_test_data(cls):
		"""Limpiar datos de test"""
		frappe.db.sql("DELETE FROM `tabPayment Collection` WHERE property_account LIKE 'TEST-%'")
		frappe.db.sql("DELETE FROM `tabProperty Account` WHERE name LIKE 'TEST-%'")
		frappe.db.sql("DELETE FROM `tabCredit Balance Management` WHERE property_account LIKE 'TEST-%'")
		frappe.db.sql("DELETE FROM `tabFine Management` WHERE property_account LIKE 'TEST-%'")
		frappe.db.commit()

	def create_test_property_account(self, **kwargs):
		"""Factory para crear Property Account de test"""
		defaults = {
			"doctype": "Property Account",
			"account_name": "Test Property " + frappe.utils.random_string(5),
			"property_registry": "TEST-PROP-REG-001",
			"customer": "_Test Customer Property",
			"company": "_Test Company",
			"current_balance": 0.0,
			"billing_frequency": "Monthly",
			"account_status": "Active",
		}
		defaults.update(kwargs)

		doc = frappe.get_doc(defaults)
		doc.insert()
		return doc

	def create_test_payment_collection(self, property_account, **kwargs):
		"""Factory para crear Payment Collection de test"""
		defaults = {
			"doctype": "Payment Collection",
			"property_account": property_account,
			"payment_amount": 1500.00,
			"payment_method": "Transferencia Bancaria",
			"payment_date": today(),
			"payment_status": "Pendiente",
		}
		defaults.update(kwargs)

		doc = frappe.get_doc(defaults)
		doc.insert()
		return doc

	def create_test_credit_balance(self, property_account, **kwargs):
		"""Factory para crear Credit Balance Management de test"""
		defaults = {
			"doctype": "Credit Balance Management",
			"property_account": property_account,
			"credit_amount": 500.00,
			"credit_type": "Advance Payment",
			"credit_status": "Active",
			"expiry_date": add_days(today(), 30),
		}
		defaults.update(kwargs)

		doc = frappe.get_doc(defaults)
		doc.insert()
		return doc

	def create_test_fine_management(self, property_account, **kwargs):
		"""Factory para crear Fine Management de test"""
		defaults = {
			"doctype": "Fine Management",
			"property_account": property_account,
			"fine_amount": 200.00,
			"fine_category": "Ruido excesivo",
			"fine_status": "Pendiente",
			"fine_date": today(),
		}
		defaults.update(kwargs)

		doc = frappe.get_doc(defaults)
		doc.insert()
		return doc

	def test_payment_property_account_integration(self):
		"""Test integración básica entre Payment Collection y Property Account"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()
		initial_balance = property_account.current_balance

		# 2. Crear Payment Collection
		payment = self.create_test_payment_collection(property_account.name)

		# 3. Procesar pago
		payment.payment_status = "Procesado"
		payment.save()

		# 4. Validar actualización de balance
		property_account.reload()
		expected_balance = initial_balance + 1500.00
		self.assertEqual(property_account.current_balance, expected_balance)

		# 5. Validar vinculación
		self.assertEqual(payment.property_account, property_account.name)

	def test_payment_status_workflow_integration(self):
		"""Test flujo completo de estados de pago"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear pago pendiente
		payment = self.create_test_payment_collection(property_account.name, payment_status="Pendiente")

		# 3. Validar que no afecta balance inicial
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

		# 8. Validar historial de cambios
		payment.reload()
		self.assertEqual(payment.payment_status, "Rechazado")

	def test_payment_with_service_charges(self):
		"""Test pago con cargos de servicio"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear pago con cargos de servicio
		payment = self.create_test_payment_collection(
			property_account.name, payment_amount=1000.00, service_charge=50.00, payment_status="Procesado"
		)

		# 3. Validar cálculo de monto neto
		expected_net_amount = 1000.00 - 50.00  # 950.00
		payment.reload()
		self.assertEqual(payment.net_amount, expected_net_amount)

		# 4. Validar que el balance refleja el monto neto
		property_account.reload()
		self.assertEqual(property_account.current_balance, expected_net_amount)

	def test_payment_with_discounts(self):
		"""Test pago con descuentos"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear pago con descuento
		payment = self.create_test_payment_collection(
			property_account.name, payment_amount=1000.00, discount_amount=100.00, payment_status="Procesado"
		)

		# 3. Validar cálculo de monto neto
		expected_net_amount = 1000.00 - 100.00  # 900.00
		payment.reload()
		self.assertEqual(payment.net_amount, expected_net_amount)

		# 4. Validar actualización de balance
		property_account.reload()
		self.assertEqual(property_account.current_balance, expected_net_amount)

	def test_payment_credit_balance_integration(self):
		"""Test integración con Credit Balance Management"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear crédito disponible
		credit_balance = self.create_test_credit_balance(property_account.name)

		# 3. Crear pago que utiliza crédito
		payment = self.create_test_payment_collection(
			property_account.name,
			payment_amount=1000.00,
			use_credit_balance=True,
			credit_applied=500.00,
			payment_status="Procesado",
		)

		# 4. Validar aplicación de crédito
		payment.reload()
		expected_net_amount = 1000.00 - 500.00  # 500.00
		self.assertEqual(payment.net_amount, expected_net_amount)

		# 5. Validar actualización de balance de propiedad
		property_account.reload()
		self.assertEqual(property_account.current_balance, expected_net_amount)

		# 6. Validar reducción de crédito
		credit_balance.reload()
		remaining_credit = 500.00 - 500.00  # 0.00
		self.assertEqual(credit_balance.available_balance, remaining_credit)

	def test_payment_fine_settlement(self):
		"""Test liquidación de multas a través de pagos"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear multa pendiente
		fine = self.create_test_fine_management(property_account.name)

		# 3. Crear pago que liquida multa
		payment = self.create_test_payment_collection(
			property_account.name, payment_amount=1000.00, fine_payment=200.00, payment_status="Procesado"
		)

		# 4. Validar liquidación de multa
		fine.reload()
		self.assertEqual(fine.fine_status, "Pagada")
		self.assertEqual(fine.paid_amount, 200.00)

		# 5. Validar monto neto del pago
		payment.reload()
		expected_net_amount = 1000.00 - 200.00  # 800.00
		self.assertEqual(payment.net_amount, expected_net_amount)

		# 6. Validar balance de propiedad
		property_account.reload()
		self.assertEqual(property_account.current_balance, expected_net_amount)

	def test_multiple_payment_methods_integration(self):
		"""Test integración con múltiples métodos de pago"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear pagos con diferentes métodos
		payment_methods = ["Transferencia Bancaria", "Efectivo", "Cheque", "Tarjeta de Crédito"]

		payments = []
		for method in payment_methods:
			payment = self.create_test_payment_collection(
				property_account.name,
				payment_amount=500.00,
				payment_method=method,
				payment_status="Procesado",
			)
			payments.append(payment)

		# 3. Validar balance total
		property_account.reload()
		expected_total = 500.00 * len(payment_methods)  # 2000.00
		self.assertEqual(property_account.current_balance, expected_total)

		# 4. Validar que todos los métodos se guardaron
		for payment in payments:
			payment.reload()
			self.assertIn(payment.payment_method, payment_methods)
			self.assertEqual(payment.payment_status, "Procesado")

	def test_payment_reconciliation_process(self):
		"""Test proceso de reconciliación de pagos"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear pago pendiente de reconciliación
		payment = self.create_test_payment_collection(
			property_account.name,
			payment_amount=1500.00,
			payment_status="Pendiente",
			requires_reconciliation=True,
		)

		# 3. Validar que no afecta balance inicial
		property_account.reload()
		self.assertEqual(property_account.current_balance, 0.0)

		# 4. Reconciliar pago
		payment.payment_status = "Procesado"
		payment.reconciled_date = today()
		payment.reconciled_by = "Administrator"
		payment.save()

		# 5. Validar actualización después de reconciliación
		property_account.reload()
		self.assertEqual(property_account.current_balance, 1500.00)

		# 6. Validar datos de reconciliación
		payment.reload()
		self.assertEqual(payment.payment_status, "Procesado")
		self.assertEqual(payment.reconciled_date, today())
		self.assertEqual(payment.reconciled_by, "Administrator")

	def test_payment_commission_calculation(self):
		"""Test cálculo de comisiones en pagos"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear pago con comisión
		payment = self.create_test_payment_collection(
			property_account.name,
			payment_amount=2000.00,
			commission_rate=2.5,  # 2.5%
			payment_status="Procesado",
		)

		# 3. Validar cálculo de comisión
		expected_commission = 2000.00 * 0.025  # 50.00
		payment.reload()
		self.assertEqual(payment.commission_amount, expected_commission)

		# 4. Validar monto neto
		expected_net_amount = 2000.00 - expected_commission  # 1950.00
		self.assertEqual(payment.net_amount, expected_net_amount)

		# 5. Validar balance de propiedad
		property_account.reload()
		self.assertEqual(property_account.current_balance, expected_net_amount)

	def test_payment_retry_mechanism(self):
		"""Test mecanismo de reintento de pagos"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear pago fallido
		payment = self.create_test_payment_collection(
			property_account.name, payment_amount=1000.00, payment_status="Fallido", retry_count=0
		)

		# 3. Validar que no afecta balance
		property_account.reload()
		self.assertEqual(property_account.current_balance, 0.0)

		# 4. Reintentar pago
		payment.payment_status = "Pendiente"
		payment.retry_count = 1
		payment.save()

		# 5. Procesar reintento exitoso
		payment.payment_status = "Procesado"
		payment.save()

		# 6. Validar actualización de balance
		property_account.reload()
		self.assertEqual(property_account.current_balance, 1000.00)

		# 7. Validar historial de reintentos
		payment.reload()
		self.assertEqual(payment.retry_count, 1)
		self.assertEqual(payment.payment_status, "Procesado")

	def test_payment_splitting_integration(self):
		"""Test división de pagos entre múltiples conceptos"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear pago dividido
		payment = self.create_test_payment_collection(
			property_account.name,
			payment_amount=2000.00,
			maintenance_amount=1200.00,
			utilities_amount=500.00,
			other_amount=300.00,
			payment_status="Procesado",
		)

		# 3. Validar división de conceptos
		payment.reload()
		total_concepts = payment.maintenance_amount + payment.utilities_amount + payment.other_amount
		self.assertEqual(total_concepts, 2000.00)

		# 4. Validar balance actualizado
		property_account.reload()
		self.assertEqual(property_account.current_balance, 2000.00)

	def test_bulk_payment_processing(self):
		"""Test procesamiento masivo de pagos"""
		# 1. Crear múltiples Property Accounts
		property_accounts = []
		for i in range(5):
			prop = self.create_test_property_account(account_name=f"Bulk Property {i}")
			property_accounts.append(prop)

		# 2. Crear pagos masivos
		payment_amount = 1000.00
		payments = []
		for prop in property_accounts:
			payment = self.create_test_payment_collection(
				prop.name, payment_amount=payment_amount, payment_status="Procesado"
			)
			payments.append(payment)

		# 3. Validar procesamiento masivo
		for prop in property_accounts:
			prop.reload()
			self.assertEqual(prop.current_balance, payment_amount)

		# 4. Validar conteo total de pagos
		total_payments = frappe.db.count("Payment Collection", {"property_account": ["like", "TEST-%"]})
		self.assertEqual(total_payments, 5)

		# 5. Validar suma total
		total_amount = frappe.db.sql("""
            SELECT SUM(payment_amount)
            FROM `tabPayment Collection`
            WHERE property_account LIKE 'TEST-%'
        """)[0][0]

		expected_total = payment_amount * 5
		self.assertEqual(flt(total_amount), expected_total)

	def test_payment_notification_integration(self):
		"""Test integración con sistema de notificaciones"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear pago que requiere notificación
		payment = self.create_test_payment_collection(
			property_account.name, payment_amount=1500.00, send_notification=True, payment_status="Procesado"
		)

		# 3. Validar que el pago se procesó
		payment.reload()
		self.assertEqual(payment.payment_status, "Procesado")

		# 4. Validar flag de notificación
		self.assertTrue(payment.send_notification)

		# 5. Validar balance actualizado
		property_account.reload()
		self.assertEqual(property_account.current_balance, 1500.00)

	def test_payment_audit_trail(self):
		"""Test rastro de auditoría de pagos"""
		# 1. Crear Property Account
		property_account = self.create_test_property_account()

		# 2. Crear pago con datos de auditoría
		payment = self.create_test_payment_collection(
			property_account.name,
			payment_amount=1000.00,
			payment_status="Procesado",
			processed_by="Administrator",
			processed_date=today(),
		)

		# 3. Validar datos de auditoría
		payment.reload()
		self.assertEqual(payment.processed_by, "Administrator")
		self.assertEqual(payment.processed_date, today())

		# 4. Validar integridad de datos
		self.assertEqual(payment.payment_status, "Procesado")
		self.assertEqual(payment.payment_amount, 1000.00)

		# 5. Validar que se puede rastrear el cambio
		property_account.reload()
		self.assertEqual(property_account.current_balance, 1000.00)
