# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import json
import os
from typing import ClassVar

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate


class CommitteeTestBase(FrappeTestCase):
	"""
	Base class for all Committee Management tests
	Implements REGLA #29 + shared infrastructure + mejoras del agente externo
	"""

	# Default configuration - Override in subclasses
	DOCTYPE_NAME = None
	REQUIRED_FIELDS: ClassVar[dict] = {}
	TEST_DATA: ClassVar[dict] = {}
	UNIQUE_TEST_FIELD = "name"
	TEST_IDENTIFIER_PATTERN = "%CTEST%"  # More specific pattern to avoid conflicts

	@classmethod
	def setUpClass(cls):
		"""Set up test data once for all tests - REGLA #29 Pattern Enhanced"""
		# 1. CLEANUP FIRST (orden inverso de dependencias)
		cls.cleanup_all_test_data()

		# 2. SETUP SHARED INFRASTRUCTURE (orden correcto de dependencias)
		cls.setup_shared_infrastructure()

		# 3. SETUP SPECIFIC TEST DATA (override en subclases)
		if hasattr(cls, "setup_test_data"):
			cls.setup_test_data()

	@classmethod
	def tearDownClass(cls):
		"""Enhanced cleanup with error handling"""
		cls.cleanup_all_test_data()

	@classmethod
	def cleanup_all_test_data(cls):
		"""Comprehensive cleanup in reverse dependency order"""
		try:
			# Cleanup específico del DocType (override en subclases)
			if cls.DOCTYPE_NAME and hasattr(cls, "cleanup_specific_data"):
				cls.cleanup_specific_data()

			# Cleanup general (orden inverso de dependencias)
			cleanup_queries = [
				# Child tables primero
				'DELETE FROM `tabProgress Update` WHERE parent LIKE "%CTEST%"',
				'DELETE FROM `tabMeeting Attendee` WHERE parent LIKE "%CTEST%"',
				'DELETE FROM `tabMeeting Agenda Item` WHERE parent LIKE "%CTEST%"',
				'DELETE FROM `tabAssembly Agenda` WHERE parent LIKE "%CTEST%"',
				'DELETE FROM `tabQuorum Record` WHERE parent LIKE "%CTEST%"',
				'DELETE FROM `tabVote Record` WHERE parent LIKE "%CTEST%"',
				'DELETE FROM `tabPoll Option` WHERE parent LIKE "%CTEST%"',
				# Main DocTypes
				'DELETE FROM `tabAgreement Tracking` WHERE responsible_party LIKE "%CTEST%" OR name LIKE "%CTEST%"',
				'DELETE FROM `tabCommittee Meeting` WHERE name LIKE "%CTEST%"',
				'DELETE FROM `tabAssembly Management` WHERE name LIKE "%CTEST%"',
				'DELETE FROM `tabVoting System` WHERE name LIKE "%CTEST%"',
				'DELETE FROM `tabCommittee Poll` WHERE name LIKE "%CTEST%"',
				'DELETE FROM `tabCommunity Event` WHERE name LIKE "%CTEST%"',
				'DELETE FROM `tabCommittee KPI` WHERE name LIKE "%CTEST%"',
				'DELETE FROM `tabMeeting Schedule` WHERE name LIKE "%CTEST%"',
				# Dependencies
				'DELETE FROM `tabCommittee Member` WHERE property_registry LIKE "%-CTEST-%" OR user LIKE "%CTEST%"',
				'DELETE FROM `tabProperty Registry` WHERE property_code LIKE "%-CTEST-%" OR property_name LIKE "%CTEST%"',
				'DELETE FROM `tabUser` WHERE email LIKE "%CTEST%"',
				'DELETE FROM `tabCompany` WHERE company_name LIKE "%CTEST%"',
			]

			for query in cleanup_queries:
				frappe.db.sql(query)

			# Cleanup roles and user roles
			committee_roles = [
				"Presidente del Comité",
				"Secretario del Comité",
				"Tesorero del Comité",
				"Miembro del Comité",
			]
			for role_name in committee_roles:
				# Remove from users first
				frappe.db.sql("DELETE FROM `tabHas Role` WHERE role = %s", (role_name,))
				# Then remove role itself
				frappe.db.sql("DELETE FROM `tabRole` WHERE role_name = %s", (role_name,))

		except Exception as e:
			frappe.log_error(f"Test cleanup warning: {e}", "CommitteeTestBase.cleanup_all_test_data")
		finally:
			frappe.db.commit()
			frappe.clear_cache()

	@classmethod
	def setup_shared_infrastructure(cls):
		"""Setup shared test infrastructure - Company, Users, Roles, Masters"""
		# 1. Skip company creation - use existing company from system
		# This avoids ERPNext Company setup complexity in testing

		# 2. Create test user
		if not frappe.db.exists("User", "CTEST_committee@example.com"):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": "CTEST_committee@example.com",
					"first_name": "CTEST",
					"last_name": "Committee User",
					"send_welcome_email": 0,
				}
			)
			user.insert(ignore_permissions=True)
			frappe.db.commit()

		# 3. Create committee roles
		cls.setup_committee_roles()

		# 4. Create shared masters
		cls.setup_shared_masters()

	@classmethod
	def setup_committee_roles(cls):
		"""Create committee roles if they don't exist"""
		committee_roles = [
			"Presidente del Comité",
			"Secretario del Comité",
			"Tesorero del Comité",
			"Miembro del Comité",
		]

		for role_name in committee_roles:
			try:
				if not frappe.db.exists("Role", role_name):
					role = frappe.get_doc(
						{
							"doctype": "Role",
							"role_name": role_name,
							"desk_access": 1,
						}
					)
					role.insert(ignore_permissions=True)
			except Exception as e:
				frappe.log_error(
					f"Role creation warning for {role_name}: {e}", "CommitteeTestBase.setup_committee_roles"
				)

		frappe.db.commit()

	@classmethod
	def setup_shared_masters(cls):
		"""Create shared master data - llamar desde todos los tests"""
		masters = [
			(
				"Property Usage Type",
				"Residencial",
				{
					"doctype": "Property Usage Type",
					"name": "Residencial",
					"usage_description": "Uso residencial para vivienda",
				},
			),
			(
				"Acquisition Type",
				"Compra",
				{
					"doctype": "Acquisition Type",
					"name": "Compra",
					"requires_notarization": 1,
					"legal_requirements": "Escritura pública",
				},
			),
			(
				"Property Status Type",
				"Activo",
				{
					"doctype": "Property Status Type",
					"name": "Activo",
					"status_description": "Propiedad en estado activo",
				},
			),
			(
				"Space Category",
				"Área Común",
				{
					"doctype": "Space Category",
					"name": "Área Común",
					"category_description": "Espacios de uso común del condominio",
				},
			),
		]

		for doctype, name, data in masters:
			try:
				if not frappe.db.exists(doctype, name):
					doc = frappe.get_doc(data)
					doc.insert(ignore_permissions=True)
			except Exception as e:
				frappe.log_error(
					f"Master creation warning for {doctype} {name}: {e}",
					"CommitteeTestBase.setup_shared_masters",
				)

		frappe.db.commit()

	def get_required_fields_data(self):
		"""Get required fields data for the current DocType - Override en subclases"""
		if self.REQUIRED_FIELDS:
			return self.REQUIRED_FIELDS

		# Fallback: return basic test data
		return {
			"doctype": self.DOCTYPE_NAME or "Agreement Tracking",
		}

	def test_required_fields_configuration(self):
		"""Universal test for DocType JSON configuration validation"""
		if not self.DOCTYPE_NAME:
			self.skipTest("DOCTYPE_NAME not defined")

		# Construir path al JSON del DocType
		doctype_folder = self.DOCTYPE_NAME.lower().replace(" ", "_")
		current_dir = os.path.dirname(os.path.abspath(__file__))
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

	def test_creation_with_all_required_fields(self):
		"""Dynamic test that creates document with all required fields"""
		if not self.DOCTYPE_NAME:
			self.skipTest("DOCTYPE_NAME not defined")

		required_data = self.get_required_fields_data()

		doc = frappe.get_doc(required_data)
		doc.insert(ignore_permissions=True)

		self.assertTrue(doc.name)
		self.assertEqual(doc.doctype, self.DOCTYPE_NAME)

		# Cleanup test document
		doc.delete()
