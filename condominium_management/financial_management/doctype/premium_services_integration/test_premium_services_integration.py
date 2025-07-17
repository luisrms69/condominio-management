# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPremiumServicesIntegration(FrappeTestCase):
	"""Test Premium Services Integration DocType"""

	def test_premium_services_integration_creation(self):
		"""Test basic creation of Premium Services Integration document"""
		# Create a simple Premium Services Integration document
		premium_service = frappe.new_doc("Premium Services Integration")
		premium_service.service_name = "Spa & Wellness Test"
		premium_service.service_type = "Recreational"
		premium_service.base_price = 200.0
		premium_service.currency = "MXN"
		premium_service.service_status = "Activo"
		premium_service.description = "Test premium service"
		premium_service.booking_required = 1
		premium_service.advance_booking_days = 3
		premium_service.cancellation_policy = "24 horas"

		# Test that document was created successfully
		self.assertEqual(premium_service.doctype, "Premium Services Integration")
		self.assertEqual(premium_service.service_name, "Spa & Wellness Test")
		self.assertEqual(premium_service.service_type, "Recreational")
		self.assertEqual(premium_service.base_price, 200.0)
		self.assertEqual(premium_service.currency, "MXN")
		self.assertEqual(premium_service.service_status, "Activo")
		self.assertEqual(premium_service.booking_required, 1)

		# Test that all critical fields exist
		self.assertTrue(hasattr(premium_service, "service_name"))
		self.assertTrue(hasattr(premium_service, "service_type"))
		self.assertTrue(hasattr(premium_service, "base_price"))
		self.assertTrue(hasattr(premium_service, "currency"))
		self.assertTrue(hasattr(premium_service, "service_status"))
		self.assertTrue(hasattr(premium_service, "description"))
		self.assertTrue(hasattr(premium_service, "booking_required"))
