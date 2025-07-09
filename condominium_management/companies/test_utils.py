# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe


def create_test_company_with_default_fallback(company_name, abbr=None, currency="MXN", country="Mexico"):
	"""
	Crear empresa de prueba con fallback para el error 'Test Company Default'
	"""
	if not abbr:
		abbr = "".join([word[0].upper() for word in company_name.split()[:3]])

	if frappe.db.exists("Company", company_name):
		return frappe.get_doc("Company", company_name)

	# Crear empresa dummy 'Test Company Default' si no existe (fix para ERPNext)
	if not frappe.db.exists("Company", "Test Company Default"):
		try:
			dummy_company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "Test Company Default",
					"abbr": "TCD",
					"default_currency": "USD",
					"country": "United States",
				}
			)
			dummy_company.insert(ignore_permissions=True)
		except Exception:
			pass

	# Crear la empresa solicitada
	company = frappe.get_doc(
		{
			"doctype": "Company",
			"company_name": company_name,
			"abbr": abbr,
			"default_currency": currency,
			"country": country,
		}
	)

	try:
		company.insert(ignore_permissions=True)
		return company
	except Exception as e:
		# Si falla, crear empresa más básica
		if "Row #11: Company: Test Company Default" in str(e):
			basic_company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": company_name,
					"abbr": abbr,
					"default_currency": "USD",
					"country": "United States",
				}
			)
			basic_company.insert(ignore_permissions=True)
			return basic_company
		else:
			raise e


def ensure_custom_fields_exist():
	"""
	Asegurar que los custom fields existen para testing
	"""
	custom_fields = [
		{
			"dt": "Company",
			"fieldname": "company_type",
			"label": "Company Type",
			"fieldtype": "Link",
			"options": "Company Type",
			"insert_after": "company_name",
		},
		{
			"dt": "Company",
			"fieldname": "property_usage_type",
			"label": "Property Usage Type",
			"fieldtype": "Link",
			"options": "Property Usage Type",
			"insert_after": "company_type",
		},
		{
			"dt": "Company",
			"fieldname": "total_units",
			"label": "Total Units",
			"fieldtype": "Int",
			"insert_after": "property_usage_type",
		},
		{
			"dt": "Company",
			"fieldname": "total_area_sqm",
			"label": "Total Area (sqm)",
			"fieldtype": "Float",
			"insert_after": "total_units",
		},
		{
			"dt": "Company",
			"fieldname": "construction_year",
			"label": "Construction Year",
			"fieldtype": "Int",
			"insert_after": "total_area_sqm",
		},
		{
			"dt": "Company",
			"fieldname": "floors_count",
			"label": "Floors Count",
			"fieldtype": "Int",
			"insert_after": "construction_year",
		},
		{
			"dt": "Company",
			"fieldname": "management_company",
			"label": "Management Company",
			"fieldtype": "Link",
			"options": "Company",
			"insert_after": "floors_count",
		},
		{
			"dt": "Company",
			"fieldname": "monthly_admin_fee",
			"label": "Monthly Admin Fee",
			"fieldtype": "Currency",
			"insert_after": "management_company",
		},
		{
			"dt": "Company",
			"fieldname": "reserve_fund",
			"label": "Reserve Fund",
			"fieldtype": "Currency",
			"insert_after": "monthly_admin_fee",
		},
		{
			"dt": "Company",
			"fieldname": "legal_representative_id",
			"label": "Legal Representative ID",
			"fieldtype": "Data",
			"insert_after": "reserve_fund",
		},
		{
			"dt": "Company",
			"fieldname": "insurance_expiry_date",
			"label": "Insurance Expiry Date",
			"fieldtype": "Date",
			"insert_after": "legal_representative_id",
		},
		{
			"dt": "Company",
			"fieldname": "management_start_date",
			"label": "Management Start Date",
			"fieldtype": "Date",
			"insert_after": "insurance_expiry_date",
		},
		{
			"dt": "Company",
			"fieldname": "management_contract_end_date",
			"label": "Management Contract End Date",
			"fieldtype": "Date",
			"insert_after": "management_start_date",
		},
	]

	for field in custom_fields:
		if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
			try:
				custom_field = frappe.get_doc({"doctype": "Custom Field", **field})
				custom_field.insert(ignore_permissions=True)
			except Exception:
				pass

	frappe.db.commit()
	frappe.clear_cache()
