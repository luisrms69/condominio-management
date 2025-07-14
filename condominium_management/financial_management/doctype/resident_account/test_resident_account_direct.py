# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest
from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, flt, getdate, nowdate


class TestResidentAccountDirect(FrappeTestCase):
	"""Testing directo para Resident Account sin framework granular problemático"""

	@classmethod
	def setUpClass(cls):
		"""Setup class para testing directo"""
		super().setUpClass()

		# Usar company existente en test database
		cls.test_company = "_Test Company"

	def setUp(self):
		"""Setup por test"""
		frappe.set_user("Administrator")

	def tearDown(self):
		"""Cleanup después de cada test"""
		# Limpiar documentos creados en tests
		frappe.db.rollback()

	def test_resident_account_field_assignments(self):
		"""Test básico de asignación de campos"""
		doc = frappe.new_doc("Resident Account")

		# Test field assignment básico
		doc.account_code = "TEST-RES01-JD"
		doc.resident_name = "Juan Pérez"
		doc.resident_type = "Propietario"
		doc.account_status = "Activa"
		doc.current_balance = 0.0
		doc.credit_limit = 5000.0
		doc.spending_limits = 1000.0
		doc.approval_required_amount = 2000.0

		# Verificar assignments exitosos
		self.assertEqual(doc.doctype, "Resident Account")
		self.assertEqual(doc.account_code, "TEST-RES01-JD")
		self.assertEqual(doc.resident_name, "Juan Pérez")
		self.assertEqual(doc.resident_type, "Propietario")
		self.assertEqual(doc.account_status, "Activa")
		self.assertEqual(flt(doc.current_balance), 0.0)
		self.assertEqual(flt(doc.credit_limit), 5000.0)
		self.assertEqual(flt(doc.spending_limits), 1000.0)
		self.assertEqual(flt(doc.approval_required_amount), 2000.0)

	def test_resident_account_validation_methods(self):
		"""Test métodos de validación con mocks"""
		with (
			patch("frappe.get_doc") as mock_get_doc,
			patch("frappe.db.get_value") as mock_get_value,
			patch("frappe.db.count") as mock_count,
		):
			# Mock Property Account dependency
			mock_property = MagicMock()
			mock_property.account_status = "Activa"
			mock_property.company = "_Test Company"
			mock_property.account_name = "PROP-001"
			mock_get_doc.return_value = mock_property

			# Mock uniqueness check
			mock_get_value.return_value = None

			# Mock count for sequence
			mock_count.return_value = 0

			# Crear documento REAL para testing
			doc = frappe.new_doc("Resident Account")
			doc.property_account = "PROP-001"
			doc.resident_name = "María García"
			doc.resident_type = "Inquilino"
			doc.current_balance = 1500.0
			doc.credit_limit = 3000.0
			doc.spending_limits = 800.0
			doc.approval_required_amount = 1500.0

			# Execute validation methods
			doc.validate_property_account()
			doc.validate_resident_data()
			doc.validate_financial_limits()
			doc.validate_credit_configuration()
			doc.calculate_credit_metrics()
			doc.set_default_values()
			doc.generate_account_code()

			# Verify business logic calculations
			self.assertEqual(doc.company, "_Test Company")
			self.assertEqual(flt(doc.available_credit), 1500.0)  # 3000 - 1500
			self.assertEqual(flt(doc.credit_utilization_percentage), 50.0)  # (1500/3000)*100
			self.assertEqual(flt(doc.pending_charges), 0.0)  # positive balance
			self.assertIn("PROP-001-RES01-MG", doc.account_code)

	def test_resident_account_with_real_integration(self):
		"""Test con integración real - crear Property Account primero"""
		# Crear Property Account real como dependencia
		if not frappe.db.exists("Property Registry", "TEST-PROP-001"):
			property_registry = frappe.get_doc(
				{
					"doctype": "Property Registry",
					"property_id": "TEST-PROP-001",
					"property_name": "Apartamento 101",
					"company": "_Test Company",
					"property_type": "Apartment",
					"property_status": "Occupied",
					"area_sqm": 85.0,
					"ownership_percentage": 100.0,
				}
			)
			property_registry.insert(ignore_permissions=True)

		# Crear Property Account vinculada
		if not frappe.db.exists("Property Account", {"property_registry": "TEST-PROP-001"}):
			property_account = frappe.get_doc(
				{
					"doctype": "Property Account",
					"property_registry": "TEST-PROP-001",
					"account_name": "PROP-TEST-001",
					"company": "_Test Company",
					"billing_frequency": "Monthly",
					"current_balance": 0.0,
					"billing_day": 1,
					"auto_generate_invoices": 1,
				}
			)
			property_account.insert(ignore_permissions=True)
		else:
			property_account = frappe.get_doc("Property Account", {"property_registry": "TEST-PROP-001"})

		# Crear Resident Account vinculada
		resident_account = frappe.get_doc(
			{
				"doctype": "Resident Account",
				"property_account": property_account.name,
				"resident_name": "Carlos Mendoza",
				"resident_type": "Familiar",
				"current_balance": -500.0,  # Saldo negativo (debe dinero)
				"credit_limit": 2000.0,
				"spending_limits": 600.0,
				"approval_required_amount": 1000.0,
				"auto_charge_enabled": 1,
				"notifications_enabled": 1,
			}
		)

		# Test insert con dependencies reales
		resident_account.insert(ignore_permissions=True)

		# Verify successful creation
		self.assertTrue(resident_account.name)
		self.assertEqual(resident_account.company, property_account.company)
		self.assertEqual(flt(resident_account.available_credit), 1500.0)  # 2000 - 500
		self.assertEqual(flt(resident_account.credit_utilization_percentage), 25.0)  # (500/2000)*100
		self.assertEqual(flt(resident_account.pending_charges), 500.0)  # negative balance
		self.assertIn("Familiar", resident_account.transaction_summary)

	def test_api_methods_functionality(self):
		"""Test métodos API principales"""
		# Setup con Property Account mock
		with patch("frappe.get_doc") as mock_get_doc:
			mock_property = MagicMock()
			mock_property.company = "_Test Company"
			mock_get_doc.return_value = mock_property

			# Crear Resident Account para testing API
			resident_account = frappe.get_doc(
				{
					"doctype": "Resident Account",
					"account_code": "TEST-API-01",
					"property_account": "MOCK-PROP-001",
					"resident_name": "Ana Torres",
					"resident_type": "Propietario",
					"current_balance": 2000.0,  # Saldo positivo
					"credit_limit": 5000.0,
					"spending_limits": 1500.0,
					"approval_required_amount": 3000.0,
				}
			)

			# Test 1: add_transaction method - payment (positive)
			result = resident_account.add_transaction(
				amount=500.0, transaction_type="Pago", description="Pago recibido"
			)

			self.assertTrue(result["success"])
			self.assertEqual(flt(result["old_balance"]), 2000.0)
			self.assertEqual(flt(result["new_balance"]), 2500.0)
			self.assertEqual(flt(result["transaction_amount"]), 500.0)

			# Test 2: transfer_to_property_account method
			transfer_result = resident_account.transfer_to_property_account(
				amount=1000.0, description="Transferencia a cuenta principal"
			)

			self.assertTrue(transfer_result["success"])
			self.assertEqual(flt(transfer_result["transferred_amount"]), 1000.0)
			self.assertEqual(flt(transfer_result["remaining_balance"]), 1500.0)

			# Test 3: get_spending_summary method
			summary = resident_account.get_spending_summary(period_days=30)

			self.assertEqual(summary["period_days"], 30)
			self.assertEqual(flt(summary["current_balance"]), 1500.0)
			self.assertEqual(summary["account_status"], "Activa")
			self.assertIn("last_transaction", summary)

	def test_validation_error_scenarios(self):
		"""Test scenarios de errores de validación"""
		# Test 1: Property Account obligatoria
		doc = frappe.new_doc("Resident Account")
		doc.resident_name = "Test User"

		with self.assertRaises(frappe.ValidationError):
			doc.validate_property_account()

		# Test 2: Nombre residente muy corto
		doc.property_account = "TEST-PROP"
		doc.resident_name = "A"  # Muy corto

		with patch("frappe.get_doc") as mock_get_doc:
			mock_property = MagicMock()
			mock_property.account_status = "Activa"
			mock_property.company = "_Test Company"
			mock_get_doc.return_value = mock_property

			with self.assertRaises(frappe.ValidationError):
				doc.validate_resident_data()

	def test_credit_calculations_detailed(self):
		"""Test detallado de cálculos de crédito"""
		doc = frappe.new_doc("Resident Account")
		doc.credit_limit = 2000.0

		# Test 1: Saldo positivo (no usa crédito)
		doc.current_balance = 500.0
		doc.calculate_credit_metrics()

		self.assertEqual(flt(doc.available_credit), 2000.0)
		self.assertEqual(flt(doc.credit_utilization_percentage), 0.0)
		self.assertEqual(flt(doc.pending_charges), 0.0)

		# Test 2: Saldo negativo (usa crédito)
		doc.current_balance = -800.0
		doc.calculate_credit_metrics()

		self.assertEqual(flt(doc.available_credit), 1200.0)  # 2000 - 800
		self.assertEqual(flt(doc.credit_utilization_percentage), 40.0)  # (800/2000)*100
		self.assertEqual(flt(doc.pending_charges), 800.0)

	def test_default_values_by_resident_type(self):
		"""Test valores por defecto según tipo de residente"""
		doc = frappe.new_doc("Resident Account")

		# Test Propietario
		doc.resident_type = "Propietario"
		doc.set_default_values()

		self.assertEqual(flt(doc.spending_limits), 5000.0)
		self.assertEqual(flt(doc.approval_required_amount), 10000.0)

		# Test Huésped
		doc = frappe.new_doc("Resident Account")
		doc.resident_type = "Huésped"
		doc.set_default_values()

		self.assertEqual(flt(doc.spending_limits), 500.0)
		self.assertEqual(flt(doc.approval_required_amount), 1000.0)

	def test_loyalty_points_calculation(self):
		"""Test cálculo de puntos de lealtad"""
		doc = frappe.new_doc("Resident Account")

		# Test 1: Saldo positivo genera puntos
		doc.current_balance = 1500.0
		doc.calculate_loyalty_points()

		self.assertEqual(doc.loyalty_points, 15)  # 1500/100 = 15

		# Test 2: Saldo negativo no genera puntos
		doc.current_balance = -500.0
		doc.calculate_loyalty_points()

		self.assertEqual(doc.loyalty_points, 0)

	def test_account_code_generation_with_mocks(self):
		"""Test generación de código de cuenta con mocks"""
		with patch("frappe.get_doc") as mock_get_doc, patch("frappe.db.count") as mock_count:
			# Mock Property Account
			mock_property = MagicMock()
			mock_property.account_name = "TORRE-A-101"
			mock_get_doc.return_value = mock_property

			# Mock count (first resident)
			mock_count.return_value = 0

			doc = frappe.new_doc("Resident Account")
			doc.property_account = "TORRE-A-101"
			doc.resident_name = "Juan Carlos Pérez"

			doc.generate_account_code()

			# Verify code generation pattern
			expected_code = "TORRE-A-101-RES01-JC"
			self.assertEqual(doc.account_code, expected_code)

	def test_diagnostic_fields_validation(self):
		"""Test diagnóstico - verificar campos críticos"""
		doc = frappe.new_doc("Resident Account")

		# Campos críticos para business logic
		critical_fields = [
			"account_code",
			"resident_name",
			"property_account",
			"company",
			"resident_type",
			"account_status",
			"current_balance",
			"credit_limit",
			"available_credit",
			"credit_utilization_percentage",
			"spending_limits",
			"approval_required_amount",
			"last_transaction_date",
			"last_transaction_amount",
			"loyalty_points",
			"auto_charge_enabled",
			"notifications_enabled",
		]

		for field in critical_fields:
			self.assertTrue(hasattr(doc, field), f"Field '{field}' not found in Resident Account")

		# Test computed fields calculation
		doc.current_balance = 1000.0
		doc.credit_limit = 2000.0
		doc.calculate_credit_metrics()

		self.assertTrue(hasattr(doc, "available_credit"))
		self.assertTrue(hasattr(doc, "credit_utilization_percentage"))
		self.assertTrue(hasattr(doc, "pending_charges"))

		# Test loyalty points calculation
		doc.calculate_loyalty_points()
		self.assertEqual(doc.loyalty_points, 10)  # 1000/100 = 10
