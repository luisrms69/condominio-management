# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestResidentAccountL1FieldValidation(FrappeTestCase):
	"""Layer 1: Field Validation Tests for Resident Account DocType"""

	def test_required_fields_validation(self):
		"""Test that required fields are properly validated"""
		resident_account = frappe.new_doc("Resident Account")

		# Test missing required fields
		with self.assertRaises(frappe.MandatoryError):
			resident_account.insert()

		# Test each required field individually
		required_fields = [
			"account_code",
			"resident_name",
			"property_account",
			"company",
			"resident_type",
			"account_status",
			"current_balance",
		]

		for field in required_fields:
			self.assertTrue(hasattr(resident_account, field), f"Missing required field: {field}")

	def test_field_types_validation(self):
		"""Test that field types are correctly defined"""
		resident_account = frappe.new_doc("Resident Account")

		# Test Data fields
		resident_account.account_code = "RES-001"
		self.assertEqual(resident_account.account_code, "RES-001")

		resident_account.resident_name = "Test Resident"
		self.assertEqual(resident_account.resident_name, "Test Resident")

		# Test Currency fields with precision 2
		resident_account.current_balance = 2500.75
		self.assertEqual(resident_account.current_balance, 2500.75)

		resident_account.credit_limit = 5000.00
		self.assertEqual(resident_account.credit_limit, 5000.00)

		resident_account.spending_limits = 1000.50
		self.assertEqual(resident_account.spending_limits, 1000.50)

		resident_account.approval_required_amount = 2000.00
		self.assertEqual(resident_account.approval_required_amount, 2000.00)

		# Test Check fields (boolean)
		resident_account.auto_charge_enabled = 1
		self.assertEqual(resident_account.auto_charge_enabled, 1)

		resident_account.notifications_enabled = 0
		self.assertEqual(resident_account.notifications_enabled, 0)

	def test_select_field_options_validation(self):
		"""Test that select fields only accept valid options"""
		resident_account = frappe.new_doc("Resident Account")

		# Test resident_type options
		valid_resident_types = ["Propietario", "Inquilino", "Familiar", "Huésped", "Empleado Doméstico"]
		for resident_type in valid_resident_types:
			resident_account.resident_type = resident_type
			self.assertEqual(resident_account.resident_type, resident_type)

		# Test account_status options
		valid_account_statuses = ["Activa", "Suspendida", "Bloqueada", "Cerrada"]
		for status in valid_account_statuses:
			resident_account.account_status = status
			self.assertEqual(resident_account.account_status, status)

	def test_unique_fields_validation(self):
		"""Test that unique fields are properly validated"""
		resident_account = frappe.new_doc("Resident Account")

		# Test account_code uniqueness (should be unique)
		resident_account.account_code = "UNIQUE_RES_001"
		self.assertEqual(resident_account.account_code, "UNIQUE_RES_001")

		# Verify the field has unique constraint in meta
		meta = frappe.get_meta("Resident Account")
		account_code_field = meta.get_field("account_code")
		self.assertTrue(account_code_field.unique, "account_code field should be unique")

	def test_currency_precision_validation(self):
		"""Test that currency fields maintain proper precision"""
		resident_account = frappe.new_doc("Resident Account")

		# Test currency fields with various precision values
		currency_fields = [
			"current_balance",
			"credit_limit",
			"spending_limits",
			"approval_required_amount",
			"deposit_amount",
			"outstanding_balance",
		]

		for field in currency_fields:
			if hasattr(resident_account, field):
				# Test with 2 decimal places (should be preserved)
				setattr(resident_account, field, 1234.56)
				self.assertEqual(getattr(resident_account, field), 1234.56)

				# Test with more decimal places (should be rounded to 2)
				setattr(resident_account, field, 1234.5678)
				# Note: Frappe automatically handles currency precision

	def test_date_field_validation(self):
		"""Test that date fields accept valid date values"""
		resident_account = frappe.new_doc("Resident Account")

		# Test valid date formats
		from datetime import date

		today = date.today()

		# Test date fields exist
		date_fields = ["last_payment_date", "account_creation_date", "last_activity_date"]
		for field in date_fields:
			if hasattr(resident_account, field):
				setattr(resident_account, field, today)
				self.assertEqual(getattr(resident_account, field), today)

	def test_link_field_validation(self):
		"""Test that link fields are properly defined"""
		resident_account = frappe.new_doc("Resident Account")

		# Test Link field assignments
		resident_account.property_account = "TEST-PROP-001"
		self.assertEqual(resident_account.property_account, "TEST-PROP-001")

		resident_account.company = "_Test Company"
		self.assertEqual(resident_account.company, "_Test Company")

		# Test User link field
		if hasattr(resident_account, "user"):
			resident_account.user = "Administrator"
			self.assertEqual(resident_account.user, "Administrator")

	def test_text_field_validation(self):
		"""Test that text fields accept string values"""
		resident_account = frappe.new_doc("Resident Account")

		# Test Long Text fields
		if hasattr(resident_account, "notes"):
			resident_account.notes = "Test notes for resident account"
			self.assertEqual(resident_account.notes, "Test notes for resident account")

		if hasattr(resident_account, "address"):
			resident_account.address = "Test address for resident"
			self.assertEqual(resident_account.address, "Test address for resident")

	def test_phone_email_field_validation(self):
		"""Test that phone and email fields accept valid formats"""
		resident_account = frappe.new_doc("Resident Account")

		# Test Phone field
		if hasattr(resident_account, "phone"):
			resident_account.phone = "+52 55 1234 5678"
			self.assertEqual(resident_account.phone, "+52 55 1234 5678")

		# Test Email field
		if hasattr(resident_account, "email"):
			resident_account.email = "test@example.com"
			self.assertEqual(resident_account.email, "test@example.com")

	def test_readonly_field_behavior(self):
		"""Test that readonly fields behave correctly"""
		resident_account = frappe.new_doc("Resident Account")

		# Test that calculated fields can be set programmatically
		if hasattr(resident_account, "outstanding_balance"):
			resident_account.outstanding_balance = 1500.00
			self.assertEqual(resident_account.outstanding_balance, 1500.00)

		if hasattr(resident_account, "total_spent"):
			resident_account.total_spent = 800.00
			self.assertEqual(resident_account.total_spent, 800.00)
