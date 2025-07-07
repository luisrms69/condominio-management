# Copyright (c) 2025, Buzola and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, today


class TestSpaceComponent(FrappeTestCase):
	def setUp(self):
		"""Configurar datos de prueba"""
		# Crear Component Type de prueba si no existe
		if not frappe.db.exists("Component Type", "Test Component Type"):
			frappe.get_doc(
				{
					"doctype": "Component Type",
					"component_type_name": "Test Component Type",
					"code_prefix": "TEST",
				}
			).insert()

	def test_component_creation(self):
		"""Test crear componente básico"""
		component = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Bomba de Agua Principal",
				"component_type": "Test Component Type",
				"quantity": 1,
				"status": "Activo",
				"brand": "Grundfos",
				"model": "CR-45",
			}
		)
		component.insert()

		# Verificar que se creó correctamente
		self.assertEqual(component.component_name, "Bomba de Agua Principal")
		self.assertEqual(component.status, "Activo")
		self.assertEqual(component.brand, "Grundfos")
		self.assertEqual(component.model, "CR-45")
		self.assertTrue(component.inventory_code)
		self.assertEqual(component.inventory_date, today())

	def test_inventory_code_generation(self):
		"""Test generación automática de código de inventario"""
		component = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Motor Eléctrico",
				"component_type": "Test Component Type",
				"quantity": 1,
			}
		)
		component.insert()

		# Verificar que se generó código
		self.assertTrue(component.inventory_code)
		self.assertIn("TEST", component.inventory_code)

	def test_component_hierarchy(self):
		"""Test jerarquía de componentes"""
		# Crear componente padre
		parent = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Sistema HVAC",
				"component_type": "Test Component Type",
				"quantity": 1,
			}
		)
		parent.insert()

		# Crear componente hijo
		child = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Compresor HVAC",
				"component_type": "Test Component Type",
				"parent_component": parent.name,
				"quantity": 1,
			}
		)
		child.insert()

		# Verificar jerarquía
		self.assertEqual(child.parent_component, parent.name)
		hierarchy_path = child.get_component_hierarchy_path()
		self.assertIn("Sistema HVAC", hierarchy_path)
		self.assertIn("Compresor HVAC", hierarchy_path)

	def test_circular_reference_validation(self):
		"""Test prevenir referencias circulares"""
		# Crear dos componentes
		comp1 = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Componente 1",
				"component_type": "Test Component Type",
				"quantity": 1,
			}
		)
		comp1.insert()

		comp2 = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Componente 2",
				"component_type": "Test Component Type",
				"parent_component": comp1.name,
				"quantity": 1,
			}
		)
		comp2.insert()

		# Intentar crear referencia circular
		comp1.parent_component = comp2.name

		with self.assertRaises(frappe.ValidationError):
			comp1.save()

	def test_self_parent_validation(self):
		"""Test prevenir que un componente sea su propio padre"""
		component = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Válvula Principal",
				"component_type": "Test Component Type",
				"quantity": 1,
			}
		)
		component.insert()

		# Intentar hacer que sea su propio padre
		component.parent_component = component.name

		with self.assertRaises(frappe.ValidationError):
			component.save()

	def test_get_all_subcomponents(self):
		"""Test obtener todos los subcomponentes recursivamente"""
		# Crear jerarquía: Sistema → Subsistema → Componente
		sistema = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Sistema de Bombeo",
				"component_type": "Test Component Type",
				"quantity": 1,
			}
		)
		sistema.insert()

		subsistema = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Subsistema de Control",
				"component_type": "Test Component Type",
				"parent_component": sistema.name,
				"quantity": 1,
			}
		)
		subsistema.insert()

		componente = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Sensor de Presión",
				"component_type": "Test Component Type",
				"parent_component": subsistema.name,
				"quantity": 1,
			}
		)
		componente.insert()

		# Verificar que obtiene todos los subcomponentes
		subcomponents = sistema.get_all_subcomponents()
		self.assertIn(subsistema.name, subcomponents)
		self.assertIn(componente.name, subcomponents)

	def test_warranty_expiry_check(self):
		"""Test verificación de vencimiento de garantía"""
		# Componente con garantía vencida
		expired_component = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Equipo Vencido",
				"component_type": "Test Component Type",
				"warranty_expiry_date": add_days(today(), -30),
				"quantity": 1,
			}
		)
		expired_component.insert()

		# Componente con garantía vigente
		valid_component = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Equipo Vigente",
				"component_type": "Test Component Type",
				"warranty_expiry_date": add_days(today(), 30),
				"quantity": 1,
			}
		)
		valid_component.insert()

		# Verificar estado de garantía
		self.assertTrue(expired_component.is_warranty_expired())
		self.assertFalse(valid_component.is_warranty_expired())

	def test_component_age_calculation(self):
		"""Test cálculo de edad del componente"""
		install_date = add_days(today(), -100)

		component = frappe.get_doc(
			{
				"doctype": "Space Component",
				"component_name": "Equipo Instalado",
				"component_type": "Test Component Type",
				"installation_date": install_date,
				"quantity": 1,
			}
		)
		component.insert()

		# Verificar edad
		age = component.get_component_age_days()
		self.assertEqual(age, 100)

	def tearDown(self):
		"""Limpiar datos de prueba"""
		# Eliminar componentes de prueba
		test_components = frappe.get_all("Space Component", filters={"component_name": ["like", "%Test%"]})
		for comp in test_components:
			frappe.delete_doc("Space Component", comp.name)

		# Eliminar componentes específicos
		component_names = [
			"Bomba de Agua Principal",
			"Motor Eléctrico",
			"Sistema HVAC",
			"Compresor HVAC",
			"Componente 1",
			"Componente 2",
			"Válvula Principal",
			"Sistema de Bombeo",
			"Subsistema de Control",
			"Sensor de Presión",
			"Equipo Vencido",
			"Equipo Vigente",
			"Equipo Instalado",
		]

		for name in component_names:
			components = frappe.get_all("Space Component", filters={"component_name": name})
			for comp in components:
				frappe.delete_doc("Space Component", comp.name)

		# Eliminar Component Type de prueba
		if frappe.db.exists("Component Type", "Test Component Type"):
			frappe.delete_doc("Component Type", "Test Component Type")

		frappe.db.commit()
