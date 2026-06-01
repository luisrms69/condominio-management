# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

from datetime import date

import frappe
from frappe.tests import UnitTestCase
from frappe.utils import nowdate


class TestCommitteeMember(UnitTestCase):
	"""Tests para Committee Member rediseñado.

	Verifica: company obligatoria, cargo por company, fechas, consistencia
	company entre property_registry / committee_position / company del miembro.
	"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.company = cls._setup_company()
		cls.position = cls._setup_position(cls.company)
		cls.property_reg = cls._setup_property_registry(cls.company)
		cls.user = cls._setup_user()

	@classmethod
	def tearDownClass(cls):
		frappe.db.delete("Committee Member", {"company": cls.company})
		frappe.db.delete("Committee Position", {"company": cls.company})
		frappe.db.delete("Property Registry", {"property_name": "Test Propiedad CM"})
		frappe.db.commit()
		super().tearDownClass()

	@classmethod
	def _setup_company(cls):
		existing = frappe.db.get_list("Company", limit=1)
		return existing[0].name if existing else "_Test Company"

	@classmethod
	def _setup_position(cls, company):
		name = f"{company}::Vocal Test CM"
		if not frappe.db.exists("Committee Position", name):
			pos = frappe.get_doc(
				{
					"doctype": "Committee Position",
					"company": company,
					"position_name": "Vocal Test CM",
					"hierarchy_level": 1,
				}
			)
			pos.insert(ignore_permissions=True)
			frappe.db.commit()
		return name

	@classmethod
	def _setup_property_registry(cls, company):
		existing = frappe.db.get_value("Property Registry", {"company": company, "is_active": 1}, "name")
		if existing:
			return existing

		usage = frappe.db.get_value("Property Usage Type", {}, "name")
		acquisition = frappe.db.get_value("Acquisition Type", {}, "name")
		status = frappe.db.get_value("Property Status Type", {}, "name")
		if not all([usage, acquisition, status]):
			return None

		pr = frappe.get_doc(
			{
				"doctype": "Property Registry",
				"naming_series": "PROP-.YYYY.-",
				"property_name": "Test Propiedad CM",
				"company": company,
				"property_usage_type": usage,
				"acquisition_type": acquisition,
				"property_status_type": status,
				"registration_date": nowdate(),
				"indiviso_percentage": 1.0,
			}
		)
		pr.insert(ignore_permissions=True)
		frappe.db.commit()
		return pr.name

	@classmethod
	def _setup_user(cls):
		email = "test_cm_member@condov16.test"
		if not frappe.db.exists("User", email):
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": "Test CM",
					"send_welcome_email": 0,
					"enabled": 1,
					"new_password": "Admin1234!",
				}
			)
			user.insert(ignore_permissions=True)
			frappe.db.commit()
		return email

	def _base_member(self, **kwargs):
		base = {
			"doctype": "Committee Member",
			"company": self.company,
			"user": self.user,
			"property_registry": self.property_reg,
			"committee_position": self.position,
			"start_date": nowdate(),
		}
		base.update(kwargs)
		return base

	# ── Tests básicos ───────────────────────────────────────────────────────────

	def test_committee_member_basic_creation(self):
		"""Creación básica con todos los campos requeridos."""
		if not self.property_reg:
			self.skipTest("No hay Property Registry disponible")
		m = frappe.get_doc(self._base_member())
		m.insert(ignore_permissions=True)
		self.assertTrue(m.name.startswith("CM-"))
		self.assertEqual(m.company, self.company)
		frappe.delete_doc("Committee Member", m.name, ignore_permissions=True)
		frappe.db.commit()

	def test_committee_member_company_enforced_by_json(self):
		"""company es reqd:1 en el JSON — el campo existe y es obligatorio en schema."""
		from frappe.model.meta import get_meta

		meta = get_meta("Committee Member")
		company_field = meta.get_field("company")
		self.assertIsNotNone(company_field, "Campo 'company' debe existir")
		self.assertEqual(company_field.reqd, 1, "Campo 'company' debe ser obligatorio (reqd:1)")

	def test_committee_member_requires_committee_position(self):
		"""committee_position es obligatorio — doc creado sin cargo."""
		if not self.property_reg:
			self.skipTest("No hay Property Registry disponible")
		data = self._base_member()
		data.pop("committee_position")
		m = frappe.get_doc(data)
		with self.assertRaises(frappe.ValidationError):
			m.insert(ignore_permissions=True)

	# ── Vigencia de fechas ───────────────────────────────────────────────────────

	def test_end_date_cannot_be_before_start_date(self):
		"""end_date no puede ser menor que start_date."""
		if not self.property_reg:
			self.skipTest("No hay Property Registry disponible")
		m = frappe.get_doc(
			self._base_member(
				start_date=date(2026, 6, 1),
				end_date=date(2026, 5, 1),
			)
		)
		with self.assertRaises(frappe.ValidationError):
			m.insert(ignore_permissions=True)

	def test_valid_date_range(self):
		"""start_date < end_date es válido."""
		if not self.property_reg:
			self.skipTest("No hay Property Registry disponible")
		m = frappe.get_doc(
			self._base_member(
				start_date=date(2026, 1, 1),
				end_date=date(2026, 12, 31),
			)
		)
		m.insert(ignore_permissions=True)
		self.assertEqual(m.end_date, date(2026, 12, 31))
		frappe.delete_doc("Committee Member", m.name, ignore_permissions=True)
		frappe.db.commit()

	# ── Consistencia de company ──────────────────────────────────────────────────

	def test_property_registry_must_match_company(self):
		"""property_registry de otra company debe ser rechazado."""
		other_company = frappe.db.get_list("Company", filters={"name": ["!=", self.company]}, limit=1)
		if not other_company:
			self.skipTest("No hay segunda company disponible")

		other_pr = frappe.db.get_value(
			"Property Registry",
			{"company": other_company[0].name, "is_active": 1},
			"name",
		)
		if not other_pr:
			self.skipTest("No hay Property Registry en otra company")

		m = frappe.get_doc(self._base_member(property_registry=other_pr))
		with self.assertRaises(frappe.ValidationError):
			m.insert(ignore_permissions=True)

	def test_committee_position_must_match_company(self):
		"""committee_position de otra company debe ser rechazado."""
		other_company = frappe.db.get_list("Company", filters={"name": ["!=", self.company]}, limit=1)
		if not other_company:
			self.skipTest("No hay segunda company disponible")

		other_pos_name = f"{other_company[0].name}::Cargo Foráneo"
		if not frappe.db.exists("Committee Position", other_pos_name):
			other_pos = frappe.get_doc(
				{
					"doctype": "Committee Position",
					"company": other_company[0].name,
					"position_name": "Cargo Foráneo",
					"hierarchy_level": 1,
				}
			)
			other_pos.insert(ignore_permissions=True)
			frappe.db.commit()

		if not self.property_reg:
			self.skipTest("No hay Property Registry disponible")

		m = frappe.get_doc(self._base_member(committee_position=other_pos_name))
		with self.assertRaises(frappe.ValidationError):
			m.insert(ignore_permissions=True)

		frappe.db.delete("Committee Position", {"name": other_pos_name})
		frappe.db.commit()
