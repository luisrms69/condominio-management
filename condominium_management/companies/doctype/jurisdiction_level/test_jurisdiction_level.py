# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestJurisdictionLevel(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		# Limpiar TODOS los jurisdiction levels para evitar conflictos con fixtures
		frappe.db.delete("Jurisdiction Level", {})
		frappe.db.commit()

	def test_jurisdiction_level_creation(self):
		"""Test crear nivel de jurisdicción básico"""
		jurisdiction = frappe.get_doc(
			{
				"doctype": "Jurisdiction Level",
				"level_name": "Test Municipal",
				"hierarchy_order": 3,
				"geographic_scope": "Municipal",
			}
		)
		jurisdiction.insert()

		# Verificar que se creó correctamente
		self.assertEqual(jurisdiction.level_name, "Test Municipal")
		self.assertEqual(jurisdiction.hierarchy_order, 3)
		self.assertEqual(jurisdiction.geographic_scope, "Municipal")
		self.assertTrue(jurisdiction.is_active)

	def test_hierarchy_order_validation(self):
		"""Test validación del orden jerárquico"""
		# Test orden negativo
		jurisdiction1 = frappe.get_doc(
			{
				"doctype": "Jurisdiction Level",
				"level_name": "Test Invalid",
				"hierarchy_order": -1,
				"geographic_scope": "Municipal",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			jurisdiction1.insert()

		# Test orden cero
		jurisdiction2 = frappe.get_doc(
			{
				"doctype": "Jurisdiction Level",
				"level_name": "Test Zero",
				"hierarchy_order": 0,
				"geographic_scope": "Municipal",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			jurisdiction2.insert()

	def test_unique_hierarchy_order(self):
		"""Test unicidad del orden jerárquico"""
		# Crear primer nivel
		jurisdiction1 = frappe.get_doc(
			{
				"doctype": "Jurisdiction Level",
				"level_name": "Test Nacional",
				"hierarchy_order": 1,
				"geographic_scope": "Nacional",
			}
		)
		jurisdiction1.insert()

		# Intentar crear segundo con mismo orden
		jurisdiction2 = frappe.get_doc(
			{
				"doctype": "Jurisdiction Level",
				"level_name": "Test Otro Nacional",
				"hierarchy_order": 1,
				"geographic_scope": "Nacional",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			jurisdiction2.insert()

	def test_geographic_scope_validation(self):
		"""Test validación del ámbito geográfico"""
		# Nacional debe ser orden 1
		jurisdiction1 = frappe.get_doc(
			{
				"doctype": "Jurisdiction Level",
				"level_name": "Test Nacional Invalid",
				"hierarchy_order": 2,
				"geographic_scope": "Nacional",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			jurisdiction1.insert()

		# Local debe ser orden 3 o mayor
		jurisdiction2 = frappe.get_doc(
			{
				"doctype": "Jurisdiction Level",
				"level_name": "Test Local Invalid",
				"hierarchy_order": 2,
				"geographic_scope": "Local",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			jurisdiction2.insert()

		# Local válido
		jurisdiction3 = frappe.get_doc(
			{
				"doctype": "Jurisdiction Level",
				"level_name": "Test Local Valid",
				"hierarchy_order": 3,
				"geographic_scope": "Local",
			}
		)
		jurisdiction3.insert()

		self.assertEqual(jurisdiction3.geographic_scope, "Local")

	def test_get_authority_description(self):
		"""Test descripción de autoridad"""
		# Sin autoridades
		jurisdiction1 = frappe.get_doc(
			{
				"doctype": "Jurisdiction Level",
				"level_name": "Test No Authority",
				"hierarchy_order": 2,
				"geographic_scope": "Departamental",
			}
		)
		jurisdiction1.insert()

		self.assertEqual(jurisdiction1.get_authority_description(), "Sin autoridades específicas")

		# Con autoridades
		jurisdiction2 = frappe.get_doc(
			{
				"doctype": "Jurisdiction Level",
				"level_name": "Test With Authority",
				"hierarchy_order": 3,
				"geographic_scope": "Municipal",
				"can_issue_permits": 1,
				"can_enforce_laws": 1,
			}
		)
		jurisdiction2.insert()

		authority_desc = jurisdiction2.get_authority_description()
		self.assertIn("Emisión de Permisos", authority_desc)
		self.assertIn("Aplicación de Leyes", authority_desc)

	def test_get_jurisdiction_hierarchy(self):
		"""Test jerarquía de jurisdicciones"""
		jurisdiction = frappe.get_doc(
			{
				"doctype": "Jurisdiction Level",
				"level_name": "Test Hierarchy",
				"hierarchy_order": 2,
				"geographic_scope": "Departamental",
			}
		)
		jurisdiction.insert()

		self.assertEqual(jurisdiction.get_jurisdiction_hierarchy(), "Segundo Nivel")

	def tearDown(self):
		"""Limpiar datos de prueba"""
		frappe.db.delete("Jurisdiction Level", {"level_name": ["like", "Test%"]})
		frappe.db.commit()
