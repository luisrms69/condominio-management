# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestBillingCycle(FrappeTestCase):
	"""Test Billing Cycle DocType"""

	def test_billing_cycle_creation(self):
		"""Test basic creation of Billing Cycle document"""
		# Create a simple Billing Cycle document
		billing_cycle = frappe.new_doc("Billing Cycle")
		billing_cycle.cycle_name = "Enero 2025 Test"
		billing_cycle.cycle_period = "Mensual"
		billing_cycle.start_date = "2025-01-01"
		billing_cycle.end_date = "2025-01-31"
		billing_cycle.due_date = "2025-02-15"
		billing_cycle.cycle_status = "Activo"
		billing_cycle.total_invoices = 0
		billing_cycle.total_amount = 0.0
		billing_cycle.collection_rate = 0.0
		billing_cycle.auto_generate = 1

		# Test that document was created successfully
		self.assertEqual(billing_cycle.doctype, "Billing Cycle")
		self.assertEqual(billing_cycle.cycle_name, "Enero 2025 Test")
		self.assertEqual(billing_cycle.cycle_period, "Mensual")
		self.assertEqual(billing_cycle.cycle_status, "Activo")
		self.assertEqual(billing_cycle.total_invoices, 0)
		self.assertEqual(billing_cycle.total_amount, 0.0)
		self.assertEqual(billing_cycle.auto_generate, 1)

		# Test that all critical fields exist
		self.assertTrue(hasattr(billing_cycle, "cycle_name"))
		self.assertTrue(hasattr(billing_cycle, "cycle_period"))
		self.assertTrue(hasattr(billing_cycle, "start_date"))
		self.assertTrue(hasattr(billing_cycle, "end_date"))
		self.assertTrue(hasattr(billing_cycle, "due_date"))
		self.assertTrue(hasattr(billing_cycle, "cycle_status"))
		self.assertTrue(hasattr(billing_cycle, "total_invoices"))
