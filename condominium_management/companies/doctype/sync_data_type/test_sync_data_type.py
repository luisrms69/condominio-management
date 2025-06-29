# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase


class TestSyncDataType(FrappeTestCase):
	"""Test cases for Sync Data Type DocType."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()

	def setUp(self):
		"""Set up test data before each test method."""
		frappe.set_user("Administrator")
		self.test_data = {
			"data_type": "Proveedor",
			"sync_enabled": 1,
			"filter_conditions": "status = 'Active'",
			"last_sync_count": 0,
		}

	def test_sync_data_type_creation(self):
		"""Test basic creation of Sync Data Type."""
		# Create a new Sync Data Type
		sync_type = frappe.get_doc({"doctype": "Sync Data Type", **self.test_data})
		sync_type.insert()

		# Verify the document was created successfully
		self.assertTrue(sync_type.name)
		self.assertEqual(sync_type.data_type, "Proveedor")
		self.assertEqual(sync_type.sync_enabled, 1)
		self.assertEqual(sync_type.filter_conditions, "status = 'Active'")

		# Clean up
		# FrappeTestCase will handle cleanup automatically via rollback

	def test_required_data_type_field(self):
		"""Test that data_type field is required."""
		with self.assertRaises(frappe.ValidationError):
			sync_type = frappe.get_doc({"doctype": "Sync Data Type", "sync_enabled": 1})
			sync_type.insert()

	def test_data_type_spanish_options(self):
		"""Test data type field accepts valid Spanish options."""
		valid_data_types = [
			"Proveedor",
			"Artículo",
			"Plantilla de Email",
			"Formato de Impresión",
			"Flujo de Trabajo",
			"Rol de Usuario",
			"Campo Personalizado",
		]

		for data_type in valid_data_types:
			sync_type = frappe.get_doc(
				{"doctype": "Sync Data Type", "data_type": data_type, "sync_enabled": 1}
			)
			sync_type.insert()
			self.assertEqual(sync_type.data_type, data_type)
			# FrappeTestCase will handle cleanup automatically via rollback

	def test_sync_enabled_default_value(self):
		"""Test that sync_enabled defaults to 1."""
		sync_type = frappe.get_doc({"doctype": "Sync Data Type", "data_type": "Proveedor"})
		sync_type.insert()

		# Should default to enabled
		self.assertEqual(sync_type.sync_enabled, 1)

		# FrappeTestCase will handle cleanup automatically via rollback

	def test_sync_count_validation(self):
		"""Test that last_sync_count field behavior."""
		sync_type = frappe.get_doc({"doctype": "Sync Data Type", "data_type": "Artículo", "sync_enabled": 1})
		sync_type.insert()

		# Check that field exists and starts at 0
		self.assertEqual(sync_type.last_sync_count, 0)

		# Verify field is read-only in meta
		meta = frappe.get_meta("Sync Data Type")
		sync_count_field = meta.get_field("last_sync_count")
		self.assertEqual(sync_count_field.read_only, 1)

		# FrappeTestCase will handle cleanup automatically via rollback

	def test_filter_conditions_optional(self):
		"""Test that filter_conditions field is optional."""
		# Test without filter conditions
		sync_type = frappe.get_doc({"doctype": "Sync Data Type", "data_type": "Proveedor", "sync_enabled": 1})
		sync_type.insert()
		self.assertTrue(sync_type.name)
		# FrappeTestCase will handle cleanup automatically via rollback

		# Test with filter conditions
		sync_type = frappe.get_doc(
			{
				"doctype": "Sync Data Type",
				"data_type": "Artículo",
				"sync_enabled": 1,
				"filter_conditions": "disabled = 0",
			}
		)
		sync_type.insert()
		self.assertEqual(sync_type.filter_conditions, "disabled = 0")
		# FrappeTestCase will handle cleanup automatically via rollback

	def test_sync_enabled_toggle(self):
		"""Test enabling and disabling sync."""
		sync_type = frappe.get_doc(
			{"doctype": "Sync Data Type", "data_type": "Plantilla de Email", "sync_enabled": 1}
		)
		sync_type.insert()

		# Test disabling sync
		sync_type.sync_enabled = 0
		sync_type.save()
		self.assertEqual(sync_type.sync_enabled, 0)

		# Test re-enabling sync
		sync_type.sync_enabled = 1
		sync_type.save()
		self.assertEqual(sync_type.sync_enabled, 1)

		# FrappeTestCase will handle cleanup automatically via rollback

	def test_spanish_labels(self):
		"""Test that DocType has proper Spanish labels."""
		meta = frappe.get_meta("Sync Data Type")

		# Check DocType label
		self.assertEqual(meta.label, "Tipo de Dato de Sincronización")

		# Check field labels
		data_type_field = meta.get_field("data_type")
		self.assertEqual(data_type_field.label, "Tipo de Dato")

		sync_enabled_field = meta.get_field("sync_enabled")
		self.assertEqual(sync_enabled_field.label, "Habilitado")

		filter_field = meta.get_field("filter_conditions")
		self.assertEqual(filter_field.label, "Condiciones de Filtro")

		sync_count_field = meta.get_field("last_sync_count")
		self.assertEqual(sync_count_field.label, "Registros Última Sync")

	def test_data_type_field_properties(self):
		"""Test data_type field has correct properties."""
		meta = frappe.get_meta("Sync Data Type")
		data_type_field = meta.get_field("data_type")

		# Should be required
		self.assertEqual(data_type_field.reqd, 1)

		# Should be in list view
		self.assertEqual(data_type_field.in_list_view, 1)

		# Should be Select type
		self.assertEqual(data_type_field.fieldtype, "Select")

		# Should have Spanish options
		expected_options = "Proveedor\nArtículo\nPlantilla de Email\nFormato de Impresión\nFlujo de Trabajo\nRol de Usuario\nCampo Personalizado"
		self.assertEqual(data_type_field.options, expected_options)

	def tearDown(self):
		"""Clean up test data after each test method."""
		frappe.set_user("Administrator")
		# FrappeTestCase automatically handles transaction rollback
