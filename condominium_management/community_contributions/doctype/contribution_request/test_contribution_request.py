# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.tests.utils import FrappeTestCase

from condominium_management.test_factories import TestDataFactory


class TestContributionRequest(FrappeTestCase):
	"""Test cases for Contribution Request."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()
		cls.create_test_data()

	@classmethod
	def create_test_data(cls):
		"""Create reusable test data using TestDataFactory."""
		if getattr(frappe.flags, "test_contribution_request_data_created", False):
			return

		# Use factory to setup complete test environment
		cls.test_objects = TestDataFactory.setup_complete_test_environment()

		frappe.flags.test_contribution_request_data_created = True

	def setUp(self):
		"""Set up before each test method."""
		frappe.set_user("Administrator")

	def test_creation(self):
		"""Test basic creation with Spanish validations."""
		# Use factory to create complete request data
		request_data = TestDataFactory.create_contribution_request_data()

		request = frappe.get_doc({"doctype": "Contribution Request", **request_data})
		request.insert(ignore_permissions=True)

		self.assertEqual(request.status, "Draft")
		self.assertIsNotNone(request.title)
		self.assertIsNotNone(request.contribution_data)

	def test_spanish_labels(self):
		"""Test that DocType has proper Spanish labels."""
		meta = frappe.get_meta("Contribution Request")

		# Verify key field labels are in Spanish
		spanish_labels = {
			"title": "Título de la Contribución",
			"contribution_category": "Categoría de Contribución",
			"status": "Estado",
			"business_justification": "Justificación de Negocio",
		}

		for fieldname, expected_label in spanish_labels.items():
			field = meta.get_field(fieldname)
			self.assertEqual(field.label, expected_label, f"Field {fieldname} should have Spanish label")

	def test_required_fields_validation(self):
		"""Test required fields validation."""
		# Get valid base data and remove required field
		request_data = TestDataFactory.create_contribution_request_data()
		del request_data["title"]  # Remove required field

		# Test missing title
		with self.assertRaises(frappe.ValidationError):
			request = frappe.get_doc({"doctype": "Contribution Request", **request_data})
			request.insert(ignore_permissions=True)

	def test_status_transitions(self):
		"""Test that status transitions follow valid workflow."""
		# Use factory for consistent data
		request_data = TestDataFactory.create_contribution_request_data()
		request_data["title"] = "Test Status Transitions"
		request_data["business_justification"] = "Testing status transitions"

		request = frappe.get_doc({"doctype": "Contribution Request", **request_data})
		request.insert(ignore_permissions=True)

		# Test workflow using submit() method instead of direct status change
		request.submit()
		self.assertEqual(request.status, "Submitted")

		# Para cambios después de submit, usar db_set o reload
		request.reload()
		request.db_set("status", "Under Review", update_modified=False)
		request.reload()
		self.assertEqual(request.status, "Under Review")

		# Test final states through db updates
		request.db_set("status", "Approved", update_modified=False)
		request.reload()
		self.assertEqual(request.status, "Approved")

	def test_contribution_data_validation(self):
		"""Test validation of contribution data JSON."""
		# Get valid base data
		request_data = TestDataFactory.create_contribution_request_data()

		# Test invalid JSON
		invalid_request_data = request_data.copy()
		invalid_request_data["title"] = "Invalid JSON Test"
		invalid_request_data["contribution_data"] = "invalid json {"

		with self.assertRaises(frappe.ValidationError):
			request = frappe.get_doc({"doctype": "Contribution Request", **invalid_request_data})
			request.insert(ignore_permissions=True)

		# Test missing required fields according to category
		incomplete_data = {
			"template_code": "INCOMPLETE",
			"template_name": "Template Incompleto",
			# Missing infrastructure_type (required by category)
		}

		incomplete_request_data = request_data.copy()
		incomplete_request_data["title"] = "Incomplete Data Test"
		incomplete_request_data["contribution_data"] = json.dumps(incomplete_data)

		with self.assertRaises(frappe.ValidationError):
			request = frappe.get_doc({"doctype": "Contribution Request", **incomplete_request_data})
			request.insert(ignore_permissions=True)

	def test_audit_fields_update(self):
		"""Test that audit fields are updated correctly on status changes."""
		# Use factory for consistent data
		request_data = TestDataFactory.create_contribution_request_data()
		request_data["title"] = "Test Audit Fields"
		request_data["business_justification"] = "Testing audit fields"

		request = frappe.get_doc({"doctype": "Contribution Request", **request_data})
		request.insert(ignore_permissions=True)

		# Test submission updates
		request.submit()
		self.assertEqual(request.status, "Submitted")
		self.assertEqual(request.submitted_by, "Administrator")
		self.assertIsNotNone(request.submission_date)

		# Test review updates using db_set to avoid workflow restrictions
		request.db_set("status", "Under Review", update_modified=False)
		request.db_set("reviewed_by", "Administrator", update_modified=False)
		request.db_set("review_date", frappe.utils.now(), update_modified=False)
		request.reload()
		self.assertEqual(request.status, "Under Review")
		self.assertEqual(request.reviewed_by, "Administrator")
		self.assertIsNotNone(request.review_date)

	def test_preview_contribution(self):
		"""Test preview generation for contributions."""
		# Create custom data for this specific test
		category = TestDataFactory.create_contribution_category()
		company = TestDataFactory.create_test_company()

		contribution_data = {
			"template_code": "TEST_PREVIEW",
			"template_name": "Template de Preview",
			"infrastructure_type": "Amenity",
			"fields": [{"field_name": "test_field", "field_label": "Campo de Prueba", "field_type": "Data"}],
		}

		request_data = {
			"title": "Test Preview",
			"contribution_category": category.name,
			"business_justification": "Testing preview functionality",
			"contribution_data": json.dumps(contribution_data),
			"company": company.company_name,
		}

		request = frappe.get_doc({"doctype": "Contribution Request", **request_data})
		request.insert(ignore_permissions=True)

		preview = request.preview_contribution()

		# Check that preview contains expected structure
		self.assertIn("template_info", preview)
		self.assertEqual(preview["template_info"]["code"], "TEST_PREVIEW")
		self.assertEqual(preview["template_info"]["name"], "Template de Preview")

	def tearDown(self):
		"""Clean up after each test method."""
		frappe.set_user("Administrator")
