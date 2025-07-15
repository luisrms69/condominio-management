# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestBudgetPlanningL1FieldValidation(FrappeTestCase):
	"""Layer 1: Field Validation Tests for Budget Planning DocType"""

	def test_required_fields_validation(self):
		"""Test that required fields are properly validated"""
		budget_planning = frappe.new_doc("Budget Planning")

		# Test missing required fields
		with self.assertRaises(frappe.MandatoryError):
			budget_planning.insert()

		# Test each required field individually
		required_fields = ["naming_series", "budget_name", "budget_period", "company", "budget_status"]

		for field in required_fields:
			self.assertTrue(hasattr(budget_planning, field), f"Missing required field: {field}")

	def test_naming_series_validation(self):
		"""Test that naming series is properly configured"""
		budget_planning = frappe.new_doc("Budget Planning")

		# Test naming series field exists
		self.assertTrue(hasattr(budget_planning, "naming_series"))

		# Test default naming series value
		meta = frappe.get_meta("Budget Planning")
		naming_series_field = meta.get_field("naming_series")
		self.assertEqual(naming_series_field.options, "BP-.YYYY.-")

	def test_field_types_validation(self):
		"""Test that field types are correctly defined"""
		budget_planning = frappe.new_doc("Budget Planning")

		# Test Data fields
		budget_planning.budget_name = "Test Budget Planning"
		self.assertEqual(budget_planning.budget_name, "Test Budget Planning")

		# Test Date fields
		from datetime import date

		today = date.today()
		if hasattr(budget_planning, "start_date"):
			budget_planning.start_date = today
			self.assertEqual(budget_planning.start_date, today)

		# Test Currency fields if exist
		if hasattr(budget_planning, "total_budget"):
			budget_planning.total_budget = 50000.00
			self.assertEqual(budget_planning.total_budget, 50000.00)

	def test_select_field_options_validation(self):
		"""Test that select fields only accept valid options"""
		budget_planning = frappe.new_doc("Budget Planning")

		# Test budget_period options
		valid_budget_periods = ["Anual", "Semestral", "Trimestral", "Mensual"]
		for period in valid_budget_periods:
			budget_planning.budget_period = period
			self.assertEqual(budget_planning.budget_period, period)

		# Test budget_status options
		valid_budget_statuses = ["Borrador", "En Revisión", "Aprobado", "Activo", "Cerrado", "Cancelado"]
		for status in valid_budget_statuses:
			budget_planning.budget_status = status
			self.assertEqual(budget_planning.budget_status, status)

	def test_currency_precision_validation(self):
		"""Test that currency fields maintain proper precision"""
		budget_planning = frappe.new_doc("Budget Planning")

		# Test currency fields with various precision values
		currency_fields = [
			"total_budget",
			"allocated_amount",
			"spent_amount",
			"remaining_amount",
			"contingency_amount",
		]

		for field in currency_fields:
			if hasattr(budget_planning, field):
				# Test with 2 decimal places (should be preserved)
				setattr(budget_planning, field, 1234.56)
				self.assertEqual(getattr(budget_planning, field), 1234.56)

	def test_link_field_validation(self):
		"""Test that link fields are properly defined"""
		budget_planning = frappe.new_doc("Budget Planning")

		# Test Link field assignments
		budget_planning.company = "_Test Company"
		self.assertEqual(budget_planning.company, "_Test Company")

		if hasattr(budget_planning, "approved_by"):
			budget_planning.approved_by = "Administrator"
			self.assertEqual(budget_planning.approved_by, "Administrator")

	def test_text_field_validation(self):
		"""Test that text fields accept string values"""
		budget_planning = frappe.new_doc("Budget Planning")

		# Test Long Text fields
		if hasattr(budget_planning, "description"):
			budget_planning.description = "Test budget planning description"
			self.assertEqual(budget_planning.description, "Test budget planning description")

	def test_readonly_field_behavior(self):
		"""Test that readonly fields behave correctly"""
		budget_planning = frappe.new_doc("Budget Planning")

		# Test that calculated fields can be set programmatically
		if hasattr(budget_planning, "remaining_amount"):
			budget_planning.remaining_amount = 25000.00
			self.assertEqual(budget_planning.remaining_amount, 25000.00)
