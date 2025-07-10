# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestCompanyType(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		# Limpiar datos de prueba anteriores
		frappe.db.delete("Company Type", {"type_name": ["like", "Test%"]})
		frappe.db.commit()

	def test_company_type_creation(self):
		"""Test crear tipo de empresa básico"""
		company_type = frappe.get_doc(
			{"doctype": "Company Type", "type_name": "Test Empresa Administradora", "is_management_type": 1}
		)
		company_type.insert()

		# Verificar que se creó correctamente
		self.assertEqual(company_type.type_name, "Test Empresa Administradora")
		self.assertTrue(company_type.is_management_type)
		self.assertTrue(company_type.is_active)
		self.assertTrue(company_type.type_code)

	def test_code_generation(self):
		"""Test generación automática de código"""
		company_type = frappe.get_doc({"doctype": "Company Type", "type_name": "Test Condominio Residencial"})
		company_type.insert()

		# Verificar que se generó código
		self.assertTrue(company_type.type_code)
		self.assertIn("TES", company_type.type_code)

	def test_code_uniqueness(self):
		"""Test unicidad de códigos"""
		# Crear primer tipo
		type1 = frappe.get_doc({"doctype": "Company Type", "type_name": "Test Administradora"})
		type1.insert()

		# Crear segundo tipo con nombre similar
		type2 = frappe.get_doc({"doctype": "Company Type", "type_name": "Test Administradora Dos"})
		type2.insert()

		# Verificar que tienen códigos diferentes
		self.assertNotEqual(type1.type_code, type2.type_code)

	def test_management_type_flag(self):
		"""Test flag de tipo administradora"""
		# Tipo administradora
		admin_type = frappe.get_doc(
			{"doctype": "Company Type", "type_name": "Test Admin Type", "is_management_type": 1}
		)
		admin_type.insert()
		self.assertTrue(admin_type.is_management_type)

		# Tipo condominio
		condo_type = frappe.get_doc(
			{"doctype": "Company Type", "type_name": "Test Condo Type", "is_management_type": 0}
		)
		condo_type.insert()
		self.assertFalse(condo_type.is_management_type)

	def test_active_default(self):
		"""Test valor por defecto de activo"""
		company_type = frappe.get_doc({"doctype": "Company Type", "type_name": "Test Default Active"})
		company_type.insert()

		# Verificar que está activo por defecto
		self.assertTrue(company_type.is_active)

	def tearDown(self):
		"""Limpiar datos de prueba"""
		frappe.db.delete("Company Type", {"type_name": ["like", "Test%"]})
		frappe.db.commit()
