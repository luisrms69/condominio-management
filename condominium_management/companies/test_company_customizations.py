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

		# Crear empresa condominio
		company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "Test Condominio Residencial",
				"abbr": "TCR",
				"default_currency": "COP",
				"country": "Colombia",
				"company_type": "Condominio",
				"property_usage_type": "Residencial",
				"total_units": 50,
				"total_area_sqm": 5000.0,
				"construction_year": 2020,
				"floors_count": 5,
			}
		)
		company.insert(ignore_permissions=True)

		# Verificar que se creó correctamente
		self.assertEqual(company.company_type, "Condominio")
		self.assertEqual(company.property_usage_type, "Residencial")
		self.assertEqual(company.total_units, 50)
		self.assertEqual(company.total_area_sqm, 5000.0)

	def test_administradora_company_creation(self):
		"""Test crear empresa administradora"""
		company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "Test Administradora XYZ",
				"abbr": "TAX",
				"default_currency": "COP",
				"country": "Colombia",
				"company_type": "Administradora",
				"legal_representative": "Juan Pérez",
				"legal_representative_id": "12345678",
			}
		)
		company.insert(ignore_permissions=True)

		# Verificar que se creó correctamente
		self.assertEqual(company.company_type, "Administradora")
		self.assertEqual(company.legal_representative, "Juan Pérez")
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
