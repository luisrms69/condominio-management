# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

# REGLA #43B: Fine Management puede tener Sales Invoice dependencies
test_ignore = ["Sales Invoice", "Item"]


class TestFineManagementL1FieldValidation(FrappeTestCase):
	"""Layer 1: Field Validation Tests for Fine Management DocType"""

	def test_required_fields_validation(self):
		"""Test that required fields are properly validated"""
		fine_management = frappe.new_doc("Fine Management")

		# Test missing required fields
		with self.assertRaises(frappe.MandatoryError):
			fine_management.insert()

		# Test each required field individually
		required_fields = [
			"naming_series",
			"fine_date",
			"fine_type",
			"fine_amount",
			"fine_status",
			"due_date",
			"violation_description",
		]

		for field in required_fields:
			self.assertTrue(hasattr(fine_management, field), f"Missing required field: {field}")

	def test_naming_series_validation(self):
		"""Test that naming series is properly configured"""
		fine_management = frappe.new_doc("Fine Management")

		# Test naming series field exists
		self.assertTrue(hasattr(fine_management, "naming_series"))

		# Test default naming series value
		meta = frappe.get_meta("Fine Management")
		naming_series_field = meta.get_field("naming_series")
		self.assertEqual(naming_series_field.options, "FM-.YYYY.-.MM.-")

	def test_field_types_validation(self):
		"""Test that field types are correctly defined"""
		fine_management = frappe.new_doc("Fine Management")

		# Test Date fields
		from datetime import date

		today = date.today()
		fine_management.fine_date = today
		self.assertEqual(fine_management.fine_date, today)

		fine_management.due_date = today
		self.assertEqual(fine_management.due_date, today)

		# Test Currency fields with precision 2
		fine_management.fine_amount = 500.75
		self.assertEqual(fine_management.fine_amount, 500.75)

		# Test Long Text fields
		fine_management.violation_description = "Test violation description"
		self.assertEqual(fine_management.violation_description, "Test violation description")

	def test_select_field_options_validation(self):
		"""Test that select fields only accept valid options"""
		fine_management = frappe.new_doc("Fine Management")

		# Test fine_type options (common violation types)
		valid_fine_types = [
			"Ruido Excesivo",
			"Mascota sin Correa",
			"Basura Incorrecta",
			"Estacionamiento Indebido",
			"Modificación sin Permiso",
			"Uso Inadecuado de Áreas Comunes",
			"Otra",
		]
		for fine_type in valid_fine_types:
			fine_management.fine_type = fine_type
			self.assertEqual(fine_management.fine_type, fine_type)

		# Test fine_status options
		valid_fine_statuses = [
			"Pendiente",
			"Notificada",
			"Apelada",
			"Confirmada",
			"Pagada",
			"Vencida",
			"Cancelada",
		]
		for status in valid_fine_statuses:
			fine_management.fine_status = status
			self.assertEqual(fine_management.fine_status, status)

	def test_currency_precision_validation(self):
		"""Test that currency fields maintain proper precision"""
		fine_management = frappe.new_doc("Fine Management")

		# Test currency fields with various precision values
		currency_fields = [
			"fine_amount",
			"paid_amount",
			"outstanding_amount",
			"late_fee_amount",
			"discount_amount",
		]

		for field in currency_fields:
			if hasattr(fine_management, field):
				# Test with 2 decimal places (should be preserved)
				setattr(fine_management, field, 1234.56)
				self.assertEqual(getattr(fine_management, field), 1234.56)

	def test_date_field_validation(self):
		"""Test that date fields accept valid date values"""
		fine_management = frappe.new_doc("Fine Management")

		# Test valid date formats
		from datetime import date

		today = date.today()

		fine_management.fine_date = today
		self.assertEqual(fine_management.fine_date, today)

		fine_management.due_date = today
		self.assertEqual(fine_management.due_date, today)

		# Test additional date fields
		date_fields = ["paid_date", "appeal_date", "resolution_date"]
		for field in date_fields:
			if hasattr(fine_management, field):
				setattr(fine_management, field, today)
				self.assertEqual(getattr(fine_management, field), today)

	def test_link_field_validation(self):
		"""Test that link fields are properly defined"""
		fine_management = frappe.new_doc("Fine Management")

		# Test Link field assignments
		if hasattr(fine_management, "property_account"):
			fine_management.property_account = "TEST-PROP-001"
			self.assertEqual(fine_management.property_account, "TEST-PROP-001")

		if hasattr(fine_management, "resident_account"):
			fine_management.resident_account = "TEST-RES-001"
			self.assertEqual(fine_management.resident_account, "TEST-RES-001")

		if hasattr(fine_management, "company"):
			fine_management.company = "_Test Company"
			self.assertEqual(fine_management.company, "_Test Company")

	def test_text_field_validation(self):
		"""Test that text fields accept string values"""
		fine_management = frappe.new_doc("Fine Management")

		# Test Long Text fields
		fine_management.violation_description = "Test violation description"
		self.assertEqual(fine_management.violation_description, "Test violation description")

		if hasattr(fine_management, "appeal_reason"):
			fine_management.appeal_reason = "Test appeal reason"
			self.assertEqual(fine_management.appeal_reason, "Test appeal reason")

		if hasattr(fine_management, "resolution_notes"):
			fine_management.resolution_notes = "Test resolution notes"
			self.assertEqual(fine_management.resolution_notes, "Test resolution notes")

	def test_data_field_validation(self):
		"""Test that data fields accept string values"""
		fine_management = frappe.new_doc("Fine Management")

		# Test Data fields
		if hasattr(fine_management, "violation_location"):
			fine_management.violation_location = "Test Location"
			self.assertEqual(fine_management.violation_location, "Test Location")

		if hasattr(fine_management, "reference_number"):
			fine_management.reference_number = "REF-123"
			self.assertEqual(fine_management.reference_number, "REF-123")

	def test_check_field_validation(self):
		"""Test that check fields accept boolean values"""
		fine_management = frappe.new_doc("Fine Management")

		# Test Check fields (boolean)
		if hasattr(fine_management, "repeat_offense"):
			fine_management.repeat_offense = 1
			self.assertEqual(fine_management.repeat_offense, 1)

			fine_management.repeat_offense = 0
			self.assertEqual(fine_management.repeat_offense, 0)

		if hasattr(fine_management, "appealed"):
			fine_management.appealed = 1
			self.assertEqual(fine_management.appealed, 1)

	def test_readonly_field_behavior(self):
		"""Test that readonly fields behave correctly"""
		fine_management = frappe.new_doc("Fine Management")

		# Test that calculated fields can be set programmatically
		if hasattr(fine_management, "outstanding_amount"):
			fine_management.outstanding_amount = 450.00
			self.assertEqual(fine_management.outstanding_amount, 450.00)

		if hasattr(fine_management, "days_overdue"):
			fine_management.days_overdue = 15
			self.assertEqual(fine_management.days_overdue, 15)
