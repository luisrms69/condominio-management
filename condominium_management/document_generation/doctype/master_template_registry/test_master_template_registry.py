# Copyright (c) 2025, Buzola and Contributors
# See license.txt

"""
Unit Tests para Master Template Registry - Document Generation Module
====================================================================

Tests completos siguiendo estándares de Frappe Framework y CLAUDE.md
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase


class TestMasterTemplateRegistry(FrappeTestCase):
	"""Test cases para Master Template Registry DocType."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data que persiste para todos los tests."""
		super().setUpClass()  # CRÍTICO: siempre llamar super()
		cls.create_test_dependencies()

	@classmethod
	def create_test_dependencies(cls):
		"""Crear dependencias de test si no existen."""
		# Usar flags para evitar duplicación de test data
		if getattr(frappe.flags, "test_master_template_registry_dependencies_created", False):
			return

		# Crear empresa de prueba si no existe
		if not frappe.db.exists("Company", "Test Admin Company"):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "Test Admin Company",
					"abbr": "TAC",
					"default_currency": "MXN",
					"country": "Mexico",
					"is_group": 1,
				}
			).insert(ignore_permissions=True)

		frappe.flags.test_master_template_registry_dependencies_created = True

	def setUp(self):
		"""Set up antes de cada test method."""
		frappe.set_user("Administrator")  # Usuario consistente para tests

	def tearDown(self):
		"""Clean up después de cada test method."""
		frappe.set_user("Administrator")  # Reset usuario
		# FrappeTestCase maneja rollback automáticamente

	def test_creation(self):
		"""Test creación básica del Master Template Registry."""
		# Obtener el Single DocType
		registry = frappe.get_single("Master Template Registry")
		registry.company = "Test Admin Company"
		registry.template_version = "1.0.0"
		registry.update_propagation_status = "Completado"

		# Guardar sin errores
		registry.save()

		# Validaciones básicas
		self.assertEqual(registry.company, "Test Admin Company")
		self.assertTrue(registry.template_version.startswith("1.0."))  # Allow auto-increment
		self.assertEqual(registry.update_propagation_status, "Completado")

	def test_spanish_labels(self):
		"""Test que DocType tiene labels apropiados en español."""
		meta = frappe.get_meta("Master Template Registry")

		# Verificar labels en español de campos principales
		company_field = meta.get_field("company")
		self.assertEqual(company_field.label, "Empresa Administradora")

		infrastructure_templates_field = meta.get_field("infrastructure_templates")
		self.assertEqual(infrastructure_templates_field.label, "Templates de Infraestructura")

		template_version_field = meta.get_field("template_version")
		self.assertEqual(template_version_field.label, "Versión de Templates")

	def test_required_fields_validation(self):
		"""Test validación de campos requeridos."""
		registry = frappe.get_single("Master Template Registry")

		# Test que company es requerido
		registry.company = ""

		with self.assertRaises(frappe.ValidationError):
			registry.save()

	def test_template_code_uniqueness(self):
		"""Test que códigos de templates sean únicos."""
		registry = frappe.get_single("Master Template Registry")
		registry.company = "Test Admin Company"

		# Limpiar templates existentes
		registry.infrastructure_templates = []

		# Agregar primer template
		registry.append(
			"infrastructure_templates",
			{
				"template_code": "POOL_AREA",
				"template_name": "Área de Piscina",
				"infrastructure_type": "Amenity",
			},
		)

		# Agregar template duplicado
		registry.append(
			"infrastructure_templates",
			{
				"template_code": "POOL_AREA",  # Duplicado
				"template_name": "Otra Piscina",
				"infrastructure_type": "Amenity",
			},
		)

		# Debe fallar por código duplicado
		with self.assertRaises(frappe.ValidationError):
			registry.save()

	def test_version_increment(self):
		"""Test incremento automático de versión."""
		registry = frappe.get_single("Master Template Registry")
		registry.company = "Test Admin Company"
		registry.template_version = "1.0.5"
		registry.infrastructure_templates = []
		registry.save()

		# Simular cambio en templates
		registry.append(
			"infrastructure_templates",
			{
				"template_code": "GYM_AREA",
				"template_name": "Área de Gimnasio",
				"infrastructure_type": "Amenity",
			},
		)

		registry.save()

		# Versión debe incrementarse a 1.0.6
		self.assertEqual(registry.template_version, "1.0.6")
		self.assertEqual(registry.update_propagation_status, "Pendiente")

	def test_get_template_by_code(self):
		"""Test obtener template por código."""
		registry = frappe.get_single("Master Template Registry")
		registry.company = "Test Admin Company"
		registry.infrastructure_templates = []

		# Agregar template de prueba
		registry.append(
			"infrastructure_templates",
			{
				"template_code": "TEST_POOL",
				"template_name": "Piscina de Prueba",
				"infrastructure_type": "Amenity",
				"template_content": "Template content here",
			},
		)
		registry.save()

		# Test método get_template_by_code
		template = registry.get_template_by_code("TEST_POOL")
		self.assertIsNotNone(template)
		self.assertEqual(template["template_name"], "Piscina de Prueba")

		# Test template inexistente
		template = registry.get_template_by_code("NONEXISTENT")
		self.assertIsNone(template)

	def test_assignment_rule_validation(self):
		"""Test validación de reglas de asignación."""
		registry = frappe.get_single("Master Template Registry")
		registry.company = "Test Admin Company"
		registry.auto_assignment_rules = []

		# Agregar regla que referencia template inexistente
		registry.append(
			"auto_assignment_rules",
			{
				"entity_type": "Amenity",
				"entity_subtype": "piscina",
				"target_template": "NONEXISTENT_TEMPLATE",
			},
		)

		# Debe fallar por template inexistente
		with self.assertRaises(frappe.ValidationError):
			registry.save()

	def test_get_assignment_rule_for_entity(self):
		"""Test obtener regla de asignación para entidad."""
		registry = frappe.get_single("Master Template Registry")
		registry.company = "Test Admin Company"
		registry.infrastructure_templates = []
		registry.auto_assignment_rules = []

		# Agregar template
		registry.append(
			"infrastructure_templates",
			{
				"template_code": "POOL_TEMPLATE",
				"template_name": "Template Piscina",
				"infrastructure_type": "Amenity",
			},
		)

		# Agregar regla
		registry.append(
			"auto_assignment_rules",
			{"entity_type": "Amenity", "entity_subtype": "piscina", "target_template": "POOL_TEMPLATE"},
		)
		registry.save()

		# Test obtener regla
		rule = registry.get_assignment_rule_for_entity("Amenity", "piscina")
		self.assertIsNotNone(rule)
		self.assertEqual(rule["target_template"], "POOL_TEMPLATE")

		# Test regla inexistente
		rule = registry.get_assignment_rule_for_entity("Nonexistent", "type")
		self.assertIsNone(rule)

	def test_single_doctype_behavior(self):
		"""Test comportamiento de Single DocType."""
		# Single DocTypes deben tener un solo registro
		registry1 = frappe.get_single("Master Template Registry")
		registry2 = frappe.get_single("Master Template Registry")

		# Deben ser el mismo objeto
		self.assertEqual(registry1.name, registry2.name)

		# Modificación en uno debe reflejarse en el otro después de reload
		registry1.company = "Test Admin Company"
		registry1.save()

		registry2.reload()
		self.assertEqual(registry2.company, "Test Admin Company")

	def test_propagation_status_update(self):
		"""Test actualización de estado de propagación."""
		registry = frappe.get_single("Master Template Registry")
		registry.company = "Test Admin Company"
		registry.infrastructure_templates = []
		registry.update_propagation_status = "Completado"
		registry.save()

		# Modificar templates debe cambiar estado a Pendiente
		registry.append(
			"infrastructure_templates",
			{
				"template_code": "NEW_TEMPLATE",
				"template_name": "Nuevo Template",
				"infrastructure_type": "Equipment",
			},
		)

		registry.save()
		self.assertEqual(registry.update_propagation_status, "Pendiente")
		self.assertIsNotNone(registry.last_update)
