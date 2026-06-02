# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Regression tests: Assembly fields must be mandatory when condominium_meeting_type == "Assembly"
and must NOT be mandatory when condominium_meeting_type == "Community Event".

Covers the mandatory_depends_on + server-side validation fix in event_hooks.py.
"""

import frappe
import pytest
from frappe.utils import nowdate


class TestAssemblyMandatoryFields:
	def _make_assembly(self, **overrides):
		doc = frappe.new_doc("Event")
		doc.update(
			{
				"subject": "Test Assembly",
				"event_category": "Meeting",
				"condominium_meeting_type": "Assembly",
				"starts_on": f"{nowdate()} 10:00:00",
				"asm_type": "Ordinaria",
				"asm_convocation_date": nowdate(),
				"asm_first_call": "09:00:00",
				"asm_second_call": "09:30:00",
				"asm_quorum_first": 75,
				"asm_quorum_second": 51,
			}
		)
		doc.update(overrides)
		return doc

	def _make_community_event(self, **overrides):
		doc = frappe.new_doc("Event")
		doc.update(
			{
				"subject": "Test Community Event",
				"event_category": "Meeting",
				"condominium_meeting_type": "Community Event",
				"starts_on": f"{nowdate()} 18:00:00",
				"ce_event_type": "Social",
				"ce_status": "Planeado",
			}
		)
		doc.update(overrides)
		return doc

	# ── Assembly: campos obligatorios bloqueados si faltan ───────────────────

	def test_assembly_requires_asm_type(self):
		doc = self._make_assembly(asm_type=None)
		with pytest.raises(frappe.exceptions.ValidationError, match="Tipo de Asamblea"):
			doc.run_method("validate")

	def test_assembly_requires_convocation_date(self):
		doc = self._make_assembly(asm_convocation_date=None)
		with pytest.raises(frappe.exceptions.ValidationError, match="Fecha de Convocatoria"):
			doc.run_method("validate")

	def test_assembly_requires_first_call(self):
		doc = self._make_assembly(asm_first_call=None)
		with pytest.raises(frappe.exceptions.ValidationError, match="Hora Primera Convocatoria"):
			doc.run_method("validate")

	def test_assembly_requires_second_call(self):
		doc = self._make_assembly(asm_second_call=None)
		with pytest.raises(frappe.exceptions.ValidationError, match="Hora Segunda Convocatoria"):
			doc.run_method("validate")

	def test_assembly_passes_with_all_required_fields(self):
		doc = self._make_assembly()
		doc.run_method("validate")  # must not raise

	# ── Community Event: campos de asamblea NO son obligatorios ─────────────

	def test_community_event_ignores_asm_type(self):
		doc = self._make_community_event()
		doc.run_method("validate")  # asm_type vacío — no debe lanzar error

	def test_community_event_ignores_asm_convocation_date(self):
		doc = self._make_community_event()
		doc.run_method("validate")  # asm_convocation_date vacío — no debe lanzar error

	def test_community_event_ignores_asm_calls(self):
		doc = self._make_community_event()
		doc.run_method("validate")  # asm_first/second_call vacíos — no debe lanzar error

	# ── Community Event: sus propios campos de registro ──────────────────────

	def test_community_event_registration_requires_max_capacity(self):
		doc = self._make_community_event(ce_registration_required=1, ce_max_capacity=0)
		with pytest.raises(frappe.exceptions.ValidationError, match="capacidad máxima"):
			doc.run_method("validate")

	def test_community_event_registration_requires_rsvp_deadline(self):
		doc = self._make_community_event(
			ce_registration_required=1,
			ce_max_capacity=50,
			ce_rsvp_deadline=None,
		)
		with pytest.raises(frappe.exceptions.ValidationError, match="fecha límite"):
			doc.run_method("validate")
