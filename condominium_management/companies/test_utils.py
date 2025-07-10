# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe


def ensure_test_fixtures_exist():
	"""
	Asegurar que los fixtures base existen para testing
	"""
	# Crear Company Types si no existen
	company_types = [
		{"type_name": "Administradora", "type_code": "ADMIN", "is_management_type": 1},
		{"type_name": "Condominio", "type_code": "CONDO", "is_management_type": 0},
		{"type_name": "Proveedor", "type_code": "PROV", "is_management_type": 0},
	]

	for company_type_data in company_types:
		# Verificar usando type_name ya que los fixtures están inconsistentes
		if not frappe.db.exists("Company Type", {"type_name": company_type_data["type_name"]}):
			try:
				company_type = frappe.get_doc(
					{"doctype": "Company Type", "name": company_type_data["type_name"], **company_type_data}
				)
				company_type.insert(ignore_permissions=True)
			except frappe.DuplicateEntryError:
				pass

	# Crear Property Usage Types básicos
	usage_types = ["Residencial", "Comercial", "Mixto"]
	for usage_name in usage_types:
		if not frappe.db.exists("Property Usage Type", {"usage_name": usage_name}):
			try:
				usage_type = frappe.get_doc(
					{"doctype": "Property Usage Type", "name": usage_name, "usage_name": usage_name}
				)
				usage_type.insert(ignore_permissions=True)
			except frappe.DuplicateEntryError:
				pass


def create_test_company_with_default_fallback(company_name, abbr=None, currency="MXN", country="Mexico"):
	"""
	Crear empresa de prueba con fallback para el error 'Test Company Default'
	"""
	if not abbr:
		abbr = "".join([word[0].upper() for word in company_name.split()[:3]])

	if frappe.db.exists("Company", company_name):
		return frappe.get_doc("Company", company_name)

	# Asegurar que los fixtures existen
	ensure_test_fixtures_exist()

	# Crear empresas dummy requeridas por ERPNext (fix para LinkValidationError)
	dummy_companies = [
		{"company_name": "Test Company Default", "abbr": "TCD"},
		{"company_name": "Test Condominium", "abbr": "TCS"},
		{"company_name": "Test Administration", "abbr": "TAS"},
		{"company_name": "Test Administradora XYZ", "abbr": "TAX"},
		{"company_name": "Test Company Invalid", "abbr": "TCI"},
		{"company_name": "Test Condominio Residencial", "abbr": "TCR"},
		{"company_name": "Test Invalid Units", "abbr": "TIU"},
		{"company_name": "Test Invalid Year", "abbr": "TIY"},
		{"company_name": "Test Administradora ABC", "abbr": "TAA"},
		{"company_name": "Test Condominio Administrado", "abbr": "TCA"},
		{"company_name": "Test Invalid ID", "abbr": "TII"},
		{"company_name": "Test Invalid Fee", "abbr": "TIF"},
	]

	for dummy_data in dummy_companies:
		if not frappe.db.exists("Company", dummy_data["company_name"]):
			try:
				# Generar abreviación única para dummy companies también
				unique_abbr = dummy_data["abbr"]
				counter = 1
				while frappe.db.exists("Company", {"abbr": unique_abbr}):
					unique_abbr = f"{dummy_data['abbr']}{counter}"
					counter += 1

				dummy_company = frappe.get_doc(
					{
						"doctype": "Company",
						"company_name": dummy_data["company_name"],
						"abbr": unique_abbr,
						"default_currency": "USD",
						"country": "United States",
					}
				)
				dummy_company.insert(ignore_permissions=True)
			except Exception:
				pass

	# CRÍTICO: Generar abreviación única ANTES de crear el objeto Company
	# Esto evita la validación de ERPNext que ocurre en validate()
	original_abbr = abbr
	counter = 1
	while frappe.db.exists("Company", {"abbr": abbr}):
		abbr = f"{original_abbr}{counter}"
		counter += 1

	# Crear la empresa solicitada CON abreviación ya única
	company = frappe.get_doc(
		{
			"doctype": "Company",
			"company_name": company_name,
			"abbr": abbr,  # Esta abreviación ya es única
			"default_currency": currency,
			"country": country,
		}
	)

	# Agregar company_type si el campo existe (para evitar ValidationError)
	if hasattr(company, "company_type"):
		# Buscar el tipo correcto usando type_name
		admin_type = frappe.db.get_value("Company Type", {"type_name": "Administradora"}, "name")
		if admin_type:
			company.company_type = admin_type
		else:
			# Fallback: usar el código si no se encuentra el nombre
			company.company_type = "ADMIN"

	try:
		company.insert(ignore_permissions=True)
		return company
	except frappe.DuplicateEntryError:
		# Si ya existe, simplemente devolver la existente
		return frappe.get_doc("Company", company_name)
	except Exception as e:
		# Si falla, crear empresa más básica
		if "Row #11: Company: Test Company Default" in str(e):
			# Generar nueva abreviación única para fallback (ya debería ser única, pero doble verificación)
			fallback_abbr = abbr
			counter = 10  # Start with higher number to avoid conflicts
			while frappe.db.exists("Company", {"abbr": fallback_abbr}):
				fallback_abbr = f"{original_abbr}{counter}"
				counter += 1

			basic_company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": company_name,
					"abbr": fallback_abbr,
					"default_currency": "USD",
					"country": "United States",
				}
			)
			try:
				basic_company.insert(ignore_permissions=True)
				return basic_company
			except frappe.DuplicateEntryError:
				return frappe.get_doc("Company", company_name)
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
		{
			"dt": "Company",
			"fieldname": "managed_properties",
			"label": "Managed Properties",
			"fieldtype": "Int",
			"insert_after": "management_contract_end_date",
			"read_only": 1,
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
