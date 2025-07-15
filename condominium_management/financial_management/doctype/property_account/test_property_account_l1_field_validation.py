# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Property Account - Layer 1 Testing: Field Validation (AJUSTADO)
===============================================================

METODOLOGÍA EXPERIMENTAL REGLA #41: Testing granular refinado
- AJUSTE: FrappeTestCase con setup mínimo (no unittest.TestCase)
- NO usa make_test_records
- NO interactúa con base de datos directamente
- Mocking agresivo de frappe.throw y validaciones
- PROBLEMA RESUELTO: frappe.new_doc() requiere contexto FrappeTestCase
"""

import unittest
from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPropertyAccountLayer1FieldValidation(FrappeTestCase):
	"""Layer 1: Pure field validation without database interaction"""

	def setUp(self):
		"""Setup basic document instance in memory only"""
		# EXPERIMENTAL: Solo frappe.new_doc, sin DB
		self.doc = frappe.new_doc("Property Account")

	def test_doctype_exists(self):
		"""Verify DocType is properly loaded"""
		self.assertEqual(self.doc.doctype, "Property Account")
		self.assertIsNotNone(self.doc.meta)

	def test_required_fields_exist(self):
		"""Verify all required fields are available in DocType"""
		required_fields = [
			"account_name",
			"property_registry",
			"customer",
			"company",
			"billing_frequency",
			"account_status",
			"current_balance",
		]

		for field in required_fields:
			with self.subTest(field=field):
				self.assertTrue(hasattr(self.doc, field), f"Required field '{field}' not found")

	@patch("frappe.throw")
	def test_validate_property_registry_missing(self, mock_throw):
		"""Test validation fails when property_registry is missing"""
		self.doc.property_registry = None

		# EXPERIMENTAL: Test validation logic without DB dependencies
		self.doc.validate_property_registry()

		# Verify frappe.throw was called for missing property_registry
		mock_throw.assert_called_once()
		args, kwargs = mock_throw.call_args
		self.assertIn("registro de propiedad", args[0].lower())

	@patch("frappe.get_doc")
	@patch("frappe.throw")
	def test_validate_property_registry_with_mocked_property(self, mock_throw, mock_get_doc):
		"""Test validation with mocked property document"""
		# Mock property document with active status
		mock_property = MagicMock()
		mock_property.status = "Activa"
		mock_get_doc.return_value = mock_property

		self.doc.property_registry = "MOCK_PROPERTY_001"

		# Should not throw with active property
		self.doc.validate_property_registry()

		# Verify frappe.throw was NOT called
		mock_throw.assert_not_called()
		mock_get_doc.assert_called_with("Property Registry", "MOCK_PROPERTY_001")

	@patch("frappe.throw")
	def test_validate_customer_link_missing(self, mock_throw):
		"""Test validation fails when customer is missing"""
		self.doc.customer = None

		# EXPERIMENTAL: Test validation without dependencies
		self.doc.validate_customer_link()

		# Verify validation was triggered
		mock_throw.assert_called_once()
		args, kwargs = mock_throw.call_args
		self.assertIn("cliente", args[0].lower())

	@patch("frappe.get_doc")
	@patch("frappe.throw")
	def test_validate_customer_link_with_mocked_customer(self, mock_throw, mock_get_doc):
		"""Test validation with mocked customer document"""
		# Mock customer document
		mock_customer = MagicMock()
		mock_customer.customer_group = "Condóminos"
		mock_get_doc.return_value = mock_customer

		self.doc.customer = "MOCK_CUSTOMER_001"

		# Should not throw with valid customer
		self.doc.validate_customer_link()

		# Verify frappe.throw was NOT called
		mock_throw.assert_not_called()
		mock_get_doc.assert_called_with("Customer", "MOCK_CUSTOMER_001")

	@patch("frappe.throw")
	def test_validate_billing_configuration_missing_frequency(self, mock_throw):
		"""Test billing configuration validation"""
		self.doc.billing_frequency = None
		self.doc.billing_start_date = "2025-01-15"  # Set to avoid None comparison error
		self.doc.billing_day = 1  # Set valid billing day to reach frequency validation

		self.doc.validate_billing_configuration()

		mock_throw.assert_called()
		args, kwargs = mock_throw.call_args
		self.assertIn("frecuencia de facturación", args[0].lower())

	@patch("frappe.throw")
	def test_validate_billing_configuration_missing_start_date(self, mock_throw):
		"""Test billing start date validation"""
		self.doc.billing_frequency = "Mensual"
		self.doc.billing_start_date = None
		self.doc.billing_day = 1  # Set valid billing day to reach start_date validation

		self.doc.validate_billing_configuration()

		mock_throw.assert_called()
		args, kwargs = mock_throw.call_args
		self.assertIn("fecha de inicio", args[0].lower())

	@patch("frappe.throw")
	def test_validate_financial_data_negative_credit_balance(self, mock_throw):
		"""Test financial data validation for negative credit balance"""
		self.doc.credit_balance = -500.0

		self.doc.validate_financial_data()

		mock_throw.assert_called()
		args, kwargs = mock_throw.call_args
		self.assertIn("saldo a favor", args[0].lower())
		self.assertIn("negativo", args[0].lower())

	@patch("frappe.throw")
	def test_validate_financial_data_negative_payment_amount(self, mock_throw):
		"""Test financial data validation for negative payment amount"""
		self.doc.last_payment_amount = -100.0
		self.doc.last_payment_date = "2025-01-15"  # Set date to test negative amount validation

		self.doc.validate_financial_data()

		mock_throw.assert_called()
		args, kwargs = mock_throw.call_args
		self.assertIn("último pago", args[0].lower())
		self.assertIn("negativo", args[0].lower())

	@patch("frappe.throw")
	def test_validate_financial_data_missing_payment_date(self, mock_throw):
		"""Test financial data validation for missing payment date when amount exists"""
		self.doc.last_payment_amount = 100.0
		self.doc.last_payment_date = None

		self.doc.validate_financial_data()

		mock_throw.assert_called()
		args, kwargs = mock_throw.call_args
		self.assertIn("fecha", args[0].lower())

	def test_set_default_values(self):
		"""Test default values are set correctly"""
		# Clear all values first
		self.doc.account_status = None
		self.doc.billing_frequency = None
		self.doc.billing_day = None
		self.doc.current_balance = None
		self.doc.auto_generate_invoices = None
		self.doc.discount_eligibility = None

		# EXPERIMENTAL: Test default logic without DB
		self.doc.set_default_values()

		# Verify defaults
		self.assertEqual(self.doc.account_status, "Activa")
		self.assertEqual(self.doc.billing_frequency, "Mensual")
		self.assertEqual(self.doc.billing_day, 1)
		self.assertEqual(self.doc.current_balance, 0.0)
		self.assertEqual(self.doc.auto_generate_invoices, 1)
		self.assertEqual(self.doc.discount_eligibility, 1)

	@patch("frappe.get_doc")
	def test_generate_account_name_with_property(self, mock_get_doc):
		"""Test account name generation logic"""
		# Mock property registry document
		mock_property = MagicMock()
		mock_property.property_number = "101"
		mock_get_doc.return_value = mock_property

		self.doc.property_registry = "TEST_PROPERTY_001"
		self.doc.account_name = None

		# EXPERIMENTAL: Test business logic with mocked dependencies
		self.doc.generate_account_name()

		# Verify account name was generated
		self.assertEqual(self.doc.account_name, "CUENTA-101")
		mock_get_doc.assert_called_with("Property Registry", "TEST_PROPERTY_001")

	@patch("frappe.get_doc")
	def test_generate_account_name_fallback(self, mock_get_doc):
		"""Test account name generation fallback when property_number is None"""
		# Mock property registry without property_number
		mock_property = MagicMock()
		mock_property.property_number = None
		mock_property.name = "TEST_PROPERTY_001"
		mock_get_doc.return_value = mock_property

		self.doc.property_registry = "TEST_PROPERTY_001"
		self.doc.account_name = None

		self.doc.generate_account_name()

		# Should use name as fallback
		self.assertEqual(self.doc.account_name, "CUENTA-TEST_PROPERTY_001")

	def test_account_name_not_overwritten(self):
		"""Test account name is not overwritten if already set"""
		self.doc.account_name = "EXISTING_NAME"
		self.doc.property_registry = "TEST_PROPERTY_001"

		# Should not change existing name
		with patch("frappe.get_doc") as mock_get_doc:
			self.doc.generate_account_name()

		self.assertEqual(self.doc.account_name, "EXISTING_NAME")
		# frappe.get_doc should not be called if name exists
		mock_get_doc.assert_not_called()


if __name__ == "__main__":
	unittest.main()
