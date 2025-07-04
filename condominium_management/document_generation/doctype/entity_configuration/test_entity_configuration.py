# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEntityConfiguration(FrappeTestCase):
	"""Test cases for Entity Configuration."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()
		cls.create_test_data()

	@classmethod
	def create_test_data(cls):
		"""Create reusable test data with flags to avoid duplication."""
		if getattr(frappe.flags, "test_entity_config_data_created", False):
			return

		# Create test entity type configuration
		if not frappe.db.exists("Entity Type Configuration", {"entity_doctype": "User"}):
			test_entity_type = frappe.get_doc(
				{
					"doctype": "Entity Type Configuration",
					"entity_doctype": "User",  # Use existing DocType
					"entity_name": "Usuario",  # MANDATORY
					"entity_name_plural": "Usuarios",  # MANDATORY
					"owning_module": "Document Generation",  # MANDATORY
					"entity_description": "Configuración de prueba",
					"requires_configuration": 1,
					"is_active": 1,
					"applies_to_manual": 1,
				}
			)
			test_entity_type.insert(ignore_permissions=True)

		frappe.flags.test_entity_config_data_created = True

	def setUp(self):
		"""Set up before each test method."""
		frappe.set_user("Administrator")

	def test_creation(self):
		"""Test basic creation with Spanish validations."""
		config = frappe.get_doc(
			{
				"doctype": "Entity Configuration",
				"entity_reference": "TEST-001",
				"entity_type": "Test Entity Config",
				"template_code": "TEST_TEMPLATE",
				"configuration_name": "Configuración de Prueba",
				"approval_status": "Borrador",
			}
		)
		config.insert(ignore_permissions=True)

		self.assertEqual(config.entity_reference, "TEST-001")
		self.assertEqual(config.approval_status, "Borrador")
		self.assertEqual(config.template_code, "TEST_TEMPLATE")

	def test_spanish_labels(self):
		"""Test that DocType has proper Spanish labels."""
		meta = frappe.get_meta("Entity Configuration")
		self.assertEqual(meta.get("label"), "Configuración de Entidad")

	def test_required_fields_validation(self):
		"""Test required fields validation."""
		with self.assertRaises(frappe.ValidationError):
			config = frappe.get_doc(
				{"doctype": "Entity Configuration", "configuration_name": "Missing required fields"}
			)
			config.insert(ignore_permissions=True)

	def test_spanish_options(self):
		"""Test that Select field options are in Spanish."""
		meta = frappe.get_meta("Entity Configuration")
		status_field = meta.get_field("approval_status")

		# Verify Spanish status options
		spanish_statuses = ["Borrador", "Pendiente Aprobación", "Aprobado", "Rechazado"]
		options = status_field.options.split("\n")

		for status in spanish_statuses:
			self.assertIn(status, options)

	def test_status_transition_validation(self):
		"""Test status transition validation."""
		config = frappe.get_doc(
			{
				"doctype": "Entity Configuration",
				"entity_reference": "TRANSITION-001",
				"entity_type": "Test Entity Config",
				"template_code": "TRANSITION_TEST",
				"configuration_name": "Test de Transiciones",
				"approval_status": "Borrador",
			}
		)
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
		config = frappe.get_doc(
			{
				"doctype": "Entity Configuration",
				"entity_reference": "FIELDS-001",
				"entity_type": "Test Entity Config",
				"template_code": "FIELDS_TEST",
				"configuration_name": "Test de Campos",
				"approval_status": "Borrador",
			}
		)

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
