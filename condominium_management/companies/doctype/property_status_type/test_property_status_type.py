# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPropertyStatusType(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		frappe.db.delete("Property Status Type", {"status_name": ["like", "Test%"]})
		frappe.db.commit()

	def test_status_type_creation(self):
		"""Test crear tipo de estado básico"""
		status_type = frappe.get_doc(
			{"doctype": "Property Status Type", "status_name": "Test Habitada por Propietario"}
		)
		status_type.insert()

		# Verificar que se creó correctamente
		self.assertEqual(status_type.status_name, "Test Habitada por Propietario")
		self.assertTrue(status_type.is_active)

	def test_unique_status_name(self):
		"""Test unicidad del nombre de estado"""
		# Crear primer estado
		status1 = frappe.get_doc({"doctype": "Property Status Type", "status_name": "Test Rentada"})
		status1.insert()

		# Intentar crear segundo con mismo nombre
		status2 = frappe.get_doc({"doctype": "Property Status Type", "status_name": "Test Rentada"})

		with self.assertRaises(frappe.DuplicateEntryError):
			status2.insert()

	def test_active_default(self):
		"""Test valor por defecto de activo"""
		status_type = frappe.get_doc({"doctype": "Property Status Type", "status_name": "Test Desocupada"})
		status_type.insert()

		# Verificar que está activo por defecto
		self.assertTrue(status_type.is_active)

	def tearDown(self):
		"""Limpiar datos de prueba"""
		frappe.db.delete("Property Status Type", {"status_name": ["like", "Test%"]})
		frappe.db.commit()
