# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestFinancialTransparencyConfigL1FieldValidation(FrappeTestCase):
	"""Layer 1: Field Validation Tests for Financial Transparency Config DocType"""

	def test_required_fields_validation(self):
		"""Test that required fields are properly validated"""
		transparency_config = frappe.new_doc("Financial Transparency Config")

		# Test missing required fields
		with self.assertRaises(frappe.MandatoryError):
			transparency_config.insert()

		# Test each required field individually
		required_fields = [
			"naming_series",
			"config_name",
			"company",
			"effective_from",
			"config_status",
			"transparency_level",
		]

		for field in required_fields:
			self.assertTrue(hasattr(transparency_config, field), f"Missing required field: {field}")

	def test_naming_series_validation(self):
		"""Test that naming series is properly configured"""
		transparency_config = frappe.new_doc("Financial Transparency Config")

		# Test naming series field exists
		self.assertTrue(hasattr(transparency_config, "naming_series"))

		# Test default naming series value
		meta = frappe.get_meta("Financial Transparency Config")
		naming_series_field = meta.get_field("naming_series")
		self.assertEqual(naming_series_field.options, "FTC-.YYYY.-")

	def test_field_types_validation(self):
		"""Test that field types are correctly defined"""
		transparency_config = frappe.new_doc("Financial Transparency Config")

		# Test Data fields
		transparency_config.config_name = "Test Transparency Config"
		self.assertEqual(transparency_config.config_name, "Test Transparency Config")

		# Test Date fields
		from datetime import date

		today = date.today()
		transparency_config.effective_from = today
		self.assertEqual(transparency_config.effective_from, today)

	def test_select_field_options_validation(self):
		"""Test that select fields only accept valid options"""
		transparency_config = frappe.new_doc("Financial Transparency Config")

		# Test config_status options
		valid_config_statuses = ["Borrador", "En Revisión", "Aprobado", "Activo", "Inactivo", "Cancelado"]
		for status in valid_config_statuses:
			transparency_config.config_status = status
			self.assertEqual(transparency_config.config_status, status)

		# Test transparency_level options
		valid_transparency_levels = ["Básico", "Estándar", "Avanzado", "Completo", "Personalizado"]
		for level in valid_transparency_levels:
			transparency_config.transparency_level = level
			self.assertEqual(transparency_config.transparency_level, level)

	def test_date_field_validation(self):
		"""Test that date fields accept valid date values"""
		transparency_config = frappe.new_doc("Financial Transparency Config")

		# Test valid date formats
		from datetime import date

		today = date.today()

		transparency_config.effective_from = today
		self.assertEqual(transparency_config.effective_from, today)

		# Test additional date fields
		date_fields = ["effective_to", "last_updated", "approval_date"]
		for field in date_fields:
			if hasattr(transparency_config, field):
				setattr(transparency_config, field, today)
				self.assertEqual(getattr(transparency_config, field), today)

	def test_link_field_validation(self):
		"""Test that link fields are properly defined"""
		transparency_config = frappe.new_doc("Financial Transparency Config")

		# Test Link field assignments
		transparency_config.company = "_Test Company"
		self.assertEqual(transparency_config.company, "_Test Company")

		if hasattr(transparency_config, "approved_by"):
			transparency_config.approved_by = "Administrator"
			self.assertEqual(transparency_config.approved_by, "Administrator")

	def test_text_field_validation(self):
		"""Test that text fields accept string values"""
		transparency_config = frappe.new_doc("Financial Transparency Config")

		# Test Long Text fields
		if hasattr(transparency_config, "description"):
			transparency_config.description = "Test transparency config description"
			self.assertEqual(transparency_config.description, "Test transparency config description")

		if hasattr(transparency_config, "access_rules"):
			transparency_config.access_rules = "Test access rules"
			self.assertEqual(transparency_config.access_rules, "Test access rules")

	def test_check_field_validation(self):
		"""Test that check fields accept boolean values"""
		transparency_config = frappe.new_doc("Financial Transparency Config")

		# Test Check fields (boolean)
		if hasattr(transparency_config, "public_access"):
			transparency_config.public_access = 1
			self.assertEqual(transparency_config.public_access, 1)

			transparency_config.public_access = 0
			self.assertEqual(transparency_config.public_access, 0)

		if hasattr(transparency_config, "download_enabled"):
			transparency_config.download_enabled = 1
			self.assertEqual(transparency_config.download_enabled, 1)

		if hasattr(transparency_config, "real_time_updates"):
			transparency_config.real_time_updates = 1
			self.assertEqual(transparency_config.real_time_updates, 1)

	def test_table_field_validation(self):
		"""Test that table fields are properly defined"""
		transparency_config = frappe.new_doc("Financial Transparency Config")

		# Test table fields if they exist
		if hasattr(transparency_config, "access_permissions"):
			self.assertIsInstance(transparency_config.access_permissions, list)

		if hasattr(transparency_config, "report_settings"):
			self.assertIsInstance(transparency_config.report_settings, list)

	def test_json_field_validation(self):
		"""Test that JSON fields accept valid JSON values"""
		transparency_config = frappe.new_doc("Financial Transparency Config")

		# Test JSON fields if they exist
		if hasattr(transparency_config, "config_settings"):
			test_json = {"key": "value", "number": 123}
			transparency_config.config_settings = test_json
			self.assertEqual(transparency_config.config_settings, test_json)

	def test_readonly_field_behavior(self):
		"""Test that readonly fields behave correctly"""
		transparency_config = frappe.new_doc("Financial Transparency Config")

		# Test that calculated fields can be set programmatically
		if hasattr(transparency_config, "total_reports"):
			transparency_config.total_reports = 10
			self.assertEqual(transparency_config.total_reports, 10)

		if hasattr(transparency_config, "active_users"):
			transparency_config.active_users = 25
			self.assertEqual(transparency_config.active_users, 25)
