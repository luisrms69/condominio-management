# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPolicyCategory(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		frappe.db.delete("Policy Category", {"category_name": ["like", "Test%"]})
		frappe.db.commit()

	def test_policy_category_creation(self):
		"""Test crear categoría de política básica"""
		category = frappe.get_doc(
			{"doctype": "Policy Category", "category_name": "Test Convivencia", "chapter_mapping": "XVIII-XX"}
		)
		category.insert()

		# Verificar que se creó correctamente
		self.assertEqual(category.category_name, "Test Convivencia")
		self.assertEqual(category.chapter_mapping, "XVIII-XX")
		self.assertTrue(category.is_active)

	def test_chapter_mapping_validation(self):
		"""Test validación del mapeo de capítulos"""
		category = frappe.get_doc(
			{
				"doctype": "Policy Category",
				"category_name": "Test Seguridad",
				"chapter_mapping": "XV-XVII, XXI",
			}
		)
		category.insert()

		# Verificar que se acepta formato válido
		self.assertEqual(category.chapter_mapping, "XV-XVII, XXI")

	def test_get_related_chapters(self):
		"""Test obtener capítulos relacionados"""
		category = frappe.get_doc(
			{
				"doctype": "Policy Category",
				"category_name": "Test Mantenimiento",
				"chapter_mapping": "XII, XIII-XV, XVIII",
			}
		)
		category.insert()

		chapters = category.get_related_chapters()
		self.assertEqual(len(chapters), 3)
		self.assertIn("XII", chapters)
		self.assertIn("XIII-XV", chapters)

	def test_unique_category_name(self):
		"""Test unicidad del nombre de categoría"""
		# Crear primera categoría
		category1 = frappe.get_doc({"doctype": "Policy Category", "category_name": "Test Áreas Comunes"})
		category1.insert()

		# Intentar crear segunda con mismo nombre
		category2 = frappe.get_doc({"doctype": "Policy Category", "category_name": "Test Áreas Comunes"})

		with self.assertRaises(frappe.DuplicateEntryError):
			category2.insert()

	def tearDown(self):
		"""Limpiar datos de prueba"""
		frappe.db.delete("Policy Category", {"category_name": ["like", "Test%"]})
		frappe.db.commit()
