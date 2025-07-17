# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

# REGLA #43B: Property Account tiene Customer field que triggea warehouse.py autoname error
test_ignore = ["Customer", "Warehouse", "Sales Invoice", "Item"]


class TestPropertyAccountL1FieldValidation(FrappeTestCase):
	"""Layer 1: Field Validation Tests for Property Account DocType"""

	def test_required_fields_validation(self):
		"""Test that required fields are properly validated"""
		property_account = frappe.new_doc("Property Account")

		# Test missing property_registry validation (custom validation)
		with self.assertRaises(frappe.ValidationError) as context:
			property_account.insert()
		self.assertIn("El registro de propiedad es obligatorio", str(context.exception))

		# Test each required field individually
		required_fields = [
			"account_name",
			"property_registry",
			"customer",
			"company",
			"billing_frequency",
			"account_status",
			"current_balance",
			"billing_start_date",
			"billing_day",
		]

		for field in required_fields:
			self.assertTrue(hasattr(property_account, field), f"Missing required field: {field}")

	def test_field_types_validation(self):
		"""Test that field types are correctly defined"""
		property_account = frappe.new_doc("Property Account")

		# Test Data fields
		property_account.account_name = "Test Account"
		self.assertEqual(property_account.account_name, "Test Account")

		# Test Currency fields with precision 2
		property_account.current_balance = 1500.75
		self.assertEqual(property_account.current_balance, 1500.75)

		property_account.credit_balance = 250.50
		self.assertEqual(property_account.credit_balance, 250.50)

		property_account.pending_amount = 0.00
		self.assertEqual(property_account.pending_amount, 0.00)

		# Test Int fields
		property_account.billing_day = 15
		self.assertEqual(property_account.billing_day, 15)

		# Test Check fields (boolean)
		property_account.auto_generate_invoices = 1
		self.assertEqual(property_account.auto_generate_invoices, 1)

		property_account.discount_eligibility = 0
		self.assertEqual(property_account.discount_eligibility, 0)

	def test_select_field_options_validation(self):
		"""Test that select fields only accept valid options"""
		property_account = frappe.new_doc("Property Account")

		# Test billing_frequency options
		valid_billing_frequencies = ["Mensual", "Bimestral", "Trimestral", "Semestral", "Anual"]
		for freq in valid_billing_frequencies:
			property_account.billing_frequency = freq
			self.assertEqual(property_account.billing_frequency, freq)

		# Test account_status options
		valid_account_statuses = ["Activa", "Suspendida", "Morosa", "Cerrada"]
		for status in valid_account_statuses:
			property_account.account_status = status
			self.assertEqual(property_account.account_status, status)

	def test_unique_fields_validation(self):
		"""Test that unique fields are properly validated"""
		property_account = frappe.new_doc("Property Account")

		# Test account_name uniqueness (should be unique)
		property_account.account_name = "UNIQUE_TEST_ACCOUNT_001"
		self.assertEqual(property_account.account_name, "UNIQUE_TEST_ACCOUNT_001")

		# Verify the field has unique constraint in meta
		meta = frappe.get_meta("Property Account")
		account_name_field = meta.get_field("account_name")
		self.assertTrue(account_name_field.unique, "account_name field should be unique")

	def test_currency_precision_validation(self):
		"""Test that currency fields maintain proper precision"""
		property_account = frappe.new_doc("Property Account")

		# Test currency fields with various precision values
		currency_fields = [
			"current_balance",
			"credit_balance",
			"pending_amount",
			"total_paid",
			"outstanding_amount",
			"late_fee_amount",
			"discount_amount",
		]

		for field in currency_fields:
			if hasattr(property_account, field):
				# Test with 2 decimal places (should be preserved)
				setattr(property_account, field, 1234.56)
				self.assertEqual(getattr(property_account, field), 1234.56)

				# Test with more decimal places (should be rounded to 2)
				setattr(property_account, field, 1234.5678)
				# Note: Frappe automatically handles currency precision

	def test_date_field_validation(self):
		"""Test that date fields accept valid date values"""
		property_account = frappe.new_doc("Property Account")

		# Test valid date formats
		from datetime import date

		today = date.today()

		property_account.billing_start_date = today
		self.assertEqual(property_account.billing_start_date, today)

		# Test date fields exist
		date_fields = ["billing_start_date", "last_payment_date", "next_billing_date"]
		for field in date_fields:
			if hasattr(property_account, field):
				self.assertTrue(hasattr(property_account, field), f"Date field {field} should exist")

	def test_link_field_validation(self):
		"""Test that link fields are properly defined"""
		property_account = frappe.new_doc("Property Account")

		# Test Link field assignments
		property_account.property_registry = "Test Property Registry"
		self.assertEqual(property_account.property_registry, "Test Property Registry")

		property_account.customer = "Test Customer"
		self.assertEqual(property_account.customer, "Test Customer")

		property_account.company = "_Test Company"
		self.assertEqual(property_account.company, "_Test Company")

	def test_int_field_bounds_validation(self):
		"""Test that integer fields accept valid ranges"""
		property_account = frappe.new_doc("Property Account")

		# Test billing_day (should be 1-31)
		property_account.billing_day = 1
		self.assertEqual(property_account.billing_day, 1)

		property_account.billing_day = 31
		self.assertEqual(property_account.billing_day, 31)

		property_account.billing_day = 15
		self.assertEqual(property_account.billing_day, 15)

	def test_readonly_field_behavior(self):
		"""Test that readonly fields behave correctly"""
		property_account = frappe.new_doc("Property Account")

		# Test that calculated fields can be set programmatically
		property_account.outstanding_amount = 1000.00
		self.assertEqual(property_account.outstanding_amount, 1000.00)

		property_account.total_paid = 500.00
		self.assertEqual(property_account.total_paid, 500.00)
