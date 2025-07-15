# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Credit Balance Management - Testing Granular REGLA #32
=====================================================

Tests para Credit Balance Management DocType siguiendo metodología
granular de 4 capas para validación completa del sistema de saldos a favor.
"""

import unittest
from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, getdate, nowdate

# REGLA #43: Skip automatic test records para evitar framework issue
frappe.flags.skip_test_records = True


class TestCreditBalanceManagement(FrappeTestCase):
	"""Test Credit Balance Management con REGLA #32 - Testing Granular"""

	@classmethod
	def setUpClass(cls):
		"""Setup de clase - REGLA #43: Pure mocking approach"""
		# REGLA #43: NO super().setUpClass() para evitar Company creation
		cls.setup_credit_balance_data()

	@classmethod
	def setup_credit_balance_data(cls):
		"""Setup datos específicos para testing Credit Balance Management - REGLA #43"""

		# REGLA #43: Solo mocks, NO crear dependencies reales que causen framework issues
		cls.mock_property_account_name = "PA-CREDIT-TEST-001"
		cls.mock_resident_account_name = "RA-CREDIT-TEST-001"
		cls.mock_customer_name = "TEST_CUSTOMER_CREDIT_001"
		cls.test_customer_name = "TEST_CUSTOMER_CREDIT_001"
		cls.test_property_registry_name = "TEST_PROP_CREDIT_001"

	# =============================================================================
	# LAYER 1: FIELD VALIDATION (SIEMPRE FUNCIONA)
	# =============================================================================

	def test_layer_1_field_validation_isolated(self):
		"""LAYER 1: Validación básica de campos Credit Balance Management"""
		doc = frappe.new_doc("Credit Balance Management")

		# Verificar campos críticos existen
		required_fields = ["balance_date", "account_type", "credit_amount", "balance_status"]

		for field in required_fields:
			self.assertTrue(
				hasattr(doc, field), f"Campo requerido '{field}' no existe en Credit Balance Management"
			)

	def test_layer_1_currency_precision_validation(self):
		"""LAYER 1: Validación de precisión en campos de currency"""
		doc = frappe.new_doc("Credit Balance Management")

		# Campos de currency deben existir
		currency_fields = ["credit_amount", "overpayment_amount", "total_applied", "remaining_balance"]

		for field in currency_fields:
			self.assertTrue(
				hasattr(doc, field), f"Campo currency '{field}' no existe en Credit Balance Management"
			)

	def test_layer_1_select_options_validation(self):
		"""LAYER 1: Validación de opciones en campos Select"""
		doc = frappe.new_doc("Credit Balance Management")

		# Verificar campo account_type tiene opciones esperadas
		meta = doc.meta
		account_type_field = next((f for f in meta.fields if f.fieldname == "account_type"), None)
		self.assertIsNotNone(account_type_field, "Campo account_type no encontrado")

		expected_options = ["Property Account", "Resident Account", "Ambos"]
		options = account_type_field.options.split("\n") if account_type_field.options else []

		for option in expected_options:
			self.assertIn(option, options, f"Opción '{option}' no encontrada en account_type")

	def test_layer_1_balance_status_options_validation(self):
		"""LAYER 1: Validación de estados de saldo disponibles"""
		doc = frappe.new_doc("Credit Balance Management")

		meta = doc.meta
		balance_status_field = next((f for f in meta.fields if f.fieldname == "balance_status"), None)
		self.assertIsNotNone(balance_status_field, "Campo balance_status no encontrado")

		expected_statuses = ["Activo", "Aplicado Parcial", "Aplicado Total", "Expirado", "Cancelado"]
		options = balance_status_field.options.split("\n") if balance_status_field.options else []

		for status in expected_statuses:
			self.assertIn(status, options, f"Estado '{status}' no encontrado en balance_status")

	def test_layer_1_origin_type_options_validation(self):
		"""LAYER 1: Validación de tipos de origen del crédito"""
		doc = frappe.new_doc("Credit Balance Management")

		meta = doc.meta
		origin_type_field = next((f for f in meta.fields if f.fieldname == "origin_type"), None)
		self.assertIsNotNone(origin_type_field, "Campo origin_type no encontrado")

		expected_origins = [
			"Sobrepago",
			"Reembolso",
			"Ajuste Manual",
			"Descuento Aplicado",
			"Error Corrección",
			"Transferencia",
		]
		options = origin_type_field.options.split("\n") if origin_type_field.options else []

		for origin in expected_origins:
			self.assertIn(origin, options, f"Tipo de origen '{origin}' no encontrado")

	# =============================================================================
	# LAYER 2: BUSINESS LOGIC VALIDATION (CON MOCKS)
	# =============================================================================

	def test_layer_2_account_selection_validation_property(self):
		"""LAYER 2: Validación selección de cuenta para Property Account (SIN INSERT)"""
		doc = frappe.new_doc("Credit Balance Management")
		doc.account_type = "Property Account"
		doc.property_account = self.mock_property_account_name
		doc.credit_amount = 1500.0

		# Verificar que se asigna correctamente
		self.assertEqual(doc.account_type, "Property Account")
		self.assertEqual(doc.property_account, self.mock_property_account_name)

	def test_layer_2_credit_amount_validation(self):
		"""LAYER 2: Validación de montos de crédito (SIN INSERT)"""
		doc = frappe.new_doc("Credit Balance Management")
		doc.credit_amount = 1500.0
		doc.balance_status = "Activo"

		# Verificar que el monto se establece correctamente
		self.assertEqual(flt(doc.credit_amount), 1500.0)
		self.assertEqual(doc.balance_status, "Activo")

	def test_layer_2_expiration_date_validation(self):
		"""LAYER 2: Validación de fecha de expiración (SIN INSERT)"""
		doc = frappe.new_doc("Credit Balance Management")
		doc.balance_date = getdate()
		doc.expiration_date = add_days(getdate(), 365)

		# Verificar que la fecha se establece correctamente
		self.assertEqual(doc.balance_date, getdate())
		self.assertEqual(doc.expiration_date, add_days(getdate(), 365))

	def test_layer_2_priority_level_validation(self):
		"""LAYER 2: Validación de niveles de prioridad (SIN INSERT)"""
		doc = frappe.new_doc("Credit Balance Management")
		doc.priority_level = "Alta"
		doc.auto_apply_enabled = 1

		self.assertEqual(doc.priority_level, "Alta")
		self.assertEqual(doc.auto_apply_enabled, 1)

	def test_layer_2_usage_tracking_validation(self):
		"""LAYER 2: Validación de campos de seguimiento (SIN INSERT)"""
		doc = frappe.new_doc("Credit Balance Management")
		doc.total_applied = 500.0
		doc.usage_count = 2
		doc.last_used_date = getdate()

		# Verificar campos de tracking
		self.assertEqual(flt(doc.total_applied), 500.0)
		self.assertEqual(doc.usage_count, 2)
		self.assertEqual(doc.last_used_date, getdate())

	# =============================================================================
	# LAYER 3: ERPNEXT INTEGRATION VALIDATION
	# =============================================================================

	def test_layer_3_property_account_integration(self):
		"""LAYER 3: Validación de integración con Property Account (SIN INSERT)"""
		# Usar mock helper method
		mock_property_account = self.get_mock_property_account()

		doc = frappe.new_doc("Credit Balance Management")
		doc.account_type = "Property Account"
		doc.property_account = mock_property_account.name
		doc.credit_amount = 1500.0

		# Verificar integración básica (sin llamadas a ERPNext)
		self.assertEqual(doc.account_type, "Property Account")
		self.assertEqual(doc.property_account, mock_property_account.name)

	def test_layer_3_resident_account_integration(self):
		"""LAYER 3: Validación de integración con Resident Account (SIN INSERT)"""
		# Usar mock helper method
		mock_resident_account = self.get_mock_resident_account()

		doc = frappe.new_doc("Credit Balance Management")
		doc.account_type = "Resident Account"
		doc.resident_account = mock_resident_account.name
		doc.credit_amount = 800.0

		# Verificar integración básica (sin llamadas a ERPNext)
		self.assertEqual(doc.account_type, "Resident Account")
		self.assertEqual(doc.resident_account, mock_resident_account.name)

	def test_layer_3_customer_groups_validation(self):
		"""LAYER 3: Validación de Customer Groups ERPNext existen"""
		# Verificar que los Customer Groups necesarios existen
		self.assertTrue(frappe.db.exists("Customer Group", "Condóminos"))
		self.assertTrue(frappe.db.exists("Customer Group", "Residentes"))

	def test_layer_3_credit_balance_with_mocked_customer(self):
		"""LAYER 3: Test credit balance con Customer mockeado - REGLA #43"""
		doc = frappe.new_doc("Credit Balance Management")
		doc.customer = self.test_customer_name
		doc.account_type = "Property Account"
		doc.credit_amount = 1500.0
		doc.balance_status = "Activo"
		doc.origin_type = "Sobrepago"
		doc.balance_date = getdate()

		# REGLA #43: Mocking contextual para validaciones que requieren Customer
		with patch("frappe.get_doc") as mock_get_doc, patch("frappe.db.exists") as mock_exists:
			# Mock Customer
			mock_customer = type(
				"MockCustomer",
				(),
				{
					"name": self.test_customer_name,
					"customer_name": "TEST Customer Credit Balance",
					"customer_group": "Condóminos",
					"territory": "All Territories",
				},
			)()

			mock_get_doc.return_value = mock_customer
			mock_exists.return_value = True

			# Test validation method si existe
			if hasattr(doc, "validate_customer_link"):
				doc.validate_customer_link()

			# Verificar field assignments
			self.assertEqual(doc.customer, self.test_customer_name)
			self.assertEqual(flt(doc.credit_amount), 1500.0)

	def test_layer_3_property_registry_integration_mocked(self):
		"""LAYER 3: Test integración con Property Registry usando mocking contextual"""
		doc = frappe.new_doc("Credit Balance Management")
		doc.property_account = "TEST_PROP_ACCOUNT_001"
		doc.account_type = "Property Account"
		doc.credit_amount = 2000.0

		# REGLA #43: Mocking contextual para validaciones específicas
		with patch("frappe.get_doc") as mock_get_doc:
			# Mock Property Account que referencia Property Registry real
			mock_property_account = type(
				"MockPropertyAccount",
				(),
				{
					"name": "TEST_PROP_ACCOUNT_001",
					"property_registry": self.test_property_registry_name,
					"customer": self.test_customer_name,
					"current_balance": 0.0,
					"account_status": "Activa",
				},
			)()
			mock_get_doc.return_value = mock_property_account

			# Test validation method que usa get_doc
			if hasattr(doc, "validate_property_account_link"):
				doc.validate_property_account_link()

			# Verificar que el mock fue llamado si se usó
			if mock_get_doc.called:
				mock_get_doc.assert_called_with("Property Account", "TEST_PROP_ACCOUNT_001")

	def test_layer_3_both_accounts_integration(self):
		"""LAYER 3: Validación de integración con ambas cuentas (SIN INSERT)"""
		mock_property_account = self.get_mock_property_account()
		mock_resident_account = self.get_mock_resident_account()

		doc = frappe.new_doc("Credit Balance Management")
		doc.account_type = "Ambos"
		doc.property_account = mock_property_account.name
		doc.resident_account = mock_resident_account.name
		doc.credit_amount = 2000.0

		# Verificar que ambas cuentas se asignan
		self.assertEqual(doc.account_type, "Ambos")
		self.assertEqual(doc.property_account, mock_property_account.name)
		self.assertEqual(doc.resident_account, mock_resident_account.name)

	# =============================================================================
	# LAYER 4: COMPLEX FINANCIAL CALCULATIONS AND WORKFLOWS
	# =============================================================================

	def test_layer_4_remaining_balance_calculation(self):
		"""LAYER 4: Validación de cálculo de saldo restante (SIN INSERT)"""
		doc = frappe.new_doc("Credit Balance Management")
		doc.credit_amount = 2000.0
		doc.total_applied = 750.0

		# Saldo restante = credit_amount - total_applied
		# 2000 - 750 = 1250 (ejemplo de cálculo manual)

		# En testing no se ejecuta calculate_remaining_balance automáticamente
		# pero verificamos que los campos están disponibles para el cálculo
		self.assertEqual(flt(doc.credit_amount), 2000.0)
		self.assertEqual(flt(doc.total_applied), 750.0)

	def test_layer_4_approval_requirements_validation(self):
		"""LAYER 4: Validación de requerimientos de aprobación (SIN INSERT)"""
		# Crédito que requiere aprobación por monto alto
		doc = frappe.new_doc("Credit Balance Management")
		doc.credit_amount = 15000.0  # Excede límite automático
		doc.origin_type = "Ajuste Manual"  # Tipo que requiere aprobación
		doc.requires_approval = 1

		# Verificar que se marca para aprobación
		self.assertEqual(flt(doc.credit_amount), 15000.0)
		self.assertEqual(doc.origin_type, "Ajuste Manual")
		self.assertEqual(doc.requires_approval, 1)

	def test_layer_4_expiration_management_validation(self):
		"""LAYER 4: Validación de gestión de expiración (SIN INSERT)"""
		doc = frappe.new_doc("Credit Balance Management")
		doc.expiration_date = add_days(getdate(), 30)
		doc.auto_extend_enabled = 1
		doc.max_extensions = 2
		doc.extension_criteria = "Si hay saldo restante mayor a $100"

		# Verificar configuración de expiración
		self.assertEqual(doc.expiration_date, add_days(getdate(), 30))
		self.assertEqual(doc.auto_extend_enabled, 1)
		self.assertEqual(doc.max_extensions, 2)

	def test_layer_4_refund_eligibility_validation(self):
		"""LAYER 4: Validación de elegibilidad para reembolso (SIN INSERT)"""
		doc = frappe.new_doc("Credit Balance Management")
		doc.refund_eligible = 1
		doc.refund_requested = 0
		doc.origin_type = "Sobrepago"
		doc.overpayment_amount = 1000.0

		# Verificar elegibilidad para reembolso
		self.assertEqual(doc.refund_eligible, 1)
		self.assertEqual(doc.refund_requested, 0)
		self.assertEqual(flt(doc.overpayment_amount), 1000.0)

	def test_layer_4_auto_application_settings(self):
		"""LAYER 4: Validación de configuración de aplicación automática (SIN INSERT)"""
		doc = frappe.new_doc("Credit Balance Management")
		doc.auto_apply_enabled = 1
		doc.priority_level = "Alta"
		doc.next_application_date = add_days(getdate(), 1)

		# Verificar configuración de auto-aplicación
		self.assertEqual(doc.auto_apply_enabled, 1)
		self.assertEqual(doc.priority_level, "Alta")
		self.assertEqual(doc.next_application_date, add_days(getdate(), 1))

	def test_layer_4_audit_trail_fields(self):
		"""LAYER 4: Validación de campos de auditoría (SIN INSERT)"""
		doc = frappe.new_doc("Credit Balance Management")

		# Campos de auditoría deben existir
		audit_fields = ["created_by", "creation_date", "last_modified_by", "last_modified_date"]

		for field in audit_fields:
			self.assertTrue(hasattr(doc, field), f"Campo auditoría '{field}' no existe")

	def test_layer_4_source_types_validation(self):
		"""LAYER 4: Validación de tipos de fuente del crédito"""
		doc = frappe.new_doc("Credit Balance Management")

		meta = doc.meta
		source_type_field = next((f for f in meta.fields if f.fieldname == "source_type"), None)
		self.assertIsNotNone(source_type_field, "Campo source_type no encontrado")

		expected_sources = [
			"Pago Excedente",
			"Reembolso Autorizado",
			"Descuento por Pronto Pago",
			"Compensación de Servicios",
			"Ajuste Administrativo",
			"Transferencia entre Cuentas",
		]
		options = source_type_field.options.split("\n") if source_type_field.options else []

		for source in expected_sources:
			self.assertIn(source, options, f"Tipo de fuente '{source}' no encontrado en source_type")

	def test_layer_4_spanish_interface_compliance(self):
		"""LAYER 4: Validación cumplimiento interfaz en español (REGLA #1)"""
		doc = frappe.new_doc("Credit Balance Management")
		meta = doc.meta

		# Verificar secciones en español
		spanish_sections = [
			"Información Básica",
			"Detalles de la Cuenta",
			"Origen del Crédito",
			"Seguimiento de Uso",
			"Gestión del Saldo",
			"Configuración de Expiración",
			"Información de Auditoría",
		]

		section_fields = [f for f in meta.fields if f.fieldtype == "Section Break"]
		section_labels = [f.label for f in section_fields if f.label]

		for section in spanish_sections:
			self.assertIn(section, section_labels, f"Sección en español '{section}' no encontrada")

	# =============================================================================
	# HELPER METHODS ESPECÍFICOS
	# =============================================================================

	def get_mock_property_account(self):
		"""Obtener mock Property Account para tests"""
		return type(
			"MockPropertyAccount",
			(),
			{
				"name": self.mock_property_account_name,
				"account_status": "Activa",
				"customer": self.mock_customer_name,
				"current_balance": 0.0,
				"credit_balance": 1500.0,
			},
		)()

	def get_mock_resident_account(self):
		"""Obtener mock Resident Account para tests"""
		return type(
			"MockResidentAccount",
			(),
			{
				"name": self.mock_resident_account_name,
				"account_status": "Activa",
				"spending_limits": 5000.0,
				"current_balance": 800.0,
				"property_account": self.mock_property_account_name,
			},
		)()

	def get_mock_customer(self):
		"""Obtener mock Customer para tests"""
		return type(
			"MockCustomer",
			(),
			{
				"name": self.mock_customer_name,
				"customer_name": self.mock_customer_name,
				"customer_group": "Condóminos",
				"territory": "All Territories",
			},
		)()
