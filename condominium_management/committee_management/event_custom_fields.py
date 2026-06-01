# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

"""
Custom fields on Frappe Event DocType for condominium event management.

Called from after_migrate hook — idempotent, safe to run multiple times.
Only creates fields that don't exist yet; never modifies or deletes existing ones.
"""

import frappe

MEETING_DEPENDS = "eval:doc.event_category=='Meeting'"
COMMITTEE_DEPENDS = "eval:doc.condominium_meeting_type=='Committee Meeting'"

CUSTOM_FIELDS = [
	# ── Meeting type selector (visible when event_category == Meeting) ─────────
	{
		"dt": "Event",
		"fieldname": "condominium_meeting_type",
		"fieldtype": "Select",
		"label": "Tipo de Reunión",
		"options": "Committee Meeting\nAssembly\nWork Meeting",
		"insert_after": "event_participants",
		"depends_on": MEETING_DEPENDS,
	},
	# ── Committee Meeting specific ─────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "committee_meeting_type",
		"fieldtype": "Select",
		"label": "Tipo de Sesión",
		"options": "Ordinaria\nExtraordinaria\nEmergencia\nTrabajo",
		"insert_after": "committee_tab",
		"depends_on": COMMITTEE_DEPENDS,
	},
	# ── Agenda child table ─────────────────────────────────────────────────────
	{
		"dt": "Event",
		"fieldname": "committee_agenda_section",
		"fieldtype": "Section Break",
		"label": "Agenda",
		"insert_after": "committee_meeting_type",
		"depends_on": COMMITTEE_DEPENDS,
	},
	{
		"dt": "Event",
		"fieldname": "committee_agenda_items",
		"fieldtype": "Table",
		"label": "Puntos de Agenda",
		"options": "Event Committee Agenda Item",
		"insert_after": "committee_agenda_section",
		"depends_on": COMMITTEE_DEPENDS,
	},
]


def setup_event_committee_fields():
	"""Create custom fields on Event for committee meeting support.

	Idempotent: skips fields that already exist.
	"""
	created = []
	for field in CUSTOM_FIELDS:
		name = f"{field['dt']}-{field['fieldname']}"
		if frappe.db.exists("Custom Field", name):
			continue
		doc = frappe.get_doc({"doctype": "Custom Field", **field})
		doc.insert(ignore_permissions=True)
		created.append(field["fieldname"])

	if created:
		frappe.db.commit()

	return created
