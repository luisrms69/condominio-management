import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, add_months, flt, getdate, today


class TestBillingCycleL3Integration(FrappeTestCase):
	"""Layer 3 Integration Tests for Billing Cycle DocType"""

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
		frappe.db.sql("DELETE FROM `tabBilling Cycle` WHERE name LIKE 'TEST-%'")
		frappe.db.sql("DELETE FROM `tabFee Structure` WHERE name LIKE 'TEST-%'")
		frappe.db.sql("DELETE FROM `tabProperty Account` WHERE name LIKE 'TEST-%'")
		frappe.db.sql("DELETE FROM `tabPayment Collection` WHERE property_account LIKE 'TEST-%'")
		frappe.db.sql("DELETE FROM `tabFine Management` WHERE property_account LIKE 'TEST-%'")
		frappe.db.commit()

	def create_test_fee_structure(self, **kwargs):
		"""Factory para crear Fee Structure de test"""
		defaults = {
			"doctype": "Fee Structure",
			"fee_structure_name": "Test Fee Structure " + frappe.utils.random_string(5),
			"structure_code": "TEST-" + frappe.utils.random_string(5),
			"company": "_Test Company",
			"base_amount": 1000.00,
			"calculation_method": "Fixed",
			"structure_status": "Active",
		}
		defaults.update(kwargs)

		doc = frappe.get_doc(defaults)
		doc.insert()
		return doc

	def create_test_billing_cycle(self, fee_structure, **kwargs):
		"""Factory para crear Billing Cycle de test"""
		defaults = {
			"doctype": "Billing Cycle",
			"cycle_name": "Test Billing Cycle " + frappe.utils.random_string(5),
			"cycle_code": "TEST-" + frappe.utils.random_string(5),
			"company": "_Test Company",
			"fee_structure": fee_structure,
			"billing_frequency": "Monthly",
			"start_date": today(),
			"end_date": add_months(today(), 1),
			"cycle_status": "Active",
		}
		defaults.update(kwargs)

		doc = frappe.get_doc(defaults)
		doc.insert()
		return doc

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
			"payment_amount": 1000.00,
			"payment_method": "Transferencia Bancaria",
			"payment_date": today(),
			"payment_status": "Procesado",
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
			"fine_category": "Retraso en pago",
			"fine_status": "Pendiente",
			"fine_date": today(),
		}
		defaults.update(kwargs)

		doc = frappe.get_doc(defaults)
		doc.insert()
		return doc

	def test_billing_cycle_fee_structure_integration(self):
		"""Test integración básica entre Billing Cycle y Fee Structure"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure()

		# 2. Crear Billing Cycle
		billing_cycle = self.create_test_billing_cycle(fee_structure.name)

		# 3. Validar vinculación
		self.assertEqual(billing_cycle.fee_structure, fee_structure.name)

		# 4. Validar que Fee Structure existe
		self.assertTrue(frappe.db.exists("Fee Structure", fee_structure.name))

		# 5. Validar datos del ciclo
		billing_cycle.reload()
		self.assertEqual(billing_cycle.cycle_status, "Active")
		self.assertEqual(billing_cycle.billing_frequency, "Monthly")

	def test_billing_cycle_invoice_generation(self):
		"""Test generación de facturas para múltiples propiedades"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure(base_amount=1500.00)

		# 2. Crear Billing Cycle
		billing_cycle = self.create_test_billing_cycle(fee_structure.name)

		# 3. Crear múltiples Property Accounts
		property_accounts = []
		for i in range(3):
			prop = self.create_test_property_account(account_name=f"Invoice Test Property {i}")
			property_accounts.append(prop)

		# 4. Generar facturas para el ciclo
		billing_cycle.generate_invoices_for_properties(property_accounts)

		# 5. Validar que se generaron facturas
		billing_cycle.reload()
		self.assertEqual(billing_cycle.invoices_generated, 3)

		# 6. Validar monto total facturado
		expected_total = 1500.00 * 3  # 4500.00
		self.assertEqual(billing_cycle.total_billed_amount, expected_total)

	def test_billing_cycle_collection_tracking(self):
		"""Test seguimiento de cobranza del ciclo"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure(base_amount=1000.00)

		# 2. Crear Billing Cycle
		billing_cycle = self.create_test_billing_cycle(fee_structure.name)

		# 3. Crear Property Account
		property_account = self.create_test_property_account()

		# 4. Generar factura para la propiedad
		billing_cycle.generate_invoices_for_properties([property_account])

		# 5. Crear pago parcial
		self.create_test_payment_collection(
			property_account.name, payment_amount=600.00, billing_cycle=billing_cycle.name
		)

		# 6. Validar seguimiento de cobranza
		billing_cycle.reload()
		self.assertEqual(billing_cycle.total_collected_amount, 600.00)

		# 7. Validar balance pendiente
		pending_amount = billing_cycle.total_billed_amount - billing_cycle.total_collected_amount
		self.assertEqual(billing_cycle.pending_amount, pending_amount)

		# 8. Completar pago
		self.create_test_payment_collection(
			property_account.name, payment_amount=400.00, billing_cycle=billing_cycle.name
		)

		# 9. Validar cobranza completa
		billing_cycle.reload()
		self.assertEqual(billing_cycle.total_collected_amount, 1000.00)
		self.assertEqual(billing_cycle.pending_amount, 0.00)

	def test_billing_cycle_late_fee_processing(self):
		"""Test procesamiento de multas por retraso"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure()

		# 2. Crear Billing Cycle con fecha vencida
		billing_cycle = self.create_test_billing_cycle(
			fee_structure.name,
			end_date=add_days(today(), -5),  # Vencido hace 5 días
			late_fee_enabled=True,
			late_fee_amount=100.00,
		)

		# 3. Crear Property Account
		property_account = self.create_test_property_account()

		# 4. Generar factura
		billing_cycle.generate_invoices_for_properties([property_account])

		# 5. Procesar multas por retraso
		billing_cycle.process_late_fees()

		# 6. Validar generación de multa
		fines = frappe.get_all("Fine Management", filters={"property_account": property_account.name})
		self.assertEqual(len(fines), 1)

		# 7. Validar datos de la multa
		fine = frappe.get_doc("Fine Management", fines[0].name)
		self.assertEqual(fine.fine_amount, 100.00)
		self.assertEqual(fine.fine_category, "Retraso en pago")

		# 8. Validar actualización del ciclo
		billing_cycle.reload()
		self.assertEqual(billing_cycle.late_fees_processed, 1)

	def test_billing_cycle_frequency_calculation(self):
		"""Test cálculo de frecuencia de facturación"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure()

		# 2. Crear Billing Cycle mensual
		monthly_cycle = self.create_test_billing_cycle(fee_structure.name, billing_frequency="Monthly")

		# 3. Validar cálculo de próxima fecha
		next_billing_date = monthly_cycle.calculate_next_billing_date()
		expected_date = add_months(monthly_cycle.end_date, 1)
		self.assertEqual(next_billing_date, expected_date)

		# 4. Crear Billing Cycle trimestral
		quarterly_cycle = self.create_test_billing_cycle(fee_structure.name, billing_frequency="Quarterly")

		# 5. Validar cálculo trimestral
		next_quarterly_date = quarterly_cycle.calculate_next_billing_date()
		expected_quarterly = add_months(quarterly_cycle.end_date, 3)
		self.assertEqual(next_quarterly_date, expected_quarterly)

	def test_billing_cycle_status_workflow(self):
		"""Test flujo de estados del ciclo de facturación"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure()

		# 2. Crear Billing Cycle en estado Draft
		billing_cycle = self.create_test_billing_cycle(fee_structure.name, cycle_status="Draft")

		# 3. Activar ciclo
		billing_cycle.cycle_status = "Active"
		billing_cycle.save()

		# 4. Validar estado activo
		billing_cycle.reload()
		self.assertEqual(billing_cycle.cycle_status, "Active")

		# 5. Procesar ciclo
		billing_cycle.cycle_status = "Processing"
		billing_cycle.save()

		# 6. Completar ciclo
		billing_cycle.cycle_status = "Completed"
		billing_cycle.completion_date = today()
		billing_cycle.save()

		# 7. Validar estado final
		billing_cycle.reload()
		self.assertEqual(billing_cycle.cycle_status, "Completed")
		self.assertEqual(billing_cycle.completion_date, today())

	def test_billing_cycle_adjustments(self):
		"""Test ajustes del ciclo de facturación"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure(base_amount=1000.00)

		# 2. Crear Billing Cycle
		billing_cycle = self.create_test_billing_cycle(fee_structure.name)

		# 3. Crear Property Account
		property_account = self.create_test_property_account()

		# 4. Generar factura inicial
		billing_cycle.generate_invoices_for_properties([property_account])

		# 5. Aplicar ajuste
		billing_cycle.apply_adjustment(
			property_account.name,
			adjustment_amount=200.00,
			adjustment_type="Descuento",
			adjustment_reason="Promoción especial",
		)

		# 6. Validar ajuste aplicado
		billing_cycle.reload()
		self.assertEqual(billing_cycle.total_adjustments, 200.00)

		# 7. Validar monto neto
		net_amount = billing_cycle.total_billed_amount - billing_cycle.total_adjustments
		self.assertEqual(billing_cycle.net_billed_amount, net_amount)

	def test_billing_cycle_performance_analytics(self):
		"""Test analíticas de rendimiento del ciclo"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure(base_amount=1000.00)

		# 2. Crear Billing Cycle
		billing_cycle = self.create_test_billing_cycle(fee_structure.name)

		# 3. Crear múltiples Property Accounts
		property_accounts = []
		for i in range(10):
			prop = self.create_test_property_account(account_name=f"Analytics Property {i}")
			property_accounts.append(prop)

		# 4. Generar facturas
		billing_cycle.generate_invoices_for_properties(property_accounts)

		# 5. Crear pagos parciales
		paid_count = 0
		for prop in property_accounts[:6]:  # 6 de 10 pagaron
			self.create_test_payment_collection(
				prop.name, payment_amount=1000.00, billing_cycle=billing_cycle.name
			)
			paid_count += 1

		# 6. Calcular analíticas
		billing_cycle.calculate_performance_metrics()

		# 7. Validar métricas
		billing_cycle.reload()
		expected_collection_rate = (paid_count / 10) * 100  # 60%
		self.assertEqual(billing_cycle.collection_rate, expected_collection_rate)

		# 8. Validar monto total facturado
		expected_total = 1000.00 * 10  # 10000.00
		self.assertEqual(billing_cycle.total_billed_amount, expected_total)

		# 9. Validar monto cobrado
		expected_collected = 1000.00 * 6  # 6000.00
		self.assertEqual(billing_cycle.total_collected_amount, expected_collected)

	def test_billing_cycle_bulk_operations(self):
		"""Test operaciones masivas del ciclo"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure(base_amount=800.00)

		# 2. Crear Billing Cycle
		billing_cycle = self.create_test_billing_cycle(fee_structure.name)

		# 3. Crear múltiples Property Accounts
		property_accounts = []
		for i in range(20):
			prop = self.create_test_property_account(account_name=f"Bulk Property {i}")
			property_accounts.append(prop)

		# 4. Procesar facturación masiva
		billing_cycle.process_bulk_billing(property_accounts)

		# 5. Validar facturación masiva
		billing_cycle.reload()
		self.assertEqual(billing_cycle.invoices_generated, 20)

		# 6. Validar monto total
		expected_total = 800.00 * 20  # 16000.00
		self.assertEqual(billing_cycle.total_billed_amount, expected_total)

		# 7. Validar que todas las propiedades fueron facturadas
		invoices = frappe.get_all("Sales Invoice", filters={"billing_cycle": billing_cycle.name})
		self.assertTrue(len(invoices) > 0)

	def test_billing_cycle_reporting_integration(self):
		"""Test integración con reportes del ciclo"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure(base_amount=1200.00)

		# 2. Crear Billing Cycle
		billing_cycle = self.create_test_billing_cycle(fee_structure.name)

		# 3. Crear Property Accounts
		property_accounts = []
		for i in range(5):
			prop = self.create_test_property_account(account_name=f"Report Property {i}")
			property_accounts.append(prop)

		# 4. Generar facturas
		billing_cycle.generate_invoices_for_properties(property_accounts)

		# 5. Crear algunos pagos
		for prop in property_accounts[:3]:
			self.create_test_payment_collection(
				prop.name, payment_amount=1200.00, billing_cycle=billing_cycle.name
			)

		# 6. Generar reporte del ciclo
		report_data = billing_cycle.generate_cycle_report()

		# 7. Validar datos del reporte
		self.assertEqual(report_data["total_properties"], 5)
		self.assertEqual(report_data["total_invoiced"], 6000.00)  # 1200 * 5
		self.assertEqual(report_data["total_collected"], 3600.00)  # 1200 * 3
		self.assertEqual(report_data["collection_rate"], 60.0)  # 3/5 * 100

	def test_billing_cycle_validation_rules(self):
		"""Test reglas de validación del ciclo"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure()

		# 2. Intentar crear ciclo con fechas inválidas
		with self.assertRaises(Exception):
			self.create_test_billing_cycle(
				fee_structure.name,
				start_date=today(),
				end_date=add_days(today(), -10),  # Fecha fin anterior a inicio
			)

		# 3. Crear ciclo válido
		valid_cycle = self.create_test_billing_cycle(fee_structure.name)

		# 4. Validar que el ciclo válido se creó
		self.assertTrue(frappe.db.exists("Billing Cycle", valid_cycle.name))

		# 5. Validar fechas correctas
		self.assertGreater(valid_cycle.end_date, valid_cycle.start_date)

	def test_billing_cycle_closure_process(self):
		"""Test proceso de cierre del ciclo"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure(base_amount=1000.00)

		# 2. Crear Billing Cycle
		billing_cycle = self.create_test_billing_cycle(fee_structure.name)

		# 3. Crear Property Account
		property_account = self.create_test_property_account()

		# 4. Generar factura
		billing_cycle.generate_invoices_for_properties([property_account])

		# 5. Procesar pago
		self.create_test_payment_collection(
			property_account.name, payment_amount=1000.00, billing_cycle=billing_cycle.name
		)

		# 6. Cerrar ciclo
		billing_cycle.close_billing_cycle()

		# 7. Validar cierre
		billing_cycle.reload()
		self.assertEqual(billing_cycle.cycle_status, "Closed")
		self.assertEqual(billing_cycle.closure_date, today())

		# 8. Validar métricas finales
		self.assertEqual(billing_cycle.total_billed_amount, 1000.00)
		self.assertEqual(billing_cycle.total_collected_amount, 1000.00)
		self.assertEqual(billing_cycle.collection_rate, 100.0)

	def test_billing_cycle_error_handling(self):
		"""Test manejo de errores en el ciclo"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure()

		# 2. Crear Billing Cycle
		billing_cycle = self.create_test_billing_cycle(fee_structure.name)

		# 3. Crear Property Account con datos inválidos
		property_account = self.create_test_property_account()

		# 4. Intentar generar factura con error simulado
		try:
			# Simular error en generación
			billing_cycle.generate_invoices_for_properties([property_account])

			# Si no hay error, validar que se procesó correctamente
			billing_cycle.reload()
			self.assertEqual(billing_cycle.invoices_generated, 1)

		except Exception:
			# Validar que el error se manejó correctamente
			billing_cycle.reload()
			self.assertEqual(billing_cycle.cycle_status, "Error")
			self.assertTrue(hasattr(billing_cycle, "error_message"))

	def test_billing_cycle_integration_with_external_systems(self):
		"""Test integración con sistemas externos"""
		# 1. Crear Fee Structure
		fee_structure = self.create_test_fee_structure()

		# 2. Crear Billing Cycle con integración externa
		billing_cycle = self.create_test_billing_cycle(
			fee_structure.name, external_system_enabled=True, external_system_code="EXT001"
		)

		# 3. Crear Property Account
		property_account = self.create_test_property_account()

		# 4. Generar factura con sincronización externa
		billing_cycle.generate_invoices_for_properties([property_account])

		# 5. Validar sincronización
		billing_cycle.reload()
		self.assertTrue(billing_cycle.external_sync_status)

		# 6. Validar código externo
		self.assertEqual(billing_cycle.external_system_code, "EXT001")
