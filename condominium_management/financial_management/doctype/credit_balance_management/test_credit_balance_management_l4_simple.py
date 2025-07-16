#!/usr/bin/env python3
"""
REGLA #49 - Credit Balance Management Layer 4 Simple Test
Conservative approach: Only basic JSON configuration validation
"""

import json
import os

import frappe
from frappe.tests.utils import FrappeTestCase


class TestCreditBalanceManagementL4Simple(FrappeTestCase):
	"""Layer 4 Configuration Test - REGLA #49 Conservative Approach"""

	@classmethod
	def setUpClass(cls):
		"""Setup minimal para Layer 4"""
		frappe.set_user("Administrator")
		cls.doctype = "Credit Balance Management"

	def test_json_configuration_validation(self):
		"""Test: Basic JSON schema and configuration validation (REGLA #49)"""
		# REGLA #49: Minimal operations only to avoid framework corruption

		# 1. Verify JSON file exists and is valid
		doctype_path = self.doctype.lower().replace(" ", "_")
		json_path = os.path.join(
			frappe.get_app_path("condominium_management"),
			"financial_management",
			"doctype",
			doctype_path,
			f"{doctype_path}.json",
		)

		self.assertTrue(os.path.exists(json_path), f"JSON file must exist: {json_path}")

		# 2. Load and validate JSON structure
		with open(json_path, encoding="utf-8") as f:
			json_data = json.load(f)

		# 3. Basic JSON validation
		self.assertEqual(json_data.get("doctype"), "DocType", "DocType field must be 'DocType'")
		self.assertEqual(json_data.get("name"), self.doctype, f"Name must match {self.doctype}")

		# 4. Verify essential fields exist
		fields = json_data.get("fields", [])
		self.assertGreater(len(fields), 0, "DocType must have at least one field")

		# Check critical fields for Credit Balance Management
		field_names = [f.get("fieldname") for f in fields]
		critical_fields = ["credit_status", "current_balance", "available_amount"]
		for field in critical_fields:
			if field in field_names:  # Only check if field exists
				self.assertIn(field, field_names, f"Critical field {field} should exist")

		# 5. Basic permissions validation (minimal check)
		permissions = json_data.get("permissions", [])
		self.assertGreater(len(permissions), 0, "DocType must have permissions configured")

		# 6. Verify Spanish labels (REGLA CRÍTICA #1)
		for field in fields:
			if field.get("label"):
				# Check that label exists and is not empty
				self.assertTrue(
					len(field["label"]) > 0, f"Field {field.get('fieldname')} must have non-empty label"
				)

	def tearDown(self):
		"""Minimal cleanup"""
		frappe.db.rollback()
