# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import UnitTestCase


class TestCommitteePosition(UnitTestCase):
	def setUp(self):
		self.company = self._get_test_company()
		frappe.db.delete("Committee Position", {"company": self.company})
		frappe.db.commit()

	def tearDown(self):
		frappe.db.delete("Committee Position", {"company": self.company})
		frappe.db.commit()

	def _get_test_company(self):
		existing = frappe.db.get_list("Company", limit=1)
		if existing:
			return existing[0].name
		company = frappe.get_doc(
			{
				"doctype": "Company",
				"company_name": "Test Condo CM",
				"abbr": "TCCM",
				"default_currency": "MXN",
				"country": "Mexico",
			}
		)
		company.insert(ignore_permissions=True)
		frappe.db.commit()
		return "Test Condo CM"

	def _make_position(self, position_name="Presidente", hierarchy_level=4, **kwargs):
		return frappe.get_doc(
			{
				"doctype": "Committee Position",
				"company": self.company,
				"position_name": position_name,
				"hierarchy_level": hierarchy_level,
				**kwargs,
			}
		)

	def test_committee_position_creation(self):
		"""Crear cargo básico para un condominio."""
		pos = self._make_position("Presidente", 4)
		pos.insert(ignore_permissions=True)

		self.assertEqual(pos.company, self.company)
		self.assertEqual(pos.position_name, "Presidente")
		self.assertEqual(pos.hierarchy_level, 4)
		# El name se genera como company::position_name
		self.assertIn("Presidente", pos.name)

	def test_committee_position_unique_per_company(self):
		"""No se permite duplicar cargo en el mismo condominio."""
		pos1 = self._make_position("Secretario", 3)
		pos1.insert(ignore_permissions=True)

		pos2 = self._make_position("Secretario", 3)
		with self.assertRaises(frappe.ValidationError):
			pos2.insert(ignore_permissions=True)

	def test_committee_position_same_name_different_company_ok(self):
		"""El mismo nombre de cargo en distinto condominio es válido."""
		other_company = frappe.db.get_list("Company", filters={"name": ["!=", self.company]}, limit=1)
		if not other_company:
			self.skipTest("No hay segunda company disponible para este test")

		pos1 = self._make_position("Vocal", 1)
		pos1.insert(ignore_permissions=True)

		pos2 = frappe.get_doc(
			{
				"doctype": "Committee Position",
				"company": other_company[0].name,
				"position_name": "Vocal",
				"hierarchy_level": 1,
			}
		)
		pos2.insert(ignore_permissions=True)
		frappe.db.delete("Committee Position", {"company": other_company[0].name})
		frappe.db.commit()

	def test_hierarchy_level_must_be_positive(self):
		"""Nivel jerárquico debe ser mayor a 0."""
		pos = self._make_position("Vocal", 0)
		with self.assertRaises(frappe.ValidationError):
			pos.insert(ignore_permissions=True)

	def test_setup_default_positions(self):
		"""setup_default_positions crea los 4 cargos base y es idempotente."""
		from condominium_management.committee_management.doctype.committee_position.committee_position import (
			CommitteePosition,
		)

		created = CommitteePosition.setup_default_positions(self.company)
		self.assertEqual(len(created), 4)
		self.assertIn("Presidente", created)

		# Segunda llamada no crea duplicados
		created_again = CommitteePosition.setup_default_positions(self.company)
		self.assertEqual(len(created_again), 0)

		count = frappe.db.count("Committee Position", {"company": self.company})
		self.assertEqual(count, 4)
