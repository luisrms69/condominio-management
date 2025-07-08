# Copyright (c) 2025, Buzola and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPhysicalSpace(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		# Crear company de prueba si no existe
		if not frappe.db.exists("Company", "Test Condominium"):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "Test Condominium",
					"abbr": "TC",
					"default_currency": "USD",
				}
			).insert()

	def test_physical_space_creation(self):
		"""Test crear espacio físico básico"""
		space = frappe.get_doc(
			{
				"doctype": "Physical Space",
				"space_name": "Torre A",
				"company": "Test Condominium",
				"description": "Edificio principal del condominio",
			}
		)
		space.insert()

		# Verificar que se creó correctamente
		self.assertEqual(space.space_name, "Torre A")
		self.assertEqual(space.space_level, 0)
		self.assertEqual(space.space_path, "/Torre A")
		self.assertTrue(space.space_code)
		self.assertTrue(space.is_active)

	def test_hierarchy_validation(self):
		"""Test validaciones de jerarquía"""
		# Crear espacio padre
		parent = frappe.get_doc(
			{"doctype": "Physical Space", "space_name": "Torre B", "company": "Test Condominium"}
		)
		parent.insert()

		# Crear espacio hijo
		child = frappe.get_doc(
			{
				"doctype": "Physical Space",
				"space_name": "Piso 1",
				"company": "Test Condominium",
				"parent_space": parent.name,
			}
		)
		child.insert()

		# Verificar jerarquía
		self.assertEqual(child.space_level, 1)
		self.assertEqual(child.space_path, "/Torre B/Piso 1")
		self.assertEqual(child.parent_space, parent.name)

	def test_circular_reference_validation(self):
		"""Test prevenir referencias circulares"""
		# Crear dos espacios
		space1 = frappe.get_doc(
			{"doctype": "Physical Space", "space_name": "Espacio 1", "company": "Test Condominium"}
		)
		space1.insert()

		space2 = frappe.get_doc(
			{
				"doctype": "Physical Space",
				"space_name": "Espacio 2",
				"company": "Test Condominium",
				"parent_space": space1.name,
			}
		)
		space2.insert()

		# Intentar crear referencia circular
		space1.parent_space = space2.name

		with self.assertRaises(frappe.ValidationError):
			space1.save()

	def test_self_parent_validation(self):
		"""Test prevenir que un espacio sea su propio padre"""
		space = frappe.get_doc(
			{"doctype": "Physical Space", "space_name": "Torre C", "company": "Test Condominium"}
		)
		space.insert()

		# Intentar hacer que sea su propio padre
		space.parent_space = space.name

		with self.assertRaises(frappe.ValidationError):
			space.save()

	def test_get_all_children(self):
		"""Test obtener todos los hijos recursivamente"""
		# Crear jerarquía: Torre -> Piso -> Apartamento
		torre = frappe.get_doc(
			{"doctype": "Physical Space", "space_name": "Torre D", "company": "Test Condominium"}
		)
		torre.insert()

		piso = frappe.get_doc(
			{
				"doctype": "Physical Space",
				"space_name": "Piso 2",
				"company": "Test Condominium",
				"parent_space": torre.name,
			}
		)
		piso.insert()

		apto = frappe.get_doc(
			{
				"doctype": "Physical Space",
				"space_name": "Apartamento 201",
				"company": "Test Condominium",
				"parent_space": piso.name,
			}
		)
		apto.insert()

		# Verificar que obtiene todos los hijos
		children = torre.get_space_hierarchy_children()
		self.assertIn(piso.name, children)
		self.assertIn(apto.name, children)

	def test_space_code_generation(self):
		"""Test generación automática de código"""
		space = frappe.get_doc(
			{"doctype": "Physical Space", "space_name": "Área Común Piscina", "company": "Test Condominium"}
		)
		space.insert()

		# Verificar que se generó código
		self.assertTrue(space.space_code)
		self.assertIn("AREACOMUN", space.space_code)

	def tearDown(self):
		"""Limpiar datos de prueba"""
		# Eliminar espacios de prueba
		frappe.db.delete("Physical Space", {"company": "Test Condominium"})
		frappe.db.commit()
