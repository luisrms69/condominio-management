# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Tests for Property User Authorization — Condominium People Phase 1.

Covers: validations, vigency, uniqueness (D2), helpers.
Compatible with bench run-tests (UnitTestCase — avoids FrappeTestCase record generation).
"""

import frappe
from frappe.tests import UnitTestCase
from frappe.utils import add_days, nowdate

from condominium_management.condominium_people.utils import (
	can_user_act_for_property,
	can_user_respond_poll_for_property,
	can_user_vote_for_property,
	get_active_authorization,
	get_authorized_properties,
	get_authorized_users_for_property,
)


class TestPropertyUserAuthorization(UnitTestCase):
	"""Tests compatibles con bench run-tests."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")
		cls._setup_prerequisites()

	@classmethod
	def _setup_prerequisites(cls):
		"""Crea datos base: Space Category, Physical Space y Property Registry."""
		# Space Category
		if not frappe.db.exists("Space Category", {"category_name": "Test PUA Unit"}):
			frappe.get_doc(
				{"doctype": "Space Category", "category_name": "Test PUA Unit", "is_active": 1}
			).insert(ignore_permissions=True)

		# Property Usage Type (reqd en Property Registry)
		if not frappe.db.exists("Property Usage Type", {"usage_name": "Residencial"}):
			frappe.get_doc({"doctype": "Property Usage Type", "usage_name": "Residencial"}).insert(
				ignore_permissions=True
			)

		# Acquisition Type
		if not frappe.db.exists("Acquisition Type", {"acquisition_name": "Compra"}):
			frappe.get_doc(
				{"doctype": "Acquisition Type", "acquisition_name": "Compra", "requires_notary": 0}
			).insert(ignore_permissions=True)

		# Property Status Type
		if not frappe.db.exists("Property Status Type", {"status_name": "Activo"}):
			frappe.get_doc({"doctype": "Property Status Type", "status_name": "Activo"}).insert(
				ignore_permissions=True
			)

		# Property Relationship Type
		if not frappe.db.exists("Property Relationship Type", {"relationship_name": "Propietario"}):
			frappe.get_doc(
				{
					"doctype": "Property Relationship Type",
					"relationship_name": "Propietario",
					"is_active": 1,
					"default_can_vote": 1,
					"default_can_respond_polls": 1,
					"default_can_rsvp_events": 1,
					"default_can_create_tickets": 1,
					"default_can_reserve_amenities": 1,
					"default_can_view_statement": 1,
					"default_can_receive_portal_communications": 1,
				}
			).insert(ignore_permissions=True)

		# Buscar company existente
		companies = frappe.get_all("Company", fields=["name"], limit=1)
		cls.test_company = companies[0].name if companies else "_Test Company"

		# Physical Space para tests
		space_name = "Test PUA Space"
		existing = frappe.db.get_value(
			"Physical Space", {"space_name": space_name, "company": cls.test_company}, "name"
		)
		if existing:
			cls.test_space = existing
		else:
			space = frappe.get_doc(
				{
					"doctype": "Physical Space",
					"space_name": space_name,
					"company": cls.test_company,
					"space_category": "Test PUA Unit",
				}
			).insert(ignore_permissions=True)
			cls.test_space = space.name

		# Property Registry para tests
		registry_name = frappe.db.get_value(
			"Property Registry",
			{"property_name": "Test PUA Property", "company": cls.test_company},
			"name",
		)
		if registry_name:
			cls.test_property = registry_name
		else:
			from datetime import date

			reg = frappe.get_doc(
				{
					"doctype": "Property Registry",
					"naming_series": "PROP-.YYYY.-",
					"property_name": "Test PUA Property",
					"company": cls.test_company,
					"physical_space": cls.test_space,
					"property_usage_type": "Residencial",
					"acquisition_type": "Compra",
					"property_status_type": "Activo",
					"registration_date": date.today(),
					"indiviso_percentage": 1.0,
				}
			).insert(ignore_permissions=True)
			cls.test_property = reg.name

		# Crear usuarios de test (Link User se valida en insert)
		for email in [
			"test@condominios.test",
			"test_expired@condominios.test",
			"test_future@condominios.test",
			"test_dup@condominios.test",
			"test_inactive@condominios.test",
			"test_act@condominios.test",
			"test_nopoll@condominios.test",
			"test_props@condominios.test",
			"test_users@condominios.test",
		]:
			if not frappe.db.exists("User", email):
				frappe.get_doc(
					{
						"doctype": "User",
						"email": email,
						"first_name": email.split("@")[0],
						"user_type": "Website User",
						"send_welcome_email": 0,
					}
				).insert(ignore_permissions=True)

		frappe.db.commit()

	def tearDown(self):
		"""Limpia PUAs de test después de cada test."""
		frappe.db.delete("Property User Authorization", {"property_registry": self.test_property})
		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		frappe.db.delete("Property Registry", {"property_name": "Test PUA Property"})
		frappe.db.delete("Physical Space", {"space_name": "Test PUA Space"})
		frappe.db.commit()
		super().tearDownClass()

	# ── helpers ──────────────────────────────────────────────────────────────

	def _make_pua(self, user, relationship_type="Propietario", **overrides):
		doc = frappe.new_doc("Property User Authorization")
		doc.update(
			{
				"user": user,
				"property_registry": self.test_property,
				"relationship_type": relationship_type,
				"is_active": 1,
				"can_vote": 1,
				"can_respond_polls": 1,
				"can_rsvp_events": 1,
				"can_create_tickets": 1,
			}
		)
		doc.update(overrides)
		return doc

	def _insert_pua(self, user, **overrides):
		doc = self._make_pua(user, **overrides)
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		return doc

	# ── validations ──────────────────────────────────────────────────────────

	def test_company_derived_from_property(self):
		doc = self._make_pua("test@condominios.test")
		doc.validate()
		self.assertEqual(doc.company, self.test_company)

	def test_company_consistency_error(self):
		doc = self._make_pua("test@condominios.test", company="WRONG_COMPANY")
		with self.assertRaises(frappe.exceptions.ValidationError):
			doc._validate_company_consistency()

	def test_invalid_dates(self):
		doc = self._make_pua(
			"test@condominios.test",
			valid_from=nowdate(),
			valid_until=add_days(nowdate(), -1),
		)
		with self.assertRaises(frappe.exceptions.ValidationError):
			doc._validate_dates()

	def test_valid_dates(self):
		doc = self._make_pua(
			"test@condominios.test",
			valid_from=nowdate(),
			valid_until=add_days(nowdate(), 30),
		)
		doc._validate_dates()  # must not raise

	# ── vigency ───────────────────────────────────────────────────────────────

	def test_expired_pua_not_returned(self):
		user = "test_expired@condominios.test"
		self._insert_pua(user, valid_until=add_days(nowdate(), -1))
		self.assertIsNone(get_active_authorization(user, self.test_property))

	def test_future_pua_not_returned(self):
		user = "test_future@condominios.test"
		self._insert_pua(user, valid_from=add_days(nowdate(), 5))
		self.assertIsNone(get_active_authorization(user, self.test_property))

	# ── uniqueness (D2) ───────────────────────────────────────────────────────

	def test_duplicate_active_blocked(self):
		user = "test_dup@condominios.test"
		self._insert_pua(user)
		with self.assertRaises(frappe.exceptions.ValidationError):
			self._make_pua(user).insert(ignore_permissions=True)

	def test_inactive_does_not_block(self):
		user = "test_inactive@condominios.test"
		self._insert_pua(user, is_active=0)
		doc = self._insert_pua(user, is_active=1)  # must not raise
		self.assertTrue(doc.name)

	# ── helpers ───────────────────────────────────────────────────────────────

	def test_can_user_act_returns_true_for_valid_permission(self):
		user = "test_act@condominios.test"
		self._insert_pua(user)
		self.assertTrue(can_user_vote_for_property(user, self.test_property))
		self.assertTrue(can_user_respond_poll_for_property(user, self.test_property))

	def test_can_user_act_returns_false_when_no_pua(self):
		self.assertFalse(can_user_act_for_property("nobody@test.test", self.test_property, "can_vote"))

	def test_can_user_act_returns_false_for_disabled_permission(self):
		user = "test_nopoll@condominios.test"
		self._insert_pua(user, can_respond_polls=0)
		self.assertFalse(can_user_respond_poll_for_property(user, self.test_property))

	def test_get_authorized_properties_returns_correct_list(self):
		user = "test_props@condominios.test"
		self._insert_pua(user)
		props = get_authorized_properties(user, permission="can_vote")
		self.assertIn(self.test_property, props)

	def test_get_authorized_users_for_property(self):
		user = "test_users@condominios.test"
		self._insert_pua(user)
		users = get_authorized_users_for_property(self.test_property, permission="can_vote")
		self.assertIn(user, users)

	def test_invalid_permission_raises(self):
		with self.assertRaises(frappe.exceptions.ValidationError):
			can_user_act_for_property("test@test.test", self.test_property, "invalid_permission")
