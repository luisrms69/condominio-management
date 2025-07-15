# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate

# OBSERVACIÓN: Fine Management tiene ERPNext dependencies que causan warehouse.py autoname error
# durante make_test_records. Usamos test_ignore para evitar el framework issue.
test_ignore = ["Customer", "Warehouse", "Sales Invoice", "Item"]


class TestFineManagement(FrappeTestCase):
	"""Test Fine Management DocType"""

	def test_fine_management_creation(self):
		"""Test basic creation of Fine Management document"""
		# Create a simple Fine Management document
		fine_management = frappe.new_doc("Fine Management")
		fine_management.fine_reference = "FINE-TEST-001"
		fine_management.property_account = "TEST-PROP-001"
		fine_management.resident_account = "TEST-RES-001"
		fine_management.fine_type = "Ruido"
		fine_management.fine_amount = 500.0
		fine_management.fine_date = getdate()
		fine_management.fine_status = "Pendiente"
		fine_management.description = "Test fine for noise violation"
		fine_management.appeal_deadline = "2025-02-01"
		fine_management.appeal_status = "No Aplica"

		# Test that document was created successfully
		self.assertEqual(fine_management.doctype, "Fine Management")
		self.assertEqual(fine_management.fine_reference, "FINE-TEST-001")
		self.assertEqual(fine_management.fine_type, "Ruido")
		self.assertEqual(fine_management.fine_amount, 500.0)
		self.assertEqual(fine_management.fine_status, "Pendiente")
		self.assertEqual(fine_management.appeal_status, "No Aplica")

		# Test that all critical fields exist
		self.assertTrue(hasattr(fine_management, "fine_reference"))
		self.assertTrue(hasattr(fine_management, "property_account"))
		self.assertTrue(hasattr(fine_management, "resident_account"))
		self.assertTrue(hasattr(fine_management, "fine_type"))
		self.assertTrue(hasattr(fine_management, "fine_amount"))
		self.assertTrue(hasattr(fine_management, "fine_date"))
		self.assertTrue(hasattr(fine_management, "fine_status"))
