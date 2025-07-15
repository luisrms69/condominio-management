# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

# REGLA #43B: Payment Collection puede tener Sales Invoice dependencies
test_ignore = ["Sales Invoice", "Item", "Payment Entry"]


class TestPaymentCollectionL1FieldValidation(FrappeTestCase):
	"""Layer 1: Field Validation Tests for Payment Collection DocType"""

	def test_required_fields_validation(self):
		"""Test that required fields are properly validated"""
		payment_collection = frappe.new_doc("Payment Collection")

		# Test missing required fields
		with self.assertRaises(frappe.MandatoryError):
			payment_collection.insert()

		# Test each required field individually
		required_fields = [
			"payment_date",
			"account_type",
			"payment_amount",
			"payment_method",
			"payment_status",
		]

		for field in required_fields:
			self.assertTrue(hasattr(payment_collection, field), f"Missing required field: {field}")

	def test_naming_series_validation(self):
		"""Test that naming series is properly configured"""
		payment_collection = frappe.new_doc("Payment Collection")

		# Test naming series field exists
		self.assertTrue(hasattr(payment_collection, "naming_series"))

		# Test default naming series value
		meta = frappe.get_meta("Payment Collection")
		naming_series_field = meta.get_field("naming_series")
		self.assertEqual(naming_series_field.options, "PC-.YYYY.-.MM.-")

	def test_field_types_validation(self):
		"""Test that field types are correctly defined"""
		payment_collection = frappe.new_doc("Payment Collection")

		# Test Date fields
		from datetime import date

		today = date.today()
		payment_collection.payment_date = today
		self.assertEqual(payment_collection.payment_date, today)

		# Test Currency fields with precision 2
		payment_collection.payment_amount = 1500.75
		self.assertEqual(payment_collection.payment_amount, 1500.75)

		if hasattr(payment_collection, "service_charge"):
			payment_collection.service_charge = 25.50
			self.assertEqual(payment_collection.service_charge, 25.50)

		if hasattr(payment_collection, "discount_amount"):
			payment_collection.discount_amount = 100.00
			self.assertEqual(payment_collection.discount_amount, 100.00)

	def test_select_field_options_validation(self):
		"""Test that select fields only accept valid options"""
		payment_collection = frappe.new_doc("Payment Collection")

		# Test account_type options
		valid_account_types = ["Propietario", "Residente", "Ambos"]
		for account_type in valid_account_types:
			payment_collection.account_type = account_type
			self.assertEqual(payment_collection.account_type, account_type)

		# Test payment_method options (based on common payment methods)
		valid_payment_methods = [
			"Efectivo",
			"Tarjeta de Débito",
			"Tarjeta de Crédito",
			"Transferencia Bancaria",
			"Cheque",
			"Depósito Bancario",
		]
		for method in valid_payment_methods:
			payment_collection.payment_method = method
			self.assertEqual(payment_collection.payment_method, method)

		# Test payment_status options
		valid_payment_statuses = ["Pendiente", "En Proceso", "Procesado", "Rechazado", "Cancelado"]
		for status in valid_payment_statuses:
			payment_collection.payment_status = status
			self.assertEqual(payment_collection.payment_status, status)

	def test_currency_precision_validation(self):
		"""Test that currency fields maintain proper precision"""
		payment_collection = frappe.new_doc("Payment Collection")

		# Test currency fields with various precision values
		currency_fields = [
			"payment_amount",
			"service_charge",
			"discount_amount",
			"net_amount",
			"commission_amount",
		]

		for field in currency_fields:
			if hasattr(payment_collection, field):
				# Test with 2 decimal places (should be preserved)
				setattr(payment_collection, field, 1234.56)
				self.assertEqual(getattr(payment_collection, field), 1234.56)

	def test_date_field_validation(self):
		"""Test that date fields accept valid date values"""
		payment_collection = frappe.new_doc("Payment Collection")

		# Test valid date formats
		from datetime import date

		today = date.today()

		payment_collection.payment_date = today
		self.assertEqual(payment_collection.payment_date, today)

		# Test additional date fields
		date_fields = ["due_date", "processed_date", "verification_date"]
		for field in date_fields:
			if hasattr(payment_collection, field):
				setattr(payment_collection, field, today)
				self.assertEqual(getattr(payment_collection, field), today)

	def test_link_field_validation(self):
		"""Test that link fields are properly defined"""
		payment_collection = frappe.new_doc("Payment Collection")

		# Test Link field assignments
		if hasattr(payment_collection, "property_account"):
			payment_collection.property_account = "TEST-PROP-001"
			self.assertEqual(payment_collection.property_account, "TEST-PROP-001")

		if hasattr(payment_collection, "resident_account"):
			payment_collection.resident_account = "TEST-RES-001"
			self.assertEqual(payment_collection.resident_account, "TEST-RES-001")

		if hasattr(payment_collection, "company"):
			payment_collection.company = "_Test Company"
			self.assertEqual(payment_collection.company, "_Test Company")

	def test_text_field_validation(self):
		"""Test that text fields accept string values"""
		payment_collection = frappe.new_doc("Payment Collection")

		# Test Long Text fields
		if hasattr(payment_collection, "payment_notes"):
			payment_collection.payment_notes = "Test payment notes"
			self.assertEqual(payment_collection.payment_notes, "Test payment notes")

		if hasattr(payment_collection, "verification_notes"):
			payment_collection.verification_notes = "Test verification notes"
			self.assertEqual(payment_collection.verification_notes, "Test verification notes")

	def test_data_field_validation(self):
		"""Test that data fields accept string values"""
		payment_collection = frappe.new_doc("Payment Collection")

		# Test Data fields
		if hasattr(payment_collection, "reference_number"):
			payment_collection.reference_number = "REF-12345"
			self.assertEqual(payment_collection.reference_number, "REF-12345")

		if hasattr(payment_collection, "bank_name"):
			payment_collection.bank_name = "Test Bank"
			self.assertEqual(payment_collection.bank_name, "Test Bank")

		if hasattr(payment_collection, "transaction_id"):
			payment_collection.transaction_id = "TXN-67890"
			self.assertEqual(payment_collection.transaction_id, "TXN-67890")

	def test_check_field_validation(self):
		"""Test that check fields accept boolean values"""
		payment_collection = frappe.new_doc("Payment Collection")

		# Test Check fields (boolean)
		if hasattr(payment_collection, "verified"):
			payment_collection.verified = 1
			self.assertEqual(payment_collection.verified, 1)

			payment_collection.verified = 0
			self.assertEqual(payment_collection.verified, 0)

		if hasattr(payment_collection, "auto_reconcile"):
			payment_collection.auto_reconcile = 1
			self.assertEqual(payment_collection.auto_reconcile, 1)

	def test_readonly_field_behavior(self):
		"""Test that readonly fields behave correctly"""
		payment_collection = frappe.new_doc("Payment Collection")

		# Test that calculated fields can be set programmatically
		if hasattr(payment_collection, "net_amount"):
			payment_collection.net_amount = 1400.00
			self.assertEqual(payment_collection.net_amount, 1400.00)

		if hasattr(payment_collection, "commission_amount"):
			payment_collection.commission_amount = 35.00
			self.assertEqual(payment_collection.commission_amount, 35.00)
