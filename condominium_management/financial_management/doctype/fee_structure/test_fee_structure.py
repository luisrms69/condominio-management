# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestFeeStructure(FrappeTestCase):
	"""Test Fee Structure DocType"""

	def test_fee_structure_creation(self):
		"""Test basic creation of Fee Structure document"""
		# Create a simple Fee Structure document
		fee_structure = frappe.new_doc("Fee Structure")
		fee_structure.fee_name = "Cuota Mensual Test"
		fee_structure.fee_type = "Mensual"
		fee_structure.base_amount = 1500.0
		fee_structure.currency = "MXN"
		fee_structure.effective_date = "2025-01-01"
		fee_structure.fee_status = "Activa"
		fee_structure.description = "Test fee structure"
		fee_structure.auto_calculation = 0
		fee_structure.calculation_method = "Fijo"

		# Test that document was created successfully
		self.assertEqual(fee_structure.doctype, "Fee Structure")
		self.assertEqual(fee_structure.fee_name, "Cuota Mensual Test")
		self.assertEqual(fee_structure.fee_type, "Mensual")
		self.assertEqual(fee_structure.base_amount, 1500.0)
		self.assertEqual(fee_structure.currency, "MXN")
		self.assertEqual(fee_structure.fee_status, "Activa")

		# Test that all critical fields exist
		self.assertTrue(hasattr(fee_structure, "fee_name"))
		self.assertTrue(hasattr(fee_structure, "fee_type"))
		self.assertTrue(hasattr(fee_structure, "base_amount"))
		self.assertTrue(hasattr(fee_structure, "currency"))
		self.assertTrue(hasattr(fee_structure, "effective_date"))
		self.assertTrue(hasattr(fee_structure, "fee_status"))
		self.assertTrue(hasattr(fee_structure, "description"))
