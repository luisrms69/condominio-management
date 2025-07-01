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

	def test_required_data_type_field(self):
		"""Test that data_type field is required."""
		with self.assertRaises(frappe.ValidationError):
			sync_type = frappe.get_doc({"doctype": "Sync Data Type", "sync_enabled": 1})
			sync_type.insert()

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
