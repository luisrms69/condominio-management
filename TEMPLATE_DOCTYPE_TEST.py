# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

"""
TEMPLATE PARA UNIT TESTS DE DOCTYPES - FRAPPE FRAMEWORK
=======================================================

Este archivo es una plantilla que DEBE ser usada para crear todos los unit tests
de nuevos DocTypes en el módulo Companies del proyecto Condominium Management.

INSTRUCCIONES DE USO:
1. Copiar este archivo como test_{doctype_name}.py
2. Reemplazar todas las instancias de:
   - "TemplateDocType" → "Nombre Real Del DocType"
   - "TestTemplateDocType" → "TestNombreRealDocType"
   - "Template Doc Type" → "Nombre Real Del DocType"
   - "Template de DocType" → "Traducción Española"
3. Implementar los tests específicos según los campos del DocType
4. Verificar que pase todos los tests con: bench run-tests

REGLAS OBLIGATORIAS:
- ✅ Heredar siempre de FrappeTestCase
- ✅ Implementar setUpClass() con super().setUpClass()
- ✅ Usar frappe.set_user("Administrator") en setUp/tearDown
- ✅ Usar flags para evitar duplicación de test data
- ✅ NO hacer cleanup manual - confiar en rollback automático
- ✅ Incluir test_spanish_labels obligatorio
- ✅ Usar ignore_permissions=True en document.insert()
"""

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase


