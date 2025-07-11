# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import unittest

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, nowdate


class TestCommitteeMember(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		"""Set up test data once for all tests - REGLA #29 Pattern"""
		# Clean up any existing test data FIRST (critical for unique constraints)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code = "TEST-PROP-001"')
		frappe.db.sql('DELETE FROM `tabCommittee Member` WHERE user = "test_committee@example.com"')
		frappe.db.sql('DELETE FROM `tabUser` WHERE email = "test_committee@example.com"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Company"')

		# Clean up test roles
		test_roles = ["Committee President", "Committee Secretary", "Committee Treasurer", "Committee Member"]
		for role_name in test_roles:
			frappe.db.sql("DELETE FROM `tabRole` WHERE role_name = %s", (role_name,))

		# Commit cleanup before creating new test data
		frappe.db.commit()

		# Now create test data
		cls.setup_test_data()

	@classmethod
	def tearDownClass(cls):
		"""Clean up test data after all tests - REGLA #29 Pattern"""
		# Clean up all test data using SQL (bypasses validation)
		frappe.db.sql('DELETE FROM `tabProperty Registry` WHERE property_code = "TEST-PROP-001"')
		frappe.db.sql('DELETE FROM `tabCommittee Member` WHERE user = "test_committee@example.com"')
		frappe.db.sql('DELETE FROM `tabUser` WHERE email = "test_committee@example.com"')
		frappe.db.sql('DELETE FROM `tabCompany` WHERE company_name = "Test Company"')

		# Clean up test roles
		test_roles = ["Committee President", "Committee Secretary", "Committee Treasurer", "Committee Member"]
		for role_name in test_roles:
			frappe.db.sql("DELETE FROM `tabRole` WHERE role_name = %s", (role_name,))

		# Final commit
		frappe.db.commit()
		frappe.clear_cache()

	@classmethod
	def setup_test_data(cls):
		"""Create test data for committee member tests"""
		# Create a test company if it doesn't exist
		if not frappe.db.exists("Company", "Test Company"):
			frappe.db.sql(
				"INSERT INTO `tabCompany` (name, company_name, abbr, default_currency) VALUES ('Test Company', 'Test Company', 'TC', 'USD')"
			)
			frappe.db.commit()

		# Create required committee roles if they don't exist
		committee_roles = [
			"Committee President",
			"Committee Secretary",
			"Committee Treasurer",
			"Committee Member",
		]

		for role_name in committee_roles:
			if not frappe.db.exists("Role", role_name):
				frappe.db.sql(
					"INSERT INTO `tabRole` (name, role_name, desk_access) VALUES (%s, %s, %s)",
					(role_name, role_name, 1),
				)

		# Create a test user if it doesn't exist
		if not frappe.db.exists("User", "test_committee@example.com"):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": "test_committee@example.com",
					"first_name": "Test",
					"last_name": "Committee Member",
					"user_type": "System User",
				}
			)
			user.insert(ignore_permissions=True)

		# Create a test property registry if it doesn't exist with property_code TEST-PROP-001
		existing_property = frappe.db.get_value(
			"Property Registry", {"property_code": "TEST-PROP-001"}, "name"
		)
		if not existing_property:
			property_doc = frappe.get_doc(
				{
					"doctype": "Property Registry",
					"property_code": "TEST-PROP-001",
					"property_name": "Test Property Committee",
					"naming_series": "PROP-.YYYY.-",
					"company": "Test Company",
					"property_usage_type": "Residencial",
					"acquisition_type": "Compra",
					"property_status_type": "Activo",
					"registration_date": nowdate(),
					"is_active": 1,
				}
			)
			property_doc.insert(ignore_permissions=True)
			cls.test_property_name = property_doc.name
		else:
			cls.test_property_name = existing_property

	def test_committee_member_creation(self):
		"""Test basic committee member creation"""
		member = frappe.get_doc(
			{
				"doctype": "Committee Member",
				"user": "test_committee@example.com",
				"property_registry": self.test_property_name,
				"role_in_committee": "Vocal",
				"start_date": nowdate(),
				"responsibilities": "Participar en reuniones del comité",
			}
		)

		member.insert()

		# Verify the document was created
		self.assertTrue(member.name)
		self.assertEqual(member.role_in_committee, "Vocal")
		self.assertEqual(member.committee_position_weight, 1)
		self.assertEqual(member.is_active, 1)

		# Clean up
		member.delete()

	def test_unique_role_validation(self):
		"""Test that unique roles (Presidente, Secretario, Tesorero) are enforced"""
		# Create first president
		president1 = frappe.get_doc(
			{
				"doctype": "Committee Member",
				"user": "test_committee@example.com",
				"property_registry": self.test_property_name,
				"role_in_committee": "Presidente",
				"start_date": nowdate(),
			}
		)
		president1.insert()

		# Try to create second president - should fail
		president2 = frappe.get_doc(
			{
				"doctype": "Committee Member",
				"user": "test_committee@example.com",
				"property_registry": self.test_property_name,
				"role_in_committee": "Presidente",
				"start_date": nowdate(),
			}
		)

		with self.assertRaises(frappe.ValidationError):
			president2.insert()

		# Clean up
		president1.delete()

	def test_default_permissions_by_role(self):
		"""Test that default permissions are set correctly based on role"""
		# Test Presidente permissions
		president = frappe.get_doc(
			{
				"doctype": "Committee Member",
				"user": "test_committee@example.com",
				"property_registry": self.test_property_name,
				"role_in_committee": "Presidente",
				"start_date": nowdate(),
			}
		)
		president.insert()

		self.assertEqual(president.can_approve_expenses, 1)
		self.assertEqual(president.can_call_assembly, 1)
		self.assertEqual(president.can_sign_documents, 1)
		self.assertEqual(president.can_create_polls, 1)

		# Test Vocal permissions
		vocal = frappe.get_doc(
			{
				"doctype": "Committee Member",
				"user": "test_committee@example.com",
				"property_registry": self.test_property_name,
				"role_in_committee": "Vocal",
				"start_date": nowdate(),
			}
		)
		vocal.insert()

		self.assertEqual(vocal.can_approve_expenses, 0)
		self.assertEqual(vocal.can_call_assembly, 0)
		self.assertEqual(vocal.can_sign_documents, 0)
		self.assertEqual(vocal.can_create_polls, 1)

		# Clean up
		president.delete()
		vocal.delete()

	def test_committee_position_weight(self):
		"""Test committee position weight assignment"""
		roles_weights = [("Presidente", 4), ("Secretario", 3), ("Tesorero", 2), ("Vocal", 1)]

		created_members = []

		for role, expected_weight in roles_weights:
			member = frappe.get_doc(
				{
					"doctype": "Committee Member",
					"user": "test_committee@example.com",
					"property_registry": self.test_property_name,
					"role_in_committee": role,
					"start_date": nowdate(),
				}
			)
			member.insert()
			created_members.append(member)

			self.assertEqual(member.committee_position_weight, expected_weight)

		# Clean up
		for member in created_members:
			member.delete()

	def test_date_validation(self):
		"""Test date validation"""
		# Test that start date cannot be after end date
		member = frappe.get_doc(
			{
				"doctype": "Committee Member",
				"user": "test_committee@example.com",
				"property_registry": self.test_property_name,
				"role_in_committee": "Vocal",
				"start_date": nowdate(),
				"end_date": add_days(nowdate(), -1),  # End date before start date
			}
		)

		with self.assertRaises(frappe.ValidationError):
			member.insert()

	def test_expense_approval_permission(self):
		"""Test expense approval permission logic"""
		# Create treasurer with approval limit
		treasurer = frappe.get_doc(
			{
				"doctype": "Committee Member",
				"user": "test_committee@example.com",
				"property_registry": self.test_property_name,
				"role_in_committee": "Tesorero",
				"start_date": nowdate(),
				"expense_approval_limit": 5000,
			}
		)
		treasurer.insert()

		# Test approval permissions
		self.assertTrue(treasurer.has_permission_to_approve_expense(3000))
		self.assertFalse(treasurer.has_permission_to_approve_expense(6000))

		# Test member without approval permission
		vocal = frappe.get_doc(
			{
				"doctype": "Committee Member",
				"user": "test_committee@example.com",
				"property_registry": self.test_property_name,
				"role_in_committee": "Vocal",
				"start_date": nowdate(),
			}
		)
		vocal.insert()

		self.assertFalse(vocal.has_permission_to_approve_expense(1000))

		# Clean up
		treasurer.delete()
		vocal.delete()

	def test_get_active_committee_members(self):
		"""Test getting active committee members"""
		# Create multiple committee members
		roles = ["Presidente", "Secretario", "Tesorero", "Vocal"]
		created_members = []

		for role in roles:
			member = frappe.get_doc(
				{
					"doctype": "Committee Member",
					"user": "test_committee@example.com",
					"property_registry": self.test_property_name,
					"role_in_committee": role,
					"start_date": nowdate(),
				}
			)
			member.insert()
			created_members.append(member)

		# Get active members
		active_members = frappe.get_doc(
			"Committee Member", created_members[0].name
		).get_active_committee_members()

		# Should return all 4 members, ordered by position weight
		self.assertEqual(len(active_members), 4)
		self.assertEqual(active_members[0]["role_in_committee"], "Presidente")
		self.assertEqual(active_members[-1]["role_in_committee"], "Vocal")

		# Clean up
		for member in created_members:
			member.delete()

	def test_get_committee_member_by_role(self):
		"""Test getting committee member by specific role"""
		# Create president
		president = frappe.get_doc(
			{
				"doctype": "Committee Member",
				"user": "test_committee@example.com",
				"property_registry": self.test_property_name,
				"role_in_committee": "Presidente",
				"start_date": nowdate(),
			}
		)
		president.insert()

		# Get president by role
		president_info = frappe.get_doc("Committee Member", president.name).get_committee_member_by_role(
			"Presidente"
		)

		self.assertIsNotNone(president_info)
		self.assertEqual(president_info[0], president.name)

		# Test non-existent role
		treasurer_info = frappe.get_doc("Committee Member", president.name).get_committee_member_by_role(
			"Tesorero"
		)
		self.assertIsNone(treasurer_info)

		# Clean up
		president.delete()

	def tearDown(self):
		"""Clean up test data"""
		# Clean up any remaining committee members
		frappe.db.delete("Committee Member", {"user": "test_committee@example.com"})
		frappe.db.commit()


if __name__ == "__main__":
	unittest.main()
