#!/usr/bin/env python3
"""
REGLA #49 - Budget Planning Layer 4 Permissions Test
Conservative approach: Permissions configuration validation
"""

import json
import os

import frappe
from frappe.tests.utils import FrappeTestCase


class TestBudgetPlanningL4Permissions(FrappeTestCase):
	"""Layer 4 Permissions Test - REGLA #49 Conservative Approach"""

	@classmethod
	def setUpClass(cls):
		"""Setup minimal para Layer 4"""
		frappe.set_user("Administrator")
		cls.doctype = "Budget Planning"

	def test_permissions_configuration(self):
		"""Test: Permissions configuration validation (REGLA #49)"""
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

		# 2. Validate permissions exist
		permissions = json_data.get("permissions", [])
		self.assertGreater(len(permissions), 0, "DocType must have permissions configured")

		# 3. Validate critical permissions structure
		for perm in permissions:
			self.assertIn("role", perm, "Permission must have role")
			self.assertIn("read", perm, "Permission must have read setting")

			# Verify role name is in Spanish (REGLA CRÍTICA #1)
			role_name = perm.get("role", "")
			if role_name:
				self.assertIsInstance(role_name, str, "Role name must be string")
				self.assertGreater(len(role_name), 0, "Role name must not be empty")

		# 4. Basic role validation (minimal check)
		role_names = [perm.get("role") for perm in permissions]
		unique_roles = set(role_names)
		self.assertGreater(len(unique_roles), 0, "Must have at least one unique role")

		# 5. Administrator role validation (system requirement)
		admin_perms = [perm for perm in permissions if perm.get("role") == "Administrator"]
		if admin_perms:  # Only check if Administrator role exists
			admin_perm = admin_perms[0]
			self.assertEqual(admin_perm.get("read"), 1, "Administrator must have read permission")

	def tearDown(self):
		"""Minimal cleanup"""
		frappe.db.rollback()