class TestTemplateDocType(FrappeTestCase):
	"""Test cases for Template Doc Type DocType."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()  # CRÍTICO: siempre llamar super()
		cls.create_test_dependencies()

	@classmethod
	def create_test_dependencies(cls):
		"""Create test dependencies if they don't exist."""
		# Usar flags para evitar duplicación de test data
		if getattr(frappe.flags, "test_template_dependencies_created", False):
			return

		# Ejemplo: Crear Company de test si es necesario
		if not frappe.db.exists("Company", "Test Company Template"):
			company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "Test Company Template",
					"abbr": "TCT",
					"default_currency": "MXN",
				}
			)
			company.insert(ignore_permissions=True)

		# Marcar como creado para evitar duplicación
		frappe.flags.test_template_dependencies_created = True

	def setUp(self):
		"""Set up test data before each test method."""
		frappe.set_user("Administrator")  # Usuario consistente para todos los tests

		# Data de test reutilizable - ajustar según campos del DocType
		self.test_data = {
			"field_name_1": "Valor de Test 1",
			"field_name_2": "Valor de Test 2",
			"select_field": "Opción en Español",
			"required_field": "Campo Requerido Test",
		}

	def test_template_doctype_creation(self):
		"""Test basic creation of Template Doc Type."""
		# Crear nuevo documento
		doc = frappe.get_doc({"doctype": "Template Doc Type", **self.test_data})
		doc.insert(ignore_permissions=True)  # Usar ignore_permissions para tests

		# Verificaciones básicas
		self.assertTrue(doc.name)
		self.assertEqual(doc.field_name_1, "Valor de Test 1")
		self.assertEqual(doc.field_name_2, "Valor de Test 2")

		# FrappeTestCase maneja rollback automáticamente - NO hacer doc.delete()

	def test_required_fields_validation(self):
		"""Test that required fields are validated."""
		# Test campo requerido faltante
		with self.assertRaises(frappe.ValidationError):
			doc = frappe.get_doc(
				{
					"doctype": "Template Doc Type",
					"field_name_1": "Test",
					# required_field faltante intencionalmente
				}
			)
			doc.insert(ignore_permissions=True)

	def test_spanish_options_validation(self):
		"""Test that Select/MultiSelect fields accept valid Spanish options."""
		# Definir opciones válidas en español según el DocType
		valid_options = ["Opción Uno", "Opción Dos", "Opción Tres"]

		# Probar cada opción válida
		for option in valid_options:
			doc = frappe.get_doc(
				{
					"doctype": "Template Doc Type",
					"select_field": option,
					"required_field": f"Test {option}",
					**self.test_data,
				}
			)
			doc.insert(ignore_permissions=True)
			self.assertEqual(doc.select_field, option)
			# FrappeTestCase maneja rollback automáticamente

	def test_field_types_validation(self):
		"""Test field types and constraints."""
		# Ejemplo: Test de campo numérico
		doc = frappe.get_doc(
			{
				"doctype": "Template Doc Type",
				"numeric_field": 100,
				"date_field": "2025-01-01",
				"required_field": "Test Numeric",
				**self.test_data,
			}
		)
		doc.insert(ignore_permissions=True)

		self.assertEqual(doc.numeric_field, 100)
		self.assertEqual(str(doc.date_field), "2025-01-01")

		# FrappeTestCase maneja rollback automáticamente

	def test_business_logic_validation(self):
		"""Test specific business logic validations."""
		# Implementar validaciones específicas del DocType
		# Ejemplo: Fechas de inicio/fin, rangos numéricos, etc.

		# Template - ajustar según lógica específica
		doc = frappe.get_doc(
			{
				"doctype": "Template Doc Type",
				"start_date": "2025-01-01",
				"end_date": "2024-12-31",  # Fecha fin antes de inicio
				"required_field": "Test Business Logic",
			}
		)

		# Si hay validación de fechas, debería fallar
		# with self.assertRaises(frappe.ValidationError):
		#     doc.insert(ignore_permissions=True)

		# Por ahora solo insert sin validación específica
		doc.insert(ignore_permissions=True)

	def test_spanish_labels(self):
		"""Test that DocType has proper Spanish labels."""
		meta = frappe.get_meta("Template Doc Type")

		# Verificar label del DocType
		self.assertEqual(meta.get("label"), "Template de DocType")

		# Verificar labels de campos específicos - ajustar según DocType real
		field_1 = meta.get_field("field_name_1")
		if field_1:
			self.assertIn("Campo", field_1.label)  # Verificar que contiene texto español

		required_field = meta.get_field("required_field")
		if required_field:
			self.assertEqual(required_field.reqd, 1)  # Verificar que es requerido

	def test_field_properties(self):
		"""Test field properties like precision, length, etc."""
		meta = frappe.get_meta("Template Doc Type")

		# Ejemplo: Verificar propiedades de campos
		numeric_field = meta.get_field("numeric_field")
		if numeric_field:
			self.assertEqual(numeric_field.fieldtype, "Float")
			# self.assertEqual(numeric_field.precision, 2)  # Si aplica

		select_field = meta.get_field("select_field")
		if select_field:
			self.assertEqual(select_field.fieldtype, "Select")
			# Verificar opciones en español
			if select_field.options:
				options = select_field.options.split("\n")
				for option in options:
					self.assertNotEqual(option.strip(), "")  # No opciones vacías

	def test_naming_and_title(self):
		"""Test naming series and title field if applicable."""
		doc = frappe.get_doc(
			{"doctype": "Template Doc Type", "required_field": "Test Naming", **self.test_data}
		)
		doc.insert(ignore_permissions=True)

		# Verificar que el documento tiene nombre
		self.assertTrue(doc.name)

		# Si hay naming series, verificar patrón
		# import re
		# pattern = r'^TDT-\d{4}-\d+$'  # Ejemplo: TDT-2025-001
		# self.assertIsNotNone(re.match(pattern, doc.name))

		# Si hay title field, verificar
		meta = frappe.get_meta("Template Doc Type")
		if meta.title_field:
			self.assertTrue(getattr(doc, meta.title_field))

	def test_permissions_and_roles(self):
		"""Test permissions configuration."""
		meta = frappe.get_meta("Template Doc Type")

		# Verificar que hay permisos configurados
		self.assertTrue(len(meta.permissions) > 0)

		# Verificar permisos básicos para System Manager
		system_manager_perms = [p for p in meta.permissions if p.role == "System Manager"]
		self.assertTrue(len(system_manager_perms) > 0)

		# Verificar permisos de lectura al menos
		for perm in system_manager_perms:
			self.assertEqual(perm.read, 1)

	def tearDown(self):
		"""Clean up test data after each test method."""
		frappe.set_user("Administrator")  # Reset usuario al original
		# FrappeTestCase maneja rollback de transacciones automáticamente
		# NO hacer cleanup manual de documentos
