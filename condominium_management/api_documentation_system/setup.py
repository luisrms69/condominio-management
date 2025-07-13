# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Setup functions for API Documentation System
"""

import frappe


def setup_roles():
	"""Create required roles for API Documentation System"""

	roles_to_create = [
		{
			"role_name": "API Manager",
			"desk_access": 1,
			"home_page": "api-documentation",
			"permissions": ["create", "read", "write", "delete", "export", "import"],
		},
		{"role_name": "API User", "desk_access": 1, "permissions": ["read", "export"]},
	]

	for role_data in roles_to_create:
		if not frappe.db.exists("Role", role_data["role_name"]):
			role = frappe.new_doc("Role")
			role.role_name = role_data["role_name"]
			role.desk_access = role_data.get("desk_access", 0)
			role.home_page = role_data.get("home_page", "")
			role.insert()
			frappe.db.commit()
			print(f"Created role: {role_data['role_name']}")
		else:
			print(f"Role already exists: {role_data['role_name']}")


@frappe.whitelist()
def install_api_documentation_system():
	"""
	Install and setup API Documentation System

	TODO: PHASE2: SETUP - Auto-scan existing APIs on install
	TODO: PHASE2: SETUP - Create default collections
	"""
	try:
		# Setup roles
		setup_roles()

		# TODO: PHASE2: AUTO-SCAN - Scan existing APIs
		# scan_and_register_existing_apis()

		# TODO: PHASE2: COLLECTIONS - Create default collections
		# create_default_collections()

		frappe.msgprint("API Documentation System installed successfully!")
		return {"status": "success", "message": "Installation completed"}

	except Exception as e:
		frappe.throw(f"Error installing API Documentation System: {e!s}")


def scan_and_register_existing_apis():
	"""
	Scan codebase for existing @frappe.whitelist() APIs

	TODO: PHASE2: SCANNER - Implement full code scanner
	"""
	pass


def create_default_collections():
	"""
	Create default API collections for existing modules

	TODO: PHASE2: COLLECTIONS - Implement API Collection DocType first
	"""
	pass
