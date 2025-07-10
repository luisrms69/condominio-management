#!/usr/bin/env python3

import frappe

from condominium_management.companies.install import install_company_customizations

if __name__ == "__main__":
	frappe.init(site="admin1.dev")
	frappe.connect()

	try:
		install_company_customizations()
		print("✅ Company customizations installed successfully")
	except Exception as e:
		print(f"❌ Error: {e}")
		import traceback

		traceback.print_exc()
