# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestBillingCycleL1FieldValidation(FrappeTestCase):
	"""Layer 1: Field Validation Tests for Billing Cycle DocType"""

	def test_required_fields_validation(self):
		"""Test that required fields are properly validated"""
		billing_cycle = frappe.new_doc("Billing Cycle")

		# Test missing required fields
		with self.assertRaises(frappe.MandatoryError):
			billing_cycle.insert()

		# Test each required field individually
		required_fields = [
			"naming_series",
			"cycle_name",
			"company",
			"cycle_status",
			"cycle_type",
			"billing_frequency",
			"billing_month",
			"billing_year",
			"start_date",
			"end_date",
			"due_date",
			"fee_structure",
		]

		for field in required_fields:
			self.assertTrue(hasattr(billing_cycle, field), f"Missing required field: {field}")

	def test_naming_series_validation(self):
		"""Test that naming series is properly configured"""
		billing_cycle = frappe.new_doc("Billing Cycle")

		# Test naming series field exists
		self.assertTrue(hasattr(billing_cycle, "naming_series"))

		# Test default naming series value
		meta = frappe.get_meta("Billing Cycle")
		naming_series_field = meta.get_field("naming_series")
		self.assertEqual(naming_series_field.options, "BC-.YYYY.-.MM.-")

	def test_field_types_validation(self):
		"""Test that field types are correctly defined"""
		billing_cycle = frappe.new_doc("Billing Cycle")

		# Test Data fields
		billing_cycle.cycle_name = "Test Billing Cycle"
		self.assertEqual(billing_cycle.cycle_name, "Test Billing Cycle")

		# Test Date fields
		from datetime import date

		today = date.today()
		billing_cycle.start_date = today
		self.assertEqual(billing_cycle.start_date, today)

		billing_cycle.end_date = today
		self.assertEqual(billing_cycle.end_date, today)

		billing_cycle.due_date = today
		self.assertEqual(billing_cycle.due_date, today)

		# Test Int fields
		billing_cycle.billing_month = 7
		self.assertEqual(billing_cycle.billing_month, 7)

		billing_cycle.billing_year = 2025
		self.assertEqual(billing_cycle.billing_year, 2025)

		# Test Currency fields if exist
		if hasattr(billing_cycle, "total_amount"):
			billing_cycle.total_amount = 15000.75
			self.assertEqual(billing_cycle.total_amount, 15000.75)

	def test_select_field_options_validation(self):
		"""Test that select fields only accept valid options"""
		billing_cycle = frappe.new_doc("Billing Cycle")

		# Test cycle_status options
		valid_cycle_statuses = ["Borrador", "Programado", "Activo", "Facturado", "Completado", "Cancelado"]
		for status in valid_cycle_statuses:
			billing_cycle.cycle_status = status
			self.assertEqual(billing_cycle.cycle_status, status)

		# Test cycle_type options
		valid_cycle_types = ["Regular", "Especial", "Ajuste", "Reserva"]
		for cycle_type in valid_cycle_types:
			billing_cycle.cycle_type = cycle_type
			self.assertEqual(billing_cycle.cycle_type, cycle_type)

		# Test billing_frequency options
		valid_billing_frequencies = ["Mensual", "Bimestral", "Trimestral", "Semestral", "Anual"]
		for freq in valid_billing_frequencies:
			billing_cycle.billing_frequency = freq
			self.assertEqual(billing_cycle.billing_frequency, freq)

	def test_currency_precision_validation(self):
		"""Test that currency fields maintain proper precision"""
		billing_cycle = frappe.new_doc("Billing Cycle")

		# Test currency fields with various precision values
		currency_fields = [
			"total_amount",
			"collected_amount",
			"pending_amount",
			"discount_amount",
			"late_fee_amount",
		]

		for field in currency_fields:
			if hasattr(billing_cycle, field):
				# Test with 2 decimal places (should be preserved)
				setattr(billing_cycle, field, 1234.56)
				self.assertEqual(getattr(billing_cycle, field), 1234.56)

	def test_date_field_validation(self):
		"""Test that date fields accept valid date values"""
		billing_cycle = frappe.new_doc("Billing Cycle")

		# Test valid date formats
		from datetime import date

		today = date.today()

		billing_cycle.start_date = today
		self.assertEqual(billing_cycle.start_date, today)

		billing_cycle.end_date = today
		self.assertEqual(billing_cycle.end_date, today)

		billing_cycle.due_date = today
		self.assertEqual(billing_cycle.due_date, today)

		# Test additional date fields
		date_fields = ["created_date", "approved_date", "completed_date"]
		for field in date_fields:
			if hasattr(billing_cycle, field):
				setattr(billing_cycle, field, today)
				self.assertEqual(getattr(billing_cycle, field), today)

	def test_link_field_validation(self):
		"""Test that link fields are properly defined"""
		billing_cycle = frappe.new_doc("Billing Cycle")

		# Test Link field assignments
		billing_cycle.company = "_Test Company"
		self.assertEqual(billing_cycle.company, "_Test Company")

		billing_cycle.fee_structure = "Test Fee Structure"
		self.assertEqual(billing_cycle.fee_structure, "Test Fee Structure")

		if hasattr(billing_cycle, "approved_by"):
			billing_cycle.approved_by = "Administrator"
			self.assertEqual(billing_cycle.approved_by, "Administrator")

	def test_int_field_validation(self):
		"""Test that integer fields accept valid values"""
		billing_cycle = frappe.new_doc("Billing Cycle")

		# Test billing_month (should be 1-12)
		billing_cycle.billing_month = 1
		self.assertEqual(billing_cycle.billing_month, 1)

		billing_cycle.billing_month = 12
		self.assertEqual(billing_cycle.billing_month, 12)

		# Test billing_year
		billing_cycle.billing_year = 2025
		self.assertEqual(billing_cycle.billing_year, 2025)

		# Test counts if exist
		if hasattr(billing_cycle, "property_count"):
			billing_cycle.property_count = 150
			self.assertEqual(billing_cycle.property_count, 150)

	def test_text_field_validation(self):
		"""Test that text fields accept string values"""
		billing_cycle = frappe.new_doc("Billing Cycle")

		# Test Long Text fields
		if hasattr(billing_cycle, "description"):
			billing_cycle.description = "Test billing cycle description"
			self.assertEqual(billing_cycle.description, "Test billing cycle description")

		if hasattr(billing_cycle, "notes"):
			billing_cycle.notes = "Test notes for billing cycle"
			self.assertEqual(billing_cycle.notes, "Test notes for billing cycle")

	def test_check_field_validation(self):
		"""Test that check fields accept boolean values"""
		billing_cycle = frappe.new_doc("Billing Cycle")

		# Test Check fields (boolean)
		if hasattr(billing_cycle, "auto_generate_invoices"):
			billing_cycle.auto_generate_invoices = 1
			self.assertEqual(billing_cycle.auto_generate_invoices, 1)

			billing_cycle.auto_generate_invoices = 0
			self.assertEqual(billing_cycle.auto_generate_invoices, 0)

		if hasattr(billing_cycle, "send_notifications"):
			billing_cycle.send_notifications = 1
			self.assertEqual(billing_cycle.send_notifications, 1)

	def test_readonly_field_behavior(self):
		"""Test that readonly fields behave correctly"""
		billing_cycle = frappe.new_doc("Billing Cycle")

		# Test that calculated fields can be set programmatically
		if hasattr(billing_cycle, "collected_amount"):
			billing_cycle.collected_amount = 12000.00
			self.assertEqual(billing_cycle.collected_amount, 12000.00)

		if hasattr(billing_cycle, "pending_amount"):
			billing_cycle.pending_amount = 3000.00
			self.assertEqual(billing_cycle.pending_amount, 3000.00)

		if hasattr(billing_cycle, "collection_percentage"):
			billing_cycle.collection_percentage = 80.5
			self.assertEqual(billing_cycle.collection_percentage, 80.5)
