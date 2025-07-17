import frappe


def create_test_companies():
	"""Crear companies de test necesarias"""

	companies_to_create = [
		{
			"company_name": "TEST_FINANCIAL_COMPANY",
			"abbr": "TFC",
			"default_currency": "MXN",
			"country": "Mexico",
		},
		{"company_name": "_Test Company", "abbr": "_TC", "default_currency": "MXN", "country": "Mexico"},
	]

	for company_data in companies_to_create:
		company_name = company_data["company_name"]

		if not frappe.db.exists("Company", company_name):
			try:
				company = frappe.get_doc({"doctype": "Company", **company_data})
				company.insert(ignore_permissions=True)
				print(f"✅ Company {company_name} creada")
			except Exception as e:
				print(f"❌ Error: {e!s}")
		else:
			print(f"✅ Company {company_name} ya existe")


create_test_companies()
frappe.db.commit()
