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

from test_base import FinancialTestBaseGranular


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
		doc = self.create_test_document(
			"Property Account",
			{
				"account_name": "TEST Cuenta Básica",
				"property_registry": "TEST_PROP_001",
				"customer": "TEST_CUSTOMER_001",
				"company": "TEST_FINANCIAL_COMPANY",
				"billing_frequency": "Mensual",
				"current_balance": 0.0,
				"billing_start_date": getdate(),
				"billing_day": 1,
			},
		)

		self.assertEqual(doc.doctype, "Property Account")
		self.assertEqual(doc.account_name, "TEST Cuenta Básica")
		self.assertEqual(doc.billing_frequency, "Mensual")
		self.assertEqual(doc.current_balance, 0.0)
		self.assertEqual(doc.account_status, "Activa")  # Default value

	def test_layer_2_validation_methods(self):
		"""LAYER 2: Validación de métodos de negocio"""
		# Test validación de día de facturación inválido
		with self.assertRaises(frappe.ValidationError):
			doc = frappe.get_doc(
				{
					"doctype": "Property Account",
					"account_name": "TEST Invalid Billing Day",
					"property_registry": "TEST_PROP_001",
					"customer": "TEST_CUSTOMER_001",
					"company": "TEST_FINANCIAL_COMPANY",
					"billing_frequency": "Mensual",
					"current_balance": 0.0,
					"billing_start_date": getdate(),
					"billing_day": 35,  # Inválido
				}
			)
			doc.save()

		# Test validación de saldo a favor negativo
		with self.assertRaises(frappe.ValidationError):
			doc = frappe.get_doc(
				{
					"doctype": "Property Account",
					"account_name": "TEST Invalid Credit",
					"property_registry": "TEST_PROP_002",
					"customer": "TEST_CUSTOMER_002",
					"company": "TEST_FINANCIAL_COMPANY",
					"billing_frequency": "Mensual",
					"current_balance": 0.0,
					"credit_balance": -500.0,  # Negativo inválido
					"billing_start_date": getdate(),
					"billing_day": 1,
				}
			)
			doc.save()

	def test_layer_2_default_values_assignment(self):
		"""LAYER 2: Verificar asignación de valores por defecto"""
		doc = self.create_test_document(
			"Property Account",
			{
				"account_name": "TEST Default Values",
				"property_registry": "TEST_PROP_003",
				"customer": "TEST_CUSTOMER_003",
				"company": "TEST_FINANCIAL_COMPANY",
				"billing_frequency": "Mensual",
				"current_balance": 0.0,
			},
		)

		# Verificar valores por defecto
		self.assertEqual(doc.account_status, "Activa")
		self.assertEqual(doc.billing_frequency, "Mensual")
		self.assertEqual(doc.billing_day, 1)
		self.assertEqual(doc.billing_start_date, getdate())
		self.assertTrue(doc.auto_generate_invoices)
		self.assertTrue(doc.discount_eligibility)

	def test_layer_2_audit_information(self):
		"""LAYER 2: Verificar información de auditoría"""
		doc = self.create_test_document(
			"Property Account",
			{
				"account_name": "TEST Audit Info",
				"property_registry": "TEST_PROP_004",
				"customer": "TEST_CUSTOMER_004",
				"company": "TEST_FINANCIAL_COMPANY",
				"billing_frequency": "Mensual",
				"current_balance": 0.0,
				"billing_start_date": getdate(),
				"billing_day": 1,
			},
		)

		# Verificar campos de auditoría se establecen automáticamente
		self.assertEqual(doc.created_by, "Administrator")
		self.assertIsNotNone(doc.creation_date)
		self.assertEqual(doc.last_modified_by, "Administrator")
		self.assertIsNotNone(doc.last_modified_date)

	@patch("frappe.get_doc")
	def test_layer_3_property_registry_integration(self, mock_get_doc):
		"""LAYER 3: Integración con Property Registry"""
		# Mock Property Registry
		mock_property = MagicMock()
		mock_property.status = "Activa"
		mock_property.property_number = "101"
		mock_property.name = "TEST_PROP_005"
		mock_get_doc.return_value = mock_property

		doc = self.create_test_document(
			"Property Account",
			{
				"property_registry": "TEST_PROP_005",
				"customer": "TEST_CUSTOMER_005",
				"company": "TEST_FINANCIAL_COMPANY",
				"billing_frequency": "Mensual",
				"current_balance": 0.0,
				"billing_start_date": getdate(),
				"billing_day": 1,
			},
		)

		# Verificar que se generó account_name automáticamente
		self.assertEqual(doc.account_name, "CUENTA-101")

	@patch("frappe.db.exists")
	def test_layer_3_customer_validation(self, mock_exists):
		"""LAYER 3: Validación de Customer ERPNext"""
		mock_exists.return_value = True

		with patch("frappe.get_doc") as mock_get_doc:
			# Mock Customer
			mock_customer = MagicMock()
			mock_customer.customer_group = "Condóminos"
			mock_get_doc.return_value = mock_customer

			doc = self.create_test_document(
				"Property Account",
				{
					"account_name": "TEST Customer Validation",
					"property_registry": "TEST_PROP_006",
					"customer": "TEST_CUSTOMER_006",
					"company": "TEST_FINANCIAL_COMPANY",
					"billing_frequency": "Mensual",
					"current_balance": 0.0,
					"billing_start_date": getdate(),
					"billing_day": 1,
				},
			)

			self.assertEqual(doc.customer, "TEST_CUSTOMER_006")

	@patch("frappe.db.sql")
	def test_layer_3_pending_amount_calculation(self, mock_sql):
		"""LAYER 3: Cálculo de monto pendiente"""
		# Mock SQL query para facturas pendientes
		mock_sql.return_value = [(1500.00,)]

		doc = self.create_test_document(
			"Property Account",
			{
				"account_name": "TEST Pending Amount",
				"property_registry": "TEST_PROP_007",
				"customer": "TEST_CUSTOMER_007",
				"company": "TEST_FINANCIAL_COMPANY",
				"billing_frequency": "Mensual",
				"current_balance": 0.0,
				"billing_start_date": getdate(),
				"billing_day": 1,
			},
		)

		# Forzar cálculo de monto pendiente
		doc.calculate_pending_amount()
		self.assertEqual(doc.pending_amount, 1500.00)

	@patch("frappe.db.sql")
	def test_layer_3_payment_summary_calculation(self, mock_sql):
		"""LAYER 3: Cálculo de resumen de pagos"""
		# Mock SQL queries para pagos YTD y facturas YTD
		mock_sql.side_effect = [
			[(2500.00,)],  # YTD payments
			[(3000.00,)],  # YTD invoiced
		]

		doc = self.create_test_document(
			"Property Account",
			{
				"account_name": "TEST Payment Summary",
				"property_registry": "TEST_PROP_008",
				"customer": "TEST_CUSTOMER_008",
				"company": "TEST_FINANCIAL_COMPANY",
				"billing_frequency": "Mensual",
				"current_balance": 0.0,
				"billing_start_date": getdate(),
				"billing_day": 1,
			},
		)

		# Forzar actualización de resumen de pagos
		doc.update_payment_summary()

		self.assertEqual(doc.ytd_paid_amount, 2500.00)
		self.assertEqual(doc.total_invoiced_ytd, 3000.00)
		self.assertEqual(doc.payment_success_rate, 83.33)  # 2500/3000 * 100

	@patch("frappe.get_doc")
	def test_layer_3_monthly_fee_calculation(self, mock_get_doc):
		"""LAYER 3: Cálculo de cuota mensual"""
		# Mock Fee Structure con cálculo
		mock_fee_structure = MagicMock()
		mock_fee_structure.calculate_fee_for_property.return_value = {
			"total_fee": 1250.00,
			"base_fee": 1000.00,
			"reserve_fund": 250.00,
		}
		mock_get_doc.return_value = mock_fee_structure

		doc = self.create_test_document(
			"Property Account",
			{
				"account_name": "TEST Monthly Fee",
				"property_registry": "TEST_PROP_009",
				"customer": "TEST_CUSTOMER_009",
				"company": "TEST_FINANCIAL_COMPANY",
				"billing_frequency": "Mensual",
				"current_balance": 0.0,
				"billing_start_date": getdate(),
				"billing_day": 1,
				"fee_structure": "TEST_FEE_STRUCTURE",
			},
		)

		# Forzar cálculo de cuota mensual
		doc.calculate_monthly_fee()
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

	@patch("frappe.db.get_value")
	def test_layer_4_uniqueness_constraints(self, mock_get_value):
		"""LAYER 4: Verificación de constraints de unicidad"""
		# Test constraint: Una cuenta por propiedad
		mock_get_value.return_value = "EXISTING_ACCOUNT"

		with self.assertRaises(frappe.ValidationError):
			doc = frappe.get_doc(
				{
					"doctype": "Property Account",
					"account_name": "TEST Duplicate Property",
					"property_registry": "TEST_PROP_DUPLICATE",
					"customer": "TEST_CUSTOMER_010",
					"company": "TEST_FINANCIAL_COMPANY",
					"billing_frequency": "Mensual",
					"current_balance": 0.0,
					"billing_start_date": getdate(),
					"billing_day": 1,
				}
			)
			doc.save()

	@patch("frappe.db.sql")
	def test_layer_4_api_methods_functionality(self, mock_sql):
		"""LAYER 4: Verificación de métodos API"""
		doc = self.create_test_document(
			"Property Account",
			{
				"account_name": "TEST API Methods",
				"property_registry": "TEST_PROP_011",
				"customer": "TEST_CUSTOMER_011",
				"company": "TEST_FINANCIAL_COMPANY",
				"billing_frequency": "Mensual",
				"current_balance": 0.0,
				"billing_start_date": getdate(),
				"billing_day": 1,
			},
		)

		# Test get_outstanding_invoices
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
