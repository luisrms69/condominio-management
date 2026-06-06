# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Verifica que los Custom Fields críticos sobre Company existen tras migrate.

Si este test falla en una instalación limpia, significa que companies_custom_field.json
no se importó correctamente. Revisar hooks.py fixtures y re-exportar.
"""

import frappe
from frappe.tests.utils import FrappeTestCase

_REQUIRED_COMPANY_FIELDS = [
	# Sección Condominio
	"company_type",
	"property_usage_type",
	"total_units",
	# Sección Administración
	"management_company",
	# Sección Financiero
	"monthly_admin_fee",
	"reserve_fund",
]


class TestCompanyCustomFieldsInstalled(FrappeTestCase):
	"""Verifica que los Custom Fields del módulo Companies están instalados."""

	def test_critical_company_custom_fields_exist(self):
		missing = [field for field in _REQUIRED_COMPANY_FIELDS if not frappe.db.has_column("Company", field)]
		self.assertFalse(
			missing,
			f"Faltan Custom Fields en Company: {missing}. "
			"Ejecutar: bench migrate y verificar companies_custom_field.json en fixtures.",
		)

	def test_company_type_field_is_link(self):
		meta = frappe.get_meta("Company")
		field = meta.get_field("company_type")
		self.assertIsNotNone(field, "El campo company_type no existe en Company")
		self.assertEqual(field.fieldtype, "Link")
		self.assertEqual(field.options, "Company Type")

	def test_management_company_field_is_link(self):
		meta = frappe.get_meta("Company")
		field = meta.get_field("management_company")
		self.assertIsNotNone(field, "El campo management_company no existe en Company")
		self.assertEqual(field.fieldtype, "Link")
		self.assertEqual(field.options, "Company")
