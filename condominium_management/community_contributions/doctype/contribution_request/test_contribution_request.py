# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.tests.utils import FrappeTestCase


class TestContributionRequest(FrappeTestCase):
	"""Test cases for Contribution Request."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()
		cls.create_test_data()

	@classmethod
	def create_test_data(cls):
		"""Create reusable test data with flags to avoid duplication."""
		if getattr(frappe.flags, "test_contribution_request_data_created", False):
			return

		# Create test category - ensure it exists
		category_name = "Document Generation-Test Infrastructure"
		if not frappe.db.exists("Contribution Category", category_name):
			test_category = frappe.get_doc(
				{
					"doctype": "Contribution Category",
					"module_name": "Document Generation",
					"contribution_type": "Test Infrastructure",
					"description": "Categoría de prueba para infraestructura",
					"export_doctype": "Master Template Registry",
					"required_fields": json.dumps(["template_code", "template_name", "infrastructure_type"]),
					"is_active": 1,
				}
			)
			test_category.insert(ignore_permissions=True)
			frappe.db.commit()  # Ensure it's committed

		# Ensure test company exists
		if not frappe.db.exists("Company", "Test Company"):
			test_company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "Test Company",
					"default_currency": "MXN",
					"country": "Mexico",
				}
			)
			test_company.insert(ignore_permissions=True)

		frappe.flags.test_contribution_request_data_created = True

	def setUp(self):
		"""Set up before each test method."""
		frappe.set_user("Administrator")

	def test_creation(self):
		"""Test basic creation with Spanish validations."""
		contribution_data = {
			"template_code": "TEST_POOL",
			"template_name": "Piscina de Prueba",
			"infrastructure_type": "Amenity",
			"fields": [{"field_name": "capacity", "field_label": "Capacidad", "field_type": "Int"}],
		}

		request = frappe.get_doc(
			{
				"doctype": "Contribution Request",
				"title": "Template de Piscina de Prueba",
				"contribution_category": "Document Generation-Test Infrastructure",
				"business_justification": "Necesario para testing del sistema",
				"contribution_data": json.dumps(contribution_data),
				"company": "Test Company",
			}
		)
		request.insert(ignore_permissions=True)

		self.assertEqual(request.status, "Draft")
		self.assertEqual(request.title, "Template de Piscina de Prueba")
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
		# Test missing title
		with self.assertRaises(frappe.ValidationError):
			request = frappe.get_doc(
				{
					"doctype": "Contribution Request",
					"contribution_category": "Document Generation-Test Infrastructure",
					"business_justification": "Test",
					"contribution_data": json.dumps({"template_code": "TEST"}),
					"company": "Test Company",
				}
			)
			request.insert(ignore_permissions=True)

	def test_status_transitions(self):
		"""Test that status transitions follow valid workflow."""
		contribution_data = {
			"template_code": "TEST_TRANSITION",
			"template_name": "Template de Transición",
			"infrastructure_type": "Amenity",
		}

		request = frappe.get_doc(
			{
				"doctype": "Contribution Request",
				"title": "Test Status Transitions",
				"contribution_category": "Document Generation-Test Infrastructure",
				"business_justification": "Testing status transitions",
				"contribution_data": json.dumps(contribution_data),
				"company": "Test Company",
			}
		)
		request.insert(ignore_permissions=True)

		# Test valid transition: Draft → Submitted
		request.status = "Submitted"
		request.save()

		# Test valid transition: Submitted → Under Review
		request.status = "Under Review"
		request.save()

		# Test invalid transition: Under Review → Integrated (should go through Approved first)
		with self.assertRaises(frappe.ValidationError):
			request.status = "Integrated"
			request.save()

		# Test valid transition: Under Review → Approved
		request.status = "Approved"
		request.save()

		# Test valid transition: Approved → Integrated
		request.status = "Integrated"
		request.save()

	def test_contribution_data_validation(self):
		"""Test validation of contribution data JSON."""
		# Test invalid JSON
		with self.assertRaises(frappe.ValidationError):
			request = frappe.get_doc(
				{
					"doctype": "Contribution Request",
					"title": "Invalid JSON Test",
					"contribution_category": "Document Generation-Test Infrastructure",
					"business_justification": "Testing invalid JSON",
					"contribution_data": "invalid json {",
					"company": "Test Company",
				}
			)
			request.insert(ignore_permissions=True)

		# Test missing required fields according to category
		incomplete_data = {
			"template_code": "INCOMPLETE",
			"template_name": "Template Incompleto",
			# Missing infrastructure_type (required by category)
		}

		with self.assertRaises(frappe.ValidationError):
			request = frappe.get_doc(
				{
					"doctype": "Contribution Request",
					"title": "Incomplete Data Test",
					"contribution_category": "Document Generation-Test Infrastructure",
					"business_justification": "Testing incomplete data",
					"contribution_data": json.dumps(incomplete_data),
					"company": "Test Company",
				}
			)
			request.insert(ignore_permissions=True)

	def test_audit_fields_update(self):
		"""Test that audit fields are updated correctly on status changes."""
		contribution_data = {
			"template_code": "TEST_AUDIT",
			"template_name": "Template de Auditoría",
			"infrastructure_type": "Amenity",
		}

		request = frappe.get_doc(
			{
				"doctype": "Contribution Request",
				"title": "Test Audit Fields",
				"contribution_category": "Document Generation-Test Infrastructure",
				"business_justification": "Testing audit fields",
				"contribution_data": json.dumps(contribution_data),
				"company": "Test Company",
			}
		)
		request.insert(ignore_permissions=True)

		# Test submission updates
		request.submit()
		self.assertEqual(request.status, "Submitted")
		self.assertEqual(request.submitted_by, "Administrator")
		self.assertIsNotNone(request.submission_date)

		# Test review updates
		request.status = "Under Review"
		request.save()
		self.assertEqual(request.reviewed_by, "Administrator")
		self.assertIsNotNone(request.review_date)

		# Test approval updates
		request.status = "Approved"
		request.save()
		self.assertEqual(request.approved_by, "Administrator")
		self.assertIsNotNone(request.approval_date)

	def test_preview_contribution(self):
		"""Test preview generation for contributions."""
		contribution_data = {
			"template_code": "TEST_PREVIEW",
			"template_name": "Template de Preview",
			"infrastructure_type": "Amenity",
			"fields": [{"field_name": "test_field", "field_label": "Campo de Prueba", "field_type": "Data"}],
		}

		request = frappe.get_doc(
			{
				"doctype": "Contribution Request",
				"title": "Test Preview",
				"contribution_category": "Document Generation-Test Infrastructure",
				"business_justification": "Testing preview functionality",
				"contribution_data": json.dumps(contribution_data),
				"company": "Test Company",
			}
		)
		request.insert(ignore_permissions=True)

		preview = request.preview_contribution()

		# Check that preview contains expected structure
		self.assertIn("template_info", preview)
		self.assertEqual(preview["template_info"]["code"], "TEST_PREVIEW")
		self.assertEqual(preview["template_info"]["name"], "Template de Preview")

	def tearDown(self):
		"""Clean up after each test method."""
		frappe.set_user("Administrator")
