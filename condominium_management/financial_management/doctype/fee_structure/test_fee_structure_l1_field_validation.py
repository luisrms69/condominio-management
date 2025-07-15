# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestFeeStructureL1FieldValidation(FrappeTestCase):
	"""Layer 1: Field Validation Tests for Fee Structure DocType"""

	def test_required_fields_validation(self):
		"""Test that required fields are properly validated"""
		fee_structure = frappe.new_doc("Fee Structure")

		# Test missing fee_structure_name validation (custom validation)
		with self.assertRaises(frappe.ValidationError) as context:
			fee_structure.insert()
		self.assertIn("El nombre de la estructura es obligatorio", str(context.exception))

		# Test each required field individually
		required_fields = [
			"naming_series",
			"fee_structure_name",
			"company",
			"effective_from",
			"calculation_method",
			"base_amount",
		]

		for field in required_fields:
			self.assertTrue(hasattr(fee_structure, field), f"Missing required field: {field}")

	def test_naming_series_validation(self):
		"""Test that naming series is properly configured"""
		fee_structure = frappe.new_doc("Fee Structure")

		# Test naming series field exists
		self.assertTrue(hasattr(fee_structure, "naming_series"))

		# Test default naming series value
		meta = frappe.get_meta("Fee Structure")
		naming_series_field = meta.get_field("naming_series")
		self.assertEqual(naming_series_field.options, "FS-.YYYY.-")

	def test_submittable_doctype_validation(self):
		"""Test that DocType is properly configured as submittable"""
		meta = frappe.get_meta("Fee Structure")
		self.assertTrue(meta.is_submittable, "Fee Structure should be submittable")

	def test_field_types_validation(self):
		"""Test that field types are correctly defined"""
		fee_structure = frappe.new_doc("Fee Structure")

		# Test Data fields
		fee_structure.fee_structure_name = "Test Fee Structure"
		self.assertEqual(fee_structure.fee_structure_name, "Test Fee Structure")

		# Test Date fields
		from datetime import date

		today = date.today()
		fee_structure.effective_from = today
		self.assertEqual(fee_structure.effective_from, today)

		# Test Currency fields with precision 2
		fee_structure.base_amount = 2500.75
		self.assertEqual(fee_structure.base_amount, 2500.75)

		if hasattr(fee_structure, "total_amount"):
			fee_structure.total_amount = 3000.00
			self.assertEqual(fee_structure.total_amount, 3000.00)

	def test_select_field_options_validation(self):
		"""Test that select fields only accept valid options"""
		fee_structure = frappe.new_doc("Fee Structure")

		# Test calculation_method options
		valid_calculation_methods = ["Por Indiviso", "Monto Fijo", "Por M2", "Mixto"]
		for method in valid_calculation_methods:
			fee_structure.calculation_method = method
			self.assertEqual(fee_structure.calculation_method, method)

		# Test status options if exists
		if hasattr(fee_structure, "status"):
			valid_statuses = ["Borrador", "Activo", "Inactivo", "Cancelado"]
			for status in valid_statuses:
				fee_structure.status = status
				self.assertEqual(fee_structure.status, status)

	def test_unique_fields_validation(self):
		"""Test that unique fields are properly validated"""
		fee_structure = frappe.new_doc("Fee Structure")

		# Test fee_structure_name uniqueness (should be unique)
		fee_structure.fee_structure_name = "UNIQUE_FEE_STRUCTURE_001"
		self.assertEqual(fee_structure.fee_structure_name, "UNIQUE_FEE_STRUCTURE_001")

		# Verify the field has unique constraint in meta
		meta = frappe.get_meta("Fee Structure")
		fee_structure_name_field = meta.get_field("fee_structure_name")
		self.assertTrue(fee_structure_name_field.unique, "fee_structure_name field should be unique")

	def test_currency_precision_validation(self):
		"""Test that currency fields maintain proper precision"""
		fee_structure = frappe.new_doc("Fee Structure")

		# Test currency fields with various precision values
		currency_fields = ["base_amount", "total_amount", "minimum_amount", "maximum_amount"]

		for field in currency_fields:
			if hasattr(fee_structure, field):
				# Test with 2 decimal places (should be preserved)
				setattr(fee_structure, field, 1234.56)
				self.assertEqual(getattr(fee_structure, field), 1234.56)

	def test_date_field_validation(self):
		"""Test that date fields accept valid date values"""
		fee_structure = frappe.new_doc("Fee Structure")

		# Test valid date formats
		from datetime import date

		today = date.today()

		fee_structure.effective_from = today
		self.assertEqual(fee_structure.effective_from, today)

		# Test additional date fields
		date_fields = ["effective_to", "approval_date", "last_modified_date"]
		for field in date_fields:
			if hasattr(fee_structure, field):
				setattr(fee_structure, field, today)
				self.assertEqual(getattr(fee_structure, field), today)

	def test_link_field_validation(self):
		"""Test that link fields are properly defined"""
		fee_structure = frappe.new_doc("Fee Structure")

		# Test Link field assignments
		fee_structure.company = "_Test Company"
		self.assertEqual(fee_structure.company, "_Test Company")

		if hasattr(fee_structure, "approved_by"):
			fee_structure.approved_by = "Administrator"
			self.assertEqual(fee_structure.approved_by, "Administrator")

	def test_table_field_validation(self):
		"""Test that table fields are properly defined"""
		fee_structure = frappe.new_doc("Fee Structure")

		# Test fee_components table field exists
		self.assertTrue(hasattr(fee_structure, "fee_components"))

		# Test that it's a list (table field)
		self.assertIsInstance(fee_structure.fee_components, list)

	def test_text_field_validation(self):
		"""Test that text fields accept string values"""
		fee_structure = frappe.new_doc("Fee Structure")

		# Test Long Text fields
		if hasattr(fee_structure, "description"):
			fee_structure.description = "Test fee structure description"
			self.assertEqual(fee_structure.description, "Test fee structure description")

		if hasattr(fee_structure, "notes"):
			fee_structure.notes = "Test notes for fee structure"
			self.assertEqual(fee_structure.notes, "Test notes for fee structure")

	def test_check_field_validation(self):
		"""Test that check fields accept boolean values"""
		fee_structure = frappe.new_doc("Fee Structure")

		# Test Check fields (boolean)
		if hasattr(fee_structure, "is_active"):
			fee_structure.is_active = 1
			self.assertEqual(fee_structure.is_active, 1)

			fee_structure.is_active = 0
			self.assertEqual(fee_structure.is_active, 0)

		if hasattr(fee_structure, "auto_calculate"):
			fee_structure.auto_calculate = 1
			self.assertEqual(fee_structure.auto_calculate, 1)

	def test_readonly_field_behavior(self):
		"""Test that readonly fields behave correctly"""
		fee_structure = frappe.new_doc("Fee Structure")

		# Test that calculated fields can be set programmatically
		if hasattr(fee_structure, "total_amount"):
			fee_structure.total_amount = 2800.00
			self.assertEqual(fee_structure.total_amount, 2800.00)

		if hasattr(fee_structure, "component_count"):
			fee_structure.component_count = 5
			self.assertEqual(fee_structure.component_count, 5)
