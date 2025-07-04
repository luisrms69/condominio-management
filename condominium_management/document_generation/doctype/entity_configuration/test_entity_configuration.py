# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from condominium_management.test_factories import TestDataFactory


class TestEntityConfiguration(FrappeTestCase):
	"""Test cases for Entity Configuration."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()
		cls.create_test_data()

	@classmethod
	def create_test_data(cls):
		"""Create reusable test data using TestDataFactory."""
		if getattr(frappe.flags, "test_entity_config_data_created", False):
			return

		# Use factory to setup complete test environment
		cls.test_objects = TestDataFactory.setup_complete_test_environment()

		frappe.flags.test_entity_config_data_created = True

	def setUp(self):
		"""Set up before each test method."""
		frappe.set_user("Administrator")

	def test_creation(self):
		"""Test basic creation with Spanish validations."""
		# Use factory to create complete entity configuration data
		config_data = TestDataFactory.create_entity_configuration_data()

		config = frappe.get_doc({"doctype": "Entity Configuration", **config_data})
		config.insert(ignore_permissions=True)

		self.assertIsNotNone(config.entity_reference)
		self.assertEqual(config.approval_status, "Borrador")
		self.assertIsNotNone(config.template_code)

	def test_spanish_labels(self):
		"""Test that DocType has proper Spanish labels."""
		meta = frappe.get_meta("Entity Configuration")
		self.assertEqual(meta.get("label"), "Configuración de Entidad")

	def test_required_fields_validation(self):
		"""Test required fields validation."""
		# Test missing required fields
		with self.assertRaises(frappe.ValidationError):
			config = frappe.get_doc(
				{
					"doctype": "Entity Configuration",
					"configuration_name": "Missing required fields",
					# Missing entity_reference, entity_type, template_code, etc.
				}
			)
			config.insert(ignore_permissions=True)

	def test_spanish_options(self):
		"""Test that Select field options are in Spanish."""
		meta = frappe.get_meta("Entity Configuration")
		status_field = meta.get_field("approval_status")

		# Check if field exists and has options
		if status_field and status_field.options:
			# Verify Spanish status options
			spanish_statuses = ["Borrador", "Pendiente Aprobación", "Aprobado", "Rechazado"]
			options = status_field.options.split("\n")

			for status in spanish_statuses:
				self.assertIn(status, options)
		else:
			self.skipTest("approval_status field not found or has no options")

	def test_status_transition_validation(self):
		"""Test status transition validation."""
		# Use factory for base data and customize
		config_data = TestDataFactory.create_entity_configuration_data()
		config_data["configuration_name"] = "Test de Transiciones"

		config = frappe.get_doc({"doctype": "Entity Configuration", **config_data})
		config.insert(ignore_permissions=True)

		# Test valid transition: Borrador → Pendiente Aprobación
		old_status = config.approval_status
		config.approval_status = "Pendiente Aprobación"
		config.validate_status_transition(old_status, config.approval_status)

		# This should not raise an exception
		config.save()
		self.assertEqual(config.approval_status, "Pendiente Aprobación")

	def test_configuration_fields_child_table(self):
		"""Test configuration fields child table functionality."""
		# Use factory for base data
		config_data = TestDataFactory.create_entity_configuration_data()
		config_data["configuration_name"] = "Test de Campos"

		config = frappe.get_doc({"doctype": "Entity Configuration", **config_data})

		# Add configuration fields using append method
		config.append(
			"configuration_fields",
			{
				"field_name": "test_capacity",
				"field_label": "Capacidad de Prueba",
				"field_type": "Int",
				"field_value": "50",
				"is_required": 1,
			},
		)

		config.append(
			"configuration_fields",
			{
				"field_name": "test_description",
				"field_label": "Descripción de Prueba",
				"field_type": "Text",
				"field_value": "Esta es una descripción de prueba",
				"is_required": 0,
			},
		)

		config.insert(ignore_permissions=True)

		self.assertEqual(len(config.configuration_fields), 2)
		self.assertEqual(config.configuration_fields[0].field_name, "test_capacity")
		self.assertEqual(config.configuration_fields[1].field_type, "Text")

	def tearDown(self):
		"""Clean up after each test method."""
		frappe.set_user("Administrator")
