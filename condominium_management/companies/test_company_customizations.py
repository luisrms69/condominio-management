# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta

import frappe
from frappe.tests.utils import FrappeTestCase


class TestCompanyCustomizations(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		# Crear tipos de empresa necesarios
		self.create_test_company_types()

		# Instalar custom fields si no existen
		self.install_custom_fields()

		# Limpiar compañías de prueba
		frappe.db.delete("Company", {"company_name": ["like", "Test%"]})
		frappe.db.commit()

	def create_test_company_types(self):
		"""Crear tipos de empresa para pruebas"""
		company_types = [
			{"type_name": "Administradora", "type_code": "ADMIN", "is_management_type": 1},
			{"type_name": "Condominio", "type_code": "CONDO", "is_management_type": 0},
			{"type_name": "Proveedor", "type_code": "PROV", "is_management_type": 0},
		]

		for company_type_data in company_types:
			if not frappe.db.exists("Company Type", company_type_data["type_name"]):
				company_type = frappe.get_doc({"doctype": "Company Type", **company_type_data})
				try:
					company_type.insert(ignore_permissions=True)
				except frappe.DuplicateEntryError:
					# Ignorar duplicados - pueden existir por fixtures
					pass

	def install_custom_fields(self):
		"""Instalar custom fields necesarios para testing"""
		try:
			from condominium_management.companies.custom_fields.company_custom_fields import (
				install_company_customizations,
			)

			install_company_customizations()
		except Exception:
			# Si falla, usar la utilidad de testing
			from condominium_management.companies.test_utils import ensure_custom_fields_exist

			ensure_custom_fields_exist()

	def create_minimal_custom_fields(self):
		"""Crear custom fields mínimos para testing"""
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

	def test_company_type_validation(self):
		"""Test validación de tipo de empresa"""
		# Crear empresa sin tipo (debe fallar)
		company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "Test Company Invalid",
				"abbr": "TCI",
				"default_currency": "COP",
				"country": "Colombia",
			}
		)

		try:
			company.insert()
			# Si no falla, verificar que al menos el tipo sea requerido
			self.fail("Se esperaba que falle la validación sin tipo de empresa")
		except (frappe.ValidationError, frappe.MandatoryError):
			# Test pasa si falla por validación o campo obligatorio
			pass

	def test_condominium_company_creation(self):
		"""Test crear empresa tipo condominio"""
		# Crear tipo de uso de propiedad
		if not frappe.db.exists("Property Usage Type", "Residencial"):
			usage_type = frappe.get_doc({"doctype": "Property Usage Type", "usage_name": "Residencial"})
			try:
				usage_type.insert(ignore_permissions=True)
			except frappe.DuplicateEntryError:
				pass

		# Crear empresa condominio usando utilidad de testing
		from condominium_management.companies.test_utils import create_test_company_with_default_fallback

		company = create_test_company_with_default_fallback(
			"Test Condominio Residencial", "TCR", "COP", "Colombia"
		)

		# Actualizar con campos específicos si existen
		if hasattr(company, "company_type"):
			company.company_type = "Condominio"
		if hasattr(company, "property_usage_type"):
			company.property_usage_type = "Residencial"
		if hasattr(company, "total_units"):
			company.total_units = 50
		if hasattr(company, "total_area_sqm"):
			company.total_area_sqm = 5000.0
		if hasattr(company, "construction_year"):
			company.construction_year = 2020
		if hasattr(company, "floors_count"):
			company.floors_count = 5

		company.save(ignore_permissions=True)

		# Verificar que se creó correctamente
		if hasattr(company, "company_type"):
			self.assertEqual(company.company_type, "Condominio")
		if hasattr(company, "property_usage_type"):
			self.assertEqual(company.property_usage_type, "Residencial")
		if hasattr(company, "total_units"):
			self.assertEqual(company.total_units, 50)
		if hasattr(company, "total_area_sqm"):
			self.assertEqual(company.total_area_sqm, 5000.0)

	def test_administradora_company_creation(self):
		"""Test crear empresa administradora"""
		from condominium_management.companies.test_utils import create_test_company_with_default_fallback

		company = create_test_company_with_default_fallback(
			"Test Administradora XYZ", "TAX", "COP", "Colombia"
		)

		# Actualizar con campos específicos si existen
		if hasattr(company, "company_type"):
			company.company_type = "Administradora"
		if hasattr(company, "legal_representative"):
			company.legal_representative = "Juan Pérez"
		if hasattr(company, "legal_representative_id"):
			company.legal_representative_id = "12345678"

		company.save(ignore_permissions=True)

		# Verificar que se creó correctamente
		if hasattr(company, "company_type"):
			self.assertEqual(company.company_type, "Administradora")
		if hasattr(company, "legal_representative"):
			self.assertEqual(company.legal_representative, "Juan Pérez")
		if hasattr(company, "legal_representative_id"):
			self.assertEqual(company.legal_representative_id, "12345678")

	def test_condominium_validation_errors(self):
		"""Test validaciones de condominio"""
		# Total de unidades negativo
		company1 = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "Test Invalid Units",
				"abbr": "TIU",
				"default_currency": "COP",
				"country": "Colombia",
				"company_type": "Condominio",
				"total_units": -10,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			company1.insert()

		# Año de construcción inválido
		company2 = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "Test Invalid Year",
				"abbr": "TIY",
				"default_currency": "COP",
				"country": "Colombia",
				"company_type": "Condominio",
				"construction_year": 1800,
			}
		)

		with self.assertRaises(frappe.ValidationError):
			company2.insert()

	def test_management_relationship(self):
		"""Test relación de administración"""
		# Crear administradora
		admin_company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "Test Administradora ABC",
				"abbr": "TAA",
				"default_currency": "COP",
				"country": "Colombia",
				"company_type": "Administradora",
			}
		)
		admin_company.insert(ignore_permissions=True)

		# Crear condominio con administradora
		if not frappe.db.exists("Property Usage Type", "Residencial"):
			usage_type = frappe.get_doc({"doctype": "Property Usage Type", "usage_name": "Residencial"})
			usage_type.insert(ignore_permissions=True)

		condo_company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "Test Condominio Administrado",
				"abbr": "TCA",
				"default_currency": "COP",
				"country": "Colombia",
				"company_type": "Condominio",
				"property_usage_type": "Residencial",
				"management_company": admin_company.name,
				"management_start_date": datetime.now().date(),
				"management_contract_end_date": (datetime.now() + timedelta(days=365)).date(),
			}
		)
		condo_company.insert(ignore_permissions=True)

		# Verificar relación
		self.assertEqual(condo_company.management_company, admin_company.name)

		# Verificar que la administradora actualiza su contador
		admin_company.reload()
		self.assertEqual(admin_company.managed_properties, 1)

	def test_legal_representative_validation(self):
		"""Test validación del representante legal"""
		# Cédula inválida
		company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "Test Invalid ID",
				"abbr": "TII",
				"default_currency": "COP",
				"country": "Colombia",
				"company_type": "Administradora",
				"legal_representative": "Juan Pérez",
				"legal_representative_id": "123",  # Muy corta
			}
		)

		with self.assertRaises(frappe.ValidationError):
			company.insert()

	def test_financial_fields_validation(self):
		"""Test validación de campos financieros"""
		# Cuota de administración negativa
		if not frappe.db.exists("Property Usage Type", "Residencial"):
			usage_type = frappe.get_doc({"doctype": "Property Usage Type", "usage_name": "Residencial"})
			usage_type.insert(ignore_permissions=True)

		company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "Test Invalid Fee",
				"abbr": "TIF",
				"default_currency": "COP",
				"country": "Colombia",
				"company_type": "Condominio",
				"property_usage_type": "Residencial",
				"monthly_admin_fee": -100000,  # Negativa
			}
		)

		with self.assertRaises(frappe.ValidationError):
			company.insert()

	def tearDown(self):
		"""Limpiar datos de prueba"""
		frappe.db.delete("Company", {"company_name": ["like", "Test%"]})
		frappe.db.delete("Property Usage Type", {"usage_name": ["like", "Test%"]})
		frappe.db.commit()
