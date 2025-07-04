# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.tests.utils import FrappeTestCase


class TestContributionCategory(FrappeTestCase):
	"""Test cases for Contribution Category."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()
		cls.create_test_data()

	@classmethod
	def create_test_data(cls):
		"""Create reusable test data with flags to avoid duplication."""
		if getattr(frappe.flags, "test_contribution_category_data_created", False):
			return

		# No additional test data needed for this DocType
		frappe.flags.test_contribution_category_data_created = True

	def setUp(self):
		"""Set up before each test method."""
		frappe.set_user("Administrator")

	def test_creation(self):
		"""Test basic creation with Spanish validations."""
		category = frappe.get_doc(
			{
				"doctype": "Contribution Category",
				"module_name": "Document Generation",
				"contribution_type": "Test Template",
				"description": "Categoría de prueba para templates",
				"export_doctype": "Master Template Registry",
				"required_fields": json.dumps(["template_code", "template_name"]),
				"is_active": 1,
			}
		)
		category.insert(ignore_permissions=True)

		self.assertEqual(category.module_name, "Document Generation")
		self.assertEqual(category.contribution_type, "Test Template")
		self.assertTrue(category.is_active)

		# Verify JSON parsing
		required_fields = category.get_required_fields_list()
		self.assertIn("template_code", required_fields)
		self.assertIn("template_name", required_fields)

	def test_spanish_labels(self):
		"""Test that DocType has proper Spanish labels."""
		meta = frappe.get_meta("Contribution Category")

		# Verify key field labels are in Spanish
		spanish_labels = {
			"module_name": "Módulo",
			"contribution_type": "Tipo de Contribución",
			"description": "Descripción",
			"is_active": "Activo",
		}

		for fieldname, expected_label in spanish_labels.items():
			field = meta.get_field(fieldname)
			self.assertEqual(field.label, expected_label, f"Field {fieldname} should have Spanish label")

	def test_required_fields_validation(self):
		"""Test required fields validation."""
		# Test missing module_name
		with self.assertRaises(frappe.ValidationError):
			category = frappe.get_doc(
				{"doctype": "Contribution Category", "contribution_type": "Test Template"}
			)
			category.insert(ignore_permissions=True)

		# Test missing contribution_type
		with self.assertRaises(frappe.ValidationError):
			category = frappe.get_doc(
				{"doctype": "Contribution Category", "module_name": "Document Generation"}
			)
			category.insert(ignore_permissions=True)

	def test_unique_category_validation(self):
		"""Test that duplicate module-type combinations are prevented."""
		# Create first category
		category1 = frappe.get_doc(
			{
				"doctype": "Contribution Category",
				"module_name": "Document Generation",
				"contribution_type": "Unique Template",
				"is_active": 1,
			}
		)
		category1.insert(ignore_permissions=True)

		# Try to create duplicate
		with self.assertRaises(frappe.ValidationError):
			category2 = frappe.get_doc(
				{
					"doctype": "Contribution Category",
					"module_name": "Document Generation",
					"contribution_type": "Unique Template",
					"is_active": 1,
				}
			)
			category2.insert(ignore_permissions=True)

	def test_json_validation(self):
		"""Test JSON validation for required_fields."""
		# Test invalid JSON
		with self.assertRaises(frappe.ValidationError):
			category = frappe.get_doc(
				{
					"doctype": "Contribution Category",
					"module_name": "Document Generation",
					"contribution_type": "Invalid JSON Test",
					"required_fields": "invalid json {",
					"is_active": 1,
				}
			)
			category.insert(ignore_permissions=True)

		# Test valid JSON
		category = frappe.get_doc(
			{
				"doctype": "Contribution Category",
				"module_name": "Document Generation",
				"contribution_type": "Valid JSON Test",
				"required_fields": json.dumps(["field1", "field2"]),
				"is_active": 1,
			}
		)
		category.insert(ignore_permissions=True)

		self.assertEqual(len(category.get_required_fields_list()), 2)

	def test_contribution_data_validation(self):
		"""Test validation of contribution data against category requirements."""
		category = frappe.get_doc(
			{
				"doctype": "Contribution Category",
				"module_name": "Document Generation",
				"contribution_type": "Validation Test",
				"required_fields": json.dumps(["template_code", "template_name", "infrastructure_type"]),
				"is_active": 1,
			}
		)
		category.insert(ignore_permissions=True)

		# Test valid data
		valid_data = {
			"template_code": "TEST_TEMPLATE",
			"template_name": "Template de Prueba",
			"infrastructure_type": "Amenity",
		}

		try:
			category.validate_contribution_data(valid_data)
		except frappe.ValidationError:
			self.fail("Valid data should not raise ValidationError")

		# Test invalid data (missing required field)
		invalid_data = {
			"template_code": "TEST_TEMPLATE",
			"template_name": "Template de Prueba",
			# Missing infrastructure_type
		}

		with self.assertRaises(frappe.ValidationError):
			category.validate_contribution_data(invalid_data)

	def test_module_handler_path(self):
		"""Test that module handler paths are correctly mapped."""
		category = frappe.get_doc(
			{
				"doctype": "Contribution Category",
				"module_name": "Document Generation",
				"contribution_type": "Handler Test",
				"is_active": 1,
			}
		)
		category.insert(ignore_permissions=True)

		handler_path = category.get_module_handler_path()
		expected_path = "condominium_management.document_generation.contrib.handler"
		self.assertEqual(handler_path, expected_path)

		# Test unknown module
		category.module_name = "Unknown Module"
		handler_path = category.get_module_handler_path()
		self.assertIsNone(handler_path)

	def tearDown(self):
		"""Clean up after each test method."""
		frappe.set_user("Administrator")
