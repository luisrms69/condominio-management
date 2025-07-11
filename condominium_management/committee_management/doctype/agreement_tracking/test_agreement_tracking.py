# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, nowdate


class TestAgreementTrackingCorrected(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		"""Set up test data once for all tests - Forum-validated pattern"""
		# Clean up any existing test data first (critical for unique constraints)
		frappe.db.sql('DELETE FROM `tabCommittee Member` WHERE property_registry = "PROP-TEST-001"')
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code = "PROP-TEST-001"')
		frappe.db.sql('DELETE FROM `tabUser` WHERE email = "test_agreement@example.com"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Committee Company"')
		frappe.db.sql('DELETE FROM `tabAgreement Tracking` WHERE responsible_party LIKE "%test_agreement%"')

		# Clean up committee roles
		committee_roles = [
			"Presidente del Comité",
			"Secretario del Comité",
			"Tesorero del Comité",
			"Miembro del Comité",
		]
		for role_name in committee_roles:
			frappe.db.sql("DELETE FROM `tabRole` WHERE role_name = %s", (role_name,))

		# Commit cleanup before creating new test data
		frappe.db.commit()

		# Now create test data
		cls.setup_test_data()

	@classmethod
	def tearDownClass(cls):
		"""Clean up test data after all tests - Forum-validated pattern"""
		# Clean up all test data using SQL (bypasses validation)
		frappe.db.sql('DELETE FROM `tabCommittee Member` WHERE property_registry = "PROP-TEST-001"')
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code = "PROP-TEST-001"')
		frappe.db.sql('DELETE FROM `tabUser` WHERE email = "test_agreement@example.com"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Committee Company"')
		frappe.db.sql('DELETE FROM `tabAgreement Tracking` WHERE responsible_party LIKE "%test_agreement%"')

		# Clean up masters (only if they exist)
		try:
			frappe.db.sql('DELETE FROM `tabProperty Usage Type` WHERE usage_type_name = "Residencial"')
			frappe.db.sql('DELETE FROM `tabAcquisition Type` WHERE acquisition_type_name = "Compra"')
			frappe.db.sql('DELETE FROM `tabProperty Status Type` WHERE status_type_name = "Activo"')
		except Exception:
			pass  # Ignore if tables don't exist

		# Clean up committee roles
		committee_roles = [
			"Presidente del Comité",
			"Secretario del Comité",
			"Tesorero del Comité",
			"Miembro del Comité",
		]
		for role_name in committee_roles:
			frappe.db.sql("DELETE FROM `tabRole` WHERE role_name = %s", (role_name,))

		# Final commit
		frappe.db.commit()
		frappe.clear_cache()

	@classmethod
	def setup_test_data(cls):
		"""Create test data for agreement tracking tests"""
		# Create test user
		if not frappe.db.exists("User", "test_agreement@example.com"):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": "test_agreement@example.com",
					"first_name": "Test",
					"last_name": "Agreement",
					"user_type": "System User",
				}
			)
			user.insert(ignore_permissions=True)

		# Create test company first (required for property registry)
		if not frappe.db.exists("Company", "Test Committee Company"):
			company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "Test Committee Company",
					"abbr": "TCC",
					"default_currency": "USD",
				}
			)
			company.insert(ignore_permissions=True)

		# Create required master data
		cls.create_test_masters()

		# Create required committee roles in Spanish (needed for Committee Member)
		cls.create_committee_roles()

		# Create test property registry (required for committee member)
		if not frappe.db.exists("Property Registry", {"property_code": "PROP-TEST-001"}):
			property_registry = frappe.get_doc(
				{
					"doctype": "Property Registry",
					"naming_series": "PROP-.YYYY.-",
					"property_name": "Apartamento de Prueba",
					"property_code": "PROP-TEST-001",
					"company": "Test Committee Company",
					"property_usage_type": "Residencial",
					"acquisition_type": "Compra",
					"property_status_type": "Activo",
					"registration_date": nowdate(),
					"total_area_sqm": 85.5,
				}
			)
			property_registry.insert(ignore_permissions=True)
			frappe.db.commit()  # CRITICAL: Commit dependency before creating dependent records
			cls.test_property_registry = property_registry.name
		else:
			cls.test_property_registry = frappe.get_value(
				"Property Registry", {"property_code": "PROP-TEST-001"}, "name"
			)

		# Create test committee member
		if not frappe.db.exists("Committee Member", {"user": "test_agreement@example.com"}):
			member = frappe.get_doc(
				{
					"doctype": "Committee Member",
					"user": "test_agreement@example.com",
					"property_registry": cls.test_property_registry,
					"full_name": "Test Agreement Member",
					"role_in_committee": "Secretario",
					"start_date": nowdate(),
					"is_active": 1,
				}
			)
			member.insert(ignore_permissions=True)
			frappe.db.commit()  # CRITICAL: Commit after creating dependent record
			cls.test_committee_member = member.name
		else:
			cls.test_committee_member = frappe.get_value(
				"Committee Member", {"user": "test_agreement@example.com"}, "name"
			)

	@classmethod
	def create_test_masters(cls):
		"""Create required master data for tests"""
		# Create Property Usage Type
		if not frappe.db.exists("Property Usage Type", "Residencial"):
			usage_type = frappe.get_doc(
				{
					"doctype": "Property Usage Type",
					"usage_type_name": "Residencial",
					"description": "Uso residencial para vivienda",
				}
			)
			usage_type.insert(ignore_permissions=True)

		# Create Acquisition Type
		if not frappe.db.exists("Acquisition Type", "Compra"):
			acquisition_type = frappe.get_doc(
				{
					"doctype": "Acquisition Type",
					"acquisition_type_name": "Compra",
					"description": "Adquisición por compra",
				}
			)
			acquisition_type.insert(ignore_permissions=True)

		# Create Property Status Type
		if not frappe.db.exists("Property Status Type", "Activo"):
			status_type = frappe.get_doc(
				{
					"doctype": "Property Status Type",
					"status_type_name": "Activo",
					"description": "Propiedad activa",
				}
			)
			status_type.insert(ignore_permissions=True)

	@classmethod
	def create_committee_roles(cls):
		"""Create required committee roles in Spanish"""
		committee_roles = [
			"Presidente del Comité",
			"Secretario del Comité",
			"Tesorero del Comité",
			"Miembro del Comité",
		]

		for role_name in committee_roles:
			if not frappe.db.exists("Role", role_name):
				frappe.db.sql(
					"INSERT INTO `tabRole` (name, role_name, desk_access) VALUES (%s, %s, %s)",
					(role_name, role_name, 1),
				)

	def test_agreement_tracking_creation(self):
		"""Test basic agreement tracking creation with ALL REQUIRED FIELDS"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				# ALL REQUIRED FIELDS FROM JSON ANALYSIS:
				"source_type": "Asamblea",  # REQUIRED - Select
				"agreement_date": nowdate(),  # REQUIRED - Date
				"agreement_category": "Operativo",  # REQUIRED - Select
				"responsible_party": self.__class__.test_committee_member,  # REQUIRED - Link
				"priority": "Alta",  # REQUIRED - Select
				"agreement_text": "Acuerdo de prueba para testing automático",  # REQUIRED - Text Editor
				# Optional fields for completeness
				"due_date": add_days(nowdate(), 30),
				"status": "Pendiente",
			}
		)

		agreement.insert()

		# Verify the document was created
		self.assertTrue(agreement.name)
		self.assertEqual(agreement.source_type, "Asamblea")
		self.assertEqual(agreement.status, "Pendiente")
		self.assertEqual(agreement.priority, "Alta")

	def test_required_fields_are_defined_in_doctype(self):
		"""Test that required fields are properly defined in DocType JSON - Configuration verification"""
		# Read the DocType JSON and verify reqd: 1 fields exist
		import json
		import os

		json_path = os.path.join(os.path.dirname(__file__), "agreement_tracking.json")

		with open(json_path) as f:
			doctype_def = json.load(f)

		# Get all required fields from JSON
		required_fields = []
		for field in doctype_def.get("fields", []):
			if field.get("reqd") == 1:
				required_fields.append(field["fieldname"])

		# Verify the expected required fields are present
		expected_required = [
			"source_type",
			"agreement_date",
			"agreement_category",
			"responsible_party",
			"priority",
			"agreement_text",
		]

		for field in expected_required:
			self.assertIn(
				field, required_fields, f"Field '{field}' should be marked as required in DocType JSON"
			)

		# Verify we have the minimum expected number of required fields
		self.assertGreaterEqual(len(required_fields), 6, "Should have at least 6 required fields")

	def test_mandatory_field_validation_runtime_behavior(self):
		"""Test runtime validation behavior - Critical coverage for production safety"""
		# This test ensures that mandatory field validation actually works at runtime
		# Protects against: human error, Frappe bugs, CI/CD version issues

		# Create minimal document with one required field missing
		test_cases = [
			{
				"missing_field": "source_type",
				"data": {
					"doctype": "Agreement Tracking",
					# "source_type": Missing
					"agreement_category": "Operativo",
					"responsible_party": self.__class__.test_committee_member,
					"priority": "Alta",
					"agreement_text": "Test agreement",
				},
			},
			{
				"missing_field": "agreement_category",
				"data": {
					"doctype": "Agreement Tracking",
					"source_type": "Asamblea",
					# "agreement_category": Missing
					"responsible_party": self.__class__.test_committee_member,
					"priority": "Alta",
					"agreement_text": "Test agreement",
				},
			},
			{
				"missing_field": "responsible_party",
				"data": {
					"doctype": "Agreement Tracking",
					"source_type": "Asamblea",
					"agreement_category": "Operativo",
					# "responsible_party": Missing
					"priority": "Alta",
					"agreement_text": "Test agreement",
				},
			},
			{
				"missing_field": "priority",
				"data": {
					"doctype": "Agreement Tracking",
					"source_type": "Asamblea",
					"agreement_category": "Operativo",
					"responsible_party": self.__class__.test_committee_member,
					# "priority": Missing
					"agreement_text": "Test agreement",
				},
			},
			{
				"missing_field": "agreement_text",
				"data": {
					"doctype": "Agreement Tracking",
					"source_type": "Asamblea",
					"agreement_category": "Operativo",
					"responsible_party": self.__class__.test_committee_member,
					"priority": "Alta",
					# "agreement_text": Missing
				},
			},
		]

		for test_case in test_cases:
			with self.subTest(missing_field=test_case["missing_field"]):
				agreement = frappe.get_doc(test_case["data"])

				# Critical: This MUST raise an exception for mandatory fields
				# If this doesn't raise an exception, we have a serious problem
				try:
					agreement.insert(ignore_permissions=True)
					# If we get here, the validation failed - this is BAD
					self.fail(
						f"CRITICAL: Mandatory field '{test_case['missing_field']}' validation failed! "
						f"Document was created without required field. This indicates a serious "
						f"configuration or framework issue that could lead to data corruption."
					)
				except Exception as e:
					# Good - an exception was raised as expected
					# Verify it's the right type of exception
					self.assertIn(
						type(e).__name__,
						["MandatoryError", "ValidationError", "RequiredError"],
						f"Expected mandatory field exception for '{test_case['missing_field']}', "
						f"got {type(e).__name__}: {e!s}",
					)

	def test_successful_agreement_creation_with_all_fields(self):
		"""Test successful creation when all required fields are provided"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"source_type": "Asamblea",
				"agreement_date": nowdate(),
				"agreement_category": "Operativo",
				"responsible_party": self.__class__.test_committee_member,
				"priority": "Alta",
				"agreement_text": "Complete test agreement with all required fields",
				"due_date": add_days(nowdate(), 30),
			}
		)

		# This should succeed without any errors
		agreement.insert(ignore_permissions=True)

		# Verify the document was created successfully
		self.assertTrue(agreement.name)
		self.assertEqual(agreement.source_type, "Asamblea")
		self.assertEqual(agreement.agreement_category, "Operativo")
		self.assertEqual(agreement.priority, "Alta")
		self.assertTrue(agreement.agreement_text)

		# Clean up
		agreement.delete(ignore_permissions=True)

	def test_date_validation(self):
		"""Test that agreement date must be before due date"""
		with self.assertRaises(frappe.ValidationError):
			agreement = frappe.get_doc(
				{
					"doctype": "Agreement Tracking",
					"source_type": "Asamblea",
					"agreement_date": add_days(nowdate(), 30),  # After due date
					"agreement_category": "Operativo",
					"responsible_party": self.__class__.test_committee_member,
					"priority": "Alta",
					"agreement_text": "Test agreement",
					"due_date": nowdate(),  # Before agreement date
				}
			)
			agreement.insert(ignore_permissions=True)

	def test_add_progress_update(self):
		"""Test adding progress updates"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"source_type": "Asamblea",
				"agreement_date": nowdate(),
				"agreement_category": "Operativo",
				"responsible_party": self.__class__.test_committee_member,
				"priority": "Alta",
				"agreement_text": "Test agreement with progress",
				"due_date": add_days(nowdate(), 30),
			}
		)
		agreement.insert()

		# Add progress update
		agreement.add_progress_update("Avance del 25%", 25)
		agreement.save()

		# Verify progress update was added
		self.assertEqual(len(agreement.progress_updates), 1)
		self.assertEqual(agreement.progress_updates[0].percentage_complete, 25)
		self.assertEqual(agreement.completion_percentage, 25)

	def test_auto_status_update_completed(self):
		"""Test that status is automatically updated when completion is 100%"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"source_type": "Asamblea",
				"agreement_date": nowdate(),
				"agreement_category": "Operativo",
				"responsible_party": self.__class__.test_committee_member,
				"priority": "Alta",
				"agreement_text": "Test agreement completion",
				"due_date": add_days(nowdate(), 30),
				"completion_percentage": 100,
			}
		)
		agreement.insert()

		# Should auto-update to Completed
		self.assertEqual(agreement.status, "Completado")

	def test_mark_as_completed(self):
		"""Test marking agreement as completed"""
		agreement = frappe.get_doc(
			{
				"doctype": "Agreement Tracking",
				"source_type": "Asamblea",
				"agreement_date": nowdate(),
				"agreement_category": "Operativo",
				"responsible_party": self.__class__.test_committee_member,
				"priority": "Alta",
				"agreement_text": "Test agreement to complete",
				"due_date": add_days(nowdate(), 30),
			}
		)
		agreement.insert()

		# Mark as completed
		agreement.mark_as_completed("Completado exitosamente")

		# Verify completion
		self.assertEqual(agreement.status, "Completado")
		self.assertEqual(agreement.completion_percentage, 100)

	# Additional tests following the same pattern...
	# All using the corrected field names and including all required fields
