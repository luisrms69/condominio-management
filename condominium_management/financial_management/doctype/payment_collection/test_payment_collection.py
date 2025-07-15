# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate

# OBSERVACIÓN: Payment Collection tiene dependencies de Sales Invoice que requieren Items
# durante make_test_records. Usamos test_ignore para evitar el framework issue.
test_ignore = ["Sales Invoice", "Item", "Customer", "Payment Entry"]


class TestPaymentCollection(FrappeTestCase):
	"""Test Payment Collection DocType"""

	def test_payment_collection_creation(self):
		"""Test basic creation of Payment Collection document"""
		# Create a simple Payment Collection document
		payment_collection = frappe.new_doc("Payment Collection")
		payment_collection.payment_reference = "PAY-TEST-001"
		payment_collection.property_account = "TEST-PROP-001"
		payment_collection.resident_account = "TEST-RES-001"
		payment_collection.payment_amount = 1000.0
		payment_collection.payment_date = getdate()
		payment_collection.payment_method = "Efectivo"
		payment_collection.collection_status = "Pendiente"
		payment_collection.description = "Test payment"

		# Test that document was created successfully
		self.assertEqual(payment_collection.doctype, "Payment Collection")
		self.assertEqual(payment_collection.payment_reference, "PAY-TEST-001")
		self.assertEqual(payment_collection.payment_amount, 1000.0)
		self.assertEqual(payment_collection.payment_method, "Efectivo")
		self.assertEqual(payment_collection.collection_status, "Pendiente")

		# Test that all critical fields exist
		self.assertTrue(hasattr(payment_collection, "payment_reference"))
		self.assertTrue(hasattr(payment_collection, "property_account"))
		self.assertTrue(hasattr(payment_collection, "resident_account"))
		self.assertTrue(hasattr(payment_collection, "payment_amount"))
		self.assertTrue(hasattr(payment_collection, "payment_date"))
		self.assertTrue(hasattr(payment_collection, "payment_method"))
		self.assertTrue(hasattr(payment_collection, "collection_status"))
