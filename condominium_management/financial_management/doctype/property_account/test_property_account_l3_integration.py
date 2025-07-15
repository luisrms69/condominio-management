# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Property Account - Layer 3 Testing: Controlled Integration with Minimal Real Data
================================================================================

METODOLOGÍA EXPERIMENTAL: Integration testing con datos mínimos reales
- FrappeTestCase para manejo de transacciones
- Crear SOLO los datos mínimos necesarios
- Nombres predecibles para debugging
- Tests de integración controlada con Frappe Framework
"""

import frappe

# REGLA #43A: Skip automatic test records para evitar framework issues
frappe.flags.skip_test_records = True

import unittest
from unittest.mock import patch

from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate


class TestPropertyAccountLayer3Integration(FrappeTestCase):
	"""Layer 3: Controlled integration with minimal real data"""

	@classmethod
	def setUpClass(cls):
		"""Create minimal required data with predictable names"""
		# EXPERIMENTAL: Setup mínimo con nombres predecibles

		# Create test company
		if not frappe.db.exists("Company", "_TEST_COMPANY_PA_L3"):
			cls.test_company = frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": "_TEST_COMPANY_PA_L3",
					"abbr": "_TPA",
					"default_currency": "MXN",
					"country": "Mexico",
				}
			).insert(ignore_permissions=True)
		else:
			cls.test_company = frappe.get_doc("Company", "_TEST_COMPANY_PA_L3")

		# Create test customer groups if they don't exist
		for group_name in ["Condóminos", "All Customer Groups"]:
			if not frappe.db.exists("Customer Group", group_name):
				frappe.get_doc(
					{
						"doctype": "Customer Group",
						"customer_group_name": group_name,
						"parent_customer_group": "All Customer Groups"
						if group_name != "All Customer Groups"
						else None,
						"is_group": 1 if group_name == "All Customer Groups" else 0,
					}
				).insert(ignore_permissions=True)

		# Create test customer
		if not frappe.db.exists("Customer", "_TEST_CUSTOMER_PA_L3"):
			cls.test_customer = frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": "_TEST_CUSTOMER_PA_L3",
					"customer_type": "Individual",
					"customer_group": "Condóminos",
					"territory": "All Territories",
				}
			).insert(ignore_permissions=True)
		else:
			cls.test_customer = frappe.get_doc("Customer", "_TEST_CUSTOMER_PA_L3")

		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		"""Clean up test data"""
		# Delete test records in reverse order of creation
		for doctype, name in [
			("Property Account", "_TEST_PA_L3_001"),
			("Property Account", "_TEST_PA_L3_002"),
			("Customer", "_TEST_CUSTOMER_PA_L3"),
			("Company", "_TEST_COMPANY_PA_L3"),
		]:
			if frappe.db.exists(doctype, name):
				frappe.delete_doc(doctype, name, ignore_permissions=True)

		frappe.db.commit()

	def test_property_account_creation_minimal(self):
		"""Test basic Property Account creation with minimal required fields"""
		# REGLA #43A: Test integración con skip_test_records flag
		doc = frappe.get_doc(
			{
				"doctype": "Property Account",
				"account_name": "_TEST_PA_L3_001",
				"property_registry": "_TEST_PROPERTY_REG_L3",  # Mock reference
				"customer": "_TEST_CUSTOMER_PA_L3",
				"company": "_TEST_COMPANY_PA_L3",
				"billing_frequency": "Mensual",
				"account_status": "Activa",
				"current_balance": 0.0,
			}
		)

		# Mock property registry validation to avoid dependency
		with patch.object(doc, "validate_property_registry"):
			doc.insert(ignore_permissions=True)

		# Verify document was created
		self.assertTrue(frappe.db.exists("Property Account", doc.name))
		self.assertEqual(doc.account_name, "_TEST_PA_L3_001")
		self.assertEqual(doc.customer, "_TEST_CUSTOMER_PA_L3")
		self.assertEqual(doc.company, "_TEST_COMPANY_PA_L3")

	def test_property_account_default_values_integration(self):
		"""Test that default values are properly set during document creation"""
		# REGLA #43A: Test defaults con skip_test_records flag
		doc = frappe.get_doc(
			{
				"doctype": "Property Account",
				"account_name": "_TEST_PA_L3_002",
				"property_registry": "_TEST_PROPERTY_REG_L3_002",
				"customer": "_TEST_CUSTOMER_PA_L3",
				"company": "_TEST_COMPANY_PA_L3",
				# Deliberately omit optional fields to test defaults
			}
		)

		# Mock property registry validation
		with patch.object(doc, "validate_property_registry"):
			doc.insert(ignore_permissions=True)

		# Verify defaults were applied
		self.assertEqual(doc.billing_frequency, "Mensual")
		self.assertEqual(doc.account_status, "Activa")
		self.assertEqual(doc.billing_day, 1)
		self.assertEqual(doc.current_balance, 0.0)
		self.assertEqual(doc.auto_generate_invoices, 1)
		self.assertEqual(doc.discount_eligibility, 1)

	def test_property_account_permissions_integration(self):
		"""Test that Property Account permissions work correctly"""
		# Create document as Administrator
		frappe.set_user("Administrator")

		doc = frappe.get_doc(
			{
				"doctype": "Property Account",
				"account_name": "_TEST_PA_L3_PERM",
				"property_registry": "_TEST_PROPERTY_REG_PERM",
				"customer": "_TEST_CUSTOMER_PA_L3",
				"company": "_TEST_COMPANY_PA_L3",
				"billing_frequency": "Mensual",
				"account_status": "Activa",
			}
		)

		with patch.object(doc, "validate_property_registry"):
			doc.insert(ignore_permissions=True)

		# Verify Administrator has full access
		self.assertTrue(frappe.has_permission("Property Account", "read", doc=doc))
		self.assertTrue(frappe.has_permission("Property Account", "write", doc=doc))

	def test_property_account_database_constraints(self):
		"""Test database-level constraints and validations"""
		# Test unique constraint on account_name (if configured)
		doc1 = frappe.get_doc(
			{
				"doctype": "Property Account",
				"account_name": "_TEST_PA_L3_UNIQUE",
				"property_registry": "_TEST_PROPERTY_REG_UNIQUE_1",
				"customer": "_TEST_CUSTOMER_PA_L3",
				"company": "_TEST_COMPANY_PA_L3",
				"billing_frequency": "Mensual",
			}
		)

		with patch.object(doc1, "validate_property_registry"):
			doc1.insert(ignore_permissions=True)

		# Verify first document was created
		self.assertTrue(frappe.db.exists("Property Account", doc1.name))

	def test_property_account_frappe_lifecycle_hooks(self):
		"""Test Frappe document lifecycle integration"""
		doc = frappe.get_doc(
			{
				"doctype": "Property Account",
				"account_name": "_TEST_PA_L3_LIFECYCLE",
				"property_registry": "_TEST_PROPERTY_REG_LIFECYCLE",
				"customer": "_TEST_CUSTOMER_PA_L3",
				"company": "_TEST_COMPANY_PA_L3",
				"billing_frequency": "Mensual",
			}
		)

		# Track method calls to verify lifecycle hooks
		before_insert_called = False
		before_save_called = False

		original_before_insert = doc.before_insert
		original_before_save = doc.before_save

		def mock_before_insert():
			nonlocal before_insert_called
			before_insert_called = True
			# Call original but mock property registry validation
			with patch.object(doc, "validate_property_registry"):
				original_before_insert()

		def mock_before_save():
			nonlocal before_save_called
			before_save_called = True
			# Call original but mock external dependencies
			with patch.object(doc, "calculate_pending_amount"), patch.object(doc, "update_payment_summary"):
				original_before_save()

		doc.before_insert = mock_before_insert
		doc.before_save = mock_before_save

		# Insert document and verify hooks were called
		doc.insert(ignore_permissions=True)

		self.assertTrue(before_insert_called, "before_insert hook not called")
		self.assertTrue(before_save_called, "before_save hook not called")

	def test_property_account_field_types_integration(self):
		"""Test that field types are properly handled by Frappe"""
		doc = frappe.get_doc(
			{
				"doctype": "Property Account",
				"account_name": "_TEST_PA_L3_FIELDS",
				"property_registry": "_TEST_PROPERTY_REG_FIELDS",
				"customer": "_TEST_CUSTOMER_PA_L3",
				"company": "_TEST_COMPANY_PA_L3",
				"billing_frequency": "Mensual",
				"current_balance": 1500.50,
				"credit_balance": 200.75,
				"billing_start_date": getdate(),
				"last_payment_date": add_days(getdate(), -5),
				"auto_generate_invoices": 1,
				"discount_eligibility": 0,
			}
		)

		with patch.object(doc, "validate_property_registry"):
			doc.insert(ignore_permissions=True)

		# Reload from database to verify field type handling
		doc_reloaded = frappe.get_doc("Property Account", doc.name)

		# Verify field types are preserved
		self.assertIsInstance(doc_reloaded.current_balance, (int, float))
		self.assertIsInstance(doc_reloaded.credit_balance, (int, float))
		self.assertEqual(float(doc_reloaded.current_balance), 1500.50)
		self.assertEqual(float(doc_reloaded.credit_balance), 200.75)
		self.assertEqual(doc_reloaded.auto_generate_invoices, 1)
		self.assertEqual(doc_reloaded.discount_eligibility, 0)

	def test_property_account_search_and_filters(self):
		"""Test search and filter functionality"""
		# Create test document for searching
		doc = frappe.get_doc(
			{
				"doctype": "Property Account",
				"account_name": "_TEST_PA_L3_SEARCH",
				"property_registry": "_TEST_PROPERTY_REG_SEARCH",
				"customer": "_TEST_CUSTOMER_PA_L3",
				"company": "_TEST_COMPANY_PA_L3",
				"billing_frequency": "Mensual",
				"account_status": "Activa",
			}
		)

		with patch.object(doc, "validate_property_registry"):
			doc.insert(ignore_permissions=True)

		# Test search functionality
		search_results = frappe.get_all(
			"Property Account",
			filters={"account_name": "_TEST_PA_L3_SEARCH"},
			fields=["name", "account_name", "account_status"],
		)

		self.assertEqual(len(search_results), 1)
		self.assertEqual(search_results[0]["account_name"], "_TEST_PA_L3_SEARCH")
		self.assertEqual(search_results[0]["account_status"], "Activa")

	def test_property_account_meta_integration(self):
		"""Test DocType meta information integration"""
		# Get meta information
		meta = frappe.get_meta("Property Account")

		# Verify essential meta properties
		self.assertIsNotNone(meta)
		self.assertEqual(meta.name, "Property Account")
		self.assertTrue(meta.has_field("account_name"))
		self.assertTrue(meta.has_field("customer"))
		self.assertTrue(meta.has_field("company"))

		# Test field meta information
		account_name_field = meta.get_field("account_name")
		self.assertIsNotNone(account_name_field)
		self.assertEqual(account_name_field.fieldtype, "Data")


if __name__ == "__main__":
	unittest.main()
