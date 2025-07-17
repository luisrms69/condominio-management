#!/usr/bin/env python3

import frappe

frappe.init(site="admin1.dev")
frappe.connect()


def create_test_companies():
	"""Crear companies de test necesarias para Financial Management tests"""

	companies_to_create = [
		{
			"company_name": "TEST_FINANCIAL_COMPANY",
			"abbr": "TFC",
			"default_currency": "MXN",
			"country": "Mexico",
		},
		{"company_name": "_Test Company", "abbr": "_TC", "default_currency": "MXN", "country": "Mexico"},
		{
			"company_name": "Condominio Test Financiero",
			"abbr": "CTF",
			"default_currency": "MXN",
			"country": "Mexico",
		},
	]

	frappe.set_user("Administrator")

	for company_data in companies_to_create:
		company_name = company_data["company_name"]

		if not frappe.db.exists("Company", company_name):
			try:
				print(f"Creando Company: {company_name}")
				company = frappe.get_doc({"doctype": "Company", **company_data})
				company.insert(ignore_permissions=True)
				frappe.db.commit()
				print(f"✅ Company {company_name} creada exitosamente")
			except Exception as e:
				print(f"❌ Error creando {company_name}: {e!s}")
		else:
			print(f"✅ Company {company_name} ya existe")


if __name__ == "__main__":
	create_test_companies()
	print("🎯 Setup de test companies completado")
