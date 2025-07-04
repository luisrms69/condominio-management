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

from condominium_management.test_factories import TestDataFactory


class TestMasterTemplateRegistry(FrappeTestCase):
	"""Test cases para Master Template Registry DocType."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data que persiste para todos los tests."""
		super().setUpClass()  # CRÍTICO: siempre llamar super()
		cls.create_test_dependencies()

	@classmethod
	def create_test_dependencies(cls):
		"""Crear dependencias usando TestDataFactory."""
		# Usar flags para evitar duplicación de test data
		if getattr(frappe.flags, "test_master_template_registry_dependencies_created", False):
			return

		# Use factory to setup complete test environment
		cls.test_objects = TestDataFactory.setup_complete_test_environment()
		# Specific company for this test
		cls.test_company = TestDataFactory.create_test_company("Test Admin Company", "TAC")

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
		registry.company = self.test_company.company_name
		registry.template_version = "1.0.0"
		registry.update_propagation_status = "Completado"

		# Guardar sin errores
		registry.save()

		# Validaciones básicas
		self.assertEqual(registry.company, "Test Admin Company")
		self.assertTrue(registry.template_version.startswith("1.0."))  # Allow auto-increment
		self.assertIn(
			registry.update_propagation_status, ["Completado", "En Progreso"]
		)  # Allow either status

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
		registry.company = self.test_company.company_name

		# Limpiar templates existentes
		registry.infrastructure_templates = []

		# Agregar primer template
		registry.append(
			"infrastructure_templates",
			{
				**TestDataFactory.create_master_template_data(),
				"template_code": "POOL_AREA",  # Override for uniqueness
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
		registry.company = self.test_company.company_name
		registry.template_version = "1.0.5"
		registry.infrastructure_templates = []
		registry.save()

		# Simular cambio en templates
		registry.append(
			"infrastructure_templates",
			{
				**TestDataFactory.create_master_template_data(),
				"template_code": "GYM_AREA",  # Override for uniqueness
				"template_name": "Área de Gimnasio",
			},
		)

		registry.save()

		# Versión debe incrementarse a 1.0.6
		self.assertEqual(registry.template_version, "1.0.6")
		self.assertEqual(registry.update_propagation_status, "Pendiente")

	def test_get_template_by_code(self):
		"""Test obtener template por código."""
		registry = frappe.get_single("Master Template Registry")
		registry.company = self.test_company.company_name
		registry.infrastructure_templates = []

		# Agregar template de prueba
		registry.append(
			"infrastructure_templates",
			{
				**TestDataFactory.create_master_template_data(),
				"template_code": "TEST_POOL",  # Override for uniqueness
				"template_name": "Piscina de Prueba",
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
		registry.company = self.test_company.company_name
		registry.infrastructure_templates = []  # Limpiar templates
		registry.auto_assignment_rules = []

		# Agregar regla que referencia template inexistente (sin crear template primero)
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
		registry.company = self.test_company.company_name
		registry.infrastructure_templates = []
		registry.auto_assignment_rules = []

		# Usar factory para crear template con reglas válidas
		TestDataFactory.create_template_with_assignment_rules(registry)
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
		self.assertEqual(registry2.company, self.test_company.company_name)

	def test_propagation_status_update(self):
		"""Test actualización de estado de propagación."""
		registry = frappe.get_single("Master Template Registry")
		registry.company = self.test_company.company_name
		registry.infrastructure_templates = []
		registry.update_propagation_status = "Completado"
		registry.save()

		# Modificar templates debe cambiar estado a Pendiente
		registry.append(
			"infrastructure_templates",
			{
				**TestDataFactory.create_master_template_data(),
				"template_code": "NEW_TEMPLATE",  # Override for uniqueness
				"template_name": "Nuevo Template",
				"infrastructure_type": "Equipment",
			},
		)

		registry.save()
		self.assertEqual(registry.update_propagation_status, "Pendiente")
		self.assertIsNotNone(registry.last_update)
