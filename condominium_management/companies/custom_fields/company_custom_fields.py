# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def create_company_custom_fields():
	"""Crear campos personalizados para Company DocType"""

	custom_fields = {
		"Company": [
			{
				"fieldname": "condominium_section",
				"label": "Información de Condominio",
				"fieldtype": "Section Break",
				"insert_after": "company_description",
				"depends_on": "eval: doc.company_type == 'Condominio'",
				"collapsible": 1,
			},
			{
				"fieldname": "company_type",
				"label": "Tipo de Empresa",
				"fieldtype": "Link",
				"options": "Company Type",
				"insert_after": "condominium_section",
				"reqd": 0,
			},
			{
				"fieldname": "property_usage_type",
				"label": "Tipo de Uso de Propiedad",
				"fieldtype": "Link",
				"options": "Property Usage Type",
				"insert_after": "company_type",
				"depends_on": "eval: doc.company_type == 'Condominio'",
			},
			{
				"fieldname": "acquisition_type",
				"label": "Tipo de Adquisición",
				"fieldtype": "Link",
				"options": "Acquisition Type",
				"insert_after": "property_usage_type",
				"depends_on": "eval: doc.company_type == 'Condominio'",
			},
			{
				"fieldname": "property_status_type",
				"label": "Estado de la Propiedad",
				"fieldtype": "Link",
				"options": "Property Status Type",
				"insert_after": "acquisition_type",
				"depends_on": "eval: doc.company_type == 'Condominio'",
			},
			{
				"fieldname": "cb_condominium_1",
				"fieldtype": "Column Break",
				"insert_after": "property_status_type",
			},
			{
				"fieldname": "total_units",
				"label": "Total de Unidades",
				"fieldtype": "Int",
				"insert_after": "cb_condominium_1",
				"depends_on": "eval: doc.company_type == 'Condominio'",
			},
			{
				"fieldname": "total_area_sqm",
				"label": "Área Total (m²)",
				"fieldtype": "Float",
				"insert_after": "total_units",
				"depends_on": "eval: doc.company_type == 'Condominio'",
			},
			{
				"fieldname": "construction_year",
				"label": "Año de Construcción",
				"fieldtype": "Int",
				"insert_after": "total_area_sqm",
				"depends_on": "eval: doc.company_type == 'Condominio'",
			},
			{
				"fieldname": "floors_count",
				"label": "Número de Pisos",
				"fieldtype": "Int",
				"insert_after": "construction_year",
				"depends_on": "eval: doc.company_type == 'Condominio'",
			},
			{
				"fieldname": "management_section",
				"label": "Información de Administración",
				"fieldtype": "Section Break",
				"insert_after": "floors_count",
				"depends_on": "eval: doc.company_type == 'Administradora' || doc.company_type == 'Condominio'",
				"collapsible": 1,
			},
			{
				"fieldname": "management_company",
				"label": "Empresa Administradora",
				"fieldtype": "Link",
				"options": "Company",
				"insert_after": "management_section",
				"depends_on": "eval: doc.company_type == 'Condominio'",
				"filters": "[['Company', 'company_type', '=', 'Administradora']]",
			},
			{
				"fieldname": "management_start_date",
				"label": "Fecha Inicio Administración",
				"fieldtype": "Date",
				"insert_after": "management_company",
				"depends_on": "eval: doc.company_type == 'Condominio' && doc.management_company",
			},
			{
				"fieldname": "management_contract_end_date",
				"label": "Fecha Fin Contrato",
				"fieldtype": "Date",
				"insert_after": "management_start_date",
				"depends_on": "eval: doc.company_type == 'Condominio' && doc.management_company",
			},
			{
				"fieldname": "managed_properties",
				"label": "Propiedades Administradas",
				"fieldtype": "Int",
				"insert_after": "management_contract_end_date",
				"depends_on": "eval: doc.company_type == 'Administradora'",
				"read_only": 1,
			},
			{
				"fieldname": "legal_section",
				"label": "Información Legal",
				"fieldtype": "Section Break",
				"insert_after": "managed_properties",
				"collapsible": 1,
			},
			{
				"fieldname": "legal_representative",
				"label": "Representante Legal",
				"fieldtype": "Data",
				"insert_after": "legal_section",
			},
			{
				"fieldname": "legal_representative_id",
				"label": "Cédula Representante Legal",
				"fieldtype": "Data",
				"insert_after": "legal_representative",
			},
			{
				"fieldname": "cb_legal_1",
				"fieldtype": "Column Break",
				"insert_after": "legal_representative_id",
			},
			{
				"fieldname": "registration_chamber_commerce",
				"label": "Registro Cámara de Comercio",
				"fieldtype": "Data",
				"insert_after": "cb_legal_1",
			},
			{
				"fieldname": "registration_date",
				"label": "Fecha de Registro",
				"fieldtype": "Date",
				"insert_after": "registration_chamber_commerce",
			},
			{
				"fieldname": "financial_section",
				"label": "Información Financiera",
				"fieldtype": "Section Break",
				"insert_after": "registration_date",
				"collapsible": 1,
			},
			{
				"fieldname": "monthly_admin_fee",
				"label": "Cuota Administración Mensual",
				"fieldtype": "Currency",
				"insert_after": "financial_section",
				"depends_on": "eval: doc.company_type == 'Condominio'",
			},
			{
				"fieldname": "reserve_fund",
				"label": "Fondo de Reserva",
				"fieldtype": "Currency",
				"insert_after": "monthly_admin_fee",
				"depends_on": "eval: doc.company_type == 'Condominio'",
			},
			{"fieldname": "cb_financial_1", "fieldtype": "Column Break", "insert_after": "reserve_fund"},
			{
				"fieldname": "insurance_policy_number",
				"label": "Póliza de Seguro",
				"fieldtype": "Data",
				"insert_after": "cb_financial_1",
				"depends_on": "eval: doc.company_type == 'Condominio'",
			},
			{
				"fieldname": "insurance_expiry_date",
				"label": "Fecha Vencimiento Seguro",
				"fieldtype": "Date",
				"insert_after": "insurance_policy_number",
				"depends_on": "eval: doc.company_type == 'Condominio'",
			},
		]
	}

	create_custom_fields(custom_fields)
	print("Campos personalizados de Company creados exitosamente")


def remove_company_custom_fields():
	"""Eliminar campos personalizados de Company DocType"""
	custom_fields = [
		"condominium_section",
		"company_type",
		"property_usage_type",
		"acquisition_type",
		"property_status_type",
		"cb_condominium_1",
		"total_units",
		"total_area_sqm",
		"construction_year",
		"floors_count",
		"management_section",
		"management_company",
		"management_start_date",
		"management_contract_end_date",
		"managed_properties",
		"legal_section",
		"legal_representative",
		"legal_representative_id",
		"cb_legal_1",
		"registration_chamber_commerce",
		"registration_date",
		"financial_section",
		"monthly_admin_fee",
		"reserve_fund",
		"cb_financial_1",
		"insurance_policy_number",
		"insurance_expiry_date",
	]

	for field in custom_fields:
		frappe.db.sql(
			"""
			DELETE FROM `tabCustom Field`
			WHERE dt = 'Company' AND fieldname = %s
		""",
			(field,),
		)

	frappe.db.commit()
	print("Campos personalizados de Company eliminados exitosamente")
