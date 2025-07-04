# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEntityTypeConfiguration(FrappeTestCase):
	"""Test cases for Entity Type Configuration."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()
		cls.create_test_data()

	@classmethod
	def create_test_data(cls):
		"""Create reusable test data with flags to avoid duplication."""
		if getattr(frappe.flags, "test_entity_type_config_data_created", False):
			return

		# No additional test data needed for this DocType
		frappe.flags.test_entity_type_config_data_created = True

	def setUp(self):
		"""Set up before each test method."""
		frappe.set_user("Administrator")

	def test_creation(self):
		"""Test basic creation with Spanish validations."""
		config = frappe.get_doc(
			{
				"doctype": "Entity Type Configuration",
				"entity_doctype": "Company",  # Use existing DocType
				"entity_name": "Empresa",  # MANDATORY
				"entity_name_plural": "Empresas",  # MANDATORY
				"owning_module": "Document Generation",  # MANDATORY
				"entity_description": "Configuración de entidad de prueba",
				"requires_configuration": 1,
				"auto_detect_on_create": 1,
				"priority": 5,
				"is_active": 1,
				"applies_to_manual": 1,
			}
		)
		config.insert(ignore_permissions=True)

		self.assertEqual(config.entity_doctype, "Company")
		self.assertTrue(config.requires_configuration)
		self.assertTrue(config.auto_detect_on_create)

	def test_spanish_labels(self):
		"""Test that DocType has proper Spanish labels."""
		meta = frappe.get_meta("Entity Type Configuration")
		self.assertEqual(meta.get("label"), "Configuración de Tipo de Entidad")

	def test_required_fields_validation(self):
		"""Test required fields validation."""
		with self.assertRaises(frappe.ValidationError):
			config = frappe.get_doc(
				{"doctype": "Entity Type Configuration", "entity_description": "Missing entity_doctype"}
			)
			config.insert(ignore_permissions=True)

	def test_priority_validation(self):
		"""Test priority field validation."""
		config = frappe.get_doc(
			{
				"doctype": "Entity Type Configuration",
				"entity_doctype": "Customer",  # Use existing DocType
				"entity_name": "Cliente",  # MANDATORY
				"entity_name_plural": "Clientes",  # MANDATORY
				"owning_module": "Document Generation",  # MANDATORY
				"entity_description": "Testing priority validation",
				"requires_configuration": 1,
				"priority": 10,  # Should be valid (1-10 range)
				"is_active": 1,
				"applies_to_manual": 1,
			}
		)
		config.insert(ignore_permissions=True)

		self.assertEqual(config.priority, 10)

	def test_auto_detection_flags(self):
		"""Test auto-detection configuration flags."""
		config = frappe.get_doc(
			{
				"doctype": "Entity Type Configuration",
				"entity_doctype": "Item",  # Use existing DocType
				"entity_name": "Artículo",  # MANDATORY
				"entity_name_plural": "Artículos",  # MANDATORY
				"owning_module": "Document Generation",  # MANDATORY
				"entity_description": "Testing auto-detection flags",
				"requires_configuration": 1,
				"auto_detect_on_create": 1,
				"auto_detect_on_update": 0,
				"is_active": 1,
				"applies_to_manual": 1,
			}
		)
		config.insert(ignore_permissions=True)

		self.assertTrue(config.auto_detect_on_create)
		self.assertFalse(config.auto_detect_on_update)

	def tearDown(self):
		"""Clean up after each test method."""
		frappe.set_user("Administrator")
