#!/usr/bin/env python3
"""
REGLA #49 - Budget Planning Layer 4 Meta Consistency Test
Conservative approach: JSON vs Frappe Meta validation
"""

import json
import os

import frappe
from frappe.tests.utils import FrappeTestCase


class TestBudgetPlanningL4MetaConsistency(FrappeTestCase):
	"""Layer 4 Meta Consistency Test - REGLA #49 Conservative Approach"""

	@classmethod
	def setUpClass(cls):
		"""Setup minimal para Layer 4"""
		frappe.set_user("Administrator")
		cls.doctype = "Budget Planning"

	def test_json_vs_meta_consistency(self):
		"""Test: JSON definition vs Frappe Meta consistency (REGLA #49)"""
		# REGLA #49: Minimal operations only to avoid framework corruption

		# 1. Load JSON definition
		doctype_path = self.doctype.lower().replace(" ", "_")
		json_path = os.path.join(
			frappe.get_app_path("condominium_management"),
			"financial_management",
			"doctype",
			doctype_path,
			f"{doctype_path}.json",
		)

		with open(json_path, encoding="utf-8") as f:
			json_data = json.load(f)

		# 2. Get Frappe Meta (minimal operation)
		try:
			frappe_meta = frappe.get_meta(self.doctype)
		except Exception:
			self.fail(f"Could not get meta for {self.doctype}")

		# 3. Basic consistency validation
		self.assertEqual(json_data.get("name"), self.doctype, "DocType name must match")
		self.assertEqual(
			json_data.get("module"), "Financial Management", "Module must be Financial Management"
		)

		# 4. Field count consistency (basic check)
		json_fields = json_data.get("fields", [])
		meta_fields = frappe_meta.get("fields", [])

		self.assertGreater(len(json_fields), 0, "JSON must have fields")
		self.assertGreater(len(meta_fields), 0, "Meta must have fields")

		# 5. Critical fields consistency
		json_field_names = [f.get("fieldname") for f in json_fields]
		meta_field_names = [f.get("fieldname") for f in meta_fields]

		critical_fields = ["budget_name", "planning_status", "total_budget"]
		for field in critical_fields:
			if field in json_field_names:  # Only check if field exists in JSON
				self.assertIn(field, meta_field_names, f"Critical field {field} must exist in meta")

	def tearDown(self):
		"""Minimal cleanup"""
		frappe.db.rollback()
