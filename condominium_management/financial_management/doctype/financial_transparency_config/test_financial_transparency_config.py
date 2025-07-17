# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestFinancialTransparencyConfig(FrappeTestCase):
	"""Test Financial Transparency Config DocType"""

	def test_financial_transparency_config_creation(self):
		"""Test basic creation of Financial Transparency Config document"""
		# Create a simple Financial Transparency Config document
		transparency_config = frappe.new_doc("Financial Transparency Config")
		transparency_config.transparency_level = "Completa"
		transparency_config.report_frequency = "Mensual"
		transparency_config.auto_publish = 1
		transparency_config.config_status = "Activa"
		transparency_config.accessible_roles = "Condominio Administrator"
		transparency_config.confidential_items = "Información sensible"
		transparency_config.approval_required = 0
		transparency_config.notification_settings = "Email"

		# Test that document was created successfully
		self.assertEqual(transparency_config.doctype, "Financial Transparency Config")
		self.assertEqual(transparency_config.transparency_level, "Completa")
		self.assertEqual(transparency_config.report_frequency, "Mensual")
		self.assertEqual(transparency_config.auto_publish, 1)
		self.assertEqual(transparency_config.config_status, "Activa")
		self.assertEqual(transparency_config.approval_required, 0)

		# Test that all critical fields exist
		self.assertTrue(hasattr(transparency_config, "transparency_level"))
		self.assertTrue(hasattr(transparency_config, "report_frequency"))
		self.assertTrue(hasattr(transparency_config, "auto_publish"))
		self.assertTrue(hasattr(transparency_config, "config_status"))
		self.assertTrue(hasattr(transparency_config, "accessible_roles"))
		self.assertTrue(hasattr(transparency_config, "confidential_items"))
		self.assertTrue(hasattr(transparency_config, "approval_required"))
