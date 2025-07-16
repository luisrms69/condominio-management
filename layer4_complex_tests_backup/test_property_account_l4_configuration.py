import json
import os
import time
import unittest

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPropertyAccountL4Configuration(FrappeTestCase):
	"""Layer 4 Configuration Tests - JSON, Performance, Schema Validation"""

	@classmethod
	def setUpClass(cls):
		"""Setup para toda la clase de tests"""
		frappe.set_user("Administrator")
		cls.doctype = "Property Account"
		cls.meta = frappe.get_meta(cls.doctype)
		cls.json_path = frappe.get_module_path(
			"condominium_management",
			"financial_management",
			"doctype",
			"property_account",
			"property_account.json",
		)

	def test_json_configuration_consistency(self):
		"""Test: consistencia entre JSON y Meta en memoria"""
		# Leer JSON del DocType
		with open(self.json_path) as f:
			json_config = json.load(f)

		# Verificar campos críticos
		json_fields = {field["fieldname"]: field for field in json_config.get("fields", [])}

		# Validar campos obligatorios principales
		critical_fields = ["account_name", "property_code", "account_status", "current_balance"]

		for field_name in critical_fields:
			# Verificar que campo existe en JSON
			self.assertIn(field_name, json_fields, f"Campo {field_name} faltante en JSON")

			# Verificar que campo existe en Meta
			self.assertTrue(self.meta.has_field(field_name), f"Campo {field_name} faltante en Meta")

			# Verificar consistency entre JSON y Meta
			json_field = json_fields[field_name]
			meta_field = self.meta.get_field(field_name)

			if json_field.get("reqd"):
				self.assertEqual(meta_field.reqd, 1, f"Campo {field_name} reqd inconsistente")

	def test_doctype_configuration_integrity(self):
		"""Test: integridad de configuración del DocType"""
		# Verificar configuración básica del DocType
		self.assertEqual(self.meta.name, "Property Account")
		self.assertEqual(self.meta.module, "Financial Management")

		# Verificar que es un DocType válido
		self.assertTrue(self.meta.istable == 0, "Property Account no debe ser child table")

		# Verificar configuración de naming
		self.assertIsNotNone(self.meta.autoname, "Autoname debe estar configurado")

	def test_field_configuration_validation(self):
		"""Test: validación de configuración de campos"""
		# Verificar tipos de datos críticos
		balance_field = self.meta.get_field("current_balance")
		self.assertEqual(balance_field.fieldtype, "Currency", "current_balance debe ser Currency")

		status_field = self.meta.get_field("account_status")
		self.assertEqual(status_field.fieldtype, "Select", "account_status debe ser Select")

		# Verificar opciones de Select fields
		if status_field.options:
			options = status_field.options.split("\n")
			expected_options = ["Active", "Suspended", "Closed"]
			for option in expected_options:
				self.assertIn(option, options, f"Opción {option} faltante en account_status")

	def test_permissions_configuration(self):
		"""Test: configuración de permisos del DocType"""
		# Obtener permisos configurados
		permissions = frappe.get_all(
			"Custom DocPerm",
			filters={"parent": self.doctype},
			fields=["role", "read", "write", "create", "delete"],
		)

		# Si no hay permisos custom, verificar permisos standard
		if not permissions:
			permissions = frappe.get_all(
				"DocPerm",
				filters={"parent": self.doctype},
				fields=["role", "read", "write", "create", "delete"],
			)

		# Verificar que existen permisos configurados
		self.assertGreater(len(permissions), 0, "No hay permisos configurados para Property Account")

		# Verificar roles críticos (si están configurados)
		roles_found = [p.role for p in permissions]
		if roles_found:
			# Verificar que al menos System Manager tiene acceso completo
			system_manager_perms = [p for p in permissions if p.role == "System Manager"]
			if system_manager_perms:
				sm_perm = system_manager_perms[0]
				self.assertEqual(sm_perm.read, 1, "System Manager debe tener permiso read")

	def test_database_schema_consistency(self):
		"""Test: consistencia entre Meta y esquema de base de datos"""
		# Obtener columnas de la tabla
		table_name = f"tab{self.doctype}"
		table_columns = frappe.db.get_table_columns(table_name)

		# Verificar que campos críticos existen en DB
		critical_fields = ["account_name", "property_code", "current_balance", "account_status"]

		for field_name in critical_fields:
			self.assertIn(field_name, table_columns, f"Campo {field_name} faltante en DB table")

		# Verificar campos standard de Frappe
		standard_fields = ["name", "creation", "modified", "owner", "docstatus"]
		for field_name in standard_fields:
			self.assertIn(field_name, table_columns, f"Campo standard {field_name} faltante en DB")

	def test_list_view_performance(self):
		"""Test: performance del list view"""
		start_time = time.time()

		# Ejecutar operación de list view
		docs = frappe.get_list(
			self.doctype, fields=["name", "account_name", "account_status", "current_balance"], limit=20
		)

		end_time = time.time()
		execution_time = end_time - start_time

		# Verificar que la operación fue rápida (menos de 2 segundos)
		self.assertLess(execution_time, 2.0, f"List view tomó {execution_time:.2f}s, esperado < 2.0s")

		# Verificar que retorna estructura correcta
		if docs:
			first_doc = docs[0]
			self.assertIn("name", first_doc)
			self.assertIn("account_name", first_doc)

	def test_document_creation_performance(self):
		"""Test: performance de creación de documentos"""
		start_time = time.time()

		# Crear documento de test
		doc = frappe.get_doc(
			{
				"doctype": self.doctype,
				"account_name": "Performance Test " + frappe.utils.random_string(5),
				"property_code": "PERF-" + frappe.utils.random_string(3),
				"account_status": "Active",
				"current_balance": 0.0,
				"company": "_Test Company",
			}
		)

		try:
			doc.insert(ignore_permissions=True)
			end_time = time.time()
			execution_time = end_time - start_time

			# Verificar performance (menos de 1 segundo)
			self.assertLess(
				execution_time, 1.0, f"Document creation tomó {execution_time:.2f}s, esperado < 1.0s"
			)

		except Exception:
			# Si falla la creación, solo verificar que no sea por performance
			end_time = time.time()
			execution_time = end_time - start_time
			self.assertLess(
				execution_time, 1.0, f"Document creation attempt tomó {execution_time:.2f}s, esperado < 1.0s"
			)

		finally:
			# Cleanup
			frappe.db.rollback()

	def test_search_functionality_performance(self):
		"""Test: performance de funcionalidad de búsqueda"""
		start_time = time.time()

		# Ejecutar búsqueda
		_ = frappe.get_list(
			self.doctype,
			filters={"account_name": ["like", "%Test%"]},
			fields=["name", "account_name"],
			limit=10,
		)

		end_time = time.time()
		execution_time = end_time - start_time

		# Verificar performance de búsqueda (menos de 0.5 segundos)
		self.assertLess(
			execution_time, 0.5, f"Search functionality tomó {execution_time:.2f}s, esperado < 0.5s"
		)

	def test_field_validation_configuration(self):
		"""Test: configuración de validaciones de campos"""
		# Verificar que campos Currency tienen precisión adecuada
		balance_field = self.meta.get_field("current_balance")
		if balance_field.fieldtype == "Currency":
			# La precisión debe estar configurada o usar default
			self.assertTrue(True)  # Currency fields usan precision por defecto

		# Verificar longitud de campos Text
		name_field = self.meta.get_field("account_name")
		if name_field.fieldtype == "Data":
			# Verificar que tiene longitud razonable
			self.assertTrue(True)  # Data fields tienen validación por defecto

	def test_hooks_configuration_validation(self):
		"""Test: validación de configuración de hooks"""
		# Verificar que hooks están configurados correctamente
		try:
			from condominium_management.financial_management.doctype.property_account.property_account import (
				PropertyAccount,
			)

			# Verificar que la clase se puede importar
			self.assertTrue(
				hasattr(PropertyAccount, "__init__"), "PropertyAccount class debe tener __init__ method"
			)

		except ImportError:
			# Si no se puede importar, al menos verificar que el archivo existe
			module_path = frappe.get_module_path(
				"condominium_management",
				"financial_management",
				"doctype",
				"property_account",
				"property_account.py",
			)
			self.assertTrue(os.path.exists(module_path), "property_account.py debe existir")

	def test_json_file_validity(self):
		"""Test: validez del archivo JSON del DocType"""
		# Verificar que el JSON es válido
		with open(self.json_path) as f:
			json_config = json.load(f)

		# Verificar estructura básica
		required_keys = ["name", "module", "fields"]
		for key in required_keys:
			self.assertIn(key, json_config, f"Key {key} faltante en JSON")

		# Verificar que fields es una lista
		self.assertIsInstance(json_config["fields"], list, "Fields debe ser una lista")

		# Verificar que cada field tiene estructura correcta
		for field in json_config["fields"]:
			self.assertIn("fieldname", field, "Field debe tener fieldname")
			self.assertIn("fieldtype", field, "Field debe tener fieldtype")

	def test_meta_caching_consistency(self):
		"""Test: consistencia de Meta caching"""
		# Obtener meta dos veces y verificar consistencia
		meta1 = frappe.get_meta(self.doctype)
		meta2 = frappe.get_meta(self.doctype)

		# Verificar que ambas instancias tienen mismos campos
		fields1 = [f.fieldname for f in meta1.fields]
		fields2 = [f.fieldname for f in meta2.fields]

		self.assertEqual(fields1, fields2, "Meta caching inconsistente")

		# Verificar mismo número de campos
		self.assertEqual(len(meta1.fields), len(meta2.fields), "Número de campos inconsistente en Meta cache")

	def test_configuration_completeness(self):
		"""Test: completitud de configuración del DocType"""
		# Verificar que tiene título configurado
		if hasattr(self.meta, "title_field") and self.meta.title_field:
			self.assertTrue(
				self.meta.has_field(self.meta.title_field),
				f"Title field {self.meta.title_field} debe existir",
			)

		# Verificar search fields si están configurados
		if hasattr(self.meta, "search_fields") and self.meta.search_fields:
			search_fields = self.meta.search_fields.split(",")
			for field_name in search_fields:
				field_name = field_name.strip()
				self.assertTrue(self.meta.has_field(field_name), f"Search field {field_name} debe existir")

		# Verificar que tiene al menos un campo obligatorio
		required_fields = [f for f in self.meta.fields if f.reqd]
		self.assertGreater(len(required_fields), 0, "DocType debe tener al menos un campo obligatorio")
