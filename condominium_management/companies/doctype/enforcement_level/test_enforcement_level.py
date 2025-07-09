# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestEnforcementLevel(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		frappe.db.delete("Enforcement Level", {"level_name": ["like", "Test%"]})
		frappe.db.commit()

	def test_enforcement_level_creation(self):
		"""Test crear nivel de aplicación básico"""
		level = frappe.get_doc(
			{"doctype": "Enforcement Level", "level_name": "Test Informativa", "severity_order": 1}
		)
		level.insert()

		# Verificar que se creó correctamente
		self.assertEqual(level.level_name, "Test Informativa")
		self.assertEqual(level.severity_order, 1)
		self.assertTrue(level.is_active)

	def test_severity_order_validation(self):
		"""Test validación del orden de severidad"""
		# Test orden negativo
		level1 = frappe.get_doc(
			{"doctype": "Enforcement Level", "level_name": "Test Invalid", "severity_order": -1}
		)

		with self.assertRaises(frappe.ValidationError):
			level1.insert()

		# Test orden cero
		level2 = frappe.get_doc(
			{"doctype": "Enforcement Level", "level_name": "Test Zero", "severity_order": 0}
		)

		with self.assertRaises(frappe.ValidationError):
			level2.insert()

	def test_unique_severity_order(self):
		"""Test unicidad del orden de severidad"""
		# Crear primer nivel
		level1 = frappe.get_doc(
			{"doctype": "Enforcement Level", "level_name": "Test Leve", "severity_order": 2}
		)
		level1.insert()

		# Intentar crear segundo con mismo orden
		level2 = frappe.get_doc(
			{"doctype": "Enforcement Level", "level_name": "Test Otro Leve", "severity_order": 2}
		)

		with self.assertRaises(frappe.ValidationError):
			level2.insert()

	def test_get_severity_level(self):
		"""Test descripción del nivel de severidad"""
		# Nivel muy bajo
		level1 = frappe.get_doc(
			{"doctype": "Enforcement Level", "level_name": "Test Muy Bajo", "severity_order": 1}
		)
		level1.insert()
		self.assertEqual(level1.get_severity_level(), "Muy Bajo")

		# Nivel medio
		level2 = frappe.get_doc(
			{"doctype": "Enforcement Level", "level_name": "Test Medio", "severity_order": 50}
		)
		level2.insert()
		self.assertEqual(level2.get_severity_level(), "Medio")

		# Nivel muy alto
		level3 = frappe.get_doc(
			{"doctype": "Enforcement Level", "level_name": "Test Muy Alto", "severity_order": 99}
		)
		level3.insert()
		self.assertEqual(level3.get_severity_level(), "Muy Alto")

	def tearDown(self):
		"""Limpiar datos de prueba"""
		frappe.db.delete("Enforcement Level", {"level_name": ["like", "Test%"]})
		frappe.db.commit()
