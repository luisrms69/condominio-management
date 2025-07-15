# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestBudgetPlanning(FrappeTestCase):
	"""Test Budget Planning DocType"""

	def test_budget_planning_creation(self):
		"""Test basic creation of Budget Planning document"""
		# Create a simple Budget Planning document
		budget_planning = frappe.new_doc("Budget Planning")
		budget_planning.budget_name = "Presupuesto Test 2025"
		budget_planning.fiscal_year = "2025"
		budget_planning.budget_type = "Anual"
		budget_planning.total_budget = 500000.0
		budget_planning.currency = "MXN"
		budget_planning.budget_status = "Borrador"
		budget_planning.description = "Test budget planning"
		budget_planning.variance_threshold = 10.0
		budget_planning.auto_alerts = 1

		# Test that document was created successfully
		self.assertEqual(budget_planning.doctype, "Budget Planning")
		self.assertEqual(budget_planning.budget_name, "Presupuesto Test 2025")
		self.assertEqual(budget_planning.fiscal_year, "2025")
		self.assertEqual(budget_planning.budget_type, "Anual")
		self.assertEqual(budget_planning.total_budget, 500000.0)
		self.assertEqual(budget_planning.currency, "MXN")
		self.assertEqual(budget_planning.budget_status, "Borrador")

		# Test that all critical fields exist
		self.assertTrue(hasattr(budget_planning, "budget_name"))
		self.assertTrue(hasattr(budget_planning, "fiscal_year"))
		self.assertTrue(hasattr(budget_planning, "budget_type"))
		self.assertTrue(hasattr(budget_planning, "total_budget"))
		self.assertTrue(hasattr(budget_planning, "currency"))
		self.assertTrue(hasattr(budget_planning, "budget_status"))
		self.assertTrue(hasattr(budget_planning, "description"))
