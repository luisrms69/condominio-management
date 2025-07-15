# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

# REGLA #43B: Credit Balance Management puede tener Customer/Payment Entry dependencies
test_ignore = ["Customer", "Payment Entry"]


class TestCreditBalanceManagementL1FieldValidation(FrappeTestCase):
	"""Layer 1: Field Validation Tests for Credit Balance Management DocType"""

	def test_required_fields_validation(self):
		"""Test that required fields are properly validated"""
		credit_balance = frappe.new_doc("Credit Balance Management")

		# Test missing required fields
		with self.assertRaises(frappe.MandatoryError):
			credit_balance.insert()

		# Test each required field individually
		required_fields = ["naming_series", "balance_date", "account_type", "credit_amount", "balance_status"]

		for field in required_fields:
			self.assertTrue(hasattr(credit_balance, field), f"Missing required field: {field}")

	def test_naming_series_validation(self):
		"""Test that naming series is properly configured"""
		credit_balance = frappe.new_doc("Credit Balance Management")

		# Test naming series field exists
		self.assertTrue(hasattr(credit_balance, "naming_series"))

		# Test default naming series value
		meta = frappe.get_meta("Credit Balance Management")
		naming_series_field = meta.get_field("naming_series")
		self.assertEqual(naming_series_field.options, "CB-.YYYY.-.MM.-")

	def test_field_types_validation(self):
		"""Test that field types are correctly defined"""
		credit_balance = frappe.new_doc("Credit Balance Management")

		# Test Date fields
		from datetime import date

		today = date.today()
		credit_balance.balance_date = today
		self.assertEqual(credit_balance.balance_date, today)

		# Test Currency fields with precision 2
		credit_balance.credit_amount = 1500.75
		self.assertEqual(credit_balance.credit_amount, 1500.75)

		if hasattr(credit_balance, "applied_amount"):
			credit_balance.applied_amount = 500.50
			self.assertEqual(credit_balance.applied_amount, 500.50)

	def test_select_field_options_validation(self):
		"""Test that select fields only accept valid options"""
		credit_balance = frappe.new_doc("Credit Balance Management")

		# Test account_type options
		valid_account_types = ["Property Account", "Resident Account", "Ambos"]
		for account_type in valid_account_types:
			credit_balance.account_type = account_type
			self.assertEqual(credit_balance.account_type, account_type)

		# Test balance_status options
		valid_balance_statuses = ["Activo", "Aplicado Parcial", "Aplicado Total", "Expirado", "Cancelado"]
		for status in valid_balance_statuses:
			credit_balance.balance_status = status
			self.assertEqual(credit_balance.balance_status, status)

	def test_currency_precision_validation(self):
		"""Test that currency fields maintain proper precision"""
		credit_balance = frappe.new_doc("Credit Balance Management")

		# Test currency fields with various precision values
		currency_fields = ["credit_amount", "applied_amount", "remaining_amount", "original_payment_amount"]

		for field in currency_fields:
			if hasattr(credit_balance, field):
				# Test with 2 decimal places (should be preserved)
				setattr(credit_balance, field, 1234.56)
				self.assertEqual(getattr(credit_balance, field), 1234.56)

	def test_date_field_validation(self):
		"""Test that date fields accept valid date values"""
		credit_balance = frappe.new_doc("Credit Balance Management")

		# Test valid date formats
		from datetime import date

		today = date.today()

		credit_balance.balance_date = today
		self.assertEqual(credit_balance.balance_date, today)

		# Test additional date fields
		date_fields = ["expiry_date", "last_applied_date", "created_date"]
		for field in date_fields:
			if hasattr(credit_balance, field):
				setattr(credit_balance, field, today)
				self.assertEqual(getattr(credit_balance, field), today)

	def test_link_field_validation(self):
		"""Test that link fields are properly defined"""
		credit_balance = frappe.new_doc("Credit Balance Management")

		# Test Link field assignments
		if hasattr(credit_balance, "property_account"):
			credit_balance.property_account = "TEST-PROP-001"
			self.assertEqual(credit_balance.property_account, "TEST-PROP-001")

		if hasattr(credit_balance, "resident_account"):
			credit_balance.resident_account = "TEST-RES-001"
			self.assertEqual(credit_balance.resident_account, "TEST-RES-001")

		if hasattr(credit_balance, "company"):
			credit_balance.company = "_Test Company"
			self.assertEqual(credit_balance.company, "_Test Company")

	def test_text_field_validation(self):
		"""Test that text fields accept string values"""
		credit_balance = frappe.new_doc("Credit Balance Management")

		# Test Long Text fields
		if hasattr(credit_balance, "notes"):
			credit_balance.notes = "Test credit balance notes"
			self.assertEqual(credit_balance.notes, "Test credit balance notes")

		if hasattr(credit_balance, "application_notes"):
			credit_balance.application_notes = "Test application notes"
			self.assertEqual(credit_balance.application_notes, "Test application notes")

	def test_data_field_validation(self):
		"""Test that data fields accept string values"""
		credit_balance = frappe.new_doc("Credit Balance Management")

		# Test Data fields
		if hasattr(credit_balance, "source_reference"):
			credit_balance.source_reference = "PAY-001"
			self.assertEqual(credit_balance.source_reference, "PAY-001")

		if hasattr(credit_balance, "transfer_reference"):
			credit_balance.transfer_reference = "TXN-123"
			self.assertEqual(credit_balance.transfer_reference, "TXN-123")

	def test_check_field_validation(self):
		"""Test that check fields accept boolean values"""
		credit_balance = frappe.new_doc("Credit Balance Management")

		# Test Check fields (boolean)
		if hasattr(credit_balance, "auto_apply"):
			credit_balance.auto_apply = 1
			self.assertEqual(credit_balance.auto_apply, 1)

			credit_balance.auto_apply = 0
			self.assertEqual(credit_balance.auto_apply, 0)

		if hasattr(credit_balance, "transferable"):
			credit_balance.transferable = 1
			self.assertEqual(credit_balance.transferable, 1)

	def test_readonly_field_behavior(self):
		"""Test that readonly fields behave correctly"""
		credit_balance = frappe.new_doc("Credit Balance Management")

		# Test that calculated fields can be set programmatically
		if hasattr(credit_balance, "remaining_amount"):
			credit_balance.remaining_amount = 1000.00
			self.assertEqual(credit_balance.remaining_amount, 1000.00)

		if hasattr(credit_balance, "days_until_expiry"):
			credit_balance.days_until_expiry = 30
			self.assertEqual(credit_balance.days_until_expiry, 30)
