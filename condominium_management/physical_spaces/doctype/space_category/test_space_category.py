# Copyright (c) 2025, Buzola and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestSpaceCategory(FrappeTestCase):
	def test_space_category_creation(self):
		"""Test crear categoría de espacio básica"""
		category = frappe.get_doc(
			{
				"doctype": "Space Category",
				"category_name": "Apartamento",
				"description": "Unidad habitacional privada",
				"category_type": "Área Privada",
				"requires_dimensions": 1,
				"requires_capacity": 1,
			}
		)
		category.insert()

		# Verificar que se creó correctamente
		self.assertEqual(category.category_name, "Apartamento")
		self.assertEqual(category.category_code, "APARTAMENTO")
		self.assertTrue(category.is_active)
		self.assertEqual(category.template_version, "1.0")

	def test_category_code_generation(self):
		"""Test generación automática de código de categoría"""
		category = frappe.get_doc(
			{
				"doctype": "Space Category",
				"category_name": "Área Común Piscina",
				"category_type": "Área Común",
			}
		)
		category.insert()

		# Verificar que se generó código
		self.assertTrue(category.category_code)
		self.assertEqual(category.category_code, "ÁREA_COMÚN_PISC")

	def test_template_configuration(self):
		"""Test configuración de template"""
		category = frappe.get_doc(
			{
				"doctype": "Space Category",
				"category_name": "Elevador",
				"category_type": "Equipamiento",
				"ps_template_code": "elevator_template_v1",
				"auto_load_template": 1,
			}
		)
		category.insert()

		# Verificar configuración de template
		self.assertEqual(category.ps_template_code, "elevator_template_v1")
		self.assertEqual(category.template_version, "1.0")
		self.assertTrue(category.auto_load_template)

	def test_validation_rules(self):
		"""Test reglas de validación"""
		category = frappe.get_doc(
			{
				"doctype": "Space Category",
				"category_name": "Gimnasio",
				"category_type": "Área Común",
				"requires_components": 1,
				"requires_dimensions": 1,
				"requires_capacity": 1,
			}
		)
		category.insert()

		# Verificar reglas de validación
		rules = category.get_validation_rules()
		self.assertTrue(rules["requires_components"])
		self.assertTrue(rules["requires_dimensions"])
		self.assertTrue(rules["requires_capacity"])

	def test_ui_configuration(self):
		"""Test configuración de UI"""
		category = frappe.get_doc(
			{
				"doctype": "Space Category",
				"category_name": "Oficina Administración",
				"category_type": "Servicios",
				"icon_class": "fa fa-office",
				"color_code": "#3498db",
				"display_order": 10,
			}
		)
		category.insert()

		# Verificar configuración de UI
		ui_config = category.get_ui_configuration()
		self.assertEqual(ui_config["icon_class"], "fa fa-office")
		self.assertEqual(ui_config["color_code"], "#3498db")
		self.assertEqual(ui_config["display_order"], 10)

	def test_default_ui_configuration(self):
		"""Test configuración de UI por defecto"""
		category = frappe.get_doc(
			{"doctype": "Space Category", "category_name": "Bodega", "category_type": "Servicios"}
		)
		category.insert()

		# Verificar configuración por defecto
		ui_config = category.get_ui_configuration()
		self.assertEqual(ui_config["icon_class"], "fa fa-building")
		self.assertEqual(ui_config["color_code"], "#808080")
		self.assertEqual(ui_config["display_order"], 0)

	def test_category_types(self):
		"""Test tipos de categorías válidos"""
		valid_types = [
			"Estructura",
			"Área Común",
			"Área Privada",
			"Instalaciones",
			"Equipamiento",
			"Seguridad",
			"Mantenimiento",
			"Servicios",
		]

		for category_type in valid_types:
			category = frappe.get_doc(
				{
					"doctype": "Space Category",
					"category_name": f"Test {category_type}",
					"category_type": category_type,
				}
			)
			category.insert()

			# Verificar que se acepta el tipo
			self.assertEqual(category.category_type, category_type)

	def tearDown(self):
		"""Limpiar datos de prueba"""
		# Eliminar categorías de prueba
		test_categories = frappe.get_all("Space Category", filters={"category_name": ["like", "Test%"]})
		for cat in test_categories:
			frappe.delete_doc("Space Category", cat.name)

		# Eliminar otras categorías de prueba
		test_names = [
			"Apartamento",
			"Área Común Piscina",
			"Elevador",
			"Gimnasio",
			"Oficina Administración",
			"Bodega",
		]
		for name in test_names:
			if frappe.db.exists("Space Category", name):
				frappe.delete_doc("Space Category", name)

		frappe.db.commit()
