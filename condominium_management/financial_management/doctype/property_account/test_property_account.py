# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import frappe
from frappe.utils import add_days, getdate

# Add the financial_management path for imports
current_dir = os.path.dirname(__file__)
if not current_dir.endswith("financial_management"):
	current_dir = os.path.join(current_dir, "..", "..")
sys.path.insert(0, current_dir)

from condominium_management.financial_management.test_base import FinancialTestBaseGranular


class TestPropertyAccount(FinancialTestBaseGranular):
	"""Tests granulares para Property Account - REGLA #32"""

	def test_layer_1_field_validation_isolated(self):
		"""LAYER 1: Validación de campos aislada (siempre funciona)"""
		doc = frappe.new_doc("Property Account")

		# Verificar campos requeridos existen
		required_fields = ["property_registry", "customer", "billing_frequency", "current_balance"]
		for field in required_fields:
			self.assertTrue(hasattr(doc, field), f"Campo '{field}' debe existir")

		# Verificar opciones de Select fields
		meta = frappe.get_meta("Property Account")
		billing_frequency_field = meta.get_field("billing_frequency")
		self.assertIn("Mensual", billing_frequency_field.options)
		self.assertIn("Bimestral", billing_frequency_field.options)
		self.assertIn("Trimestral", billing_frequency_field.options)

		account_status_field = meta.get_field("account_status")
		self.assertIn("Activa", account_status_field.options)
		self.assertIn("Suspendida", account_status_field.options)
		self.assertIn("Morosa", account_status_field.options)

	def test_layer_1_currency_fields_precision(self):
		"""LAYER 1: Verificar precisión de campos monetarios"""
		meta = frappe.get_meta("Property Account")

		currency_fields = [
			"current_balance",
			"credit_balance",
			"pending_amount",
			"last_payment_amount",
			"monthly_fee_amount",
			"ytd_paid_amount",
			"total_invoiced_ytd",
		]

		for field_name in currency_fields:
			field = meta.get_field(field_name)
			self.assertEqual(field.fieldtype, "Currency", f"Campo {field_name} debe ser Currency")
			self.assertEqual(field.precision, "2", f"Campo {field_name} debe tener precisión 2")

	def test_layer_2_basic_document_creation(self):
		"""LAYER 2: Creación básica de documento con campos mínimos"""
		# Create document directly without dependencies for basic field testing
		doc = frappe.new_doc("Property Account")

		# Set basic fields
		doc.account_name = "TEST Cuenta Básica"
		doc.property_registry = "TEST_PROP_001"
		doc.customer = "TEST_CUSTOMER_001"
		doc.company = "Test Condominium"
		doc.billing_frequency = "Mensual"
		doc.current_balance = 0.0
		doc.billing_start_date = getdate()
		doc.billing_day = 1

		# Test field assignments (no save needed)
		self.assertEqual(doc.doctype, "Property Account")
		self.assertEqual(doc.account_name, "TEST Cuenta Básica")
		self.assertEqual(doc.billing_frequency, "Mensual")
		self.assertEqual(doc.current_balance, 0.0)

		# Test default values - REGLA #36: Correct method name
		doc.set_default_values()
		self.assertEqual(doc.account_status, "Activa")  # Default value

	def test_layer_2_validation_methods(self):
		"""LAYER 2: Validación de métodos de negocio"""
		# Test validación de día de facturación inválido - business logic only
		doc = frappe.new_doc("Property Account")
		doc.billing_day = 35  # Inválido

		# Test validation method directly
		with self.assertRaises(frappe.ValidationError):
			doc.validate_billing_configuration()

		# Test validación de saldo a favor negativo - business logic only
		doc2 = frappe.new_doc("Property Account")
		doc2.credit_balance = -500.0  # Negativo inválido

		# Test validation method directly - REGLA #36: Correct method name
		with self.assertRaises(frappe.ValidationError):
			doc2.validate_financial_data()

	def test_layer_2_default_values_assignment(self):
		"""LAYER 2: Verificar asignación de valores por defecto - REGLA #36"""
		# Create document directly without save - no dependencies needed
		doc = frappe.new_doc("Property Account")
		doc.account_name = "TEST Default Values"
		doc.property_registry = "TEST_PROP_003"
		doc.customer = "TEST_CUSTOMER_003"
		doc.company = "Test Condominium"
		doc.billing_frequency = "Mensual"
		doc.current_balance = 0.0

		# Set None values to trigger default assignment
		doc.auto_generate_invoices = None
		doc.discount_eligibility = None

		# Apply default values method
		doc.set_default_values()

		# Verificar valores por defecto
		self.assertEqual(doc.account_status, "Activa")
		self.assertEqual(doc.billing_frequency, "Mensual")
		self.assertEqual(doc.billing_day, 1)
		self.assertEqual(doc.billing_start_date, getdate())
		self.assertEqual(doc.auto_generate_invoices, 1)  # REGLA #36: Check integer value
		self.assertEqual(doc.discount_eligibility, 1)  # REGLA #36: Check integer value

	def test_layer_2_audit_information(self):
		"""LAYER 2: Verificar información de auditoría - REGLA #36"""
		# Create document directly and apply audit method - no dependencies needed
		doc = frappe.new_doc("Property Account")
		doc.account_name = "TEST Audit Info"
		doc.property_registry = "TEST_PROP_004"
		doc.customer = "TEST_CUSTOMER_004"
		doc.company = "Test Condominium"
		doc.billing_frequency = "Mensual"
		doc.current_balance = 0.0
		doc.billing_start_date = getdate()
		doc.billing_day = 1

		# Apply audit information method directly
		doc.update_audit_information()

		# Verificar campos de auditoría se establecen automáticamente
		self.assertEqual(doc.created_by, "Administrator")
		self.assertIsNotNone(doc.creation_date)
		self.assertEqual(doc.last_modified_by, "Administrator")
		self.assertIsNotNone(doc.last_modified_date)

	def test_layer_3_property_registry_integration(self):
		"""LAYER 3: Integración con Property Registry - REGLA #36"""
		# Create document and test account name generation logic directly
		doc = frappe.new_doc("Property Account")
		doc.property_registry = "TEST_PROP_005"
		doc.customer = "TEST_CUSTOMER_005"
		doc.company = "Test Condominium"
		doc.billing_frequency = "Mensual"
		doc.current_balance = 0.0
		doc.billing_start_date = getdate()
		doc.billing_day = 1

		# Mock targeted frappe.get_doc only for Property Registry
		with patch("frappe.get_doc") as mock_get_doc:
			mock_property = MagicMock()
			mock_property.status = "Activa"
			mock_property.property_number = "101"
			mock_property.name = "TEST_PROP_005"
			mock_get_doc.return_value = mock_property

			# Apply account name generation method directly
			doc.generate_account_name()

			# Verificar que se generó account_name automáticamente
			self.assertEqual(doc.account_name, "CUENTA-101")

	def test_layer_3_customer_validation(self):
		"""LAYER 3: Validación de Customer ERPNext - REGLA #36"""
		# Create document and test customer validation logic directly
		doc = frappe.new_doc("Property Account")
		doc.account_name = "TEST Customer Validation"
		doc.property_registry = "TEST_PROP_006"
		doc.customer = "TEST_CUSTOMER_006"
		doc.company = "Test Condominium"
		doc.billing_frequency = "Mensual"
		doc.current_balance = 0.0
		doc.billing_start_date = getdate()
		doc.billing_day = 1

		# Mock targeted dependencies for customer validation
		with patch("frappe.db.exists") as mock_exists:
			with patch("frappe.get_doc") as mock_get_doc:
				mock_exists.return_value = True
				mock_customer = MagicMock()
				mock_customer.customer_group = "Condóminos"
				mock_get_doc.return_value = mock_customer

				# Apply customer validation method directly
				doc.validate_customer_link()

				# Verify customer assignment
				self.assertEqual(doc.customer, "TEST_CUSTOMER_006")

	def test_layer_3_pending_amount_calculation(self):
		"""LAYER 3: Cálculo de monto pendiente - REGLA #36"""
		# Create document and test pending amount calculation directly
		doc = frappe.new_doc("Property Account")
		doc.account_name = "TEST Pending Amount"
		doc.property_registry = "TEST_PROP_007"
		doc.customer = "TEST_CUSTOMER_007"
		doc.company = "Test Condominium"
		doc.billing_frequency = "Mensual"
		doc.current_balance = 0.0
		doc.billing_start_date = getdate()
		doc.billing_day = 1

		# Mock targeted SQL query for pending amount calculation
		with patch("frappe.db.sql") as mock_sql:
			mock_sql.return_value = [(1500.00,)]

			# Apply pending amount calculation method directly
			doc.calculate_pending_amount()

			# Verify calculation result
			self.assertEqual(doc.pending_amount, 1500.00)

	def test_layer_3_payment_summary_calculation(self):
		"""LAYER 3: Cálculo de resumen de pagos - REGLA #36"""
		# Create document and test payment summary calculation directly
		doc = frappe.new_doc("Property Account")
		doc.account_name = "TEST Payment Summary"
		doc.property_registry = "TEST_PROP_008"
		doc.customer = "TEST_CUSTOMER_008"
		doc.company = "Test Condominium"
		doc.billing_frequency = "Mensual"
		doc.current_balance = 0.0
		doc.billing_start_date = getdate()
		doc.billing_day = 1

		# Mock targeted SQL queries for payment summary calculation
		with patch("frappe.db.sql") as mock_sql:
			mock_sql.side_effect = [
				[(2500.00,)],  # YTD payments
				[(3000.00,)],  # YTD invoiced
				[],  # Additional calls for average payment delay
			]

			# Mock frappe.get_doc for Fee Structure calculation
			with patch("frappe.get_doc") as mock_get_doc:
				mock_fee_structure = MagicMock()
				mock_fee_structure.calculate_fee_for_property.return_value = {"total_fee": 1250.00}
				mock_get_doc.return_value = mock_fee_structure

				# Apply payment summary calculation method directly
				doc.update_payment_summary()

				# Verify calculation results
				self.assertEqual(doc.ytd_paid_amount, 2500.00)
				self.assertEqual(doc.total_invoiced_ytd, 3000.00)
				self.assertEqual(doc.payment_success_rate, 83.33)  # 2500/3000 * 100

	def test_layer_3_monthly_fee_calculation(self):
		"""LAYER 3: Cálculo de cuota mensual - REGLA #36"""
		# Create document and test monthly fee calculation directly
		doc = frappe.new_doc("Property Account")
		doc.account_name = "TEST Monthly Fee"
		doc.property_registry = "TEST_PROP_009"
		doc.customer = "TEST_CUSTOMER_009"
		doc.company = "Test Condominium"
		doc.billing_frequency = "Mensual"
		doc.current_balance = 0.0
		doc.billing_start_date = getdate()
		doc.billing_day = 1
		doc.fee_structure = "TEST_FEE_STRUCTURE"

		# Mock targeted frappe.get_doc for Fee Structure calculation
		with patch("frappe.get_doc") as mock_get_doc:
			mock_fee_structure = MagicMock()
			mock_fee_structure.calculate_fee_for_property.return_value = {
				"total_fee": 1250.00,
				"base_fee": 1000.00,
				"reserve_fund": 250.00,
			}
			mock_get_doc.return_value = mock_fee_structure

			# Apply monthly fee calculation method directly
			doc.calculate_monthly_fee()

			# Verify calculation result
			self.assertEqual(doc.monthly_fee_amount, 1250.00)

	def test_layer_4_permissions_enforcement(self):
		"""LAYER 4: Verificación de enforcement de permisos"""
		# Verificar permisos definidos en JSON
		meta = frappe.get_meta("Property Account")
		permissions = meta.permissions

		# System Manager debe tener todos los permisos
		system_manager_perms = next((p for p in permissions if p.role == "System Manager"), None)
		self.assertIsNotNone(system_manager_perms)
		self.assertEqual(system_manager_perms.create, 1)
		self.assertEqual(system_manager_perms.read, 1)
		self.assertEqual(system_manager_perms.write, 1)
		self.assertEqual(system_manager_perms.delete, 1)

		# Administrador Financiero debe poder crear/editar
		admin_perms = next((p for p in permissions if p.role == "Administrador Financiero"), None)
		self.assertIsNotNone(admin_perms, "Rol 'Administrador Financiero' debe existir en permisos")
		self.assertEqual(admin_perms.create, 1)
		self.assertEqual(admin_perms.read, 1)
		self.assertEqual(admin_perms.write, 1)

		# Contador solo debe poder leer
		contador_perms = next((p for p in permissions if p.role == "Contador Condominio"), None)
		self.assertIsNotNone(contador_perms, "Rol 'Contador Condominio' debe existir en permisos")
		self.assertEqual(contador_perms.read, 1)
		self.assertEqual(contador_perms.create, 0)

		# Condómino solo debe poder leer
		condomino_perms = next((p for p in permissions if p.role == "Condómino"), None)
		self.assertIsNotNone(condomino_perms, "Rol 'Condómino' debe existir en permisos")
		self.assertEqual(condomino_perms.read, 1)
		self.assertEqual(condomino_perms.write, 0)

	def test_layer_4_uniqueness_constraints(self):
		"""LAYER 4: Verificación de constraints de unicidad - REGLA #36"""
		# Create document and test uniqueness validation directly
		doc = frappe.new_doc("Property Account")
		doc.account_name = "TEST Duplicate Property"
		doc.property_registry = "TEST_PROP_DUPLICATE"
		doc.customer = "TEST_CUSTOMER_010"
		doc.company = "Test Condominium"
		doc.billing_frequency = "Mensual"
		doc.current_balance = 0.0
		doc.billing_start_date = getdate()
		doc.billing_day = 1

		# Mock targeted dependencies for uniqueness validation
		with patch("frappe.db.get_value") as mock_get_value:
			with patch("frappe.get_doc") as mock_get_doc:
				mock_get_value.return_value = "EXISTING_ACCOUNT"
				mock_property = MagicMock()
				mock_property.status = "Activa"
				mock_get_doc.return_value = mock_property

				# Test constraint: Una cuenta por propiedad
				with self.assertRaises(frappe.ValidationError):
					doc.validate_property_registry()

	def test_layer_4_api_methods_functionality(self):
		"""LAYER 4: Verificación de métodos API - REGLA #36"""
		# Create document and test API methods directly
		doc = frappe.new_doc("Property Account")
		doc.account_name = "TEST API Methods"
		doc.property_registry = "TEST_PROP_011"
		doc.customer = "TEST_CUSTOMER_011"
		doc.company = "Test Condominium"
		doc.billing_frequency = "Mensual"
		doc.current_balance = 0.0
		doc.billing_start_date = getdate()
		doc.billing_day = 1

		# Mock targeted SQL queries for API methods
		with patch("frappe.db.sql") as mock_sql:
			# Test get_outstanding_invoices first
			mock_sql.return_value = [
				{
					"name": "INV-001",
					"posting_date": getdate(),
					"due_date": add_days(getdate(), 30),
					"grand_total": 1000.00,
					"outstanding_amount": 1000.00,
					"days_overdue": 0,
				}
			]

			invoices = doc.get_outstanding_invoices()
			self.assertEqual(len(invoices), 1)
			self.assertEqual(invoices[0]["name"], "INV-001")
			self.assertEqual(invoices[0]["outstanding_amount"], 1000.00)

			# Test get_payment_history
			mock_sql.return_value = [
				{
					"name": "PAY-001",
					"posting_date": getdate(),
					"paid_amount": 1000.00,
					"mode_of_payment": "Transferencia",
					"reference_no": "REF001",
					"reference_date": getdate(),
				}
			]

			payments = doc.get_payment_history(5)
			self.assertEqual(len(payments), 1)
			self.assertEqual(payments[0]["name"], "PAY-001")
			self.assertEqual(payments[0]["paid_amount"], 1000.00)


if __name__ == "__main__":
	unittest.main()
