# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestResidentAccount(FrappeTestCase):
	"""Test Resident Account DocType"""

	def test_resident_account_creation(self):
		"""Test basic creation of Resident Account document"""
		# Create a simple Resident Account document
		resident_account = frappe.new_doc("Resident Account")
		resident_account.account_code = "TEST-RES-001"
		resident_account.resident_name = "Test Resident"
		resident_account.property_account = "TEST-PROP-001"
		resident_account.company = "_Test Company"
		resident_account.resident_type = "Propietario"
		resident_account.account_status = "Activa"
		resident_account.current_balance = 0.0
		resident_account.credit_limit = 5000.0
		resident_account.spending_limits = 1000.0
		resident_account.approval_required_amount = 2000.0
		resident_account.auto_charge_enabled = 1
		resident_account.notifications_enabled = 1

		# Test that document was created successfully
		self.assertEqual(resident_account.doctype, "Resident Account")
		self.assertEqual(resident_account.account_code, "TEST-RES-001")
		self.assertEqual(resident_account.resident_name, "Test Resident")
		self.assertEqual(resident_account.resident_type, "Propietario")
		self.assertEqual(resident_account.account_status, "Activa")
		self.assertEqual(resident_account.current_balance, 0.0)
		self.assertEqual(resident_account.credit_limit, 5000.0)

		# Test that all critical fields exist
		self.assertTrue(hasattr(resident_account, "account_code"))
		self.assertTrue(hasattr(resident_account, "resident_name"))
		self.assertTrue(hasattr(resident_account, "property_account"))
		self.assertTrue(hasattr(resident_account, "company"))
		self.assertTrue(hasattr(resident_account, "resident_type"))
		self.assertTrue(hasattr(resident_account, "account_status"))
		self.assertTrue(hasattr(resident_account, "current_balance"))
