# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase


class TestMasterDataSyncConfiguration(FrappeTestCase):
	"""Test cases for Master Data Sync Configuration DocType."""

	def setUp(self):
		"""Set up test data."""
		# Create test companies if they don't exist
		for company_name, abbr in [("Test Source", "TS"), ("Test Target", "TT")]:
			if not frappe.db.exists("Company", company_name):
				company = frappe.get_doc(
					{
						"doctype": "Company",
						"company_name": company_name,
						"abbr": abbr,
						"default_currency": "MXN",
						"country": "Mexico",
					}
				)
				company.insert(ignore_permissions=True)

	def test_sync_configuration_creation(self):
		"""Test basic creation of Master Data Sync Configuration."""
		doc = frappe.get_doc(
			{
				"doctype": "Master Data Sync Configuration",
				"sync_name": "Test Sync",
				"source_company": "Test Source",
				"sync_frequency": "Diario",
				"target_companies": [{"target_company": "Test Target", "sync_enabled": 1}],
				"data_types": [{"data_type": "Proveedor", "sync_enabled": 1}],
			}
		)
		doc.insert(ignore_permissions=True)
		self.assertEqual(doc.sync_name, "Test Sync")

	def test_source_target_validation(self):
		"""Test that source company cannot be same as target."""
		doc = frappe.get_doc(
			{
				"doctype": "Master Data Sync Configuration",
				"sync_name": "Invalid Sync",
				"source_company": "Test Source",
				"target_companies": [
					{
						"target_company": "Test Source",  # Same as source
						"sync_enabled": 1,
					}
				],
				"data_types": [{"data_type": "Proveedor", "sync_enabled": 1}],
			}
		)
		with self.assertRaises(frappe.ValidationError):
			doc.insert(ignore_permissions=True)

	def tearDown(self):
		"""Clean up test data."""
		frappe.db.rollback()
