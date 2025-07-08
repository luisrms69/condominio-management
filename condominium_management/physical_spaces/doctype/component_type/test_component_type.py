# Copyright (c) 2025, Buzola and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestComponentType(FrappeTestCase):
	def test_component_type_creation(self):
		"""Test crear tipo de componente básico"""
		component_type = frappe.get_doc(
			{
				"doctype": "Component Type",
				"component_type_name": "Motor Eléctrico",
				"code_prefix": "MOT",
				"description": "Motores eléctricos de diferentes potencias",
				"category": "Eléctrico",
				"requires_brand": 1,
				"requires_model": 1,
				"requires_specifications": 1,
			}
		)
		component_type.insert()

		# Verificar que se creó correctamente
		self.assertEqual(component_type.component_type_name, "Motor Eléctrico")
		self.assertEqual(component_type.code_prefix, "MOT")
		self.assertEqual(component_type.category, "Eléctrico")
		self.assertTrue(component_type.is_active)
		self.assertEqual(component_type.template_version, "1.0")

	def test_code_prefix_normalization(self):
		"""Test normalización del prefijo de código"""
		component_type = frappe.get_doc(
			{
				"doctype": "Component Type",
				"component_type_name": "Bomba Centrífuga",
				"code_prefix": "  bom cen  ",
				"category": "Mecánico",
			}
		)
		component_type.insert()

		# Verificar que se normalizó el prefijo
		self.assertEqual(component_type.code_prefix, "BOMCEN")

	def test_unique_code_prefix(self):
		"""Test que el prefijo de código sea único"""
		# Crear primer tipo
		component_type1 = frappe.get_doc(
			{
				"doctype": "Component Type",
				"component_type_name": "Válvula Manual",
				"code_prefix": "VAL",
				"category": "Mecánico",
			}
		)
		component_type1.insert()

		# Intentar crear segundo tipo con el mismo prefijo
		component_type2 = frappe.get_doc(
			{
				"doctype": "Component Type",
				"component_type_name": "Válvula Automática",
				"code_prefix": "VAL",
				"category": "Mecánico",
			}
		)

		with self.assertRaises(frappe.ValidationError):
			component_type2.insert()

	def test_validation_rules(self):
		"""Test reglas de validación"""
		component_type = frappe.get_doc(
			{
				"doctype": "Component Type",
				"component_type_name": "Sensor de Temperatura",
				"code_prefix": "TEMP",
				"category": "Electrónico",
				"requires_brand": 1,
				"requires_model": 1,
				"requires_installation_date": 1,
				"requires_warranty": 1,
				"requires_specifications": 1,
			}
		)
		component_type.insert()

		# Verificar reglas de validación
		rules = component_type.get_validation_rules()
		self.assertTrue(rules["requires_brand"])
		self.assertTrue(rules["requires_model"])
		self.assertTrue(rules["requires_installation_date"])
		self.assertTrue(rules["requires_warranty"])
		self.assertTrue(rules["requires_specifications"])

	def test_maintenance_configuration(self):
		"""Test configuración de mantenimiento"""
		component_type = frappe.get_doc(
			{
				"doctype": "Component Type",
				"component_type_name": "Compresor HVAC",
				"code_prefix": "HVAC",
				"category": "Mecánico",
				"default_maintenance_frequency": "Trimestral",
				"maintenance_type": "Preventivo",
				"estimated_lifespan_years": 15.0,
				"critical_component": 1,
				"requires_certification": 1,
			}
		)
		component_type.insert()

		# Verificar configuración de mantenimiento
		maintenance_config = component_type.get_maintenance_configuration()
		self.assertEqual(maintenance_config["default_frequency"], "Trimestral")
		self.assertEqual(maintenance_config["maintenance_type"], "Preventivo")
		self.assertEqual(maintenance_config["estimated_lifespan_years"], 15.0)
		self.assertTrue(maintenance_config["critical_component"])
		self.assertTrue(maintenance_config["requires_certification"])

	def test_ui_configuration(self):
		"""Test configuración de UI"""
		component_type = frappe.get_doc(
			{
				"doctype": "Component Type",
				"component_type_name": "Sistema de Seguridad",
				"code_prefix": "SEC",
				"category": "Seguridad",
				"icon_class": "fa fa-shield",
				"color_code": "#e74c3c",
				"display_order": 1,
			}
		)
		component_type.insert()

		# Verificar configuración de UI
		ui_config = component_type.get_ui_configuration()
		self.assertEqual(ui_config["icon_class"], "fa fa-shield")
		self.assertEqual(ui_config["color_code"], "#e74c3c")
		self.assertEqual(ui_config["display_order"], 1)

	def test_default_ui_configuration(self):
		"""Test configuración de UI por defecto"""
		component_type = frappe.get_doc(
			{
				"doctype": "Component Type",
				"component_type_name": "Componente Genérico",
				"code_prefix": "GEN",
				"category": "Otro",
			}
		)
		component_type.insert()

		# Verificar configuración por defecto
		ui_config = component_type.get_ui_configuration()
		self.assertEqual(ui_config["icon_class"], "fa fa-cog")
		self.assertEqual(ui_config["color_code"], "#606060")
		self.assertEqual(ui_config["display_order"], 0)

	def test_component_data_validation(self):
		"""Test validación de datos de componente"""
		component_type = frappe.get_doc(
			{
				"doctype": "Component Type",
				"component_type_name": "Elevador",
				"code_prefix": "ELEV",
				"category": "Mecánico",
				"requires_brand": 1,
				"requires_model": 1,
				"requires_specifications": 1,
			}
		)
		component_type.insert()

		# Datos válidos
		valid_data = {
			"brand": "Otis",
			"model": "Gen2",
			"technical_specifications": "Capacidad 1000kg, 8 personas",
		}
		errors = component_type.validate_component_data(valid_data)
		self.assertEqual(len(errors), 0)

		# Datos inválidos (falta marca)
		invalid_data = {"model": "Gen2", "technical_specifications": "Capacidad 1000kg, 8 personas"}
		errors = component_type.validate_component_data(invalid_data)
		self.assertGreater(len(errors), 0)
		self.assertIn("marca", errors[0].lower())

	def test_inventory_code_generation(self):
		"""Test generación de códigos de inventario"""
		component_type = frappe.get_doc(
			{
				"doctype": "Component Type",
				"component_type_name": "Luminaria LED",
				"code_prefix": "LED",
				"category": "Iluminación",
			}
		)
		component_type.insert()

		# Generar primer código
		first_code = component_type.get_next_inventory_code()
		self.assertEqual(first_code, "LED-0001")

		# Simular que ya existe un componente con ese código
		# (En un test real, crearíamos el componente)
		# El próximo código debería ser LED-0002

	def test_component_categories(self):
		"""Test categorías válidas de componentes"""
		valid_categories_with_prefixes = [
			("Mecánico", "MEC"),
			("Eléctrico", "ELE"),
			("Electrónico", "ELT"),  # Diferente de ELE para evitar colisión
			("Hidráulico", "HID"),
			("Neumático", "NEU"),
			("Estructural", "EST"),
			("Seguridad", "SEG"),
			("Control", "CTR"),
			("Medición", "MED"),
			("Iluminación", "ILU"),
			("Climático", "CLI"),
			("Otro", "OTR"),
		]

		for category, prefix in valid_categories_with_prefixes:
			component_type = frappe.get_doc(
				{
					"doctype": "Component Type",
					"component_type_name": f"Test {category}",
					"code_prefix": prefix,
					"category": category,
				}
			)
			component_type.insert()

			# Verificar que se acepta la categoría
			self.assertEqual(component_type.category, category)

	def tearDown(self):
		"""Limpiar datos de prueba"""
		# Eliminar tipos de componente de prueba
		test_types = frappe.get_all("Component Type", filters={"component_type_name": ["like", "Test%"]})
		for comp_type in test_types:
			frappe.delete_doc("Component Type", comp_type.name)

		# Hacer rollback para limpiar todos los datos de prueba
		frappe.db.rollback()
