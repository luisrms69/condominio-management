# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest
from typing import ClassVar

import frappe

from condominium_management.api_documentation_system.auto_importer import AutoAPIImporter
from condominium_management.api_documentation_system.parser import DocstringParser
from condominium_management.api_documentation_system.scanner import APIScanner
from condominium_management.api_documentation_system.schema_generator import SchemaGenerator
from condominium_management.committee_management.test_base import CommitteeTestBase


class TestAutoDocumentation(CommitteeTestBase):
	"""Tests para el sistema de auto-documentación del Day 2"""

	DOCTYPE_NAME = "API Documentation"
	TEST_IDENTIFIER_PATTERN = "%CTEST_auto%"

	REQUIRED_FIELDS: ClassVar[dict] = {
		"doctype": "API Documentation",
		"api_name": "Test Auto API CTEST",
		"api_path": "/api/auto-test",
		"api_version": "v1",
		"http_method": "GET",
		"description": "API de prueba para auto-documentación",
		"is_active": 1,
		"auto_generated": 1,
	}

	@classmethod
	def cleanup_specific_data(cls):
		"""Cleanup específico para tests de auto-documentación"""
		frappe.db.sql(
			'DELETE FROM `tabAPI Documentation` WHERE api_name LIKE "%CTEST_auto%" OR name LIKE "%CTEST_auto%"'
		)

	def test_api_scanner_basic_functionality(self):
		"""Test básico del scanner de APIs"""
		scanner = APIScanner("condominium_management")

		# Escanear módulo específico pequeño
		apis = scanner.scan_module("api_documentation_system.scanner")

		# Verificar que encuentra las APIs del scanner
		self.assertGreater(len(apis), 0, "Scanner debe encontrar al menos una API")

		# Verificar estructura de API encontrada
		found_api = apis[0]
		required_keys = ["function_name", "module_path", "parameters", "inferred_api_path"]
		for key in required_keys:
			self.assertIn(key, found_api, f"API debe tener clave {key}")

	def test_docstring_parser_google_style(self):
		"""Test del parser de docstrings estilo Google"""
		parser = DocstringParser()

		sample_docstring = """
		Obtiene espacios físicos con filtros.

		Args:
			filters (dict): Filtros de búsqueda
			limit (int): Límite de resultados

		Returns:
			list: Lista de espacios encontrados
		"""

		result = parser.parse_docstring(sample_docstring)

		# Verificar parseo básico
		self.assertIn("description", result)
		self.assertIn("parameters", result)
		self.assertIn("returns", result)

		# Verificar parámetros
		self.assertEqual(len(result["parameters"]), 2)
		self.assertEqual(result["parameters"][0]["name"], "filters")
		self.assertEqual(result["parameters"][0]["type"], "dict")

	def test_schema_generator_request_schema(self):
		"""Test del generador de esquemas para requests"""
		generator = SchemaGenerator()

		sample_parameters = [
			{"name": "filters", "type_annotation": "dict", "is_required": False},
			{"name": "limit", "type_annotation": "int", "is_required": False, "default_value": 20},
			{"name": "doctype", "type_annotation": "str", "is_required": True},
		]

		schema = generator.generate_request_schema(sample_parameters)

		# Verificar estructura básica
		self.assertEqual(schema["type"], "object")
		self.assertIn("properties", schema)
		self.assertIn("required", schema)

		# Verificar campos requeridos
		self.assertIn("doctype", schema["required"])
		self.assertNotIn("filters", schema["required"])

		# Verificar tipos
		self.assertEqual(schema["properties"]["limit"]["type"], "integer")
		if "default" in schema["properties"]["limit"]:
			self.assertEqual(schema["properties"]["limit"]["default"], 20)

	def test_schema_generator_response_schema(self):
		"""Test del generador de esquemas para responses"""
		generator = SchemaGenerator()

		# Test con función tipo get_
		response_schema = generator._infer_response_from_function_name("get_physical_spaces")

		self.assertEqual(response_schema["type"], "object")
		self.assertIn("message", response_schema["properties"])
		self.assertEqual(response_schema["properties"]["message"]["type"], "array")

	def test_auto_importer_dry_run(self):
		"""Test del importador automático en modo dry run"""
		importer = AutoAPIImporter("condominium_management")

		# Importar solo APIs del módulo de testing
		result = importer.import_module_apis(
			"api_documentation_system.scanner", dry_run=True, skip_existing_decorated=False
		)

		# Verificar que no hay errores
		self.assertTrue(result["success"])

		# Verificar estadísticas
		stats = result["statistics"]
		self.assertGreater(stats["total_scanned"], 0)
		self.assertEqual(stats["failed_imports"], 0)

	def test_auto_importer_full_process(self):
		"""Test del proceso completo de auto-importación"""
		importer = AutoAPIImporter("condominium_management")

		# Crear API de prueba para importar
		test_api_info = {
			"function_name": "test_auto_import_ctest",
			"module_path": "test.module",
			"parameters": [{"name": "test_param", "type_annotation": "str", "is_required": True}],
			"docstring": "API de prueba para auto-importación CTEST",
			"inferred_api_path": "/api/test/test-auto-import-ctest",
			"inferred_http_method": "POST",
			"has_api_documentation_decorator": False,
		}

		# Procesar API
		processed_api = importer._process_single_api(test_api_info)

		# Verificar procesamiento
		self.assertIn("docstring_parsed", processed_api)
		self.assertIn("request_schema", processed_api)
		self.assertIn("response_schema", processed_api)
		self.assertTrue(processed_api["auto_generated"])

		# Registrar en DocType
		result = importer._register_api_documentation(processed_api)

		try:
			self.assertTrue(result["success"])
			self.assertEqual(result["action"], "created")

			# Verificar que se creó el documento
			doc_name = result["document_name"]
			doc = frappe.get_doc("API Documentation", doc_name)

			self.assertEqual(doc.function_name, "test_auto_import_ctest")
			self.assertEqual(doc.auto_generated, 1)
			self.assertGreater(len(doc.parameters), 0)

		finally:
			# Cleanup
			if result.get("success") and result.get("document_name"):
				frappe.delete_doc("API Documentation", result["document_name"])

	def test_integration_scanner_parser_schema(self):
		"""Test de integración: scanner + parser + schema generator"""
		# 1. Escanear APIs
		scanner = APIScanner("condominium_management")
		apis = scanner.scan_module("api_documentation_system.auto_importer")

		self.assertGreater(len(apis), 0, "Debe encontrar APIs del auto_importer")

		# 2. Procesar primera API encontrada
		api_info = apis[0]

		# 3. Parsear docstring
		parser = DocstringParser()
		if api_info.get("docstring"):
			docstring_info = parser.parse_docstring(api_info["docstring"])
			api_info["docstring_parsed"] = docstring_info

		# 4. Generar esquemas
		generator = SchemaGenerator()
		schemas = generator.generate_full_api_schema(api_info)

		# Verificar que el pipeline completo funciona
		self.assertIn("request_schema", schemas)
		self.assertIn("response_schema", schemas)
		self.assertIn("openapi_format", schemas)

		# Verificar formato OpenAPI básico
		openapi = schemas["openapi_format"]
		self.assertEqual(openapi["openapi"], "3.0.0")
		self.assertIn("paths", openapi)

	def test_manual_review_detection(self):
		"""Test de detección de APIs que necesitan revisión manual"""
		importer = AutoAPIImporter()

		# API que NO necesita revisión (bien documentada)
		good_api = {"parameters": [{"name": "filters", "type_annotation": "dict"}]}
		good_docstring = {
			"description": "API bien documentada con descripción completa y detallada",
			"parameters": [{"name": "filters", "type": "dict", "description": "Filtros de búsqueda"}],
		}

		self.assertFalse(importer._needs_manual_review(good_api, good_docstring))

		# API que SÍ necesita revisión (mal documentada)
		bad_api = {
			"parameters": [
				{"name": "param1"},  # Sin tipo
				{"name": "param2"},
				{"name": "param3"},
				{"name": "param4"},
				{"name": "param5"},
				{"name": "param6"},  # Muchos parámetros
			]
		}
		bad_docstring = {
			"description": "Corto"  # Descripción muy corta
		}

		self.assertTrue(importer._needs_manual_review(bad_api, bad_docstring))

	def test_type_conversion_mapping(self):
		"""Test de conversión de tipos Python a tipos de API"""
		importer = AutoAPIImporter()

		# Test conversiones básicas
		self.assertEqual(importer._convert_python_type_to_api_type("str"), "string")
		self.assertEqual(importer._convert_python_type_to_api_type("int"), "integer")
		self.assertEqual(importer._convert_python_type_to_api_type("list[str]"), "array")
		self.assertEqual(importer._convert_python_type_to_api_type("dict[str, Any]"), "object")

		# Test fallback
		self.assertEqual(importer._convert_python_type_to_api_type("CustomType"), "string")

	def test_api_name_generation(self):
		"""Test de generación automática de nombres de API"""
		importer = AutoAPIImporter()

		# Test desde metadata del decorador
		api_with_metadata = {"api_documentation_metadata": {"name": "Custom API Name"}}
		self.assertEqual(importer._generate_api_name(api_with_metadata), "Custom API Name")

		# Test desde nombre de función
		api_from_function = {"function_name": "get_physical_spaces_list"}
		self.assertEqual(importer._generate_api_name(api_from_function), "Get Physical Spaces List")

	def test_required_fields_configuration(self):
		"""Override para usar path correcto del API Documentation System"""
		import json
		import os

		if not self.DOCTYPE_NAME:
			self.skipTest("DOCTYPE_NAME not defined")

		# Path correcto para API Documentation System
		doctype_folder = self.DOCTYPE_NAME.lower().replace(" ", "_")
		current_dir = os.path.dirname(os.path.abspath(__file__))
		# current_dir está en test_auto_documentation.py, subir a api_documentation_system
		# luego bajar a doctype/api_documentation/
		json_path = os.path.join(current_dir, "doctype", doctype_folder, f"{doctype_folder}.json")

		# Verificar que el archivo JSON existe
		self.assertTrue(os.path.exists(json_path), f"DocType JSON not found: {json_path}")

		# Leer DocType JSON
		with open(json_path, encoding="utf-8") as f:
			doctype_def = json.load(f)

		# Verificar required fields existen
		required_fields = [f["fieldname"] for f in doctype_def.get("fields", []) if f.get("reqd") == 1]

		self.assertGreater(len(required_fields), 0, f"No required fields found in {self.DOCTYPE_NAME}")

		# Verificar que tenemos datos para todos los campos requeridos
		required_data = self.get_required_fields_data()
		for field in required_fields:
			if field not in ["naming_series", "name"]:  # Skip auto-generated fields
				self.assertIn(
					field,
					required_data,
					f"Required field '{field}' not found in test data for {self.DOCTYPE_NAME}",
				)
