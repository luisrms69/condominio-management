# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.tests.utils import FrappeTestCase


class TestRegisteredContributorSite(FrappeTestCase):
	"""Test cases for Registered Contributor Site DocType."""

	@classmethod
	def setUpClass(cls):
		"""Set up test data that persists for all tests in this class."""
		super().setUpClass()
		cls.create_test_data()

	@classmethod
	def create_test_data(cls):
		"""Create reusable test data with flags to avoid duplication."""
		if getattr(frappe.flags, "test_registered_contributor_site_data_created", False):
			return

		# Cleanup existing test data
		frappe.db.delete("Registered Contributor Site", {"site_url": ["like", "%test%"]})
		frappe.db.commit()

		frappe.flags.test_registered_contributor_site_data_created = True

	def setUp(self):
		"""Set up before each test method."""
		frappe.set_user("Administrator")

	def test_site_creation(self):
		"""Test basic creation of registered contributor site."""
		site = frappe.get_doc(
			{
				"doctype": "Registered Contributor Site",
				"site_url": "https://test-admin.condominio.com",
				"company_name": "Test Administradora SA",
				"contact_email": "admin@testcompany.com",
				"business_justification": "Site de prueba para testing",
			}
		)

		site.insert(ignore_permissions=True)

		# Validations
		self.assertEqual(site.site_url, "https://test-admin.condominio.com")
		self.assertEqual(site.company_name, "Test Administradora SA")
		self.assertTrue(site.is_active)
		self.assertIsNotNone(site.api_key)
		self.assertIsNotNone(site.registration_date)
		self.assertEqual(site.total_contributions, 0)

		# Verify API key is generated
		self.assertEqual(len(site.api_key), 64)  # SHA-256 hash length

		# Verify security logs initialized (should have at least initial log)
		security_logs = json.loads(site.security_logs)
		self.assertGreaterEqual(len(security_logs), 1)
		# Find the site_registered action (should be present)
		registration_logs = [log for log in security_logs if log["action"] == "site_registered"]
		self.assertEqual(len(registration_logs), 1)

	def test_spanish_labels(self):
		"""Test that DocType has proper Spanish labels."""
		meta = frappe.get_meta("Registered Contributor Site")

		# Test some key field labels are in Spanish
		field_labels = {field.fieldname: field.label for field in meta.fields}

		self.assertEqual(field_labels.get("site_url"), "URL del Site")
		self.assertEqual(field_labels.get("company_name"), "Nombre de la Empresa")
		self.assertEqual(field_labels.get("contact_email"), "Email de Contacto")
		self.assertEqual(field_labels.get("is_active"), "Está Activo")

	def test_url_validation(self):
		"""Test URL validation and normalization."""
		# Test automatic https addition
		site = frappe.get_doc(
			{
				"doctype": "Registered Contributor Site",
				"site_url": "test-validation.condominio.com",  # No protocol
				"company_name": "Test Company",
				"contact_email": "test@validation.com",
				"business_justification": "Testing URL validation",
			}
		)

		site.insert(ignore_permissions=True)
		self.assertEqual(site.site_url, "https://test-validation.condominio.com")

		# Test duplicate URL validation
		with self.assertRaises(frappe.ValidationError):
			duplicate_site = frappe.get_doc(
				{
					"doctype": "Registered Contributor Site",
					"site_url": "https://test-validation.condominio.com",  # Same URL
					"company_name": "Another Company",
					"contact_email": "another@test.com",
					"business_justification": "Duplicate test",
				}
			)
			duplicate_site.insert(ignore_permissions=True)

	def test_api_key_regeneration(self):
		"""Test API key regeneration functionality."""
		site = frappe.get_doc(
			{
				"doctype": "Registered Contributor Site",
				"site_url": "https://test-regen.condominio.com",
				"company_name": "Regen Test Company",
				"contact_email": "regen@test.com",
				"business_justification": "Testing API key regeneration",
			}
		)

		site.insert(ignore_permissions=True)
		original_api_key = site.api_key

		# Regenerate API key
		site.regenerate_api_key()

		# Validations
		self.assertNotEqual(site.api_key, original_api_key)
		self.assertEqual(len(site.api_key), 64)
		self.assertIsNotNone(site.api_key_generated_date)

		# Check security log
		security_logs = json.loads(site.security_logs)
		regen_events = [log for log in security_logs if log["action"] == "api_key_regenerated"]
		self.assertGreaterEqual(len(regen_events), 1)

	def test_contribution_tracking(self):
		"""Test contribution counting and statistics."""
		site = frappe.get_doc(
			{
				"doctype": "Registered Contributor Site",
				"site_url": "https://test-tracking.condominio.com",
				"company_name": "Tracking Test Company",
				"contact_email": "tracking@test.com",
				"business_justification": "Testing contribution tracking",
			}
		)

		site.insert(ignore_permissions=True)

		# Test initial state
		self.assertEqual(site.total_contributions, 0)

		# Increment contribution count
		site.increment_contribution_count()

		# Validations
		self.assertEqual(site.total_contributions, 1)
		self.assertIsNotNone(site.last_contribution)
		self.assertIsNotNone(site.contribution_stats)

		# Check stats format
		stats = json.loads(site.contribution_stats)
		self.assertIsInstance(stats, dict)
		self.assertIn("last_updated", stats)

	def test_failed_requests_handling(self):
		"""Test failed requests counting and auto-deactivation."""
		site = frappe.get_doc(
			{
				"doctype": "Registered Contributor Site",
				"site_url": "https://test-failed.condominio.com",
				"company_name": "Failed Test Company",
				"contact_email": "failed@test.com",
				"business_justification": "Testing failed requests handling",
			}
		)

		site.insert(ignore_permissions=True)

		# Test initial state
		self.assertEqual(site.failed_requests_count, 0)
		self.assertTrue(site.is_active)

		# Increment failed requests
		site.increment_failed_requests()

		# Validations
		self.assertEqual(site.failed_requests_count, 1)
		self.assertTrue(site.is_active)  # Still active with few failures

		# Test successful API usage resets failures
		site.record_successful_api_usage()
		self.assertEqual(site.failed_requests_count, 0)

	def test_masked_api_key(self):
		"""Test API key masking for security."""
		site = frappe.get_doc(
			{
				"doctype": "Registered Contributor Site",
				"site_url": "https://test-mask.condominio.com",
				"company_name": "Mask Test Company",
				"contact_email": "mask@test.com",
				"business_justification": "Testing API key masking",
			}
		)

		site.insert(ignore_permissions=True)

		masked = site.get_masked_api_key()

		# Validations
		self.assertTrue(masked.endswith("*" * 56))  # 64 - 8 = 56 asterisks
		self.assertTrue(masked.startswith(site.api_key[:8]))
		self.assertNotEqual(masked, site.api_key)

	def test_connection_instructions(self):
		"""Test generation of connection instructions."""
		site = frappe.get_doc(
			{
				"doctype": "Registered Contributor Site",
				"site_url": "https://test-instructions.condominio.com",
				"company_name": "Instructions Test Company",
				"contact_email": "instructions@test.com",
				"business_justification": "Testing connection instructions",
			}
		)

		site.insert(ignore_permissions=True)

		instructions = site.get_connection_instructions()

		# Validations
		self.assertIsInstance(instructions, dict)
		self.assertEqual(instructions["site_url"], site.site_url)
		self.assertEqual(instructions["api_key"], site.api_key)
		self.assertIn("target_site", instructions)
		self.assertIn("api_endpoint", instructions)
		self.assertIn("instructions", instructions)
		self.assertIn("sample_code", instructions)

		# Check instructions are useful
		self.assertIsInstance(instructions["instructions"], list)
		self.assertGreater(len(instructions["instructions"]), 0)

	def test_security_logging(self):
		"""Test security event logging functionality."""
		site = frappe.get_doc(
			{
				"doctype": "Registered Contributor Site",
				"site_url": "https://test-security.condominio.com",
				"company_name": "Security Test Company",
				"contact_email": "security@test.com",
				"business_justification": "Testing security logging",
			}
		)

		site.insert(ignore_permissions=True)

		# Test manual security event logging
		site._log_security_event("test_action", "Test security event")

		security_logs = json.loads(site.security_logs)

		# Validations
		self.assertGreaterEqual(len(security_logs), 2)  # Initial + test event

		test_event = next((log for log in security_logs if log["action"] == "test_action"), None)
		self.assertIsNotNone(test_event)
		self.assertEqual(test_event["details"], "Test security event")
		self.assertIn("timestamp", test_event)
		self.assertIn("user", test_event)

	def tearDown(self):
		"""Clean up after each test method."""
		frappe.set_user("Administrator")
		# FrappeTestCase handles rollback automatically
