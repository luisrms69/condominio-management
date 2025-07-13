# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest
from typing import ClassVar

import frappe
from frappe.utils import nowdate

from condominium_management.committee_management.test_base import CommitteeTestBase


class TestAPIDocumentation(CommitteeTestBase):
	"""Tests para API Documentation usando framework establecido"""

	# Configuration for this specific DocType
	DOCTYPE_NAME = "API Documentation"
	TEST_IDENTIFIER_PATTERN = "%CTEST_api%"

	REQUIRED_FIELDS: ClassVar[dict] = {
		"doctype": "API Documentation",
		"api_name": "Test API CTEST",
		"api_path": "/api/test",
		"api_version": "v1",
		"http_method": "GET",
		"description": "API de prueba para testing",
		"is_active": 1,
		"sandbox_enabled": 1,
		"rate_limit": 60,
		"cache_timeout": 300,
	}

	@classmethod
	def cleanup_specific_data(cls):
		"""Cleanup specific to API Documentation tests"""
		frappe.db.sql(
			'DELETE FROM `tabAPI Documentation` WHERE api_name LIKE "%CTEST%" OR name LIKE "%CTEST%"'
		)
		# Child tables
		frappe.db.sql('DELETE FROM `tabAPI Code Example` WHERE parent LIKE "%CTEST%"')
		frappe.db.sql('DELETE FROM `tabAPI Parameter` WHERE parent LIKE "%CTEST%"')
		frappe.db.sql('DELETE FROM `tabAPI Response Code` WHERE parent LIKE "%CTEST%"')

	@classmethod
	def setup_test_data(cls):
		"""Setup minimal test data for API Documentation"""
		# API Documentation doesn't need complex external dependencies
		pass

	def get_required_fields_data(self):
		"""Get required fields data for API Documentation DocType"""
		return self.__class__.REQUIRED_FIELDS

	def test_api_documentation_creation(self):
		"""Test basic API documentation creation"""
		doc = frappe.get_doc(self.get_required_fields_data())
		doc.insert()

		# Verify creation
		self.assertTrue(doc.name)
		self.assertEqual(doc.api_name, "Test API CTEST")
		self.assertEqual(doc.api_path, "/api/test")
		self.assertEqual(doc.http_method, "GET")

		# Clean up
		doc.delete()

	def test_api_path_validation(self):
		"""Test API path format validation"""
		# Test path without leading slash
		data = self.get_required_fields_data().copy()
		data["api_path"] = "api/test/no-slash"

		doc = frappe.get_doc(data)
		doc.insert()

		# Should auto-add leading slash
		self.assertTrue(doc.api_path.startswith("/"))

		doc.delete()

	def test_deprecation_validation(self):
		"""Test deprecation date validation"""
		data = self.get_required_fields_data().copy()
		data["is_deprecated"] = 1
		# Missing deprecation_date should cause error

		doc = frappe.get_doc(data)

		with self.assertRaises(frappe.ValidationError):
			doc.insert()

	def test_rate_limit_validation(self):
		"""Test rate limit validation"""
		data = self.get_required_fields_data().copy()
		data["rate_limit"] = -1  # Invalid negative rate limit

		doc = frappe.get_doc(data)

		with self.assertRaises(frappe.ValidationError):
			doc.insert()

	def test_full_url_generation(self):
		"""Test full URL generation method"""
		doc = frappe.get_doc(self.get_required_fields_data())
		doc.insert()

		full_url = doc.get_full_url()
		self.assertIn("/api/v1/api/test", full_url)

		doc.delete()

	def test_example_request_generation(self):
		"""Test example request generation"""
		doc = frappe.get_doc(self.get_required_fields_data())
		doc.insert()

		curl_example = doc.get_example_request("curl")
		self.assertIn("curl -X GET", curl_example)
		self.assertIn("Authorization: Bearer", curl_example)

		doc.delete()

	def test_child_table_parameters(self):
		"""Test API parameters child table"""
		data = self.get_required_fields_data().copy()
		data["parameters"] = [
			{
				"parameter_name": "limit",
				"parameter_type": "query",
				"data_type": "integer",
				"is_required": 0,
				"default_value": "20",
				"parameter_description": "Número máximo de resultados",
			}
		]

		doc = frappe.get_doc(data)
		doc.insert()

		# Verify child table
		self.assertEqual(len(doc.parameters), 1)
		self.assertEqual(doc.parameters[0].parameter_name, "limit")

		doc.delete()

	def test_response_codes_child_table(self):
		"""Test response codes child table"""
		data = self.get_required_fields_data().copy()
		data["response_codes"] = [
			{
				"status_code": 200,
				"response_description": "Éxito",
				"response_example": '{"status": "success"}',
			},
			{
				"status_code": 404,
				"response_description": "No encontrado",
				"response_example": '{"status": "error", "message": "Not found"}',
			},
		]

		doc = frappe.get_doc(data)
		doc.insert()

		# Verify child table
		self.assertEqual(len(doc.response_codes), 2)
		self.assertEqual(doc.response_codes[0].status_code, 200)
		self.assertEqual(doc.response_codes[1].status_code, 404)

		doc.delete()

	def test_whitelist_functions(self):
		"""Test whitelisted functions"""
		from condominium_management.api_documentation_system.doctype.api_documentation.api_documentation import (
			get_active_apis,
			get_api_documentation_by_path,
		)

		# Create test API doc first
		doc = frappe.get_doc(self.get_required_fields_data())
		doc.insert()

		try:
			# Test get_api_documentation_by_path
			result = get_api_documentation_by_path("/api/test", "GET")
			self.assertIsInstance(result, list)

			# Test get_active_apis
			active_apis = get_active_apis()
			self.assertIsInstance(active_apis, list)

		finally:
			doc.delete()

	def test_required_fields_configuration(self):
		"""Override to use correct module path for API Documentation System"""
		import json
		import os

		if not self.DOCTYPE_NAME:
			self.skipTest("DOCTYPE_NAME not defined")

		# Special path construction for API Documentation System
		doctype_folder = self.DOCTYPE_NAME.lower().replace(" ", "_")
		current_dir = os.path.dirname(os.path.abspath(__file__))
		# current_dir ya está en el lugar correcto: .../api_documentation_system/doctype/api_documentation/
		json_path = os.path.join(current_dir, f"{doctype_folder}.json")

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
