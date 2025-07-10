# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPropertyUsageType(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		frappe.db.delete("Property Usage Type", {"usage_name": ["like", "Test%"]})
		frappe.db.commit()

	def test_usage_type_creation(self):
		"""Test crear tipo de uso básico"""
		usage_type = frappe.get_doc({"doctype": "Property Usage Type", "usage_name": "Test Residencial"})
		usage_type.insert()

		# Verificar que se creó correctamente
		self.assertEqual(usage_type.usage_name, "Test Residencial")
		self.assertTrue(usage_type.is_active)

	def test_active_default(self):
		"""Test valor por defecto de activo"""
		usage_type = frappe.get_doc({"doctype": "Property Usage Type", "usage_name": "Test Comercial"})
		usage_type.insert()

		# Verificar que está activo por defecto
		self.assertTrue(usage_type.is_active)

	def test_unique_usage_name(self):
		"""Test unicidad del nombre de uso"""
		# Crear primer tipo
		usage1 = frappe.get_doc({"doctype": "Property Usage Type", "usage_name": "Test Mixto"})
		usage1.insert()

		# Intentar crear segundo con mismo nombre
		usage2 = frappe.get_doc({"doctype": "Property Usage Type", "usage_name": "Test Mixto"})

		with self.assertRaises(frappe.DuplicateEntryError):
			usage2.insert()

	def tearDown(self):
		"""Limpiar datos de prueba"""
		frappe.db.delete("Property Usage Type", {"usage_name": ["like", "Test%"]})
		frappe.db.commit()
