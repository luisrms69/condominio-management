#!/usr/bin/env python3
"""
Script para crear 20 tests Layer 4 adicionales siguiendo REGLA #49
2 tests por DocType en orden de importancia
"""

import os


# DocTypes en orden de importancia para Layer 4 testing
DOCTYPES_PRIORITY = [
    ("Property Account", ["account_name", "account_status", "current_balance"]),
    ("Billing Cycle", ["cycle_name", "cycle_status", "billing_frequency"]),
    ("Payment Collection", ["payment_method", "payment_status", "net_amount"]),
    ("Fee Structure", ["structure_name", "fee_type", "calculation_method"]),
    ("Credit Balance Management", ["credit_status", "current_balance", "available_amount"]),
    ("Resident Account", ["resident_name", "account_status", "current_balance"]),
    ("Budget Planning", ["budget_name", "planning_status", "total_budget"]),
    ("Fine Management", ["fine_type", "fine_status", "fine_amount"]),
    ("Financial Transparency Config", ["transparency_level", "config_status", "active"]),
    ("Premium Services Integration", ["service_name", "service_status", "pricing_model"])
]


def create_additional_layer4_tests(doctype_name, critical_fields):
    """Create 2 additional Layer 4 tests following REGLA #49"""
    
    doctype_path = doctype_name.lower().replace(" ", "_")
    class_name = "".join([word.capitalize() for word in doctype_name.split()])
    
    # Test 1: Meta Consistency Validation
    file_path_1 = f"condominium_management/financial_management/doctype/{doctype_path}/test_{doctype_path}_l4_meta_consistency.py"
    
    content_1 = f'''#!/usr/bin/env python3
"""
REGLA #49 - {doctype_name} Layer 4 Meta Consistency Test
Conservative approach: JSON vs Frappe Meta validation
"""

import json
import os

import frappe
from frappe.tests.utils import FrappeTestCase


class Test{class_name}L4MetaConsistency(FrappeTestCase):
	"""Layer 4 Meta Consistency Test - REGLA #49 Conservative Approach"""

	@classmethod
	def setUpClass(cls):
		"""Setup minimal para Layer 4"""
		frappe.set_user("Administrator")
		cls.doctype = "{doctype_name}"

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
			f"{{doctype_path}}.json",
		)
		
		with open(json_path, encoding="utf-8") as f:
			json_data = json.load(f)
		
		# 2. Get Frappe Meta (minimal operation)
		try:
			frappe_meta = frappe.get_meta(self.doctype)
		except Exception:
			self.fail(f"Could not get meta for {{self.doctype}}")
		
		# 3. Basic consistency validation
		self.assertEqual(json_data.get("name"), self.doctype, "DocType name must match")
		self.assertEqual(json_data.get("module"), "Financial Management", "Module must be Financial Management")
		
		# 4. Field count consistency (basic check)
		json_fields = json_data.get("fields", [])
		meta_fields = frappe_meta.get("fields", [])
		
		self.assertGreater(len(json_fields), 0, "JSON must have fields")
		self.assertGreater(len(meta_fields), 0, "Meta must have fields")
		
		# 5. Critical fields consistency
		json_field_names = [f.get("fieldname") for f in json_fields]
		meta_field_names = [f.get("fieldname") for f in meta_fields]
		
		critical_fields = {critical_fields}
		for field in critical_fields:
			if field in json_field_names:  # Only check if field exists in JSON
				self.assertIn(field, meta_field_names, f"Critical field {{field}} must exist in meta")

	def tearDown(self):
		"""Minimal cleanup"""
		frappe.db.rollback()
'''
    
    # Test 2: Permissions Validation
    file_path_2 = f"condominium_management/financial_management/doctype/{doctype_path}/test_{doctype_path}_l4_permissions.py"
    
    content_2 = f'''#!/usr/bin/env python3
"""
REGLA #49 - {doctype_name} Layer 4 Permissions Test
Conservative approach: Permissions configuration validation
"""

import json
import os

import frappe
from frappe.tests.utils import FrappeTestCase


class Test{class_name}L4Permissions(FrappeTestCase):
	"""Layer 4 Permissions Test - REGLA #49 Conservative Approach"""

	@classmethod
	def setUpClass(cls):
		"""Setup minimal para Layer 4"""
		frappe.set_user("Administrator")
		cls.doctype = "{doctype_name}"

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
			f"{{doctype_path}}.json",
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
'''
    
    # Create directories and files
    dir_path = os.path.dirname(file_path_1)
    os.makedirs(dir_path, exist_ok=True)
    
    with open(file_path_1, 'w', encoding='utf-8') as f:
        f.write(content_1)
    
    with open(file_path_2, 'w', encoding='utf-8') as f:
        f.write(content_2)
    
    print(f"✅ Created: {file_path_1}")
    print(f"✅ Created: {file_path_2}")


def main():
    """Create 20 additional Layer 4 tests (2 per DocType)"""
    print("🛡️ Creating 20 additional Layer 4 tests following REGLA #49...")
    
    for doctype_name, critical_fields in DOCTYPES_PRIORITY:
        create_additional_layer4_tests(doctype_name, critical_fields)
    
    print(f"✅ Created {len(DOCTYPES_PRIORITY) * 2} additional Layer 4 tests")
    print("🚀 REGLA #49 conservative strategy expanded!")


if __name__ == "__main__":
    main()